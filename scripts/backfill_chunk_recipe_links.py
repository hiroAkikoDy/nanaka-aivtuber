"""
Backfill DESCRIBESリレーション: Chunk → Recipe

AIVTuber側でMERGE作成されたRecipeノードはChunkと
DESCRIBESリレーションで接続されていないため、
RAG検索時にrerank_by_final_scoreがスコアを取得できない。

このスクリプトはRecipe名でChunkのtextを検索し、
DESCRIBESリレーションを自動作成する。
"""

import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def get_driver():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    return driver


def find_orphan_recipes(session):
    result = session.run(
        """
        MATCH (r:Recipe)
        WHERE r.validated = true
          AND NOT EXISTS {
            MATCH (c:Chunk)-[:DESCRIBES]->(r)
          }
        RETURN r.name AS name, r.final_score AS final_score, r.validated AS validated
        ORDER BY r.final_score DESC
        """
    )
    return [dict(record) for record in result]


def backfill_links(session):
    result = session.run(
        """
        MATCH (c:Chunk), (r:Recipe)
        WHERE r.validated = true
          AND NOT EXISTS {
            MATCH (c2:Chunk)-[:DESCRIBES]->(r)
          }
          AND c.text CONTAINS r.name
        MERGE (c)-[:DESCRIBES]->(r)
        RETURN r.name AS recipe_name, count(c) AS linked_chunks
        """
    )
    linked = {}
    for record in result:
        linked[record["recipe_name"]] = record["linked_chunks"]
    return linked


def create_backfill_tasks(session, orphan_names):
    for name in orphan_names:
        task_id = str(uuid.uuid4())[:8]
        session.run(
            """
            MERGE (t:BackfillTask {
                id: $task_id,
                recipe_name: $recipe_name,
                reason: 'no_matching_chunk',
                priority: 'high',
                created_at: datetime(),
                status: 'pending'
            })
            """,
            task_id=task_id,
            recipe_name=name,
        )


def main():
    print("=== バックフィル開始 ===")
    driver = get_driver()

    with driver.session() as session:
        orphans = find_orphan_recipes(session)
        print(f"対象Recipe: {len(orphans)}件")
        for r in orphans:
            print(f"  - {r['name']} (final_score={r['final_score']})")

        if not orphans:
            print("バックフィル対象なし。終了します。")
            driver.close()
            return

        linked = backfill_links(session)

        linked_names = set(linked.keys())
        still_orphan = [r["name"] for r in orphans if r["name"] not in linked_names]

        print()
        for name, count in linked.items():
            print(f"  [OK] {name} -> Chunk {count}件接続")
        for name in still_orphan:
            print(f"  [NG] {name} -> Chunkなし")

        if still_orphan:
            create_backfill_tasks(session, still_orphan)
            print(f"\nBackfillTask追加: {len(still_orphan)}件")

        print()
        print("=== バックフィル完了 ===")
        print(f"接続成功: {len(linked)}件")
        print(f"BackfillTask追加: {len(still_orphan)}件")

    driver.close()


if __name__ == "__main__":
    main()
