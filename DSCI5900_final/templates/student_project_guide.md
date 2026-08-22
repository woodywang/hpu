# 学生项目指导手册 - STUDENT_PROJECT_GUIDE

发布时间：2026年7月9日 17:38
# 期末综合项目——学生指导手册

**课程：** 氛围编程(Vibe Programming)与AI编排(AI Orchestration)
**主题：** 零售库存与销售业绩优化
**角色：** 你是AI编排者——借助AI生成代码初稿，但整体方案规划、代码调试与结果验证均由你独立完成。

----
## 业务问题

一家中型零售商在3家实体门店售卖**笔记本电脑、智能手机、数码配件**及相关产品，现存业务痛点如下：
1. 低需求商品库存积压，仓储成本浪费
2. 各门店销售数据统计口径不统一，难以识别热销门店、调配库存

**你的任务：** 基于提供的关系数据表搭建一套**AI辅助数据处理流水线**（SQL数据提取 → Python数据分析 → 业务洞察输出）
>**首次操作提示：** 软件安装与CSV数据导入步骤详见 `SETUP_AND_RUN_GUIDE.md`
**执行顺序：** 环境配置 → 阅读本手册 → 方案规划 → SQL数据查询 → Python数据分析 → AI提示词日志记录

----
## 数据集（关系数据表）

|数据表名|核心字段|
|:-:|:-:|
|**products**|`product_id`, `product_name`, `category`, `cost_price`, `retail_price`|
|**sales**|`sale_id`, `product_id`, `store_id`, `sale_date`, `quantity`, `total_amount`|
|**stores**|`store_id`, `store_location`, `monthly_rent`|
数据文件路径：`data/products.csv`、`data/stores.csv`、`data/sales.csv`

----
## 项目要求自查清单

### 1. 逻辑方案规划（必做）

-  伪代码架构方案 **或** 数据处理流程图
-  清晰展示完整链路：原始数据 → SQL数据提取 → Python数据分析 → 成果输出
-  紧扣核心技能点：通过列表（list）、字典（dict）实现伪代码到Python代码的转化
- **提交文件：** PDF或图片文件（存放路径 `deliverables/01_pipeline_plan.pdf`）

### 2. SQL数据提取——智能编程环节（必做）

-  使用基于业务意图的AI提示词生成SQL初稿，并人工审核、修正代码
-  实现至少两张表关联查询（JOIN）
-  数据筛选并计算关键业务指标（例如门店/分类总销售额、营收等）
-  合理使用分组统计GROUP BY与分组筛选HAVING语法
- **提交文件：** 带注释的.sql文件（存放路径 `deliverables/02_queries.sql`）

### 3. Python数据分析（必做）

-  使用Pandas加载清洗后的SQL导出数据（或多表联合CSV数据）
-  数据处理操作：筛选、排序、聚合统计
-  显式使用列表（list）与字典（dict）（参考模板文件 `analysis_template.py`）
-  制作不少于2张专业可视化图表（柱状图、折线图、饼图等均可）
- **提交文件：** Python源码文件 `deliverables/03_analysis.py` + 至少2张图表图片（存放目录 `deliverables/charts/`）

### 4. 完整代码调试与AI提示词日志（必做）

-  记录全部原始AI提示词（包含SQL、Python代码生成提示）
-  记录AI生成代码存在的问题：语法错误、逻辑漏洞、低效代码
-  记录你修改、验证代码的完整过程（重点记录列表/字典代码、伪代码转写环节）
-  小组分工记录：每位成员负责的工作内容
- **提交文件：** PDF或Word文档（存放路径 `deliverables/04_prompt_log.pdf`）

### 5. 可选演示视频（额外加5分）

-  时长5–7分钟：讲解方案规划、智能编程完整流程、业务分析结论、列表与字典核心代码应用
- **提交方式：** 在封面页附上视频公开访问链接

----
## 推荐业务指标（至少选取4项完成分析）

|关键指标|分析价值|
|:-:|:-:|
|各门店总营收|判断门店经营表现优劣|
|单商品总销量|区分热销商品与滞销库存|
|预估利润（总销售额 - 成本价 × 销售数量）|统计各商品分类盈利空间|
|单客平均消费金额|反映顾客单次采购规模|
|各商品分类营收|分析电子产品品类销售结构|
|每日营收趋势折线图|识别销售淡旺季、销量峰值时段|

----
## 小组分工规则

- 每组3–5名学生（由授课老师分配或经老师批准自行组队）
- 每位成员需均等参与所有模块工作，分工详情记录在AI提示词日志中
- 禁止直接复制未经人工修改的AI生成代码

----
## 交付成果汇总表

|序号|交付内容|文件格式|
|:-:|:-:|:-:|
|1|逻辑方案/流程图|PDF 或 PNG图片|
|2|SQL查询脚本|.sql 文件|
|3|Python分析代码|.py 文件|
|4|可视化图表|不少于2张 PNG/JPG 图片|
|5|AI提示词日志|PDF 或 Word文档|
|6|演示视频（可选加分项）|视频链接（加5分）|
**建议附加封面页：** 小组编号、全体成员姓名、分工简述、视频链接（如有）

----
## 配套模板文件说明

|文件路径|文件用途|
|:-:|:-:|
|`SETUP_AND_RUN_GUIDE.md`|Anaconda、DBeaver、数据库工作台安装教程；CSV数据导入方法；项目整体执行顺序|
|`templates/pipeline_plan_template.md`|方案规划/流程图撰写模板|
|`templates/queries_template.sql`|SQL查询任务模板|
|`templates/analysis_template.py`|Python代码模板（内置列表、字典、绘图示例）|
|`prompt_log_template.md`|AI提示词日志标准模板|

----
## 项目顺利完成小贴士

1. **核心考核点：** 在 `analysis_template.py` 文件第四部分完整展示「伪代码 → 使用列表、字典编写Python代码」的实现过程
2. AI仅作为辅助工具：提示词日志用于体现你的独立思考与校验能力
3. 文件命名规范、分类存放，方便老师批阅
4. 提交前完整运行全部代码，确保无报错

----
祝你期末综合项目顺利，合理运用AI调度工具完成开发。

----
# Capstone Project — Student Guide

**Course:** Vibe Programming & AI Orchestration
**Theme:** Optimizing Retail Inventory & Sales Performance
**Role:** You are **AI Orchestrators** — use AI to draft code, but **you** plan, debug, and validate.

----
## Business problem

A mid-sized retailer sells **laptops, smartphones, accessories**, and related items across **3 physical stores**. Problems:
1. **Overstock** of low-demand products → wasted storage cost
2. **Inconsistent sales tracking** across stores → hard to spot top performers and rebalance inventory

**Your job:** Build an **AI-assisted data pipeline** (SQL → Python → insights) using the provided relational tables.
>**First time?** Install software and load CSV files: see **`SETUP_AND_RUN_GUIDE.md`**
**Run order:** Setup → Read this guide → Plan → SQL → Python → Prompt Log

----
## Dataset (relational tables)

|Table|Keycolumns|
|:-:|:-:|
|**products**|`product_id`, `product_name`, `category`, `cost_price`, `retail_price`|
|**sales**|`sale_id`, `product_id`, `store_id`, `sale_date`, `quantity`, `total_amount`|
|**stores**|`store_id`, `store_location`, `monthly_rent`|
Files: `data/products.csv`, `data/stores.csv`, `data/sales.csv`

----
## Project requirements checklist

### 1. Logical planning (required)

-  **Pseudocode architectural plan** or **data processing flowchart**
-  Shows: raw data → SQL extraction → Python analysis → outputs
-  Connects to core skill: **pseudocode → Python** using **lists** and **dictionaries**
- **Submit:** PDF or image (`deliverables/01_pipeline_plan.pdf`)

### 2. SQL extraction — vibe programming (required)

-  Use **intent-based AI prompts** to draft SQL; you review and fix
-  **JOIN** 2+ tables
-  **Filter** and compute KPIs (e.g., total sales, revenue by store/category)
-  Use **GROUP BY** and **HAVING** where appropriate
- **Submit:** `.sql` file with comments (`deliverables/02_queries.sql`)

### 3. Python analysis (required)

-  Load cleaned / exported SQL results (or CSV joins) with **Pandas**
-  Manipulate data: filter, sort, aggregate
-  Use **lists** and **dictionaries** explicitly (see `analysis_template.py`)
-  **≥ 2 professional visualizations** (bar, line, pie, etc.)
- **Submit:** `.py` file (`deliverables/03_analysis.py`) + **≥ 2 images** (`deliverables/charts/`)

### 4. Rigorous debugging & prompt log (required)

-  Original AI prompts (SQL + Python)
-  Errors found in AI output (syntax, logic, inefficiency)
-  How you **edited** and **validated** code (especially lists/dicts & pseudocode conversion)
-  **Group contributions** — who did what
- **Submit:** PDF or Word (`deliverables/04_prompt_log.pdf`)

### 5. Optional video (+5% bonus)

-  5–7 minutes: plan, vibe programming workflow, insights, lists/dicts skill
- **Submit:** public link in cover sheet

----
## Suggested KPIs (pick at least 4)

|KPI|Whyitmatters|
|:-:|:-:|
|Total revenue by **store**|Which location performs best?|
|Total **quantity sold** by **product**|Identify movers vs slow stock|
|**Profit** estimate (`total_amount - cost_price × quantity`)|Margin by category|
|**Average sale amount** per transaction|Basket size|
|Revenue by **category**|Electronics vs furniture mix|
|Daily revenue **trend** (line chart)|Seasonality / spikes|

----
## Group rules

- **3–5 students** per group (instructor-assigned or approved)
- **Equal contribution** to all sections — document in Prompt Log
- **No copy-paste** of unedited AI output

----
## Deliverables summary

|#|Item|Format|
|:-:|:-:|:-:|
|1|Logical plan / flowchart|PDF or PNG|
|2|SQL queries|`.sql`|
|3|Python analysis|`.py`|
|4|Visualizations|≥ 2 PNG/JPG|
|5|Prompt log|PDF or Word|
|6|Video (optional)|URL (+5%)|
**Cover sheet (recommended):** Group #, member names, contribution summary, video link.

----
## Starter files

|File|Purpose|
|:-:|:-:|
|**`SETUP_AND_RUN_GUIDE.md`**|**Install Anaconda/DBeaver/Workbench; load CSVs; run order**|
|`templates/pipeline_plan_template.md`|Plan / flowchart outline|
|`templates/queries_template.sql`|SQL TODOs|
|`templates/analysis_template.py`|Python + lists/dicts + charts|
|`prompt_log_template.md`|Prompt log structure|

----
## Notes for success

1. **Core skill:** Show pseudocode → Python with **lists** and **dictionaries** in `analysis_template.py` (Section 4).
2. **AI is a tool:** Prompt Log proves **your** critical thinking.
3. Keep files **clean and labeled** — easy grading.
4. Run all code end-to-end before submitting.

----
Good luck — orchestrate wisely.