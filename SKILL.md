---
name: dump-detective
description: "Use this skill when the user asks to 'check if a token team is dumping', 'analyze token dump risk', 'is this token safe', '查某个代币是否出货', '分析项目方出货', '检测出货行为', '某代币安全吗', '创始人还持仓吗', or mentions detecting whether a token's project team has sold their holdings on BSC chain. Runs a 5-step automated pipeline: contract audit → market data → smart money signals → social hype → creator wallet forensics (auto-detected via BSCScan + BSC RPC). Outputs a unified risk rating (🔴 HIGH / 🟡 MEDIUM-HIGH / 🟢 LOW). Best for BSC chain tokens. No API key required."
---

# 出货侦探 DumpDetective

5步自动化分析 BSC 代币是否存在项目方出货风险。所有接口均为公开端点，无需 API Key。

**GitHub：** https://github.com/JN-Bot666/dump-detective

---

## 5步分析流程

### Step 1 — 合约安全审计

```bash
curl -s --compressed -X POST "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit" \
  -H "Content-Type: application/json" \
  -d '{"binanceChainId":"56","contractAddress":"<address>","requestId":"dd-001"}'
```

关注：`riskLevel`（≥2 = ⚠️）、`isHit:true` 的风险项、用户举报、流动性质量异常

---

### Step 2 — 市场数据

```bash
curl -s --compressed "https://web3.binance.com/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info?chainId=56&contractAddress=<address>"
```

关注：`volume24hBuy` vs `volume24hSell`（卖>买 = 🔴）、`smartMoneyHolders`（=0 = 🔴）、`devHoldingPercent`（null 或 0 = 🔴）

---

### Step 3 — Smart Money 信号

```bash
curl -s --compressed -X POST "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/web/signal/smart-money" \
  -H "Content-Type: application/json" \
  -d '{"chainId":"56","page":1,"pageSize":100}'
```

`data` 为数组，检查目标合约地址是否在列表中。不在 = 🔴

---

### Step 4 — 社交热度

```bash
curl -s --compressed "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/web/pulse/social/hype/rank/leaderboard?chainId=56&sentiment=All&timeRange=1"
```

目标代币未进入 Top 榜 = 🔴

---

### Step 5 — 创始人钱包（全自动）⭐ 最关键

```bash
python3 scripts/dump_detective_step5.py <contract_address>
```

脚本自动完成：
1. 爬 BSCScan 获取合约部署者地址（无需 API Key）
2. BSC RPC `eth_call` balanceOf → 查部署者代币余额
3. 余额 = 0 → 🔴 已出货（吸烟枪证据）

> ⚠️ `--compressed` 必须加，Binance API 响应为 gzip 压缩

---

## 综合评级

| 维度 | 🔴 出货信号 |
|------|------------|
| 合约安全 | riskLevel ≥ 2 或被举报 |
| 买卖压力 | 卖压 > 60% 或 smart money = 0 |
| Smart Money | 未出现在买入榜 |
| 社交热度 | 未进 Top 榜 |
| 创始人持仓 | 余额清零 |

- 🔴 HIGH：3个以上维度红灯
- 🟡 MEDIUM-HIGH：2个维度红灯
- 🟢 LOW：1个以下红灯

---

## 注意事项

- 仅支持 **BSC (chainId: 56)**
- 不构成投资建议（DYOR）
