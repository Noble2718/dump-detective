---
name: dump-detective
description: "Use this skill when the user asks to 'check if a token team is dumping', 'analyze token dump risk', '查某个代币是否出货', '分析项目方出货', '检测出货行为', '某代币安全吗', or mentions detecting whether a token's project team has sold their holdings. Runs a 5-step Binance Web3 API pipeline: contract audit → market data → smart money signals → social hype → creator wallet forensics. Outputs a unified risk rating (🔴 HIGH / 🟡 MEDIUM-HIGH / 🟢 LOW). Best for BSC chain tokens. GitHub: https://github.com/JN-Bot666/dump-detective"
license: MIT
metadata:
  author: JN-Bot666
  version: "1.1.0"
  homepage: "https://github.com/JN-Bot666/dump-detective"
  chain: BSC (chainId: 56)
  apis: Binance Web3 Public API
---

# 出货侦探 DumpDetective

通过调用 5 个 Binance Web3 公开 API，自动分析代币是否存在项目方出货风险。

**GitHub：** https://github.com/JN-Bot666/dump-detective

---

## 使用场景

用户说以下任意内容时触发本 Skill：
- "帮我查 `0x合约地址` 是否出货了"
- "分析一下 XXX 代币的出货风险"
- "项目方跑路了吗"
- "这个币安全吗，创始人还持仓吗"

---

## 5步分析流程

### Step 1 — 合约安全审计（query-token-audit）

```http
POST https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit
{
  "binanceChainId": "56",
  "contractAddress": "<token_address>",
  "requestId": "<uuid>"
}
```

**检测项：** 蜜罐、黑名单、自毁函数、交易暂停、买卖税率、白名单限制
**信号：** riskLevel=1(LOW) ✅ | riskLevel≥2 ⚠️

---

### Step 2 — 代币市场数据（query-token-info）

```http
GET https://web3.binance.com/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info
    ?chainId=56&contractAddress=<address>
GET https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/meta/info
    ?chainId=56&contractAddress=<address>
```

**关键字段：**
- `buy24hUsd` vs `sell24hUsd` → 买卖压力比（卖>买 = 🔴）
- `smartMoneyHolders` → 聪明钱持有人数（=0 = 🔴）
- `devHoldingPercent` → 项目方持仓比（=0% = 🔴）

---

### Step 3 — Smart Money 信号（trading-signal）

```http
POST https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/web/signal/smart-money
{
  "chainId": "56",
  "page": 1,
  "pageSize": 100
}
```

**判断：** 目标代币是否出现在 Smart Money 买入列表中

---

### Step 4 — 社交热度排名（crypto-market-rank）

```http
GET https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/web/pulse/social/hype/rank/leaderboard
    ?chainId=56&sentiment=All&timeRange=1
```

**判断：** 代币是否进入社交热度 Top 榜，社区是否仍然活跃

---

### Step 5 — 创始人钱包持仓（自动化）⭐ 最关键

**全自动流程（无需手动提供部署者地址）：**

```bash
python3 scripts/dump_detective_step5.py <contract_address>
# 脚本路径: workspace-coder/scripts/dump_detective_step5.py
```

**脚本内部逻辑：**
1. 爬取 `https://bscscan.com/address/<contract>` 解析 "Contract Creator" 字段 → 获得部署者地址
2. 调用 BSC RPC `eth_call` (balanceOf) → 直接查部署者钱包的代币余额
3. 调用 BSC RPC `eth_getBalance` → 查部署者 BNB 余额（确认地址是否仍活跃）
4. 尝试 Binance Web3 API 补充（`/v3/.../active-position-list`）— 部分地址可能返回 null

**判断规则：**
- 余额 = 0 → 🔴 已完全出货（吸烟枪证据）
- 余额极少（< 1000）→ 🔴 基本出货
- 仍持有大量 → 🟡 未出货，需结合总供应量评估比例

> ℹ️ Binance API `devHoldingPercent=null` 时不影响结论，RPC 直查更准确

---

## 综合评级规则

| 维度 | 权重 | 🔴 出货信号 |
|------|------|------------|
| 合约安全 | 20% | riskLevel ≥ 2 |
| 买卖压力 | 25% | 卖压 > 60% |
| Smart Money | 20% | holders = 0 |
| 社交热度 | 15% | 未进 Top 榜 |
| 创始人持仓 | 20% | 清仓归零 |

- 🔴 HIGH：3个以上维度红灯
- 🟡 MEDIUM-HIGH：2个维度红灯
- 🟢 LOW：1个以下红灯

---

## 完整演示案例

参见仓库内：`demo_log.md`（完整演示日志）
分析对象：Baby Doge Coin (BabyDoge) → 评级：🟡 MEDIUM-HIGH RISK

---

## 注意事项

- 所有 API 均为 Binance Web3 **公开端点**，无需 API Key
- 目前仅支持 **BSC (chainId: 56)**，其他链待扩展
- 本 Skill 用于技术演示，不构成投资建议（DYOR）
