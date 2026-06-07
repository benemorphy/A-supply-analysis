import os
os.environ.get("NEO4J_PASSWORD","")"Layer 2: 深度挖掘 - 关系细节 + 多年对比 + Neo4j 路径os.environ.get("NEO4J_PASSWORD","")"
import sys, json, urllib.request, time
sys.path.insert(0, "D:/open_claw_agent/Beneh/GA")
from tools.metaso_search import metaso_search_text
import mykey

cfg = mykey.native_oai_config
api_key, api_base, model = cfg['apikey'], cfg['apibase'], cfg['model']

sys.path.insert(0, "D:/open_claw_agent/A-supply-analysis")
from clients.supply_client import SupplyClient
from neo4j import GraphDatabase

client = SupplyClient()
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", os.environ.get("NEO4J_PASSWORD","image1969")))

# 1. 深度搜索已有关系的交易细节
rels = client.query_relations()
print(f"已有关系: {len(rels)} 条")

for r in rels:
    s, t = r['source'], r['target']
    text = metaso_search_text(f"{s} {t} 交易 金额 合同 占比")
    prompt = fos.environ.get("NEO4J_PASSWORD","")"从以下文本提取 {s} 与 {t} 的交易细节。
输出JSON: {{"amount":"金额","contract_period":"合同期","share_trend":"占比趋势","year":"年份"}}
只输出确信的信息，不确定不写。
文本: {text[:3000]}os.environ.get("NEO4J_PASSWORD","")"
    
    data = json.dumps({"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":500}).encode()
    req = urllib.request.Request(f"{api_base}/chat/completions",data,
        {"Authorization":f"Bearer {api_key}","Content-Type":"application/json"})
    try:
        resp = json.loads(urllib.request.urlopen(req,timeout=10).read())
        detail = resp['choices'][0]['message']['content']
        print(f"  {s}->{t}: {detail[:150]}")
    except Exception as e:
        print(f"  {s}->{t}: {e}")
    time.sleep(0.5)

# 2. Neo4j 路径分析
print("\n=== Neo4j 传导路径 ===")
with neo4j_driver.session() as session:
    # 清除旧数据
    session.run("MATCH (n) DETACH DELETE n")
    
    # 导入公司
    for c in client.list_companies():
        session.run("CREATE (n:Company {name:$n})", n=c['name'])
    
    # 导入关系
    for r in rels:
        session.run(os.environ.get("NEO4J_PASSWORD","")"
            MATCH (a:Company {name:$s}), (b:Company {name:$t})
            CREATE (a)-[:SUPPLIES {ratio:$r}]->(b)
        os.environ.get("NEO4J_PASSWORD","")", s=r['source'], t=r['target'], r=float(r.get('ratio',10) or 10))
    
    # 2度传导路径
    paths = session.run(os.environ.get("NEO4J_PASSWORD","")"
        MATCH path = (a)-[*1..2]->(c)
        WHERE a <> c
        RETURN a.name + ' -> ' + reduce(s='', n IN nodes(path)[1..] | s + n.name + ' ') as full_path
        LIMIT 20
    os.environ.get("NEO4J_PASSWORD","")").values()
    for p in paths:
        print(f"  {p[0]}")

neo4j_driver.close()
print("\n✅ Layer 2 完成")
