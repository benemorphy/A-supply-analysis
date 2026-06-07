import os
os.environ.get("NEO4J_PASSWORD","")"
A-supply-analysis FastAPI 服务 — 供应链数据查询/推送/清洗

端口: 8765

GA 通过此 API 访问和操控供应链数据。
os.environ.get("NEO4J_PASSWORD","")"

import sys, os, json, uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
# GA 路径 (LLM 清洗用)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Beneh", "GA"))

from models.models import CompanyBase, SupplyRelation, RawTextInput, CleanResult

app = FastAPI(title="A-supply-analysis", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── 内存数据存储 (后续可迁移到 Neo4j/SQLite) ──
_companies: dict = {}        # name -> CompanyBase
_relations: list = []         # List[SupplyRelation]

# ── 公司接口 ──

@app.get("/api/companies", response_model=List[CompanyBase])
def list_companies():
    os.environ.get("NEO4J_PASSWORD","")"获取所有公司os.environ.get("NEO4J_PASSWORD","")"
    return list(_companies.values())

@app.post("/api/companies")
def add_company(company: CompanyBase):
    os.environ.get("NEO4J_PASSWORD","")"添加公司os.environ.get("NEO4J_PASSWORD","")"
    _companies[company.name] = company
    return {"status": "ok", "name": company.name}

# ── 供应链关系接口 ──

@app.get("/api/supply-chains", response_model=List[SupplyRelation])
def query_supply_chains(company: str = None, year: int = None, relation_type: str = None):
    os.environ.get("NEO4J_PASSWORD","")"查询供应链关系os.environ.get("NEO4J_PASSWORD","")"
    results = _relations
    if company:
        results = [r for r in results if r.source == company or r.target == company]
    if year:
        results = [r for r in results if r.year == year]
    if relation_type:
        results = [r for r in results if r.relation_type == relation_type]
    return results

@app.post("/api/supply-chains")
def push_supply_chain(relation: SupplyRelation):
    os.environ.get("NEO4J_PASSWORD","")"推送/添加供应链关系os.environ.get("NEO4J_PASSWORD","")"
    _relations.append(relation)
    return {"status": "ok", "count": len(_relations)}

# ── 清洗接口 (调用 GA 的 LLM) ──

@app.post("/api/clean", response_model=CleanResult)
def clean_supply_data(input_data: RawTextInput):
    os.environ.get("NEO4J_PASSWORD","")"调用 GA 的 LLM 清洗年报文本os.environ.get("NEO4J_PASSWORD","")"
    from clean_pipeline import clean_supply_chain
    items = clean_supply_chain(input_data.raw_text)
    
    filtered = 0
    clean_items = []
    # 统计过滤
    for item in items:
        if item.get("name") and len(item["name"]) > 1:
            clean_items.append(SupplyRelation(
                source=input_data.company,
                target=item["name"],
                relation_type=item.get("type", "客户"),
                year=input_data.year,
                ratio=float(item.get("ratio", "0%").replace("%", os.environ.get("NEO4J_PASSWORD","")))
            ))
        else:
            filtered += 1
    
    return CleanResult(
        company=input_data.company,
        year=input_data.year,
        items=clean_items,
        filtered_items=filtered
    )

# ── 健康检查 ──

@app.get("/api/health")
def health():
    return {"status": "ok", "companies": len(_companies), "relations": len(_relations)}

# ── 启动 ──

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
