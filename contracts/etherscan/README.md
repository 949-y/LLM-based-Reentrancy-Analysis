# Etherscan 主网合约

本目录用于存放从 Etherscan 获取的以太坊主网合约源码。

## 合约地址

| 合约名称 | 地址 | 说明 |
|---------|------|------|
| LedgerChannel | 0xf91546835f756DA0c10cFa0CDA95b15577b84aA7 | 链下支付通道合约 |
| The DAO | 0xbb9bc244d798123fde783fcc1c72d3bb8c189413 | 著名的 The DAO 合约（2016年重入攻击事件） |
| MoneyMarket | 0x0eee3e3828a45f7601d5f54bf49bb01d1a9df5ea | Lendf.Me 借贷协议核心合约 |

## 如何获取合约源码

1. 访问 `https://etherscan.io/address/<合约地址>`
2. 点击 "Contract" 标签页
3. 复制源码并保存为 `.sol` 文件

或在代码中通过 Etherscan API 获取：
```python
import requests
api_key = "YOUR_ETHERSCAN_API_KEY"
url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}"
response = requests.get(url)
source_code = response.json()["result"][0]["SourceCode"]
```
