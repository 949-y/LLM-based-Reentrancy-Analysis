# 方案一：Baseline — 直接将完整合约代码交给 LLM 分析

## System Prompt

```
You are a smart contract security analyst. Your task is to analyze Solidity smart contracts for reentrancy vulnerabilities.
```

## User Prompt Template

```
Analyze the following Solidity smart contract for reentrancy vulnerabilities.

```solidity
{code}
```

Please provide:
1. Whether the contract is vulnerable to reentrancy (Yes/No)
2. Detailed explanation of your analysis
3. If vulnerable, suggest a fix
```

## 说明

这是最基础的方案。直接将完整的 Solidity 合约源码（包括注释、view/pure 函数等）交给 LLM，不做任何预处理。LLM 需要自己在完整代码中识别重入漏洞。

**优点**：简单直接，无需额外工具
**缺点**：合约代码中大量无关信息（注释、getter 函数）可能干扰 LLM 的判断
