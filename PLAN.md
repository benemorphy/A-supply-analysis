# A-supply-analysis 推进计划

## 阶段一：数据采集（LLM + 搜索自动）

- [x] Step 1: LLM 选定 7 家标的（全产业链覆盖）
- [x] Step 2: metaso 搜索 7 家公司年报（14 次搜索，数据已保存）
- [x] Step 3: 调用 /api/clean 清洗数据（LLM 过滤匿名名）
- [x] Step 4: 调用 /api/companies + /api/supply-chains 入库（7 公司 + 6 关系）

## 阶段二：查询分析（当前阶段）

- [ ] Step 5a: 供应链查询 API（/api/supply-chains 已有）
- [ ] Step 5b: 风险传导分析（/api/risk-analysis）
- [ ] Step 5c: LLM 生成分析报告

## 阶段三：可视化

- [ ] Step 6: 图可视化 endpoint（/api/visualize）
- [ ] Step 7: 关系图展示

## 阶段四：图数据库

- [ ] Step 8: Neo4j 导入
- [ ] Step 9: Cypher 查询库
