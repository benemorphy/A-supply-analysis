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


# ── 可视化 ──

@app.get("/api/visualize")
def visualize():
    os.environ.get("NEO4J_PASSWORD","")"返回 D3 力导向图格式的 JSONos.environ.get("NEO4J_PASSWORD","")"
    nodes = {}
    for c in _companies.values():
        segment = "未知"
        for r in _relations:
            if r["source"] == c.name:
                segment = {"客户": "下游", "供应商": "上游"}.get(r["relation_type"], "中游")
        nodes[c.name] = {"id": c.name, "group": segment}
    
    links = []
    for r in _relations:
        links.append({"source": r["source"], "target": r["target"], "value": r.get("ratio", 10)})
    
    return {"nodes": list(nodes.values()), "links": links}


@app.get("/api/graph-view")
def graph_view():
    os.environ.get("NEO4J_PASSWORD","")"供应链关系图 HTML 页面os.environ.get("NEO4J_PASSWORD","")"
    return HTMLResponse(GRAPH_HTML)


GRAPH_HTML = ros.environ.get("NEO4J_PASSWORD","")"
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>供应链关系图</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>body{margin:0;background:#1a1a2e;overflow:hidden;font-family:sans-serif}
svg{width:100vw;height:100vh}
text{font-size:12px;fill:#eee;pointer-events:none}
.links line{stroke-opacity:0.6;stroke-width:2px}
.labels text{font-size:11px;fill:#ccc}
.tooltip{position:absolute;background:rgba(0,0,0,0.8);color:#fff;padding:8px;border-radius:4px;font-size:13px;display:none}
</style></head><body>
<div id="tooltip" class="tooltip"></div>
<svg id="graph"></svg>
<script>
fetch('/api/visualize').then(r=>r.json()).then(data=>{
  const svg=d3.select('#graph'), w=window.innerWidth, h=window.innerHeight
  const sim=d3.forceSimulation(data.nodes)
    .force('link',d3.forceLink(data.links).id(d=>d.id).distance(200))
    .force('charge',d3.forceManyBody().strength(-500))
    .force('center',d3.forceCenter(w/2,h/2))
  const link=svg.append('g').selectAll('line').data(data.links).join('line')
    .attr('stroke',d=>d.source.group==='上游'?'#4fc3f7':d=>d.target.group==='下游'?'#ff7043':'#66bb6a')
    .attr('stroke-width',d=>Math.sqrt(d.value||10))
  const node=svg.append('g').selectAll('circle').data(data.nodes).join('circle')
    .attr('r',8).attr('fill',d=>d.group==='上游'?'#4fc3f7':d.group==='下游'?'#ff7043':'#66bb6a')
    .call(d3.drag().on('start',(e,d)=>{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y})
      .on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y}).on('end',(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null}))
    .on('mouseover',(e,d)=>{d3.select('#tooltip').style('display','block').html(`${d.id}<br>环节:${d.group}`).style('left',e.pageX+10+'px').style('top',e.pageY-20+'px')})
    .on('mouseout',()=>d3.select('#tooltip').style('display','none'))
  const label=svg.append('g').selectAll('text').data(data.nodes).join('text').text(d=>d.id).attr('x',12).attr('y',4)
  sim.on('tick',()=>{link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);node.attr('cx',d=>d.x).attr('cy',d=>d.y);label.attr('x',d=>d.x+12).attr('y',d=>d.y+4)})
})
</script></body></html>os.environ.get("NEO4J_PASSWORD","")"


# ── 健康检查 ──

@app.get("/api/health")
def health():
    return {"status": "ok", "companies": len(_companies), "relations": len(_relations)}

# ── 启动 ──

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
