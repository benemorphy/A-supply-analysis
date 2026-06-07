# A-supply-analysis

供应链研究工具框架 — 为 GA 提供领域无关的供应链深度研究能力

## 定位

**A-supply-analysis 不是针对某个具体行业的分析系统，而是一套可复用的工具框架。** GA 通过 RESTful API 调用本框架的能力，帮助用户在**任意领域**（新能源汽车、半导体、医药、消费电子...）进行供应链深度研究。

## 核心能力

| 能力 | 说明 | 领域无关 |
|------|------|:--------:|
| LLM 清洗管线 | 自动过滤匿名名称、提取结构化关系 | ✅ |
| 多源搜索 + LLM 提取 | metaso 搜索 + LLM 提取供应链关系 | ✅ |
| 图存储与分析 | Neo4j 图数据库路径传导分析 | ✅ |
| 可视化 | D3.js 力导向图展示 | ✅ |
| 风险分析 | 依赖度计算 + 关键节点识别 | ✅ |
| 深度研究管线 | 三层逐层深化（广度/深度/推理） | ✅ |
| OWL 本体建模 | 领域概念建模 + 推理规则 | ✅ |

## 工作流程

```
用户指定领域 → GA 选定标的 → 搜索/清洗 → 入库 → 分析/可视化/风险
     │              │            │        │           │
     └── 任意行业    LLM 选择    去匿名     REST API    Neo4j/D3
```

## 快速开始

```bash
# 安装依赖
pip install fastapi uvicorn neo4j rdflib

# 启动服务
python -m uvicorn api.main:app --host 0.0.0.0 --port 8765

# GA 通过客户端推送数据
python -c "
from clients.supply_client import SupplyClient; c=SupplyClient()
c.add_company('CompanyA')
c.push_relation('CompanyA', 'CompanyB', 'supplier', 2024, 30.0)
"
```

## API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET/POST | `/api/companies` | 公司管理 |
| GET/POST | `/api/supply-chains` | 关系管理（自动去重） |
| POST | `/api/clean` | LLM 清洗文本 |
| GET | `/api/risk-analysis` | 风险分析 |
| GET | `/api/report` | 分析报告 |
| GET | `/api/visualize` | D3 图 JSON |
| GET | `/api/graph-view` | D3 力导向图 |
| GET | `/api/health` | 健康检查 |

## 深度研究管线

```
Layer 1: 广度扩展
  metaso 搜索 + LLM 提取 → FastAPI 入库 → 去重

Layer 2: 深度挖掘  
  关系细节搜索（金额/合同期/多年对比）
  Neo4j 路径分析（A→B→C 传导）

Layer 3: 智能分析
  LLM 全景报告生成
  风险传导模拟
  改进建议
```

## 演示场景

当前项目自带的演示数据为**新能源汽车供应链**（7 家公司，覆盖上游锂矿 → 中游材料 → 下游电池整车）。此数据仅用于验证框架功能，实际使用时可通过 GA 对任意领域进行全流程研究。

## 技术栈

- **后端**: FastAPI / Python 3.11
- **图数据库**: Neo4j
- **可视化**: D3.js v7
- **LLM**: deepseek（通过 GA mykey）
- **本体**: OWL / RDFLib
- **代理**: Caddy
- **搜索**: metaso_search

## 集成方式

GA 通过 RESTful API 调用本框架：

```
GA ←─ HTTP REST ─→ A-supply-analysis FastAPI (:8765)
                       │
                       ├── Neo4j 图数据库
                       ├── D3.js 可视化
                       ├── LLM 清洗管线
                       └── metaso 搜索
```

对外访问通过 Caddy 反向代理：
```
http://10.24.242.176:8000/supply/api/
```
