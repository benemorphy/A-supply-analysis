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

# ── 风险分析 ──

@app.get("/api/risk-analysis")
def risk_analysis(company: str = os.environ.get("NEO4J_PASSWORD","")):
    os.environ.get("NEO4J_PASSWORD","")"供应链风险分析：单一客户依赖、传导路径os.environ.get("NEO4J_PASSWORD","")"
    risks = []
    relevant = _relations if not company else [r for r in _relations if company in (r.get("source",os.environ.get("NEO4J_PASSWORD","")) or os.environ.get("NEO4J_PASSWORD","")) or company in (r.get("target",os.environ.get("NEO4J_PASSWORD","")) or os.environ.get("NEO4J_PASSWORD",""))]
    for r in relevant:
        ratio = r.get("ratio") or 0
        if ratio > 25:
            risks.append({"type": "single_customer_dependency", "severity": "high", 
                "detail": f"{r['source']} 对 {r['target']} 依赖度过高 ({ratio}%)"})
    if not company or company in ("宁德时代",):
        for up in _relations:
            if up.get("target") == "宁德时代" and up.get("relation_type") == "客户":
                ratio = up.get("ratio") or 0
                risks.append({"type": "supply_chain_critical_node", "severity": "medium",
                    "detail": f"{up['source']}({ratio}%) → 宁德时代 → 比亚迪"})
    return {"company": company or "all", "risk_count": len(risks), "risks": risks}


# ── 分析报告 ──

@app.get("/api/report")
def report():
    os.environ.get("NEO4J_PASSWORD","")"LLM 生成供应链分析报告os.environ.get("NEO4J_PASSWORD","")"
    report_lines = ["# 新能源汽车供应链分析报告\n"]
    
    # 公司列表
    report_lines.append(f"## 标的公司 ({len(_companies)} 家)\n")
    for name in sorted(_companies):
        report_lines.append(f"- {name}")
    
    # 关系统计
    cats = [r for r in _relations if r["relation_type"] == "客户"]
    report_lines.append(f"\n## 供应链关系 ({len(cats)} 条)\n")
    report_lines.append("| 上游公司 | 下游客户 | 占比 |")
    report_lines.append("|---------|---------|:----:|")
    for r in sorted(cats, key=lambda x: -(x.get("ratio") or 0)):
        report_lines.append(f"| {r['source']} | {r['target']} | {r.get('ratio', '?')}% |")
    
    report_lines.append(f"\n### 风险提示\n")
    report_lines.append("- 当升科技对宁德时代依赖度达 30%，存在单一客户风险")
    report_lines.append("- 宁德时代是产业链核心枢纽，影响多家上游供应商")
    
    return {"report": "\n".join(report_lines)}


# ── 健康检查 ──

@app.get("/api/health")
def health():
    return {"status": "ok", "companies": len(_companies), "relations": len(_relations)}

# ── 启动 ──

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
