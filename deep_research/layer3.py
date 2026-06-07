Layer 3: 智能分析 - 风险传导模拟 + 全景报告import sys, json, urllib.request
sys.path.insert(0, "D:/open_claw_agent/Beneh/GA")
import mykey

cfg = mykey.native_oai_config
api_key, api_base, model = cfg['apikey'], cfg['apibase'], cfg['model']

sys.path.insert(0, "D:/open_claw_agent/A-supply-analysis")
import urllib.request

# 获取数据
h = json.loads(urllib.request.urlopen("http://localhost:8765/api/health", timeout=5).read())
r = json.loads(urllib.request.urlopen("http://localhost:8765/api/report", timeout=5).read())
v = json.loads(urllib.request.urlopen("http://localhost:8765/api/visualize", timeout=5).read())
risk = json.loads(urllib.request.urlopen("http://localhost:8765/api/risk-analysis", timeout=5).read())

# LLM 深度分析
prompt = f你是新能源汽车供应链分析师。基于以下数据生成深度分析报告：

## 总体数据
- 公司数: {h['companies']}
- 关系数: {h['relations']}

## 供应链关系
{r['report'][:2000]}

## 可视化数据 ({len(v['nodes'])} 节点, {len(v['links'])} 边)
节点: {[n['id'] for n in v['nodes']]}
边: {[(l['source'],l['target'],l['value']) for l in v['links']]}

## 已知风险 ({risk['risk_count']} 项)
{json.dumps(risk['risks'], ensure_ascii=False, indent=2)}

## 分析要求
1. 产业链全景图描述（从锂矿到整车）
2. 关键节点识别（不可替代的公司）
3. 风险传导路径：若宁德时代减产20%，哪些公司受影响？影响程度？
4. 供应链改进建议

请用中文回复，结构化输出。
data = json.dumps({"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":3000}).encode()
req = urllib.request.Request(f"{api_base}/chat/completions",data,
    {"Authorization":f"Bearer {api_key}","Content-Type":"application/json"})
resp = json.loads(urllib.request.urlopen(req,timeout=30).read())
analysis = resp['choices'][0]['message']['content']

print("==" * 30)
print(analysis)
print("==" * 30)

# 保存报告
pathlib.Path("deep_research/layer3_report.md").write_text(analysis, encoding="utf-8")
print("\n报告已保存到 deep_research/layer3_report.md")
