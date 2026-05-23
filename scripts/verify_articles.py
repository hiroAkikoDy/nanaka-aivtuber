"""Verify Article nodes and MENTIONS edges in AuraDB"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)

with driver.session(database=os.getenv("NEO4J_USERNAME")) as session:
    print("=== Article nodes ===")
    result = session.run(
        "MATCH (a:Article) RETURN a.wp_id, a.title, a.domain, a.watercress_relevance, a.url"
    )
    for r in result:
        print(f"  wp_id={r['a.wp_id']} | domain={r['a.domain']} | relevance={r['a.watercress_relevance']}")
        print(f"    title={r['a.title']}")
        print(f"    url={r['a.url']}")

    print("\n=== MENTIONS edges ===")
    result2 = session.run(
        "MATCH (a:Article)-[m:MENTIONS]->(x) RETURN a.title, type(m), labels(x), x.name, x.label"
    )
    for r in result2:
        label = r['labels(x)'][0] if r['labels(x)'] else '?'
        name = r.get('x.name') or r.get('x.label') or '?'
        print(f"  {r['a.title']} -[:MENTIONS]-> ({label}: {name})")

driver.close()
