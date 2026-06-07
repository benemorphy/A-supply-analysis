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

### 方式一：HTTP REST API

GA 通过 `c
...[Truncated]...
  response = client.clean_text("宁德时代", 2024, "前五大客户：...")
```

### 方式二：Python 模块直接调用

GA 可直接 import A-supply-analysis 的客户端模块：

```python
from clients.supply_client import SupplyClient
client = SupplyClient()
companies = client.list_companies()
```

### 方式三：Caddy 反向代理

对外通过 Caddy 网关统一暴露：
```
http://10.24.242.176:8000/supply/api/<endpoint>
→ Caddy strip /supply prefix
→ http://localhost:8765/api/<endpoint>
```
