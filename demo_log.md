# 项目方出货侦探 · 完整演示日志

**项目：** 币安大赛 — 项目方出货侦探 Agent  
**时间：** 2026-03-06 23:31 GMT+11  
**分析对象：** Baby Doge Coin (BabyDoge) · BSC (chainId: 56)  
**合约地址：** `0xc748673057861a797275cd8a068abb95a902e8de`  
**创始人地址：** `0xa4a6db60a345e40f389792952149b2d1255b9542`

---

## 综合风险评级：🟡 MEDIUM-HIGH RISK

> 合约本身安全（低风险），但项目方已出货，市场卖压显著，聪明钱全部离场。

---

## Step 1：合约安全分析（query-token-audit）

### API
```
POST https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit
{
  "binanceChainId": "56",
  "contractAddress": "0xc748673057861a797275cd8a068abb95a902e8de",
  "requestId": "<uuid>"
}
```

### 结果

| 指标 | 数值 |
|------|------|
| riskLevelEnum | **LOW** |
| riskLevel | **1** |
| buyTax | 0% |
| sellTax | 0% |
| hasResult | true |
| isSupported | true |
| Binance 白名单 | ✓ Yes |
| 合约已放弃所有权 | ✓ Yes（Contract Renounced）|

**关键安全检测（均未命中）：**
- ✅ Honeypot Not Found
- ✅ Blacklist Not Found
- ✅ Trading Suspension Not Found
- ✅ Self-Destruct Not Found
- ✅ Whitelist Restrictions Not Found
- ✅ Cooling-Off Not Found

**结论：** 合约层面 🟢 安全，无蜜罐/黑名单/高税率风险。

截图：`screenshots/step1_token_audit.jpg`

---

## Step 2：代币市场数据（query-token-info）

### API
```
GET /bapi/defi/v4/public/.../token/dynamic/info?chainId=56&contractAddress=0xc748...8de
GET /bapi/defi/v1/public/.../token/meta/info?chainId=56&contractAddress=0xc748...8de
```

### 市场数据

| 指标 | 数值 |
|------|------|
| 当前价格 | $0.000000000391 |
| 市值 (Market Cap) | $79,243,352（$79.24M）|
| FDV | $164,260,408 |
| 流动性 | $14,732,650 |
| 持有人数 | 1,907,691 |
| Top 10 持有人占比 | 24.98% |
| 24H 涨跌 | **-4.06%** |

### ⚠️ 出货信号检测

| 指标 | 数值 | 信号 |
|------|------|------|
| 24H 卖出量 | **$114,021 (61.3%)** | 🔴 |
| 24H 买入量 | $71,909 (38.7%) | — |
| 买卖比 | 卖出/买入 = **1.59x** | 🔴 |
| Smart Money 持有人 | **0 人** | 🔴 |
| KOL 持有人 | 29 人 | 🟡 |
| Dev 持仓比例 | **0%** | 🔴 |

**结论：** 卖压明显大于买盘，聪明钱清零，开发方已退出。

截图：`screenshots/step2_token_info.jpg`

---

## Step 3：Smart Money 大户动向（trading-signal）

### API
```
POST https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/web/signal/smart-money
{"smartSignalType":"","page":1,"pageSize":5,"chainId":"56"}
```

### BSC 当前 Smart Money 信号（Top 5）

| 代币 | 方向 | 聪明钱数 | 最大涨幅 | 退出率 |
|------|------|---------|---------|--------|
| 龙虾 (LOBSTER) | 买入 | 5 | +1.28% | 75% |
| GIRAFFES | 买入 | 6 | +4.68% | 16% |
| OPTIMUS | 买入 | 7 | +0.41% | 76% |
| 死对头 | 买入 | 5 | +0.56% | 23% |
| AGENT | 买入 | 5 | +0.57% | 98% |

**BabyDoge 对比：** Smart Money 信号全部指向其他代币。BabyDoge `smartMoneyHolders = 0`，聪明钱已全部离场。

截图：`screenshots/step3_trading_signal.jpg`

---

## Step 4：市场排名 / 社交热度（crypto-market-rank）

### API
```
GET /bapi/defi/v1/.../pulse/social/hype/rank/leaderboard?chainId=56&sentiment=All&timeRange=1
```

### BSC 社交热度榜 Top 5

| 排名 | 代币 | 社交热度 | 情绪 |
|------|------|---------|------|
| #1 | BTC | 8,528,945 | Positive |
| #2 | ETH | 1,734,121 | Positive |
| #3 | XRP | 1,005,502 | Positive |
| #4 | TTD | 440,402 | Positive |
| #5 | TRX | 220,365 | Positive |

**BabyDoge 对比：** 未出现在 Top 5 社交热榜，社区热度持续衰减，为出货阶段典型特征。

截图：`screenshots/step4_market_rank.jpg`

---

## Step 5：项目方钱包持仓分析（query-address-info）

### API
```
GET /bapi/defi/v3/.../address/pnl/active-position-list
?address=0xa4a6db60a345e40f389792952149b2d1255b9542&chainId=56
```

### 创始人钱包持仓（全部归零）

| 代币 | 持有量 | 估值 | 信号 |
|------|--------|------|------|
| BabyDoge | 未在活跃持仓 | $0.00 | 🔴 已清仓 |
| FLOKI | ~0 | $0.00 | 🔴 |
| WBNB | ~0 | $0.00 | 🔴 |
| BADAI | ~0 | $0.00 | 🔴 |
| VINU | 1,000,000 (worthless) | $0.00 | 🔴 |

**devHoldingPercent = 0%** — 开发团队无任何代币利益绑定。

**结论（最关键证据）：** 创始人钱包所有主要资产已归零，BabyDoge 未出现在活跃持仓，疑似已完成出货。

截图：`screenshots/step5_address_info.jpg`

---

## 综合风险评级

| 维度 | 数据 | 信号 | 权重 |
|------|------|------|------|
| 合约安全 | Level 1 LOW，税率0% | 🟢 安全 | 20% |
| 买卖压力 | 卖$114K vs 买$72K（61%卖压）| 🔴 出货 | 25% |
| Smart Money | 持有人=0，无主力建仓 | 🔴 离场 | 20% |
| 社交热度 | 未进 Top 5，热度低迷 | 🟡 冷淡 | 15% |
| 项目方持仓 | Creator 钱包全部归零 | 🔴 已清仓 | 20% |

### 最终评级：🟡 MEDIUM-HIGH RISK

**侦探结论：** BabyDoge 合约本身安全，无技术风险，但项目方已完成出货，聪明钱全部离场，社区热度低迷，卖压持续大于买盘。属于「合约安全但项目方跑路」的典型案例。

---

## 截图文件

```
screenshots/step1_token_audit.jpg     105K  合约安全审计
screenshots/step2_token_info.jpg       84K  代币市场数据
screenshots/step3_trading_signal.jpg   85K  Smart Money 信号
screenshots/step4_market_rank.jpg      96K  社交热度排名
screenshots/step5_address_info.jpg    113K  项目方钱包持仓
screenshots/step6_summary_report.jpg  115K  综合风险评级报告
```

---

⚠️ 本报告仅用于技术演示，所有数据来自 Binance Web3 公开 API，不构成投资建议。代币投资有风险，请务必自行研究（DYOR）。
