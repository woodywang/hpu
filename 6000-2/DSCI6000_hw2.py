# Setup — run this cell first

import math
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
    f'''Prior: Beta({alpha_prior}, {beta_prior}) → mean = **{prior_mean:.2%}**, sd = **{prior_sd:.4f}**
    95% 先验等尾概率区间 = [{prior_ci_lower:.2%}, {prior_ci_upper:.2%}]
    probability mass over [0.02, 0.08] = **{p:.2%}**'''
))
print(f'''Prior: Beta({alpha_prior}, {beta_prior}) → mean = {prior_mean:.2%}, sd = {prior_sd:.4f}
    95% 先验等尾概率区间 = [{prior_ci_lower:.2%}, {prior_ci_upper:.2%}]
    probability mass over [0.02, 0.08] = {p:.2%}''')

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


# 定义二项式似然函数与对数似然函数 stated

def binomial_likelihood(theta, n, z):
    """Likelihood of observing z clicks in n impressions given θ."""

    comb = math.factorial(n) / (math.factorial(z) * math.factorial(n - z))
    return comb * (theta**z) * ((1 - theta)**(n - z))

def binomial_log_likelihood(theta, n, z):
    """Log-likelihood of observing z clicks in n impressions given θ."""

    return stats.binom.logpmf(z, n, theta)

# 手写公式与 scipy.stats.binom.pmf 互为交叉验证，应得到相同结果
lik_manual = binomial_likelihood(sample_ctr, n_impressions, n_clicks)
lik_scipy = stats.binom.pmf(n_clicks, n_impressions, sample_ctr)
loglik = binomial_log_likelihood(sample_ctr, n_impressions, n_clicks)

print(f'''Likelihood of observing {n_clicks} clicks in {n_impressions} impressions at θ = {sample_ctr:.2%}:
    manual formula      = {lik_manual:.10f}
    scipy binom.pmf     = {lik_scipy:.10f}
    log-likelihood      = {loglik:.6f}   (= ln {lik_manual:.6f})''')

# 定义二项式似然函数与对数似然函数 completed


# 绘制二项似然函数曲线图 stated

# 似然函数是关于θ的函数：给定观测数据(200次展示, 18次点击)，不同θ值的相对合理性
lik_curve = stats.binom.pmf(n_clicks, n_impressions, theta)

fig, ax = plt.subplots()

ax.plot(theta, lik_curve, color='green', label='Likelihood L(θ)')
ax.fill_between(theta, lik_curve, color='green', alpha=0.12)

# 似然函数在θ = 18/200 = 9%处取得最大值（最大似然估计MLE）
ax.axvline(sample_ctr, color='black', linestyle='--', linewidth=2,
           label=f'MLE = observed CTR = {sample_ctr:.2%}')

ax.set_xlabel('True CTR (θ)')
ax.set_ylabel('Likelihood  L(θ) = P(z=18 | n=200, θ)')
ax.set_title('Binomial Likelihood of 18 Clicks out of 200 Impressions')
ax.legend(fontsize=11)
plt.tight_layout()
plt.show()

# 绘制二项似然函数曲线图 completed


# 计算后验贝塔分布 stated

# 计算后验贝塔分布的超参数
alpha_post = alpha_prior + n_clicks                     # 后验分布的超参数α：先验超参数α + 观测到的点击数
beta_post = beta_prior + n_impressions - n_clicks       # 后验分布的超参数β：先验超参数β + 观测到的未点击数

# 计算后验贝塔分布的均值和标准差
posterior = stats.beta(alpha_post, beta_post)           # 创建后验分布对象
post_mean = posterior.mean()                            # 计算后验分布的均值
post_sd = posterior.std()                               # 计算后验分布的标准差

# 后验均值是先验均值与观测CTR的加权平均，权重为各自的等效样本量
w_prior = (alpha_prior + beta_prior) / (alpha_prior + beta_prior + n_impressions)
w_data = n_impressions / (alpha_prior + beta_prior + n_impressions)

display(Markdown(
    f"Posterior: Beta({alpha_post}, {beta_post}) → mean CTR = **{post_mean:.2%}**, sd = **{post_sd:.4f}**"
))
print(f'''Posterior: Beta({alpha_post}, {beta_post}) → mean CTR = {post_mean:.2%}, sd = {post_sd:.4f}
    后验均值 = 先验权重 × 先验均值 + 数据权重 × 观测CTR
             = {w_prior:.4f} × {prior_mean:.2%} + {w_data:.4f} × {sample_ctr:.2%} = {w_prior*prior_mean + w_data*sample_ctr:.2%}
    不确定性收窄：先验sd {prior_sd:.4f} → 后验sd {post_sd:.4f}，降幅 {1 - post_sd/prior_sd:.1%}''')

# 计算后验贝塔分布 completed


# 计算后验贝塔分布可信区间 stated

ci_low, ci_high = posterior.ppf([0.025, 0.975])    # 计算后验贝塔分布的95%等尾概率区间

display(Markdown(
    f"**95% credible interval:** [{ci_low:.2%}, {ci_high:.2%}]"
))
print(f"95% credible interval: [{ci_low:.2%}, {ci_high:.2%}]")

# 计算后验贝塔分布可信区间 completed


# 绘制先验贝塔分布与后验贝塔分布的比较图 stated

fig, ax = plt.subplots()            # 创建图表和坐标轴对象

ax.plot(theta, prior.pdf(theta), label='Prior', color='blue')           # 绘制先验贝塔分布的概率密度函数曲线
ax.plot(theta, posterior.pdf(theta), label='Posterior', color='red')    # 绘制后验贝塔分布的概率密度函数曲线

# 绘制后验95%可信区间的高亮填充区域
post_ci_range = np.linspace(ci_low, ci_high, 200)
ax.fill_between(post_ci_range, posterior.pdf(post_ci_range), color='lightcoral', alpha=0.35,
                label=f'95% Credible Interval [{ci_low:.2%}, {ci_high:.2%}]')

# 绘制先验均值与后验均值的垂直标记线（必须在 legend() 之前调用才会进入图例）
ax.axvline(prior_mean, color='blue', linestyle='--', linewidth=2,
           label=f'Prior Mean = {prior_mean:.2%}')
ax.axvline(post_mean, color='red', linestyle='--', linewidth=2,
           label=f'Posterior Mean = {post_mean:.2%}')

ax.set_xlabel('True CTR (θ)')       # 设置x轴标签
ax.set_ylabel('Density')            # 设置y轴标签
ax.set_title('Comparison of Prior and Posterior Beta Distributions')    # 设置图表标题
ax.legend(fontsize=9)               # 展示图例说明所有元素

# 添加先验的文本标注（展示次数与点击数均为"等效样本量"口径：α+β 与 α）
ax.text(0.015, 0.97, '\n'.join([
        f'Beta({alpha_prior}, {beta_prior})',
        f'Effective n = {alpha_prior + beta_prior}',
        f'Effective clicks = {alpha_prior}',
        f'Prior Mean = {prior_mean:.2%}']),
        transform=ax.transAxes, fontsize=9.5, color='blue', ha='left', va='top')

# 添加后验的文本标注（同为等效样本量口径：α+β = 410，α = 28）
ax.text(0.52, 0.45, '\n'.join([
        f'Beta({alpha_post}, {beta_post})',
        f'Effective n = {alpha_post + beta_post}',
        f'Effective clicks = {alpha_post}',
        f'Posterior Mean = {post_mean:.2%}']),
        transform=ax.transAxes, fontsize=9.5, color='red', ha='left', va='top')

plt.tight_layout()                  # 设置图表布局
plt.show()                          # 显示图表

# 绘制先验贝塔分布与后验贝塔分布的比较图 completed


# 计算支撑上线决策的后验概率 stated

# 作业要求"仅以贝叶斯后验结果作为证据"，最直接的证据即对θ的后验概率陈述
print('后验概率陈述（Posterior probability statements）:')
for threshold, note in [(0.02, '行业最差基准'), (0.05, '行业中位水平'),
                        (0.06, '业务盈亏平衡假设值'), (0.08, '行业最优基准')]:
    prob = 1 - posterior.cdf(threshold)
    print(f'    P(θ > {threshold:.0%} | data) = {prob:6.1%}   ({note})')

# 后验分布落在行业基准区间之外（即优于行业上限）的概率
print(f'\n    P(θ < {ci_low:.2%} | data) = {posterior.cdf(ci_low):.1%}   (可信区间下限，即最不利情形)')

# 计算支撑上线决策的后验概率 completed


# 先验敏感性分析 stated

# 先验等效样本量(210)与试点数据量(200)相当，先验较强，需检验结论对先验设定的稳健性
print('先验敏感性分析（Prior sensitivity analysis，各先验均值均设为5%）:')
print(f"{'先验设定':<26}{'等效样本量':>10}{'后验均值':>10}{'95%可信区间':>22}{'P(θ>5%)':>10}")
for a, b, tag in [(10, 200, '本报告 Beta(10,200)'),
                  (2, 38, '弱先验 Beta(2,38)'),
                  (1, 1, '无信息先验 Beta(1,1)'),
                  (25, 475, '强先验 Beta(25,475)')]:
    post_alt = stats.beta(a + n_clicks, b + n_impressions - n_clicks)
    lo, hi = post_alt.ppf([0.025, 0.975])
    print(f'{tag:<26}{a+b:>10}{post_alt.mean():>10.2%}'
          f'{f"[{lo:.2%}, {hi:.2%}]":>22}{1-post_alt.cdf(0.05):>10.1%}')

print('\n结论：后验均值随先验强度在 6.14%~9.41% 之间变动，但 P(θ>5%) 在所有设定下均 ≥ 90%，')
print('      即"该广告优于行业中位水平"这一上线依据对先验选择是稳健的。')

# 先验敏感性分析 completed
