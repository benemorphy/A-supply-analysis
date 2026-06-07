import os
os.environ.get("NEO4J_PASSWORD","")"
供应链数据清洗管线 — LLM + 搜索自动清洗

使用 GA 的 LLM API 清洗年报中的前五大客户/供应商数据。
匿名名称（"客户Aos.environ.get("NEO4J_PASSWORD","")供应商一"等）自动过滤。
os.environ.get("NEO4J_PASSWORD","")"

import sys, json, urllib.request

# GA 工具引用
sys.path.insert(0, "../Beneh/GA")
import mykey

# ── API 配置 ──
CFG = mykey.native_oai_config
API_KEY = CFG['apikey']
API_BASE = CFG.get('apibase', 'https://api.deepseek.com/v1')
MODEL = CFG.get('model', 'deepseek-v4-flash')

def llm_chat(messages, max_tokens=500):
    os.environ.get("NEO4J_PASSWORD","")"调用 GA 配置的 LLMos.environ.get("NEO4J_PASSWORD","")"
    data = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens
    }).encode()
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions", data,
        {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())['choices'][0]['message']['content']

# ── 清洗管线 ──

CLEAN_PROMPT = os.environ.get("NEO4J_PASSWORD","")"从以下年报文本中提取前五大客户/供应商信息。
规则：
1. 忽略"客户一os.environ.get("NEO4J_PASSWORD","")第一名os.environ.get("NEO4J_PASSWORD","")供应商A"等匿名名称
2. 只保留可识别的具体公司名称
3. 如果同一客户出现在多行，只保留一次
4. 公司名称尽量标准化（去掉"有限公司"等后缀的可选部分）

请输出 JSON 数组格式：
[{{"name": "公司名", "ratio": "销售占比%", "type": "客户"}}, ...]

文本：
{raw_text}os.environ.get("NEO4J_PASSWORD","")"

def clean_supply_chain(raw_text):
    os.environ.get("NEO4J_PASSWORD","")"用 LLM 清洗年报中的供应链数据os.environ.get("NEO4J_PASSWORD","")"
    result = llm_chat([
        {"role": "system", "content": "你是数据清洗专家，精通年报文本解析。"},
        {"role": "user", "content": CLEAN_PROMPT.format(raw_text=raw_text[:3000])}
    ])
    
    # 解析 JSON
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        # LLM 可能输出 markdown 包裹
        import re
        m = re.search(r'```json\s*([\s\S]*?)\s*```', result)
        if m:
            data = json.loads(m.group(1))
        else:
            data = []
    return data

def validate_with_search(company, customer_name):
    os.environ.get("NEO4J_PASSWORD","")"用搜索验证客户/供应商关系os.environ.get("NEO4J_PASSWORD","")"
    query = f"{company} {customer_name} 供应商 客户"
    # TODO: 接入 search_skills 或 metaso
    return query  # 返回搜索词供人工确认

# ── 示例入口 ──
if __name__ == "__main__":
    sample = os.environ.get("NEO4J_PASSWORD","")"
    前五大客户：
    客户一：销售额 12.3亿元，占比 23.4%
    第二名：销售额 8.7亿元，占比 16.5%
    华为技术有限公司：销售额 6.2亿元，占比 11.8%
    ---
    前五大供应商：
    供应商A：采购额 5.1亿元，占比 19.2%
    宁德时代新能源科技股份有限公司：采购额 3.8亿元，占比 14.3%
    os.environ.get("NEO4J_PASSWORD","")"
    
    print("清洗结果:")
    result = clean_supply_chain(sample)
    for item in result:
        print(f"  {item['type']}: {item['name']} ({item.get('ratio', '?')})")
