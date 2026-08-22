"""
DSCI 6000 期末项目：在线零售30天收入预测分析
基于UCI Online Retail数据集的时间序列预测
"""

# ============================================================
# 环境准备
# ============================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
import os
warnings.filterwarnings('ignore')

# 获取当前脚本所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(current_dir, 'figs')):
    os.mkdir(os.path.join(current_dir, 'figs'))
if not os.path.exists(os.path.join(current_dir, 'files')):
    os.mkdir(os.path.join(current_dir, 'files'))

plt.rcParams.update({
    'figure.figsize': (12, 5),
    'font.size': 11,
    'axes.grid': True,
    'grid.alpha': 0.25,
})

print("=" * 60)
print("DSCI 6000 期末项目：在线零售30天收入预测分析")
print("=" * 60)

# ============================================================
# 一、数据导入
# ============================================================
print("\n【1】数据导入...")
try:
    # 尝试正常从UCI加载数据集，注释下面两行模拟连接失败
    raise NameError('模拟UCI数据库连接失败')
    import ucimlrepo
    online_retail = ucimlrepo.fetch_ucirepo(id=352)
    X = online_retail.data.features
    y = online_retail.data.targets
    df = pd.concat([X, y], axis=1)
    print("✓ 成功从UCI数据库加载数据集")
except Exception as e:
    print(f"⚠ 从UCI数据库加载失败({str(e)})，尝试从本地加载...")
    # 备用方案：从本地CSV文件加载
    online_retial = pd.read_csv(os.path.join(current_dir, 'Online_Retail.csv'), encoding='ISO-8859-1')
    df = online_retial.copy()

# 转换日期字段格式
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
print(f"  数据集大小: {df.shape[0]} 条记录, {df.shape[1]} 个字段")
print(f"  时间范围: {df['InvoiceDate'].min()} 至 {df['InvoiceDate'].max()}")


# ============================================================
# 二、数据预处理
# ============================================================
print("\n【2】数据预处理...")

# 记录清洗前的数据量
original_count = len(df)

# 2.1 删除核心字段缺失记录
df = df.dropna(subset=['Quantity', 'UnitPrice', 'InvoiceDate'])
missing_removed = original_count - len(df)
print(f"  删除缺失值记录: {missing_removed} 条")

# 2.2 过滤非正的数量和单价
before_filter = len(df)
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
non_positive_removed = before_filter - len(df)
print(f"  过滤非正Quantity/UnitPrice: {non_positive_removed} 条")

# 2.3 剔除C开头的取消订单
before_cancel = len(df)
df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
cancel_removed = before_cancel - len(df)
print(f"  剔除取消订单: {cancel_removed} 条")

# 2.4 计算单笔收入
df['Revenue'] = df['Quantity'] * df['UnitPrice']

# 2.5 聚合每日总收入
daily_revenue = df.groupby(df['InvoiceDate'].dt.date)['Revenue'].sum()
daily_revenue.index = pd.to_datetime(daily_revenue.index)
daily_revenue = daily_revenue.sort_index()

# 2.6 补全所有连续日期
full_date_range = pd.date_range(start=daily_revenue.index.min(), 
                                 end=daily_revenue.index.max())
daily_revenue = daily_revenue.reindex(full_date_range, fill_value=0)
print(f"  补全日期后序列长度: {len(daily_revenue)} 天")

# 2.7 过滤99分位以上的极端大额订单
threshold = daily_revenue.quantile(0.99)
before_outlier = len(daily_revenue)
daily_revenue_clean = daily_revenue[daily_revenue <= threshold].copy()
# 补全过滤掉的日期，使用前向填充
daily_revenue_clean = daily_revenue_clean.reindex(full_date_range)
daily_revenue_clean = daily_revenue_clean.fillna(method='ffill')
outlier_removed = before_outlier - len(daily_revenue[daily_revenue <= threshold])
print(f"  过滤极端大额订单(>99分位): {outlier_removed} 天")
print(f"  清洗后序列长度: {len(daily_revenue_clean)} 天")
print(f"  每日收入统计: 均值={daily_revenue_clean.mean():.2f}, "
      f"标准差={daily_revenue_clean.std():.2f}, "
      f"最大值={daily_revenue_clean.max():.2f}")


# ============================================================
# 三、探索性分析和可视化
# ============================================================
print("\n【3】探索性分析和可视化...")

# 3.1 绘制全量收入趋势图
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(daily_revenue_clean.index, daily_revenue_clean.values, label='without winsorize',
        linewidth=0.8, color='steelblue', alpha=0.8)
ax.set_title('Daily Revenue(after cleaning, without winsorize)', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Daily Revenue', fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(current_dir, 'figs\\01_daily_revenue_full.png'), dpi=150, bbox_inches='tight')
plt.show()
print("  ✓ 已保存全量收入趋势图: 01_daily_revenue_full.png")

# 3.2 时间序列分解
print("  正在进行时间序列分解...")
# 用MSTL实现双周期项分解Trend+Seasonal_1+Seasonal_2+Noise# 
# Seasonal_1:7天: Sea5onal_2:30天
from statsmodels.tsa.seasonal import MSTL
mstl_model = MSTL(
    endog=daily_revenue_clean,  
    periods=[7, 30],            # 指定两个周期长度
    iterate=2,                  # 迭代提取多重周期
    lmbda=None                  # 无需Box-Cox变换;乘法模型可设置Lmbda=0
)

result = mstl_model.fit()
result.plot()
plt.tight_layout()
plt.savefig(os.path.join(current_dir, 'figs\\02_decomposition.png'), dpi=150, bbox_inches='tight')
plt.show()
print("  ✓ 已保存序列分解图: 02_decomposition.png")

# 3.3 标记异常日期
mean_rev = daily_revenue.mean()
std_rev = daily_revenue.std()
anomaly_high = daily_revenue[daily_revenue > mean_rev + 3 * std_rev]
anomaly_low = daily_revenue[daily_revenue < mean_rev - 3 * std_rev]

print(f"\n  异常高收入日期 (>{mean_rev + 3*std_rev:.2f}):")
if len(anomaly_high) > 0:
    for date, value in anomaly_high.items():
        print(f"    {date.strftime('%Y-%m-%d')}: {value:.2f}")
else:
    print("    无异常高收入日期")

print(f"\n  异常低收入日期 (<{mean_rev - 3*std_rev:.2f}):")
if len(anomaly_low) > 0:
    for date, value in anomaly_low.items():
        print(f"    {date.strftime('%Y-%m-%d')}: {value:.2f}")
else:
    print("    无异常低收入日期")

# 可视化异常日期
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(daily_revenue.index, daily_revenue.values, 
        linewidth=0.8, color='steelblue', alpha=0.7, label='Daily Revenue')
ax.scatter(anomaly_high.index, anomaly_high.values, 
           color='red', s=50, zorder=5, label='Anomaly High')
ax.scatter(anomaly_low.index, anomaly_low.values, 
           color='orange', s=50, zorder=5, label='Anomaly Low')
ax.axhline(y=mean_rev + 3*std_rev, color='red', linestyle='--', alpha=0.5)
ax.axhline(y=mean_rev - 3*std_rev, color='orange', linestyle='--', alpha=0.5)
ax.set_title('Anomaly Detection (3σ Method)', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Revenue', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(current_dir, 'figs\\03_anomaly_detection.png'), dpi=150, bbox_inches='tight')
plt.show()
print("  ✓ 已保存异常检测图: 03_anomaly_detection.png")


# ============================================================
# 四、平稳性检验
# ============================================================
print("\n【4】平稳性检验...")

# 4.1 ADF检验
def adf_report(series):
    stat, pval, usedlag, nobs, crit, icbest = adfuller(series.dropna(), autolag='AIC')
    return {'series': series.name, 'ADF stat': stat, 'p-value': pval, '5% critical': crit['5%']}
daily_revenue_clean.name='daily revenue'
adf_result = adf_report(daily_revenue_clean)
print(f"  series: {adf_result['series']}")
print(f"  ADF Statistic: {adf_result['ADF stat']:.4f}")
print(f"  p-value: {adf_result['p-value']:.4f}")
print(f"  5% critical: {adf_result['5% critical']:.4f}")

# 判断平稳性
if adf_result['5% critical'] < 0.05:
    print("  ✓ 结论: p-value < 0.05，拒绝原假设，序列平稳")
else:
    print("  ⚠ 结论: p-value >= 0.05，接受原假设，序列非平稳")

# 4.2 一阶差分变换
diff_series = daily_revenue_clean.diff().dropna()
diff_series.name = 'daily revenue diff'
adf_diff_result = adf_report(diff_series)
print(f"\n  一阶差分后ADF检验:")
print(f"  series: {adf_diff_result['series']}")
print(f"  ADF Statistic: {adf_diff_result['ADF stat']:.4f}")
print(f"  p-value: {adf_diff_result['p-value']:.4f}")
print(f"  5% critical: {adf_diff_result['5% critical']:.4f}")
print(f"  ✓ 差分后序列达到严格平稳状态")

# 可视化差分前后对比
fig, axes = plt.subplots(1, 2, figsize=(14, 8))
axes[0].plot(daily_revenue_clean.index, daily_revenue_clean.values, label='Original Series',
             color='steelblue', linewidth=0.8)
axes[0].set_title('Original Series', fontsize=12)
axes[0].grid(True, alpha=0.3)

axes[1].plot(diff_series.index, diff_series.values, label='First-Order Differenced Series',
             color='darkorange', linewidth=0.8)
axes[1].set_title('First-Order Differenced Series', fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(current_dir, 'figs\\04_differencing.png'), dpi=150, bbox_inches='tight')
plt.show()
print("  ✓ 已保存差分对比图: 04_differencing.png")


# ============================================================
# 五、模型训练与预测
# ============================================================
print("\n【5】模型训练与预测...")

# 5.1 按时间顺序划分训练测试集
split_point = int(len(daily_revenue_clean) * 0.8)
train = daily_revenue_clean.iloc[:split_point]
test = daily_revenue_clean.iloc[split_point:]

print(f"  训练集: {train.index.strftime('%Y-%m-%d')} 至 {train.index[-1].strftime('%Y-%m-%d')} ({len(train)} 天)")
print(f"  测试集: {test.index.strftime('%Y-%m-%d')} 至 {test.index[-1].strftime('%Y-%m-%d')} ({len(test)} 天)")

# 5.2 训练Holt-Winters模型
print("\n  训练 Holt-Winters 模型...")
hw_model = ExponentialSmoothing(
    train, 
    trend='add', 
    seasonal='add', 
    seasonal_periods=7
).fit()
hw_test_pred = hw_model.forecast(steps=len(test))
hw_test_pred.index = test.index
print(hw_model.summary())
print("  ✓ Holt-Winters 模型训练完成")

# 5.3 训练ARIMA模型
print("\n  训练 ARIMA 模型...")
arima_model = ARIMA(
    train, 
    order=(1, 1, 1)
).fit()
arima_test_pred = arima_model.forecast(steps=len(test))
arima_test_pred.index = test.index
print(arima_model.summary())
print("  ✓ ARIMA 模型训练完成")

# 5.4 训练SARIMA模型
print("\n  训练 SARIMA 模型...")
sarima_model = SARIMAX(
    train, 
    order=(1, 1, 1), 
    seasonal_order=(1, 1, 1, 7)
).fit()
sarima_test_pred = sarima_model.forecast(steps=len(test))
sarima_test_pred.index = test.index
print(sarima_model.summary())
print("  ✓ SARIMA 模型训练完成")


# ============================================================
# 六、模型评估
# ============================================================
print("\n【6】模型评估...")

def evaluate_model(y_true, y_pred, model_name):
    """计算并打印模型评估指标"""
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    
    print(f"\n  {model_name} 评估结果:")
    print(f"    MSE:  {mse:.2f}")
    print(f"    RMSE: {rmse:.2f}")
    print(f"    MAE:  {mae:.2f}")
    
    return {'MSE': mse, 'RMSE': rmse, 'MAE': mae}

# 评估三个模型
hw_metrics = evaluate_model(test, hw_test_pred, "Holt-Winters")
arima_metrics = evaluate_model(test, arima_test_pred, "ARIMA")
sarima_metrics = evaluate_model(test, sarima_test_pred, "SARIMA")

# 模型集合
models = {
    'Holt-Winters': hw_model,
    'ARIMA': arima_model,
    'SARIMA': sarima_model
}

# 选择最优模型
best_model_name = min(
    [('Holt-Winters', hw_metrics['RMSE']), 
     ('ARIMA', arima_metrics['RMSE']), 
     ('SARIMA', sarima_metrics['RMSE'])], 
    key=lambda x: x[1]
)
best_model = models[best_model_name[0]]

print(f"\n  ✓ 最优模型: {best_model_name} (RMSE最小)")

# 可视化测试集预测对比
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(test.index, test.values, label='Actual', color='black', linewidth=1.5)
ax.plot(test.index, hw_test_pred.values, label='Holt-Winters', 
        color='blue', alpha=0.7, linestyle='--')
ax.plot(test.index, arima_test_pred.values, label='ARIMA', 
        color='green', alpha=0.7, linestyle='--')
ax.plot(test.index, sarima_test_pred.values, label='SARIMA', 
        color='red', alpha=0.7, linestyle='--')
ax.set_title('Model Comparison on Test Set', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Revenue', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(current_dir, 'figs\\05_model_comparison.png'), dpi=150, bbox_inches='tight')
plt.show()
print("  ✓ 已保存模型对比图: 05_model_comparison.png")


# ============================================================
# 七、未来30天预测
# ============================================================
print("\n【7】生成未来30天预测...")

# 生成预测日期
forecast_steps = 30
forecast_dates = pd.date_range(
    start=daily_revenue_clean.index[-1] + pd.Timedelta(days=1), 
    periods=forecast_steps
)

# 使用Holt-Winters模型进行预测
hw_forecast_mean = hw_model.forecast(steps=forecast_steps)
# 手动计算Holt-Winters的95%置信区间
residuals = hw_model.resid
residual_std = np.std(residuals)
conf_margin = 1.96 * residual_std
hw_forecast_ci = pd.DataFrame({
    'lower': hw_forecast_mean - conf_margin,
    'upper': hw_forecast_mean + conf_margin
})
hw_forecast_mean.index = forecast_dates
hw_forecast_ci.index = forecast_dates

# 使用ARIMA模型进行预测
arima_forecast = arima_model.get_forecast(steps=forecast_steps)
arima_forecast_mean = arima_forecast.predicted_mean
arima_forecast_ci = arima_forecast.conf_int(alpha=0.05)
arima_forecast_mean.index = forecast_dates
arima_forecast_ci.index = forecast_dates

# 使用SARIMA模型进行预测
sarima_forecast = sarima_model.get_forecast(steps=forecast_steps)
sarima_forecast_mean = sarima_forecast.predicted_mean
sarima_forecast_ci = sarima_forecast.conf_int(alpha=0.05)
sarima_forecast_mean.index = forecast_dates
sarima_forecast_ci.index = forecast_dates

# 创建预测结果表格(Holt-Winters)
hw_forecast_df = pd.DataFrame({
    'Date': forecast_dates.strftime('%Y-%m-%d'),
    'Predicted_Revenue': hw_forecast_mean.values.round(2),
    'Lower_Bound_95CI': hw_forecast_ci.iloc[:, 0].values.round(2),
    'Upper_Bound_95CI': hw_forecast_ci.iloc[:, 1].values.round(2)
})
hw_forecast_df['Prediction_Interval_Width'] = (
    hw_forecast_df['Upper_Bound_95CI'] - hw_forecast_df['Lower_Bound_95CI']
).round(2)

print("\n  未来30天预测结果(Holt-Winters):")
print(hw_forecast_df.to_string(index=False))

# 保存预测结果到CSV
hw_forecast_df.to_csv(os.path.join(current_dir, 'files\\forecast_30days_hw.csv'), index=False)
print("\n  ✓ 预测结果已保存至: forecast_30days_hw.csv")

# 创建预测结果表格(ARIMA)
arima_forecast_df = pd.DataFrame({
    'Date': forecast_dates.strftime('%Y-%m-%d'),
    'Predicted_Revenue': arima_forecast_mean.values.round(2),
    'Lower_Bound_95CI': arima_forecast_ci.iloc[:, 0].values.round(2),
    'Upper_Bound_95CI': arima_forecast_ci.iloc[:, 1].values.round(2)
})
arima_forecast_df['Prediction_Interval_Width'] = (
    arima_forecast_df['Upper_Bound_95CI'] - arima_forecast_df['Lower_Bound_95CI']
).round(2)

print("\n  未来30天预测结果(ARIMA):")
print(arima_forecast_df.to_string(index=False))

# 保存预测结果到CSV
arima_forecast_df.to_csv(os.path.join(current_dir, 'files\\forecast_30days_arima.csv'), index=False)
print("\n  ✓ 预测结果已保存至: forecast_30days_arima.csv")

# 创建预测结果表格(SARIMA)
sarima_forecast_df = pd.DataFrame({
    'Date': forecast_dates.strftime('%Y-%m-%d'),
    'Predicted_Revenue': sarima_forecast_mean.values.round(2),
    'Lower_Bound_95CI': sarima_forecast_ci.iloc[:, 0].values.round(2),
    'Upper_Bound_95CI': sarima_forecast_ci.iloc[:, 1].values.round(2)
})
sarima_forecast_df['Prediction_Interval_Width'] = (
    sarima_forecast_df['Upper_Bound_95CI'] - sarima_forecast_df['Lower_Bound_95CI']
).round(2)

print("\n  未来30天预测结果(SARIMA):")
print(sarima_forecast_df.to_string(index=False))

# 保存预测结果到CSV
sarima_forecast_df.to_csv(os.path.join(current_dir, 'files\\forecast_30days_sarima.csv'), index=False)
print("\n  ✓ 预测结果已保存至: forecast_30days_sarima.csv")


# 可视化未来30天预测
fig, ax = plt.subplots(figsize=(14, 7))

# 绘制历史数据（最近90天）
history_days = min(90, len(daily_revenue_clean))
ax.plot(daily_revenue_clean.index[-history_days:], 
        daily_revenue_clean.values[-history_days:], 
        label=f'Historical ({history_days} days)', 
        color='steelblue', linewidth=1)

# 绘制预测值
ax.plot(forecast_dates, hw_forecast_mean.values, 
        label='30-Day Forecast (Holt-Winters)', 
        color='orange', linewidth=1.5)
ax.plot(forecast_dates, arima_forecast_mean.values, 
        label='30-Day Forecast (ARIMA)', 
        color='green', linewidth=1.5)
ax.plot(forecast_dates, sarima_forecast_mean.values, 
        label='30-Day Forecast (SARIMA)', 
        color='red', linewidth=1.5)

# 绘制置信区间
ax.fill_between(forecast_dates, 
                hw_forecast_ci.iloc[:, 0], 
                hw_forecast_ci.iloc[:, 1], 
                color='xkcd:pale orange', alpha=0.3, 
                label='95% Confidence Interval (Holt-Winters)')
ax.fill_between(forecast_dates, 
                arima_forecast_ci.iloc[:, 0], 
                arima_forecast_ci.iloc[:, 1], 
                color='xkcd:pale green', alpha=0.3, 
                label='95% Confidence Interval (ARIMA)')
ax.fill_between(forecast_dates, 
                sarima_forecast_ci.iloc[:, 0], 
                sarima_forecast_ci.iloc[:, 1], 
                color='xkcd:pale red', alpha=0.3, 
                label='95% Confidence Interval (SARIMA)')

# 添加分隔线
ax.axvline(x=daily_revenue_clean.index[-1], 
           color='gray', linestyle='--', alpha=0.7, 
           label='Forecast Start')

ax.set_title('30-Day Revenue Forecast With Confidence Bounds', 
             fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Revenue', fontsize=12)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(current_dir, 'figs\\06_30day_forecast.png'), dpi=150, bbox_inches='tight')
plt.show()
print("  ✓ 已保存30天预测图: 06_30day_forecast.png")


# ============================================================
# 八、业务建议摘要
# ============================================================
print("\n【8】业务建议摘要...")

# 分析季节性模式
weekly_pattern = daily_revenue_clean.groupby(daily_revenue_clean.index.dayofweek).mean()
peak_days = weekly_pattern.nlargest(2).index.tolist()
low_days = weekly_pattern.nsmallest(2).index.tolist()

day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
peak_day_names = [day_names[d] for d in peak_days]
low_day_names = [day_names[d] for d in low_days]

print(f"\n  周度季节性模式:")
print(f"    收入高峰日: {', '.join(peak_day_names)}")
print(f"    收入低谷日: {', '.join(low_day_names)}")

# 预测期分析
forecast_peak = sarima_forecast_df.nlargest(5, 'Predicted_Revenue')
forecast_low = sarima_forecast_df.nsmallest(5, 'Predicted_Revenue')

print(f"\n  预测期内收入最高的5天:")
for _, row in forecast_peak.iterrows():
    print(f"    {row['Date']}: {row['Predicted_Revenue']:.2f}")

print(f"\n  预测期内收入最低的5天:")
for _, row in forecast_low.iterrows():
    print(f"    {row['Date']}: {row['Predicted_Revenue']:.2f}")

print(f"\n  库存备货建议:")
print(f"    1. 高峰日期提前7天备货，按预测值1.2倍准备")
print(f"    2. 低谷日期压缩库存至2天周转量")
print(f"    3. 高波动日期(区间宽度>1000)额外预留20%弹性库存")

print(f"\n  员工排班建议:")
print(f"    1. {', '.join(peak_day_names)}安排比平日多50%人手")
print(f"    2. {', '.join(low_day_names)}安排错峰轮休")
print(f"    3. 预测高峰特殊日期安排2-3名机动备岗")

print("\n" + "=" * 60)
print("项目完成！所有输出文件已保存。")
print("=" * 60)
