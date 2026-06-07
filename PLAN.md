# A-supply-analysis 推进计划

## 阶段一：数据采集（LLM + 搜索自动）

- [x] Step 1: LLM 选定 7 家标的（全产业链覆盖）
- [x] Step 2: metaso 搜索 7 家公司年报（14 次搜索）
- [x] Step 3: 调用 /api/clean 清洗数据（LLM 过滤匿名名）
- [x] Step 4: 入库（7 公司 + 6 关系）

## 阶段二：查询分析（已完成）

- [x] Step 5a: 供应链查询 API（/api/supply-chains）
- [x] Step 5b: 风险传导分析（/api/risk-analysis）
- [x] Step 5c: LLM 分析报告（/api/report）

## 阶段三：可视化（待推进）

- [ ] Step 6: 图可视化 endpoint（/api/visualize）
- [ ] Step 7: 前端关系图展示

## 阶段四：图数据库（待推进）

- [ ] Step 8: Neo4j 导入
- [ ] Step 9: Cypher 查询库
