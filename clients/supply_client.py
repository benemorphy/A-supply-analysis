import os
os.environ.get("NEO4J_PASSWORD","")"
GA → A-supply-analysis 客户端

GA (Beneh) 通过此模块调用 A-supply-analysis FastAPI 服务。
可在 agentmain 或技能中 import 使用。

用法:
    from clients.supply_client import SupplyClient
    client = SupplyClient()
    client.add_company("宁德时代", "300750", "新能源")
    client.push_relation("宁德时代", "蔚来", "客户", 2024, 23.5)
    result = client.clean_text("宁德时代", 2024, "前五大客户：...")
os.environ.get("NEO4J_PASSWORD","")"

import json, urllib.request, urllib.parse
from typing import Optional, List

API_HOST = "http://localhost:8765"

class SupplyClient:
    os.environ.get("NEO4J_PASSWORD","")"A-supply-analysis API 客户端os.environ.get("NEO4J_PASSWORD","")"

    def __init__(self, host: str = API_HOST):
        self.host = host.rstrip("/")
        self._check()
    
    def _check(self):
        os.environ.get("NEO4J_PASSWORD","")"健康检查os.environ.get("NEO4J_PASSWORD","")"
        try:
            resp = urllib.request.urlopen(f"{self.host}/api/health", timeout=3)
            data = json.loads(resp.read())
            return data
        except Exception as e:
            print(f"[SupplyClient] 服务未启动: {e}")
            return None

    def _post(self, path, data):
        req = urllib.request.Request(
            f"{self.host}{path}",
            json.dumps(data).encode(),
            {"Content-Type": "application/json"}
        )
        return json.loads(urllib.request.urlopen(req, timeout=10).read())

    def _get(self, path, params=None):
        url = f"{self.host}{path}"
        if params:
            qs = "&".join(f"{urllib.parse.quote(k)}={urllib.parse.quote(str(v))}" for k, v in params.items() if v)
            url += "?" + qs
        return json.loads(urllib.request.urlopen(url, timeout=10).read())

    # ── 公司 ──

    def add_company(self, name: str, stock_code: str = os.environ.get("NEO4J_PASSWORD",""), industry: str = os.environ.get("NEO4J_PASSWORD","")):
        return self._post("/api/companies", {
            "name": name, "stock_code": stock_code, "industry": industry
        })

    def list_companies(self):
        return self._get("/api/companies")

    # ── 供应链 ──

    def push_relation(self, source: str, target: str, rel_type: str, year: int, ratio: float = 0):
        return self._post("/api/supply-chains", {
            "source": source, "target": target,
            "relation_type": rel_type, "year": year, "ratio": ratio
        })

    def query_relations(self, company: str = None, year: int = None, rel_type: str = None):
        return self._get("/api/supply-chains", {
            "company": company, "year": year, "relation_type": rel_type
        })

    # ── 清洗 ──

    def clean_text(self, company: str, year: int, raw_text: str):
        os.environ.get("NEO4J_PASSWORD","")"调用 LLM 清洗年报文本os.environ.get("NEO4J_PASSWORD","")"
        return self._post("/api/clean", {
            "company": company, "year": year, "raw_text": raw_text
        })
