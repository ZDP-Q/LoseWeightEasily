# 餐食规划功能测试示例

这是一个测试脚本，用于在没有 API key 时测试餐食规划功能的基本流程。

## 使用方法

### 1. 设置 API 配置

```bash
# 设置 OpenAI API Key（必需）
export LOSS_LLM_API_KEY="your-api-key-here"

# 设置 API 基础 URL（可选，默认为 OpenAI）
export LOSS_LLM_BASE_URL="https://api.openai.com/v1"

# 设置模型（可选，默认为 gpt-3.5-turbo）
export LOSS_LLM_MODEL="gpt-3.5-turbo"
```

Windows PowerShell:
```powershell
$env:LOSS_LLM_API_KEY="your-api-key-here"
$env:LOSS_LLM_BASE_URL="https://api.openai.com/v1"
$env:LOSS_LLM_MODEL="gpt-3.5-turbo"
```

### 2. 运行餐食规划

```bash
uv run loss-weight meal-plan
```

### 3. 输入示例

```
请输入你现有的食材（用空格或逗号分隔）:
> 鸡胸肉 西兰花 胡萝卜 大米 鸡蛋

是否有特殊饮食偏好？（直接回车跳过）
> 清淡 少油

是否有饮食限制？（如：素食、低碳水等，直接回车跳过）
> 
```

## 兼容其他 LLM 服务

本功能支持任何兼容 OpenAI API 格式的服务，例如：

### DeepSeek
```bash
export LOSS_LLM_API_KEY="your-deepseek-key"
export LOSS_LLM_BASE_URL="https://api.deepseek.com/v1"
export LOSS_LLM_MODEL="deepseek-chat"
```

### Azure OpenAI
```bash
export LOSS_LLM_API_KEY="your-azure-key"
export LOSS_LLM_BASE_URL="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
export LOSS_LLM_MODEL="gpt-35-turbo"
```

### 本地模型（如 Ollama）
```bash
export LOSS_LLM_API_KEY="dummy-key"
export LOSS_LLM_BASE_URL="http://localhost:11434/v1"
export LOSS_LLM_MODEL="llama2"
```
