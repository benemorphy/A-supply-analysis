"""Supply chain data cleaning pipeline - LLM-based text cleaning"""
import sys, json, urllib.request
sys.path.insert(0, "../Beneh/GA")
import mykey

CFG = mykey.native_oai_config
API_KEY = CFG['apikey']
API_BASE = CFG.get('apibase', 'https://api.deepseek.com/v1')
MODEL = CFG.get('model', 'deepseek-v4-flash')

CLEAN_PROMPT = """From the following annual report text, extract top 5 customer/supplier information.
Rules:
1. Ignore anonymous names like "客户一", "第一名", "供应商A" etc
2. Only keep identifiable company names
3. Output JSON array: [{"name": "company", "ratio": "ratio%", "type": "客户/供应商"}]

Text:
{raw_text}"""

def llm_chat(messages, max_tokens=500):
    data = json.dumps({"model": MODEL, "messages": messages, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(f"{API_BASE}/chat/completions", data,
        {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp['choices'][0]['message']['content']

def clean_supply_chain(raw_text):
    prompt = CLEAN_PROMPT.format(raw_text=raw_text[:3000])
    resp = llm_chat([{"role": "user", "content": prompt}])
    import re
    json_str = re.search(r'\[.*?\]', resp, re.DOTALL)
    if json_str:
        try:
            return json.loads(json_str.group(0))
        except:
            return []
    return []
