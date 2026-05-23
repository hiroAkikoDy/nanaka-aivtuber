"""
ブログ記事メタデータ抽出エージェント（Article Extractor）
nanaka-farm.com の WordPress 記事を LLM でメタデータ抽出し AuraDB に保存する。

設計原則:
- wp_id で MERGE -> べき等性を保証（何度実行しても重複しない）
- watercress_relevance < 0.1 かつ domain == 'personal' の記事はノードを作らない
- バッチサイズ5件ずつ処理し進捗を表示する
"""
import os
import sys
import json
import time
import re
import requests
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)
DB_NAME = os.getenv("NEO4J_USERNAME")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WP_API_BASE = "https://nanaka-farm.com/blog/wp-json/wp/v2/posts"

EXTRACTION_PROMPT = """あなたはブログ記事のメタデータ分類エキスパートです。
ナナカファーム（熊本のクレソン農家）のブログ記事を分析し、
指定スキーマのJSONのみ返してください（説明文不要）。

## 記事情報
タイトル: {title}
抜粋: {excerpt}

## 抽出スキーマ
{{
  "topics": ["トピック1", "トピック2"],
  "ingredients_mentioned": ["食材名1", "食材名2"],
  "intents_mentioned": ["健康", "時短", "ダイエット", "おもてなし", "余り活用"],
  "watercress_relevance": 0.0,
  "domain": "food",
  "is_evergreen": true,
  "summary": "この記事の要約（150字以内）"
}}

## 分類基準
- watercress_relevance: クレソン直結=0.9, 料理・栄養=0.6, 農業一般=0.4, 個人日記=0.1
- domain:
  - food: 料理・レシピ・栄養
  - farm: 農業・栽培・クレソン
  - personal: 家族・旅行・日常
  - tech: IT・システム・開発
  - other: その他
- intents_mentioned: 記事本文から推測できるもののみ（確信がなければ空配列）
- ingredients_mentioned: クレソン以外の食材名のみ（クレソンは除外）"""


def fetch_wp_articles(page: int = 1, per_page: int = 100) -> tuple[list[dict], int]:
    params = {
        "per_page": per_page,
        "page": page,
        "_fields": "id,title,link,date,excerpt"
    }
    resp = requests.get(WP_API_BASE, params=params, timeout=30)
    resp.raise_for_status()
    total = int(resp.headers.get("X-WP-Total", 0))
    return resp.json(), total


def get_registered_wp_ids() -> set[int]:
    with driver.session(database=DB_NAME) as session:
        result = session.run("MATCH (a:Article) RETURN a.wp_id AS wp_id")
        return {r["wp_id"] for r in result}


def get_unregistered_articles(page: int = 1, per_page: int = 100) -> tuple[list[dict], int]:
    articles, total = fetch_wp_articles(page, per_page)
    registered_ids = get_registered_wp_ids()
    unregistered = [a for a in articles if a["id"] not in registered_ids]
    return unregistered, total


def extract_article_metadata(title: str, excerpt: str) -> dict | None:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT.format(
                    title=title,
                    excerpt=excerpt
                )
            }],
            temperature=0.1,
            max_tokens=500,
        )
        content = response.choices[0].message.content or ""
        clean = content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        print(f"  [WARN] extract error: {e}")
        return None


def should_skip(data: dict) -> bool:
    return (data.get("watercress_relevance", 0) < 0.1
            and data.get("domain", "") == "personal")


def create_article_node(tx, wp_id: int, url: str, published_at: str,
                        raw_title: str, data: dict):
    tx.run("""
        MERGE (a:Article {wp_id: $wp_id})
        SET a.title = $title,
            a.url = $url,
            a.published_at = datetime($published_at),
            a.topics = $topics,
            a.ingredients_mentioned = $ingredients,
            a.watercress_relevance = $watercress_relevance,
            a.domain = $domain,
            a.is_evergreen = $is_evergreen,
            a.summary = $summary,
            a.created_at = datetime()
    """,
        wp_id=wp_id,
        title=raw_title,
        url=url,
        published_at=published_at,
        topics=data.get("topics", []),
        ingredients=data.get("ingredients_mentioned", []),
        watercress_relevance=data.get("watercress_relevance", 0.0),
        domain=data.get("domain", "other"),
        is_evergreen=data.get("is_evergreen", False),
        summary=data.get("summary", "")
    )

    for ingredient_name in data.get("ingredients_mentioned", []):
        tx.run("""
            MERGE (i:Ingredient {name: $name})
            WITH i
            MATCH (a:Article {wp_id: $wp_id})
            MERGE (a)-[:MENTIONS]->(i)
        """, name=ingredient_name, wp_id=wp_id)

    for intent_label in data.get("intents_mentioned", []):
        tx.run("""
            MERGE (t:Intent {label: $label})
            WITH t
            MATCH (a:Article {wp_id: $wp_id})
            MERGE (a)-[:MENTIONS]->(t)
        """, label=intent_label, wp_id=wp_id)


def run_batch(page: int = 1, per_page: int = 20, auto_approve: bool = False):
    articles, total = get_unregistered_articles(page=page, per_page=per_page)
    print(f"total: {total} | unregistered: {len(articles)} [page={page}]")

    approved = []
    skipped_filter = []
    skipped_user = []

    for i, article in enumerate(articles, 1):
        wp_id = article["id"]
        url = article["link"]
        published_at = article["date"]
        title = article["title"]["rendered"]
        excerpt_html = article["excerpt"]["rendered"]
        excerpt = re.sub(r'<[^>]+>', '', excerpt_html).strip()[:300]

        print(f"\n[{i}/{len(articles)}] extracting... wp_id={wp_id}")
        print(f"  title: {title}")

        time.sleep(0.5)
        data = extract_article_metadata(title, excerpt)

        if not data:
            print("  [FAIL] extraction failed -> skip")
            skipped_user.append(wp_id)
            continue

        wr = data.get('watercress_relevance', 0.0)
        print(f"  domain: {data['domain']} | relevance: {wr:.2f} | evergreen: {data.get('is_evergreen')}")
        print(f"  ingredients: {data.get('ingredients_mentioned', [])}")
        print(f"  intents: {data.get('intents_mentioned', [])}")

        if should_skip(data):
            print("  [SKIP] filtered out (personal + low relevance)")
            skipped_filter.append(wp_id)
            continue

        if auto_approve:
            approved.append((wp_id, url, published_at, title, data))
            print("  [OK] auto approved")
        else:
            ans = input("  approve? [y/n]: ").strip().lower()
            if ans == "y":
                approved.append((wp_id, url, published_at, title, data))
                print("  [OK] approved")
            else:
                skipped_user.append(wp_id)
                print("  [SKIP]")

    if approved:
        print(f"\nWriting to AuraDB... ({len(approved)} articles)")
        with driver.session(database=DB_NAME) as session:
            for wp_id, url, pub, title, data in approved:
                try:
                    session.execute_write(
                        create_article_node, wp_id, url, pub, title, data
                    )
                    print(f"  + {title[:40]}")
                except Exception as e:
                    print(f"  x wp_id={wp_id}: {e}")

    print(f"\napproved: {len(approved)} | filtered: {len(skipped_filter)} | skipped: {len(skipped_user)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Article Extractor Agent")
    parser.add_argument("--page", type=int, default=1, help="WordPress API page number")
    parser.add_argument("--per-page", type=int, default=20, help="Articles per page (max 100)")
    parser.add_argument("--auto", action="store_true", help="Auto approve mode")
    args = parser.parse_args()

    print("=" * 60)
    print("Article Extractor Agent")
    print(f"  page={args.page} | per_page={args.per_page} | auto={args.auto}")
    print("=" * 60)

    run_batch(page=args.page, per_page=args.per_page, auto_approve=args.auto)
    driver.close()
    print("Done")
