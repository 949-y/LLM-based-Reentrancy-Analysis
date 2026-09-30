# 方案三：Slither-Assisted — 结合 Slither 静态分析信息

## System Prompt

```
You are a smart contract security analyst. You will receive both the source code of a Solidity contract and static analysis information extracted by Slither (a Solidity static analyzer).

The Slither info includes: contract inheritance, state variables, and for each function: visibility, state variables read/written, modifiers, and external/internal calls. Use this structured information to make your analysis more precise and accurate.
```

## User Prompt Template

```
Analyze the following Solidity contract for reentrancy vulnerabilities, using both the source code and the Slither static analysis info.

## Contract Source Code
```solidity
{code}
```

## Slither Static Analysis Info
```
{slither_info}
```

Please provide:
1. Whether the contract is vulnerable to reentrancy (Yes/No)
2. Detailed explanation using the Slither info to identify:
   - Which functions make external calls
   - Whether state is modified after external calls
   - Whether reentrancy guards are applied
3. If vulnerable, suggest a fix
```

## Slither 提取的静态分析信息

`src/slither_analyzer.py` 使用 Slither 的 Python API 提取以下信息：

```
=== Contract: InsecureEtherVault ===
State variables: userBalances

  Function: deposit
    Visibility: external
    State vars read:    []
    State vars written: ['userBalances']
    Modifiers: []

  Function: withdrawAll
    Visibility: external
    State vars read:    ['userBalances']
    State vars written: ['userBalances']
    Modifiers: []
    External calls: ['msg.sender.call{value: balance}("")']
```

**关键信息**：
- 每个函数的可见性（public/external/internal/private）
- 函数读取/写入的状态变量（帮助判断 CEI 模式是否违反）
- 函数上的修饰符（判断是否有重入锁）
- 外部调用表达式（识别重入入口点）
- 内部函数调用（追踪调用链）

**优点**：结构化信息帮助 LLM 更精确地识别外部调用和状态变更顺序
**缺点**：依赖 Slither 和 solc 编译器，安装配置较复杂
