Layer 1: 广度扩展 - 搜索+LLM提取+入库import sys, json, urllib.request, time
sys.path.insert(0, "D:/open_claw_agent/Beneh/GA")
from tools.metaso_search import metaso_search_text
import mykey

cfg = mykey.native_oai_config
api_key, api_base, model = cfg['apikey'], cfg['apibase'], cfg['model']

sys.path.insert(0, "D:/open_claw_agent/A-supply-analysis")
from clients.supply_client import SupplyClient
client = SupplyClient()

companies = ["天齐锂业","华友钴业","当升科技","恩捷股份","天赐材料","宁德时代","比亚迪"]

for c in companies:
    print(f"搜索 {c}...")
    text = metaso_search_text(f"{c} 2024 年报 前五大客户 前五大供应商 供应链")
    if not text: text = "(无搜索结果)"
    
    prompt = f"从以下文本中提取{c}的客户或供应商信息。忽略匿名名称(客户一/供应商A等)。输出JSON数组格式。\n\n文本:{text[:3000]}"
    
    data = json.dumps({"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":1000}).encode()
    req = urllib.request.Request(f"{api_base}/chat/completions",data,
        {"Authorization":f"Bearer {api_key}","Content-Type":"application/json"})
    try:
        resp = json.loads(urllib.request.urlopen(req,timeout=15).read())
        result = resp['choices'][0]['message']['content']
        print(f"  -> {result[:200]}")
    except Exception as e:
        print(f"  -> error: {e}")
    time.sleep(0.5)
