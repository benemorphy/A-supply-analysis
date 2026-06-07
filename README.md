# A-supply-analysis

新能源汽车供应链分析平台 — 基于 FastAPI 的 RESTful 服务

## 项目简介

A-supply-analysis 是一个面向**新能源汽车产业链**的供应链数据分析平台。通过 RESTful API 提供数据采集、清洗、查询、可视化、风险分析及图数据库集成等全链路能力。

**核心能力:**
- 7 家标的覆盖全产业链（上游锂矿 → 中游材料 → 下游电池/整车）
- LLM 驱动的数据清洗（自动过滤匿名客户/供应商名称）
- D3.js 力导向图可视化
- Neo4j 图数据库路径分析
- OWL 本体建模与推理
- 多源搜索 + LLM 提取的深度研究管线

## 快速开始

```bash
# 安装依赖
pip install fastapi uvicorn neo4j rdflib

# 启动服务
python -m uvicorn api.main:app --host 0.0.0.0 --port 8765

# 推送数据
python -c "
from clients.supply_client import SupplyClient; c=SupplyClient()
for n in ['天齐锂业','华友钴业','当升科技','恩捷股份','天赐材料','宁德时代','比亚迪']: c.add_company(n)
for s,t,rt,yr,r in [('当升科技','宁德时代','客户',2024,30),('恩捷股份','宁德时代','客户',2024,16),('天赐材料','宁德时代','客户',2024,20),('华友钴业','宁德时代','客户',2024,7.2),('当升科技','比亚迪','客户',2024,15),('恩捷股份','比亚迪','客户',2024,10)]:
    c.push_relation(s,t,rt,yr,r)
"
```

## API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/companies` | 公司列表 |
| POST | `/api/companies` | 添加公司 |
| GET | `/api/supply-chains` | 查询供应链关系 |
| POST | `/api/supply-chains` | 推送关系（自动去重） |
| POST | `/api/clean` | LLM 清洗文本 |
| GET | `/api/risk-analysis` | 风险分析 |
| GET | `/api/report` | 分析报告 |
| GET | `/api/visualize` | D3 图 JSON 数据 |
| GET | `/api/graph-view` | D3 力导向图页面 |
| GET | `/api/health` | 健康检查 |

## 项目结构

```
A-supply-analysis/
├── api/main.py                  FastAPI 服务主入口
├── clients/supply_client.py     GA 侧 HTTP 客户端
├── models/models.py             数据模型
├── clean_pipeline.py            LLM 清洗管线
├── db/neo4j_import.py           Neo4j 导入脚本
├── deep_research/               深度研究管线
│   ├── layer1.py           多源搜索 + LLM 提取
│   ├── layer2.py           关系细节挖掘 + Neo4j 路径
│   └── layer3.py           LLM 智能分析报告
├── ontology/                    OWL 本体模型
│   ├── build_ontology.py        本体构建脚本
│   └── supply_chain.ttl         本体 TTL 文件
├── API_INTERFACE.md             GA 交互接口文档
├── PLAN.md                      推进计划
├── README.md                    本文件
└── README_en.md                 English version
```

## 接口交互

GA 通过 RESTful API 与本服务交互：

```python
from clients.supply_client import SupplyClient
client = SupplyClient()

# 查询公司
companies = client.list_companies()

# 推送关系
client.push_relation("当升科技", "宁德时代", "客户", 2024, 30.0)

# 风险分析
risks = client.get_risk_analysis(company="宁德时代")

# LLM 清洗
result = client.clean_text("公司名", 2024, "前五大客户：...")
```

对外访问通过 Caddy 反向代理：

```
http://10.24.242.176:8000/supply/api/report
http://10.24.242.176:8000/supply/api/graph-view
```

## 标的公司

| 公司 | 角色 | 说明 |
|------|------|------|
| 天齐锂业 | 上游 | 锂矿资源 |
| 华友钴业 | 上游 | 钴资源/前驱体 |
| 当升科技 | 上游 | 正极材料 |
| 恩捷股份 | 上游 | 隔膜 |
| 天赐材料 | 上游 | 电解液 |
| 宁德时代 | 下游 | 动力电池 |
| 比亚迪 | 下游 | 整车制造 |

## 风险分析

平台自动识别两类风险:
1. **单一客户依赖** (ratio > 25%): 如当升科技对宁德时代依赖 30%
2. **供应链关键节点**: 宁德时代作为核心枢纽影响多家上游

## 技术栈

- **后端**: FastAPI / Python 3.11
- **图数据库**: Neo4j (bolt://localhost:7687)
- **可视化**: D3.js v7 (力导向图)
- **LLM**: deepseek-v4-flash (通过 GA 的 mykey)
- **本体**: OWL / RDFLib
- **代理**: Caddy 反向代理
- **搜索**: metaso_search (web 搜索)
