# 流水线方案 — 第 [NUMBER] 组

**项目**： 优化零售库存&销售表现
**成员**： [姓名 1], [姓名 2], [姓名 3], …

## 1. 业务问题（请填写）

1. 哪些**产品**的销量最高 / 最低？
2. 哪家**门店**创造的营收最多？
3. 哪里存在**库存积压风险**（库存成本高、销量低）？
4. [补充你自己的问题]

## 2. 数据流水线流程图（绘制或描述）

用你自己的流程图图片替换下方 ASCII 图，或在此图基础上扩展。
```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌─────────────┐
│ Raw CSV     │ --> │ SQL JOIN +   │ --> │ Export / load │ --> │ Python      │
│ products,   │     │ GROUP BY KPIs│     │ into Pandas   │     │ lists/dicts │
│ sales,      │     │ (vibe SQL)   │     │ DataFrame     │     │ + charts    │
│ stores      │     └──────────────┘     └───────────────┘     └─────────────┘
└─────────────┘                                                      │
                                                                     v
                                                            ┌─────────────────┐
                                                            │ Recommendations │
                                                            │ (inventory)     │
                                                            └─────────────────┘
```


## 3. 伪代码架构方案（必填）

用通俗的中文/英文描述你将要转换为 Python 的逻辑（写入 `analysis_template.py` 的第 4 部分）。
```
BEGIN pipeline

STEP 1: 加载关系表
- 从 CSV 读取 products, sales, stores

STEP 2: SQL 层 (或 Pandas 等价连接)
- JOIN sales 与 products ON product_id
- JOIN sales 与 stores ON store_id
- 如需要，按日期范围 FILTER
- GROUP BY store_location, product_name
- COMPUTE sum(quantity), sum(total_amount), 利润估算
- HAVING 总销量低于阈值 → 标记为滞销品

STEP 3: Python 数据组织 (列表与字典)
- BUILD 字典: key = product_name, value = 总销量
- BUILD 字典列表: 每家门店一个字典，包含 KPI
- 按营收降序 SORT 列表

STEP 4: 分析与可视化
- CHART 1: 柱状图 — 各门店营收
- CHART 2: 柱状图或折线图 — 销量最高的产品
- 根据滞销品列表 PRINT 库存建议

END pipeline
```

### 你的伪代码（编辑上方内容 — 必须为你们小组的逻辑）

>…

## 4. 伪代码 → Python 映射表

|伪代码步骤|Python结构（list/dict/Pandas）|
|:-:|:-:|
|例：“BUILD 产品→销量 字典”|`product_qty: dict[str, int] = {}`|
|例：“BUILD 门店 KPI 字典列表”|`store_kpis: list[dict] = []`|
||
||


## 5. 预期产出

|产出|格式|受众|
|:-:|:-:|:-:|
|门店业绩汇总|表格 / 控制台|运营经理|
|滞销产品清单|字典列表|库存团队|
|图表 1|PNG|汇报展示|
|图表 2|PNG|汇报展示|
