import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from neo4j import GraphDatabase

JST = timezone(timedelta(hours=9))


class MemoryAgent:
    def __init__(self):
        load_dotenv()
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def save_interaction(self, viewer_name: str, comment: str, emotion: str, response: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (v:Viewer {name: $name})
                    ON CREATE SET v.first_seen = datetime($now)
                    SET v.last_seen = datetime($now)
                    CREATE (c:Comment {
                        text: $comment,
                        timestamp: datetime($now),
                        emotion: $emotion,
                        response: $response
                    })
                    CREATE (v)-[:COMMENTED]->(c)
                    """,
                    name=viewer_name,
                    now=now,
                    comment=comment,
                    emotion=emotion,
                    response=response,
                )
        except Exception as e:
            print(f"[MemoryAgent] save_interaction error: {e}")

    def get_memory(self, viewer_name: str) -> str:
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (v:Viewer {name: $name})-[:COMMENTED]->(c:Comment)
                    RETURN c.text AS text, c.response AS response, c.timestamp AS ts, c.emotion AS emotion
                    ORDER BY c.timestamp DESC
                    LIMIT 3
                    """,
                    name=viewer_name,
                )
                records = list(result)
                if not records:
                    return ""
                lines = ["過去の会話履歴:"]
                for r in records:
                    ts_utc = r["ts"]
                    if hasattr(ts_utc, "to_native"):
                        ts_utc = ts_utc.to_native()
                    ts_jst = ts_utc.replace(tzinfo=timezone.utc).astimezone(JST)
                    ts_str = ts_jst.strftime("%Y-%m-%d %H:%M")
                    lines.append(
                        f"- [{ts_str}] コメント「{r['text']}」→ 応答「{r['response']}」"
                    )
                return "\n".join(lines)
        except Exception as e:
            print(f"[MemoryAgent] get_memory error: {e}")
            return ""


if __name__ == "__main__":
    agent = MemoryAgent()
    agent.save_interaction("テスト太郎", "テストコメント", "普通", "テスト応答")
    print(agent.get_memory("テスト太郎"))
    agent.close()
