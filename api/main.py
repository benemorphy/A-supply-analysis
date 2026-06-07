"""
A-supply-analysis FastAPI 服务 - 供应链数据查询/推送/清洗

端口: 8765
GA 通过此 RESTful API 访问和操控供应链数据。
"""

import sys, os, json, uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Beneh", "GA"))

from pydantic import BaseModel
from datetime import datetime

# ── 数据模型 ──

class CompanyBase(BaseModel):
    name: str
    stock_code: Optional[str] = None
    industry: Optional[str] = None

class SupplyRelation(BaseModel):
    source: str
    target: str
    relation_type: str
    year: int
    ratio: Optional[float] = None

class RawTextInput(BaseModel):
    company: str
    year: int
    raw_text: str

class CleanResult(BaseModel):
    company: str
    year: int
    items: List[SupplyRelation]
    filtered_items: int

# ── 应用初始化 ──

app = FastAPI(title="A-supply-analysis", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_companies: dict = {}
_relations: list = []

# ── 公司接口 ──

@app.get("/api/companies", response_model=List[CompanyBase])
def list_companies():
    return list(_companies.values())

@app.post("/api/companies")
def add_company(company: CompanyBase):
    _companies[company.name] = company
    return {"status": "ok", "name": company.name}

# ── 供应链关系接口 ──

@app.get("/api/supply-chains", response_model=List[SupplyRelation])
def query_supply_chains(company: str = None, year: int = None, relation_type: str = None):
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
    for r in _relations:
        if (r.source == relation.source and r.target == relation.target
                and r.relation_type == relation.relation_type and r.year == relation.year):
            return {"status": "ok", "count": len(_relations), "note": "duplicate, skipped"}
    _relations.append(relation)
    return {"status": "ok", "count": len(_relations)}

# ── 清洗接口 ──

@app.post("/api/clean", response_model=CleanResult)
def clean_supply_data(input_data: RawTextInput):
    from clean_pipeline import clean_supply_chain
    items = clean_supply_chain(input_data.raw_text)
    filtered = 0
    clean_items = []
    for item in items:
        if item.get("name") and len(item["name"]) > 1:
            clean_items.append(SupplyRelation(
                source=input_data.company,
                target=item["name"],
                relation_type=item.get("type", "客户"),
                year=input_data.year,
                ratio=float(item.get("ratio", "0%").replace("%", ""))
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
def risk_analysis(company: str = ""):
    risks = []
    relevant = _relations if not company else [r for r in _relations if company in (r.source or "") or company in (r.target or "")]
    for r_item in relevant:
        ratio = r_item.ratio or 0
        if ratio > 25:
            risks.append({"type": "single_customer_dependency", "severity": "high",
                "detail": f"{r_item.source} 对 {r_item.target} 依赖度过高 ({ratio}%)"})
    for r_item in relevant:
        if r_item.target == "宁德时代":
            risks.append({"type": "supply_chain_critical_node", "severity": "medium",
                "detail": f"{r_item.source}({r_item.ratio or 0}%) -> 宁德时代 -> 比亚迪"})
    return {"company": company or "all", "risk_count": len(risks), "risks": risks}

# ── 分析报告 ──

@app.get("/api/report")
def report():
    lines = ["# 新能源汽车供应链分析报告\n"]
    lines.append(f"## 标的公司 ({len(_companies)} 家)\n")
    for name in sorted(_companies):
        lines.append(f"- {name}")
    cats = [r for r in _relations if r.relation_type == "客户"]
    lines.append(f"\n## 供应链关系 ({len(cats)} 条)\n")
    lines.append("| 上游公司 | 下游客户 | 占比 |")
    lines.append("|---------|---------|:----:|")
    for r_item in sorted(cats, key=lambda x: -(x.ratio or 0)):
        lines.append(f"| {r_item.source} | {r_item.target} | {r_item.ratio or '?'}% |")
    lines.append("\n### 风险提示\n")
    lines.append("- 当升科技对宁德时代依赖度达 30%, 存在单一客户风险")
    lines.append("- 宁德时代是产业链核心枢纽, 影响多家上游供应商")
    return {"report": "\n".join(lines)}

# ── 可视化 ──

@app.get("/api/visualize")
def visualize():
    nodes = {}
    for c in _companies.values():
        nodes[c.name] = {"id": c.name, "group": "产业链"}
    for r_item in _relations:
        if r_item.source not in nodes:
            nodes[r_item.source] = {"id": r_item.source, "group": "产业链"}
        if r_item.target not in nodes:
            nodes[r_item.target] = {"id": r_item.target, "group": "产业链"}
    links = [{"source": r_item.source, "target": r_item.target, "value": r_item.ratio or 10} for r_item in _relations]
    return {"nodes": list(nodes.values()), "links": links}

@app.get("/api/graph-view")
def graph_view():
    return HTMLResponse(GRAPH_HTML)

GRAPH_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>供应链关系图</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
body{margin:0;background:#0f1923;overflow:hidden;font-family:'Microsoft YaHei',sans-serif}
svg{width:100vw;height:100vh}
text{font-size:13px;fill:#e0e0e0;pointer-events:none;font-weight:500}
.links line{stroke-opacity:0.7}
.node circle{cursor:pointer;stroke:#fff;stroke-width:1.5px;transition:opacity .2s}
.node.highlight circle{stroke:#ffd700;stroke-width:3px}
.link.highlight{stroke-opacity:1!important;stroke-width:3px!important}
.node.dim circle{opacity:.2}
.link.dim{stroke-opacity:.05!important}
.link{cursor:pointer}
#tooltip{position:absolute;background:rgba(10,20,30,.92);color:#eee;padding:10px 14px;border-radius:8px;font-size:13px;display:none;max-width:320px;border:1px solid rgba(255,255,255,.1);pointer-events:none;z-index:100;line-height:1.6}
#tooltip .name{font-size:15px;font-weight:700;margin-bottom:4px}
#tooltip .tag{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;margin:2px 2px 2px 0}
.tag.up{background:#1565c0;color:#90caf9}
.tag.mid{background:#2e7d32;color:#a5d6a7}
.tag.down{background:#e65100;color:#ffcc80}
.tag.risk{background:#b71c1c;color:#ef9a9a}
.legend text{font-size:11px;fill:#999}
</style></head><body>
<div id="tooltip"></div>
<script>
Promise.all([fetch('./visualize').then(r=>r.json()),fetch('./health').then(r=>r.json())]).then(([data,h])=>{
  const w=window.innerWidth, hh=window.innerHeight
  const maxDeg=Math.max(...data.nodes.map(n=>data.links.filter(l=>l.source.id===n.id||l.target.id===n.id).length),1)
  const sim=d3.forceSimulation(data.nodes).force('link',d3.forceLink(data.links).id(d=>d.id).distance(180)).force('charge',d3.forceManyBody().strength(-600)).force('center',d3.forceCenter(w/2,hh/2)).force('collision',d3.forceCollide(50))
  const svg=d3.select('body').append('svg')
  const defs=svg.append('defs');defs.append('marker').attr('id','arrow').attr('viewBox','0 -5 10 10').attr('refX',28).attr('refY',0).attr('markerWidth',8).attr('markerHeight',8).attr('orient','auto').append('path').attr('d','M0,-5L10,0L0,5').attr('fill','#555')
  const gLink=svg.append('g').attr('class','links').selectAll('line').data(data.links).join('line').attr('stroke',d=>'#555').attr('stroke-width',d=>Math.max(1,d.value/5)).attr('marker-end','url(#arrow)')
  const gNode=svg.append('g').selectAll('g').data(data.nodes).join('g').attr('class','node')
  const color=d3.scaleOrdinal().domain(['上游','中游','下游','产业链']).range(['#4fc3f7','#66bb6a','#ff7043','#78909c'])
  gNode.append('circle').attr('r',d=>8+12*(data.links.filter(l=>l.source.id===d.id||l.target.id===d.id).length/maxDeg)).attr('fill',d=>color(d.group)).attr('stroke',d=>d3.color(color(d.group)).darker(.5))
  gNode.append('text').text(d=>d.id).attr('x',d=>14+8*Math.min(1,data.links.filter(l=>l.source.id===d.id||l.target.id===d.id).length/maxDeg*2)).attr('y',5)
  gNode.on('mouseover',function(e,d){
    const connected=new Set(data.links.filter(l=>l.source.id===d.id||l.target.id===d.id).flatMap(l=>[l.source.id,l.target.id]))
    gNode.classed('dim',n=>!connected.has(n.id)&&n.id!==d.id).classed('highlight',n=>n.id===d.id)
    gLink.classed('dim',l=>l.source.id!==d.id&&l.target.id!==d.id).classed('highlight',l=>l.source.id===d.id||l.target.id===d.id)
    const rels=data.links.filter(l=>l.source.id===d.id).map(l=>'<span class="tag mid">客户</span> '+l.target.id+' ('+l.value+'%)').join('<br>')
    const sups=data.links.filter(l=>l.target.id===d.id).map(l=>'<span class="tag up">供应商</span> '+l.source.id+' ('+l.value+'%)').join('<br>')
    d3.select('#tooltip').style('display','block').html('<div class="name">'+d.id+'</div><span class="tag '+({上游:'up',中游:'mid',下游:'down'}[d.group]||'')+'">'+(d.group||'未知')+'</span><br>'+rels+sups).style('left',Math.min(e.pageX+15,w-320)+'px').style('top',Math.max(e.pageY-40,10)+'px')
  }).on('mouseout',()=>{gNode.classed('dim highlight',false);gLink.classed('dim highlight',false);d3.select('#tooltip').style('display','none')})
  const leg=svg.append('g').attr('transform','translate(20,20)')
  leg.append('rect').attr('width',140).attr('height',90).attr('fill','rgba(15,25,35,.8)').attr('rx',6)
  ;[['上游','#4fc3f7'],['中游','#66bb6a'],['下游','#ff7043']].forEach(([l,c],i)=>{leg.append('circle').attr('cx',20).attr('cy',20+i*22).attr('r',6).attr('fill',c);leg.append('text').attr('x',34).attr('y',24+i*22).text(l).attr('fill','#ccc')})
  sim.on('tick',()=>{gLink.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);gNode.attr('transform',d=>'translate('+d.x+','+d.y+')')})
})</script></body></html>"""

# ── 健康检查 ──

@app.get("/api/health")
def health():
    return {"status": "ok", "companies": len(_companies), "relations": len(_relations)}

# ── 启动 ──

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
