
import sqlite3
import os
import pandas as pd

# 获取当前脚本所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 连接 SQLite 数据库（文件 sales.db 不存在会自动创建）
conn = sqlite3.connect(os.path.join(current_dir, "sales.db"))
cursor = conn.cursor()

# 2. 读取 csv 文件
df = pd.read_csv(os.path.join(current_dir, "sales.csv"))
print("CSV 原始数据预览：")
print(df)

# 3. 将数据写入 SQLite 表 sales，如果存在先覆盖
df.to_sql(name="sales", con=conn, if_exists="replace", index=False)

# 4. 验证数据表是否创建成功
print("\n=== 数据库 sales 表全部数据 ===")
res = cursor.execute("SELECT * FROM sales;").fetchall()
for row in res:
    print(row)


# 5. 按分类分组，查询【**分类名、销售总额、平均订单金额**】
print("\n=== 按分类分组，查询【分类名、销售总额、平均订单金额】 ===")
res = cursor.execute("""
    SELECT 
        category, 
        SUM(amount) AS total_sales, 
        AVG(amount) AS avg_order_amount
    FROM sales
    GROUP BY category;
""").fetchall()
for row in res:
    print(row)


# 6. 分组后，只保留「销售总额大于 700」的分类
print("\n=== 分组后，只保留「销售总额大于 700」的分类 ===")
res = cursor.execute("""
    SELECT 
        category, 
        SUM(amount) AS total_sales, 
        AVG(amount) AS avg_order_amount
    FROM sales
    GROUP BY category
    HAVING total_sales > 700;
""").fetchall()
for row in res:
    print(row)


# 关闭连接
conn.close()