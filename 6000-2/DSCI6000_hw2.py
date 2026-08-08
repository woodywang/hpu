# Setup — run this cell first

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from IPython.display import display, Markdown

# 设置绘图参数
plt.rcParams.update({
    'figure.figsize': (9, 5),
    'font.size': 12,
    'axes.grid': True,
    'grid.alpha': 0.25,
})

print('Setup complete.')

# 设置观测数据 stated

# 定义观测数据：总展示数和总点击数
n_impressions = 200      # 总展示数
n_clicks = 18            # 总点击数

# 计算样本CTR： 总点击数 / 总展示数
sample_ctr = n_clicks / n_impressions

display(Markdown(
    f"Pilot: **{n_clicks}** clicks out of **{n_impressions}** impressions → sample CTR = **{sample_ctr:.1%}**"
))
print(f"Pilot: {n_clicks} clicks out of {n_impressions} impressions → sample CTR = {sample_ctr:.1%}")

# 设置观测数据 completed


# 选择先验贝塔分布的超参数值 stated

# 定义先验贝塔分布的超参数α和β
alpha_prior = 10        # 先验贝塔分布超参数α
beta_prior = 200        # 先验贝塔分布超参数β

# 计算先验贝塔分布的均值和标准差
prior = stats.beta(alpha_prior, beta_prior)     # 创建贝塔分布对象
prior_mean = prior.mean()                       # 计算先验分布的均值
prior_sd = prior.std()                          # 计算先验分布的标准差

# 计算先验贝塔分布的95%等尾概率区间
prior_ci_lower = prior.ppf(0.025)
prior_ci_upper = prior.ppf(0.975)

p = prior.cdf(0.08) - prior.cdf(0.02)           # 计算probability mass over [0.02, 0.08]

display(Markdown(
    f'''Prior: Beta({alpha_prior}, {beta_prior}) → mean = **{prior_mean:.2%}**, sd = **{prior_sd:.3f}**
    95% 先验等尾概率区间 = [{prior_ci_lower:.2%}, {prior_ci_upper:.2%}]
    probability mass over [0.02, 0.08] = **{p:.2%}**'''
))
print(f'''Prior: Beta({alpha_prior}, {beta_prior}) → mean = **{prior_mean:.2%}**, sd = **{prior_sd:.3f}**
    95% 先验等尾概率区间 = [{prior_ci_lower:.2%}, {prior_ci_upper:.2%}]
    probability mass over [0.02, 0.08] = **{p:.2%}**''')

# 选择先验贝塔分布的超参数值 completed


# 绘制先验概率密度函数曲线图 stated

theta = np.linspace(0.001, 0.20, 500)    # θ的取值范围

fig, ax = plt.subplots()                # 创建图表和坐标轴对象

# 绘制先验概率密度函数曲线
ax.plot(theta, prior.pdf(theta), label='Prior', color='blue')

# 绘制95%等尾概率区间的高亮填充区域
ci_theta_range = np.linspace(prior_ci_lower, prior_ci_upper, 200)
ax.fill_between(ci_theta_range, prior.pdf(ci_theta_range), color='lightblue', alpha=0.4, 
                label=f'95% Prior Probability Interval')

# 绘制先验均值的垂直标记线
ax.axvline(prior_mean, color='red', linestyle='--', linewidth=2, 
           label=f'Prior Mean = {prior_mean:.2%}')

# 辅助标记指定的2%-8%行业基准区间
ax.axvspan(0.02, 0.08, color='gray', alpha=0.15, label=f'Industry 2%-8% CTR Baseline')

ax.set_xlabel('True CTR (θ)')           # 设置x轴标签
ax.set_ylabel('Density')                # 设置y轴标签
ax.set_title('Prior PDF of CTR (θ) with Mean and 95% Probability Interval')    # 设置图表标题
ax.legend(fontsize=11)                  # 展示图例说明所有元素
plt.tight_layout()                      # 设置图表布局
plt.show()                              # 显示图表

# 绘制先验概率密度函数曲线图 completed


# 定义二项式对数似然函数 stated

import math
def likelihood(theta, n, z):
    """Likelihood of observing z clicks in n impressions given θ."""

    comb = math.factorial(n) / (math.factorial(z) * math.factorial(n - z))
    return comb * (theta**z) * ((1 - theta)**(n - z))

print(f'''Likelihood of observing {n_clicks} clicks in {n_impressions} 
      impressions at θ = {sample_ctr:.2%}: {likelihood(sample_ctr, n_impressions, n_clicks)}''')

def binomial_log_likelihood(theta, n, k):
    """Log-likelihood of observing k clicks in n impressions given θ."""

    return stats.binom.pmf(k, n, theta)

print(f'''Log-likelihood of observing {n_clicks} clicks in {n_impressions} 
      impressions at θ = {sample_ctr:.2%}: {binomial_log_likelihood(sample_ctr, n_impressions, n_clicks)}''')

# 定义二项式对数似然函数 completed


# 计算后验贝塔分布 stated

# 计算后验贝塔分布的超参数
alpha_post = alpha_prior + n_clicks                     # 后验分布的超参数α：先验超参数α + 观测到的点击数
beta_post = beta_prior + n_impressions - n_clicks       # 后验分布的超参数β：先验超参数β + 观测到的未点击数

# 计算后验贝塔分布的均值
posterior = stats.beta(alpha_post, beta_post)           # 创建后验分布对象
post_mean = posterior.mean()                            # 计算后验分布的均值

display(Markdown(
    f"Posterior: Beta({alpha_post}, {beta_post}) → mean CTR = **{post_mean:.2%}**"
))
print(f"Posterior: Beta({alpha_post}, {beta_post}) → mean CTR = **{post_mean:.2%}**")

# 计算后验贝塔分布 completed


# 绘制先验贝塔分布与后验贝塔分布的比较图 stated

fig, ax = plt.subplots()            # 创建图表和坐标轴对象

ax.plot(theta, prior.pdf(theta), label='Prior', color='blue')           # 绘制先验贝塔分布的概率密度函数曲线
ax.plot(theta, posterior.pdf(theta), label='Posterior', color='red')    # 绘制后验贝塔分布的概率密度函数曲线

ax.set_xlabel('True CTR (θ)')       # 设置x轴标签
ax.set_ylabel('Density')            # 设置y轴标签
ax.set_title('Comparison of Prior and Posterior Beta Distributions')    # 设置图表标题
ax.legend()                         # 展示图例说明所有元素

# 添加先验均值的文本标注
ax.text(0.1, 0.75, f'''Beta({alpha_prior}, {beta_prior})
        Prior Impressions = {beta_prior + alpha_prior}
        Prior Clicks = {alpha_prior}
        Prior Mean = {prior_mean:.2%}''', 
        transform=ax.transAxes, fontsize=10, color='blue', ha='center')

# 添加后验均值的文本标注
ax.text(0.5, 0.73, f'''Beta({alpha_post}, {beta_post})
        Posterior Impressions = {n_impressions}
        Posterior Clicks = {n_clicks}
        Posterior Mean = {post_mean:.2%}''', 
        transform=ax.transAxes, fontsize=10, color='red', ha='center')

plt.tight_layout()                  # 设置图表布局
plt.show()                          # 显示图表

# 绘制先验贝塔分布与后验贝塔分布的比较图 completed


# 计算后验贝塔分布可信区间 stated

ci_low, ci_high = posterior.ppf([0.025, 0.975])    # 计算后验贝塔分布的95%等尾概率区间

display(Markdown(
    f"**95% credible interval:** [{ci_low:.2%}, {ci_high:.2%}]"
))
print(f"95% credible interval: [{ci_low:.2%}, {ci_high:.2%}]")

# 计算后验贝塔分布可信区间 completed
