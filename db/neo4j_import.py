import os
os.environ.get("NEO4J_PASSWORD","")"供应链数据 -> Neo4j 导入脚本os.environ.get("NEO4J_PASSWORD","")"

import sys, urllib.request, json
sys.path.insert(0, "D:/open_claw_agent/A-supply-analysis")
from clients.supply_client import SupplyClient
from neo4j import GraphDatabase


def import_to_neo4j(uri="bolt://localhost:7687", user="neo4j", password=os.environ.get("NEO4J_PASSWORD","image1969")):
    client = SupplyClient()
    companies = client.list_companies()
    rels = client.query_relations()
    print(f"API: {len(companies)} 公司, {len(rels)} 关系")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")
        for c in companies:
            s.run("CREATE (:Company {name:$n, segment:'?'})", n=c['name'])
        for r in rels:
            s.run("MATCH (a:Company{name:$s}),(b:Company{name:$t}) CREATE (a)-[:SUPPLIES{ratio:$r}]->(b)",
                  s=r['source'], t=r['target'], r=float(r.get('ratio', 0) or 0))
        cn = s.run("MATCH (n) RETURN count(n)").single()[0]
        cr = s.run("MATCH ()-[r]->() RETURN count(r)").single()[0]
        print(f"Neo4j: {cn} 节点, {cr} 关系")
    driver.close()


if __name__ == "__main__":
    import_to_neo4j()
