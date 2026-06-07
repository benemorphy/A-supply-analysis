供应链 OWL 本体from rdflib import Graph, Namespace, Literal, RDF, RDFS, OWL, XSD
import json, urllib.request, pathlib

NS = Namespace("http://supply-chain.ontology/")
SC = Namespace("http://supply-chain.ontology/terms/")
g = Graph()
g.bind("sc", SC)
g.bind("owl", OWL)

g.add((SC.Company, RDF.type, OWL.Class))
g.add((SC.SupplyChainRelation, RDF.type, OWL.Class))
g.add((SC.Risk, RDF.type, OWL.Class))
g.add((SC.HighDependencyRisk, RDF.type, OWL.Class))

g.add((SC.suppliesTo, RDF.type, OWL.ObjectProperty))
g.add((SC.purchasesFrom, RDF.type, OWL.ObjectProperty))
g.add((SC.hasRatio, RDF.type, OWL.DatatypeProperty))
g.add((SC.hasRatio, RDFS.range, XSD.float))
g.add((SC.hasRiskLevel, RDF.type, OWL.DatatypeProperty))

v = json.loads(urllib.request.urlopen("http://localhost:8765/api/visualize", timeout=5).read())
for n in v['nodes']:
    c = SC[n['id']]; g.add((c, RDF.type, SC.Company))
for l in v['links']:
    s, t = SC[l['source']], SC[l['target']]
    r = float(l.get('value', 0))
    g.add((s, SC.suppliesTo, t)); g.add((t, SC.purchasesFrom, s))
    if r > 25:
        risk = SC["risk_{}_{}".format(l['source'], l['target'])]
        g.add((risk, RDF.type, SC.HighDependencyRisk))
        g.add((risk, SC.hasRiskLevel, Literal("high")))

out = pathlib.Path("D:/open_claw_agent/A-supply-analysis/ontology/supply_chain.ttl")
g.serialize(destination=str(out), format="turtle")
print(f"OWL 本体已保存: {out}")
print(f"  类: {len(list(g.triples((None, RDF.type, OWL.Class))))}")
print(f"  实例: {len(list(g.triples((None, RDF.type, SC.Company))))} 公司")
print(f"  关系: {len(list(g.triples((None, SC.suppliesTo, None))))} 条")
print(f"  推理风险: {len(list(g.triples((None, RDF.type, SC.HighDependencyRisk))))} 项")

q = "PREFIX sc:<http://supply-chain.ontology/terms/> SELECT ?risk WHERE {?risk a sc:HighDependencyRisk}"
for row in g.query(q): print(f"  高风险: {row.risk}")
