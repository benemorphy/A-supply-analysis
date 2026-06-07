# A-supply-analysis

New Energy Vehicle (NEV) Supply Chain Analysis Platform — A FastAPI-based RESTful Service

## Overview

A-supply-analysis is a supply chain data analysis platform for the **NEV (New Energy Vehicle) industry**. It provides end-to-end capabilities including data collection, cleaning, query, visualization, risk analysis, and graph database integration through RESTful APIs.

**Core Capabilities:**
- 7 target companies covering the full NEV supply chain (lithium mining upstream → materials midstream → battery/EV downstream)
- LLM-powered data cleaning (automatic filtering of anonymous customer/supplier names)
- D3.js force-directed graph visualization
- Neo4j graph database path analysis
- OWL ontology modeling with reasoning
- Multi-source search + LLM extraction deep research pipeline

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn neo4j rdflib

# Start service
python -m uvicorn api.main:app --host 0.0.0.0 --port 8765

# Push sample data
python -c "
from clients.supply_client import SupplyClient; c=SupplyClient()
for n in ['Tianqi Lithium','Huayou Cobalt','Easpring','Senior','Tinci','CATL','BYD']: c.add_company(n)
for s,t,rt,yr,r in [('Easpring','CATL','customer',2024,30),('Senior','CATL','customer',2024,16),('Tinci','CATL','customer',2024,20),('Huayou Cobalt','CATL','customer',2024,7.2),('Easpring','BYD','customer',2024,15),('Senior','BYD','customer',2024,10)]:
    c.push_relation(s,t,rt,yr,r)
"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/companies` | List companies |
| POST | `/api/companies` | Add a company |
| GET | `/api/supply-chains` | Query supply chain relations |
| POST | `/api/supply-chains` | Push relation (auto-dedup) |
| POST | `/api/clean` | LLM text cleaning |
| GET | `/api/risk-analysis` | Risk analysis |
| GET | `/api/report` | Analysis report (Markdown) |
| GET | `/api/visualize` | D3 graph JSON data |
| GET | `/api/graph-view` | D3 force-directed graph page |
| GET | `/api/health` | Health check |

## Project Structure

```
A-supply-analysis/
├── api/main.py                  FastAPI main entry
├── clients/supply_client.py     GA-side HTTP client
├── models/models.py             Data models
├── clean_pipeline.py            LLM cleaning pipeline
├── db/neo4j_import.py           Neo4j import script
├── deep_research/               Deep research pipeline
│   ├── layer1.py           Multi-source search + LLM extraction
│   ├── layer2.py           Relation detail mining + Neo4j paths
│   └── layer3.py           LLM deep analysis report
├── ontology/                    OWL ontology models
│   ├── build_ontology.py        Ontology builder
│   └── supply_chain.ttl         Ontology TTL file
├── API_INTERFACE.md             GA integration docs
├── PLAN.md                      Progress plan
├── README.md                    This file (Chinese)
└── README_en.md                 English version
```

## Integration with GA

GA interacts with this service via RESTful API:

```python
from clients.supply_client import SupplyClient
client = SupplyClient()

# Query companies
companies = client.list_companies()

# Push relation
client.push_relation("Easpring", "CATL", "customer", 2024, 30.0)

# Risk analysis
risks = client.get_risk_analysis(company="CATL")

# LLM text cleaning
result = client.clean_text("CompanyName", 2024, "Top 5 customers: ...")
```

External access via Caddy reverse proxy:

```
http://10.24.242.176:8000/supply/api/report
http://10.24.242.176:8000/supply/api/graph-view
```

## Target Companies

| Company | Role | Description |
|---------|------|-------------|
| Tianqi Lithium | Upstream | Lithium mining |
| Huayou Cobalt | Upstream | Cobalt resources / precursors |
| Easpring Material | Upstream | Cathode materials |
| Senior Technology | Upstream | Separator membranes |
| Tinci Materials | Upstream | Electrolyte |
| CATL | Downstream | Power batteries |
| BYD | Downstream | EV manufacturing |

## Risk Analysis

The platform automatically identifies two types of risk:

1. **Single Customer Dependency** (ratio > 25%): e.g., Easpring depends on CATL for 30% of revenue
2. **Supply Chain Critical Node**: CATL as the central hub affecting multiple upstream suppliers

## Risk Propagation Simulation

Example: If CATL reduces production by 20%:
- Easpring loses 7.5% of total revenue (30% x 20% + 15% x 20%)
- Senior loses 5.2%
- Tinci loses 4.0%
- Huayou Cobalt loses 1.44%

## Tech Stack

- **Backend**: FastAPI / Python 3.11
- **Graph Database**: Neo4j (bolt://localhost:7687)
- **Visualization**: D3.js v7 (force-directed graph)
- **LLM**: deepseek-v4-flash (via GA's mykey)
- **Ontology**: OWL / RDFLib
- **Proxy**: Caddy reverse proxy
- **Search**: metaso_search (web search)
