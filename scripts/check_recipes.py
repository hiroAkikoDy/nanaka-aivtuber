"""Check Recipe DESCRIBES status on AuraDB"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)

with driver.session() as session:
    result = session.run(
        """
        MATCH (r:Recipe)
        OPTIONAL MATCH (c:Chunk)-[:DESCRIBES]->(r)
        RETURN r.name AS name,
               r.final_score AS score,
               r.validated AS validated,
               count(c) AS chunk_count
        ORDER BY r.final_score DESC
        """
    )
    for record in result:
        v = "T" if record["validated"] else "F"
        print(f"  {record['name']} | score={record['score']} | validated={v} | chunks={record['chunk_count']}")

driver.close()
