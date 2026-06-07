"""GA -> A-supply-analysis 客户端"""
import json, urllib.request, urllib.parse

API_HOST = "http://localhost:8765"

class SupplyClient:
    def __init__(self, host=API_HOST):
        self.host = host

    def _get(self, path, params=None):
        url = f"{self.host}{path}"
        if params:
            qs = "&".join(f"{urllib.parse.quote(k)}={urllib.parse.quote(str(v))}" for k, v in params.items() if v)
            url += "?" + qs
        return json.loads(urllib.request.urlopen(url, timeout=10).read())

    def _post(self, path, data):
        req = urllib.request.Request(f"{self.host}{path}",
            json.dumps(data).encode(), {"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=10).read())

    def list_companies(self):
        return self._get("/api/companies")

    def add_company(self, name, stock_code=None, industry=None):
        return self._post("/api/companies", {"name": name, "stock_code": stock_code, "industry": industry})

    def push_relation(self, source, target, rel_type, year, ratio=0):
        return self._post("/api/supply-chains", {
            "source": source, "target": target, "relation_type": rel_type, "year": year, "ratio": ratio
        })

    def query_relations(self, company=None, year=None, rel_type=None):
        return self._get("/api/supply-chains", {"company": company, "year": year, "relation_type": rel_type})

    def clean_text(self, company, year, raw_text):
        return self._post("/api/clean", {"company": company, "year": year, "raw_text": raw_text})
