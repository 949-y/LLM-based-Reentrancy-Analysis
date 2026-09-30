# 方案二：Code Trimming — 裁剪代码后交给 LLM 分析

## System Prompt

```
You are a smart contract security analyst specializing in reentrancy vulnerability detection.

Note: The contract code provided to you has been preprocessed — comments and view/pure getter functions (which are irrelevant to reentrancy) have been removed to help you focus on the security-critical logic.
```

## User Prompt Template

```
Analyze the following trimmed Solidity contract for reentrancy vulnerabilities.

```solidity
{trimmed_code}
```

Please provide:
1. Whether the contract is vulnerable to reentrancy (Yes/No)
2. Detailed explanation focusing on external calls and state updates
3. If vulnerable, suggest a fix
```

## 裁剪策略

`src/code_trimmer.py` 对原始合约代码执行以下处理：

1. **移除注释**：删除单行注释 (`//`) 和多行注释 (`/* */`)
2. **移除 view/pure getter 函数**：识别所有 `view` 或 `pure` 修饰符的函数，若它们不包含外部调用，则移除
3. **清理空行**：合并多余空行

保留的部分：
- 合约声明、继承关系
- 状态变量声明
- 修饰符（modifier）
- 包含外部调用的函数（`.call`, `.transfer`, `.send`, 外部合约方法调用）
- 构造函数、接口定义、导入语句

**优点**：减少噪声，让 LLM 聚焦于安全关键逻辑
**缺点**：可能丢失部分上下文信息
