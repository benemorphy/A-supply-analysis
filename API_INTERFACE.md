# A-supply-analysis 与 GA 接口文档

## 架构总览

```
GA (Beneh, D:\open_claw_agent\Beneh\GA)
  │
  │  1. HTTP (localhost:8765)  ── 数据查询/推送
  │  2. import clean_pipeline ── LLM 清洗能力
  │  3. SupplyClient 类封装    ── Python 客户端
  │
  ▼
A-supply-analysis FastAPI (D:\open_claw_agent\A-supply-analysis, port 8765)
  │
  │  Caddy 反向代理 :8000/supply/*
  │
  ▼
对外暴露: http://10.24.242.176:8000/supply/api/
```

## 通信方式

GA 与 A-supply-analysis 之间**仅通过 RESTful API 通信**。

```
GA (Beneh) ── HTTP (localhost:8765) ──→ A-supply-analysis FastAPI
                │
                ├── SupplyClient Python 封装 (实际走 HTTP)
                └── Caddy :8000/supply/* (对外暴露)
```

### SupplyClient 使用方式

```python
from clients.supply_client import SupplyClient
client = SupplyClient()  # 默认 http://localhost:8765

# 公司管理
client.add_company("宁德时代", "300750", "新能源")
companies = client.list_companies()

# 供应链关系管理
client.push_relation("当升科技", "宁德时代", "客户", 2024, 30.0)
rels = client.query_relations(company="宁德时代")

# LLM 清洗
result = client.clean_text("宁德时代", 2024, "前五大客户：...")
```

### Caddy 反向代理（对外访问）

```
http://10.24.242.176:8000/supply/api/<endpoint>
→ Caddy strip /supply prefix
→ http://localhost:8765/api/<endpoint>
```
