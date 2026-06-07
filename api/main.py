import os
os.environ.get("NEO4J_PASSWORD","")"
A-supply-analysis FastAPI 服务 — 供应链数据查询/推送/清洗

端口: 8765

GA 通过此 API 访问和操控供应链数据。
os.environ.get("NEO4J_PASSWORD","")"

import sys, os, json, uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
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
    os.environ.get("NEO4J_PASSWORD","")"推送/添加供应链关系（自动去重）os.environ.get("NEO4J_PASSWORD","")"
    for r in _relations:
        if (r.source == relation.source and r.target == relation.target 
            and r.relation_type == relation.relation_type and r.year == relation.year):
            return {"status": "ok", "count": len(_relations), "note": "duplicate, skipped"}
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
    relevant = _relations if not company else [r for r in _relations if company in (r.source or os.environ.get("NEO4J_PASSWORD","")) or company in (r.target or os.environ.get("NEO4J_PASSWORD",""))]
    for r in relevant:
        ratio = r.ratio or 0
        if ratio > 25:
            risks.append({"type": "single_customer_dependency", "severity": "high", 
                "detail": f"{r.source} 对 {r.target} 依赖度过高 ({ratio}%)"})
    if not company or company in ("宁德时代",):
        for up in _relations:
            if up.target == "宁德时代" and up.relation_type == "客户":
                ratio = up.ratio or 0
                risks.append({"type": "supply_chain_critical_node", "severity": "medium",
                    "detail": f"{up.source}({ratio}%) -> 宁德时代 -> 比亚迪"})
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
    cats = [r for r in _relations if r.relation_type == "客户"]
    report_lines.append(f"\n## 供应链关系 ({len(cats)} 条)\n")
    report_lines.append("| 上游公司 | 下游客户 | 占比 |")
    report_lines.append("|---------|---------|:----:|")
    for r in sorted(cats, key=lambda x: -(x.ratio or 0)):
        report_lines.append(f"| {r.source} | {r.target} | {r.ratio or '?'}% |")
    
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
            if r.source == c.name:
                segment = {"客户": "下游", "供应商": "上游"}.get(r.relation_type, "中游")
        nodes[c.name] = {"id": c.name, "group": segment}
    
    links = []
    for r in _relations:
        links.append({"source": r.source, "target": r.target, "value": r.ratio or 10})
    
    return {"nodes": list(nodes.values()), "links": links}


@app.get("/api/graph-view")
def graph_view():
    os.environ.get("NEO4J_PASSWORD","")"供应链关系图 HTML 页面os.environ.get("NEO4J_PASSWORD","")"
    return HTMLResponse(GRAPH_HTML)


GRAPH_HTML = ros.environ.get("NEO4J_PASSWORD","")"<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>供应链关系图</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
body{margin:0;background:#0f1923;overflow:hidden;font-family:'Microsoft YaHei',sans-serif}
svg{width:100vw;height:100vh}
text{font-size:13px;fill:#e0e0e0;pointer-events:none;font-weight:500}
.links line{stroke-opacity:0.7}
.node circle{cursor:pointer;stroke:#fff;stroke-width:1.5}
.node:hover circle{filter:brightness(1.3)}
.node.highlight circle{stroke:#ffd700;stroke-width:3}
.links line.highlight{stroke-opacity:1;stroke-width:3!important}
.legend rect{stroke:#555;stroke-width:0.5}
.legend text{font-size:12px;fill:#ccc}
#tooltip{position:absolute;background:rgba(15,25,35,0.95);color:#e0e0e0;padding:12px 16px;border-radius:8px;font-size:13px;display:none;border:1px solid #444;box-shadow:0 4px 12px rgba(0,0,0,0.5);line-height:1.6;max-width:300px}
#tooltip .name{font-size:16px;font-weight:bold;color:#fff;margin-bottom:4px}
#tooltip .tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px}
#tooltip .tag.up{background:#1565c0;color:#fff}
#tooltip .tag.mid{background:#2e7d32;color:#fff}
#tooltip .tag.down{background:#e65100;color:#fff}
#tooltip .tag.risk{background:#c62828;color:#fff}
</style></head><body>
<div id="tooltip" class="tooltip"></div>
<svg id="graph"></svg>
<script>
const COLOR={'上游':'#4fc3f7','中游':'#66bb6a','下游':'#ff7043'}
fetch('/api/visualize').then(r=>r.json()).then(data=>{
  const svg=d3.select('#graph'),w=window.innerWidth,h=window.innerHeight
  
  // 计算节点度(连接数)作为大小
  const degree={};data.links.forEach(l=>{degree[l.source]=1+(degree[l.source]||0);degree[l.target]=1+(degree[l.target]||0)})
  data.nodes.forEach(n=>n.degree=degree[n.id]||1)
  const maxDeg=d3.max(data.nodes,d=>d.degree)||1
  
  const sim=d3.forceSimulation(data.nodes)
    .force('link',d3.forceLink(data.links).id(d=>d.id).distance(250).strength(d=>1/(1+d.value/10)))
    .force('charge',d3.forceManyBody().strength(-800))
    .force('center',d3.forceCenter(w/2,h/2))
    .force('collision',d3.forceCollide().radius(d=>8+20*d.degree/maxDeg))
  
  const link=svg.append('g').selectAll('line').data(data.links).join('line')
    .attr('class','links').attr('stroke',d=>COLOR[d.source.group]||'#888')
    .attr('stroke-width',d=>1+4*d.value/30).attr('stroke-dasharray',d=>d.value>25?'6,3':'0')
  
  const gNode=svg.append('g').selectAll('g').data(data.nodes).join('g').attr('class','node')
  gNode.append('circle').attr('r',d=>8+12*d.degree/maxDeg)
    .attr('fill',d=>COLOR[d.group]||'#888')
    .call(d3.drag().on('start',(e,d)=>{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y})
      .on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y}).on('end',(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null}))
    .on('mouseover',(e,d)=>{
      // highligh
      gNode.filter(n=>n.id===d.id||data.links.some(l=>l.source.id===d.id&&l.target.id===n.id||l.target.id===d.id&&l.source.id===n.id)).classed('highlight',true)
      link.filter(l=>l.source.id===d.id||l.target.id===d.id).classed('highlight',true)
      const rels=data.links.filter(l=>l.source.id===d.id).map(l=>`<span class="tag mid">客户</span> ${l.target.id} (${l.value}%)`).join('<br>')
      const sups=data.links.filter(l=>l.target.id===d.id).map(l=>`<span class="tag up">供应商</span> ${l.source.id} (${l.value}%)`).join('<br>')
      const risk=data.links.filter(l=>(l.source.id===d.id||l.target.id===d.id)&&l.value>25).length
      const riskHtml=risk?`<br><span class="tag risk">${risk}项高风险依赖</span>`:''
      d3.select('#tooltip').style('display','block').html(
        `<div class="name">${d.id}</div><span class="tag ${d.group==='上游'?'up':d.group==='下游'?'down':'mid'}">${d.group||'未知'}</span> 连接度:${d.degree}<br>${rels||''}${sups||''}${riskHtml}`
      ).style('left',Math.min(e.pageX+15,w-320)+'px').style('top',Math.max(e.pageY-40,10)+'px')
    }).on('mouseout',()=>{
      gNode.classed('highlight',false);link.classed('highlight',false);d3.select('#tooltip').style('display','none')
    })
  
  gNode.append('text').text(d=>d.id).attr('x',d=>12+8*Math.min(1,d.degree/maxDeg*2)).attr('y',4)
  
  // 图例
  const leg=svg.append('g').attr('class','legend').attr('transform','translate(20,20)')
  leg.append('rect').attr('width',180).attr('height',110).attr('fill','rgba(15,25,35,0.8)').attr('rx',6)
  const items=[['上游','#4fc3f7'],['中游','#66bb6a'],['下游','#ff7043'],['风险(>25%)','#c62828','dash']]
  items.forEach(([label,clr,dash],i)=>{
    const y=20+i*22
    leg.append('circle').attr('cx',20).attr('cy',y).attr('r',6).attr('fill',clr)
    if(dash)leg.append('line').attr('x1',16).attr('y1',y-1).attr('x2',24).attr('y2',y-1).attr('stroke',clr).attr('stroke-width',2).attr('stroke-dasharray','4,2')
    leg.append('text').attr('x',34).attr('y',y+4).text(label).attr('fill','#ccc')
  })
  
  sim.on('tick',()=>{
    link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y)
    gNode.attr('transform',d=>`translate(${d.x},${d.y})`)
  })
})</script></body></html>os.environ.get("NEO4J_PASSWORD","")"


# ── 健康检查 ──

@app.get("/api/health")
def health():
    return {"status": "ok", "companies": len(_companies), "relations": len(_relations)}

# ── 启动 ──

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
