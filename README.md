# LLM-based Reentrancy Analysis

基于大语言模型（LLM）的智能合约重入漏洞分析实验。

## 项目简介

本项目设计了一套智能合约安全分析流程，利用大语言模型（LLM）对 Solidity 智能合约进行重入漏洞（Reentrancy）检测。项目实现了四种不同的分析方案，通过对比实验探索如何为 LLM 提供更有针对性的上下文信息，从而辅助漏洞判断。

## 重入漏洞背景

重入漏洞是智能合约中的经典安全问题。当合约执行外部调用时，攻击者可以通过回调函数（`receive()` / `fallback()`）重新进入合约逻辑，在状态更新完成前重复执行提现等操作，导致状态不一致或资产损失。

典型的重入漏洞违反了 **Checks-Effects-Interactions (CEI)** 模式：
1. **Checks**：检查条件
2. **Effects**：更新状态变量
3. **Interactions**：最后执行外部调用

如果状态更新在外部调用之后，合约就存在重入风险。

## 四种分析方案

| 方案 | 说明 | 核心思路 |
|------|------|---------|
| 1. Baseline | 直接将完整合约代码交给 LLM | 不做预处理，测试 LLM 原始分析能力 |
| 2. Code Trimming | 裁剪代码后交给 LLM | 移除注释和 view/pure 函数，减少噪声 |
| 3. Slither-Assisted | 结合 Slither 静态分析信息 | 用 Slither 提取函数级静态信息作为上下文 |
| 4. Prompt Engineering | 结构化 Prompt + 链式推理 | 注入重入知识、检查清单、结构化输出 |

## 项目结构

```
LLM-based-Reentrancy-Analysis/
├── README.md
├── requirements.txt              # Python 依赖
├── .env.example                   # 环境变量模板
├── .gitignore
├── run.py                         # 主入口：运行四种方案
├── src/
│   ├── __init__.py
│   ├── llm_client.py              # 智谱 AI LLM 客户端
│   ├── contract_loader.py         # 合约加载与测试集定义
│   ├── code_trimmer.py            # 代码裁剪（方案二）
│   ├── slither_analyzer.py        # Slither 静态分析（方案三）
│   └── prompts.py                 # 四种方案的 Prompt 模板
├── contracts/                     # 测试合约
│   ├── solidity-security-by-example/   # 来自 GitHub 的示例合约
│   │   ├── 02_reentrancy/              # 基础重入
│   │   ├── 03_reentrancy_via_modifier/ # 修饰符重入
│   │   ├── 04_cross_function_reentrancy/ # 跨函数重入
│   │   └── 05_cross_contract_reentrancy/ # 跨合约重入
│   └── etherscan/                 # 以太坊主网合约（需手动获取）
├── prompts/                       # Prompt 文档
│   ├── 01_baseline.md
│   ├── 02_code_trimming.md
│   ├── 03_slither_assisted.md
│   └── 04_prompt_engineering.md
└── results/                       # 分析结果输出
```

## 测试合约

### solidity-security-by-example 合约

来源：https://github.com/serial-coder/solidity-security-by-example/

| 合约 | 类型 | 是否有漏洞 | 漏洞描述 |
|------|------|-----------|---------|
| InsecureEtherVault (02) | 基础重入 | 是 | 无锁，违反 CEI 模式 |
| FixedEtherVault (02) | 基础重入 | 否 | 加 ReentrancyGuard + CEI |
| InsecureAirdrop (03) | 修饰符重入 | 是 | 修饰符顺序错误 |
| FixedAirdrop (03) | 修饰符重入 | 否 | 修正修饰符顺序 + 加锁 |
| InsecureEtherVault (04) | 跨函数重入 | 是 | transfer() 缺少锁 |
| FixedEtherVault (04) | 跨函数重入 | 否 | 所有函数加锁 + CEI |
| InsecureMoonVault (05) | 跨合约重入 | 是 | burn 在 Ether 发送之后 |
| FixedMoonVault (05) | 跨合约重入 | 否 | burn 在 Ether 发送之前 |

### Etherscan 主网合约

| 合约 | 地址 |
|------|------|
| LedgerChannel | 0xf91546835f756DA0c10cFa0CDA95b15577b84aA7 |
| The DAO | 0xbb9bc244d798123fde783fcc1c72d3bb8c189413 |
| MoneyMarket | 0x0eee3e3828a45f7601d5f54bf49bb01d1a9df5ea |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填入智谱 AI API Key：

```bash
cp .env.example .env
```

编辑 `.env`：
```
ZHIPU_API_KEY=your_api_key_here
ZHIPU_MODEL=glm-4-flash-250414
```

智谱 AI 免费模型申请：https://bigmodel.cn/

### 3. 运行分析

```bash
python run.py
```

程序将对 8 个测试合约分别运行 4 种分析方案，结果保存到 `results/` 目录。

### 4. 查看结果

每个合约×方案生成一个 JSON 文件：
```json
{
    "contract": "02_reentrancy/InsecureEtherVault",
    "approach": "baseline",
    "ground_truth_vulnerable": true,
    "response": "LLM 的分析结果...",
    "elapsed_seconds": 3.21
}
```

## LLM 模型

使用智谱 AI（BigModel）免费模型，API 兼容 OpenAI 格式：

- **API 端点**：`https://open.bigmodel.cn/api/paas/v4/`
- **免费模型**：`glm-4-flash-250414` / `glm-4.7-flash`
- **调用方式**：通过 OpenAI SDK，设置 `base_url` 即可

## 技术栈

- **LLM**：智谱 AI GLM-4-Flash（免费）
- **静态分析**：Slither（Python API）
- **Solidity 编译器**：solc（通过 py-solc-x 自动安装）
- **语言**：Python 3.8+
