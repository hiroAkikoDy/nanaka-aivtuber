"""Delete old Article nodes (wrong API endpoint) and re-run"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)
with driver.session(database=os.getenv("NEO4J_USERNAME")) as session:
    result = session.run("MATCH (a:Article) DETACH DELETE a RETURN count(a) AS cnt")
    print(f"Deleted {result.single()['cnt']} Article nodes")
driver.close()
