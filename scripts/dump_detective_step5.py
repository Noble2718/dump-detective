#!/usr/bin/env python3
"""
出货侦探 Step 5 — 创始人钱包自动化查询
自动找到合约部署者并查其持仓

用法:
  python3 dump_detective_step5.py <contract_address> [--chain bsc]
"""

import sys
import re
import json
import argparse
import urllib.request
import urllib.parse

# BSC RPC 端点
BSC_RPC = "https://bsc-dataseed1.binance.org/"
BSCSCAN_BASE = "https://bscscan.com"

def rpc_call(method, params):
    """调用 BSC RPC"""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }).encode()
    req = urllib.request.Request(BSC_RPC, data=payload,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["result"]


def get_deployer_from_bscscan(contract_addr):
    """
    从 BSCScan 页面爬取合约部署者地址
    无需 API Key
    """
    url = f"{BSCSCAN_BASE}/address/{contract_addr}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        # 找 Creator Address
        match = re.search(
            r"Creator.*?href='/address/(0x[0-9a-fA-F]{40})'",
            html, re.DOTALL | re.IGNORECASE
        )
        if match:
            return match.group(1).lower()
    except Exception as e:
        print(f"  ⚠️  BSCScan 爬取失败: {e}")
    return None


def get_token_balance(wallet_addr, token_addr):
    """
    通过 BSC RPC 查询钱包持有某代币的余额
    ERC20 balanceOf(address) = 0x70a08231
    """
    padded = wallet_addr.lower().replace("0x", "").zfill(64)
    data = "0x70a08231" + padded
    result = rpc_call("eth_call", [{"to": token_addr, "data": data}, "latest"])
    return int(result, 16)


def get_token_decimals(token_addr):
    """查代币小数位"""
    try:
        result = rpc_call("eth_call", [{"to": token_addr, "data": "0x313ce567"}, "latest"])
        return int(result, 16)
    except:
        return 18


def get_bnb_balance(wallet_addr):
    """查 BNB 余额"""
    result = rpc_call("eth_getBalance", [wallet_addr, "latest"])
    return int(result, 16) / 1e18


def check_binance_active_positions(wallet_addr, chain_id="56"):
    """
    尝试 Binance Web3 API 查活跃持仓
    （部分地址可能无数据）
    """
    url = (f"https://web3.binance.com/bapi/defi/v3/public/wallet-direct/buw/"
           f"wallet/address/pnl/active-position-list?address={wallet_addr}&chainId={chain_id}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "gzip, deflate"
    })
    try:
        import gzip
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read()
            if r.info().get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            data = json.loads(raw)
            if data.get("code") == "000000":
                return data.get("data", [])
    except Exception as e:
        pass
    return None


def analyze(contract_addr, chain="bsc"):
    print(f"\n🔍 出货侦探 Step 5 — 创始人钱包追踪")
    print(f"   合约: {contract_addr}")
    print(f"   链:   {chain.upper()}\n")

    # 1. 找部署者
    print("📋 [1/3] 从 BSCScan 获取合约部署者...")
    deployer = get_deployer_from_bscscan(contract_addr)
    if not deployer:
        print("  ❌ 无法获取部署者地址，请手动在 BscScan 查询")
        return
    print(f"  ✅ 部署者地址: {deployer}")

    # 2. 查代币余额
    print("\n📋 [2/3] 查询部署者持仓...")
    try:
        decimals = get_token_decimals(contract_addr)
        balance_raw = get_token_balance(deployer, contract_addr)
        balance = balance_raw / (10 ** decimals)
        bnb = get_bnb_balance(deployer)

        print(f"  代币余额: {balance:,.4f} ({contract_addr[:10]}...)")
        print(f"  BNB 余额: {bnb:.4f} BNB")

        # 3. 判断
        print("\n📋 [3/3] 出货判断...")
        if balance == 0:
            print("  🔴 项目方持仓为 0 — 已完全出货！（吸烟枪证据）")
            verdict = "🔴 已出货"
        elif balance < 1000:
            print(f"  🔴 项目方持仓极少（{balance:.4f}），基本可认定已出货")
            verdict = "🔴 基本出货"
        else:
            print(f"  🟡 项目方仍持有 {balance:,.0f} 代币，需结合市值判断比例")
            verdict = "🟡 仍持仓"

        # 4. 尝试 Binance API 补充
        print("\n📋 [补充] Binance Web3 活跃持仓 API...")
        positions = check_binance_active_positions(deployer)
        if positions is not None:
            token_pos = [p for p in positions
                         if p.get("contractAddress", "").lower() == contract_addr.lower()]
            if token_pos:
                print(f"  ✅ 在 Binance 活跃持仓中找到该代币")
            else:
                print(f"  ⚠️  Binance 活跃持仓中无该代币（共 {len(positions)} 个持仓）")
        else:
            print("  ⚠️  Binance API 无法查询该地址（地址未索引）")

        print(f"\n{'='*50}")
        print(f"  最终结论: {verdict}")
        print(f"  部署者:   {deployer}")
        print(f"  BscScan:  https://bscscan.com/address/{deployer}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"  ❌ 查询失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="出货侦探 Step 5 - 创始人钱包自动化")
    parser.add_argument("contract", help="代币合约地址")
    parser.add_argument("--chain", default="bsc", help="链名称 (默认: bsc)")
    args = parser.parse_args()
    analyze(args.contract, args.chain)
