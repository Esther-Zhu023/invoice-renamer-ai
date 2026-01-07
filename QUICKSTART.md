# 🚀 发票智能重命名工具 - 快速开始

## ✅ 已完成安装

所有依赖已安装完成：
- ✅ PaddleOCR 3.3.2
- ✅ PaddlePaddle 3.2.2
- ✅ pdfplumber 0.11.8
- ✅ LangChain 0.3.81
- ✅ poppler 25.12.0
- ✅ DeepSeek API已配置

## 📂 项目文件

```
/Users/esther/Downloads/发票重命名/G-P-1-ChatAi/
├── main.py                      # 主程序入口
├── chat_ai_rename.py            # AI和OCR封装
├── rename_function.py           # 重命名核心逻辑
├── invoice_rename_config.py     # GUI配置界面
├── requirements.txt             # Python依赖
├── .env                         # DeepSeek API配置
├── README.md                    # 项目说明
├── SETUP_GUIDE.md               # 安装指南
│
├── test_paddleocr.py            # 测试PaddleOCR
├── test_image_invoice.py        # 测试图片发票
├── demo_test.py                 # 测试你的收据
└── .git/                        # Git仓库
```

## 🎯 使用方法

### 方法1：GUI界面（推荐）

```bash
cd /Users/esther/Downloads/发票重命名/G-P-1-ChatAi
python3 main.py
```

**步骤：**
1. 点击"选择文件夹" - 选择 `/Users/esther/Downloads/consolidated_receipts`
2. 勾选需要的字段（默认：销方名称、开票日期、合计）
3. 点击"确认"开始批量处理

### 方法2：测试单个文件

```bash
# 测试PaddleOCR是否正常
python3 test_paddleocr.py

# 测试图片发票
python3 test_image_invoice.py /path/to/invoice.jpg

# 测试你的收据图片
python3 demo_test.py
```

## 📊 你的收据统计

从你的目录 `/Users/esther/Downloads/consolidated_receipts/`：

| 类型 | 数量 | 文件格式 |
|------|------|----------|
| Airbnb收据 | 3 | PDF |
| 保险发票 | 11 | PDF |
| 会议室收据 | 5 | PDF |
| 杂项收据 | 43 | JPG/PNG |
| 其他收据 | 363 | JPG |
| 旅行收据 | 12 | PDF/JPG |

**总计：437个文件**

## 🚀 发布到GitHub

### 步骤1：创建GitHub仓库

1. 访问 https://github.com/new
2. 仓库名：`invoice-renamer-ai`
3. 描述：`基于PDF解析+OCR识别+AI模型的智能发票重命名工具`
4. 选择：Public
5. ❌ 不要初始化README
6. 点击"Create repository"

### 步骤2：推送代码

```bash
cd /Users/esther/Downloads/发票重命名/G-P-1-ChatAi

# 添加远程仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/invoice-renamer-ai.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤3：或者使用GitHub CLI

```bash
# 安装GitHub CLI
brew install gh

# 登录
gh auth login

# 创建仓库并推送
gh repo create invoice-renamer-ai --public --source=. --remote=origin --push
```

## 🧪 测试你的收据

### 测试Airbnb PDF发票

```bash
python3 test_airbnb.py
```

### 测试图片收据

```bash
# 测试单个图片
python3 test_image_invoice.py /Users/esther/Downloads/consolidated_receipts/misc_153678.png

# 批量测试
python3 demo_test.py
```

## 💡 处理流程

```
输入发票 → PDF文本提取(成功) → 正则匹配 → 完成 ✅
         ↓ (失败)
         图片OCR识别(PaddleOCR) → 中文文本
                                    ↓
                              AI智能提取(DeepSeek)
                                    ↓
                            11个字段完整提取 ✅
```

## 📝 配置说明

### API配置 (.env)

```bash
MODEL_NAME=deepseek-chat
OPENAI_API_KEY=sk-962a9d9427404c23b44b339810855092
OPENAI_API_BASE=https://api.deepseek.com
```

**已配置：** DeepSeek API (成本：¥1/百万tokens，约2000张发票)

### 切换到其他AI

编辑 `.env` 文件：

**Moonshot（月之暗面）**
```bash
MODEL_NAME=moonshot-v1-8k
OPENAI_API_KEY=your-moonshot-key
OPENAI_API_BASE=https://api.moonshot.cn/v1
```

**OpenAI**
```bash
MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=your-openai-key
OPENAI_API_BASE=https://api.openai.com/v1
```

## ⚙️ 可提取字段

- 发票号码
- 开票日期
- 购方名称 / 购方税号
- 销方名称 / 销方税号
- 合计金额
- 总税额
- 价税合计（小写/大写）
- 开票人

## 📸 图片 vs PDF

| 特性 | 图片 (JPG/PNG) | PDF |
|------|---------------|-----|
| 速度 | ⚡⚡⚡ 2-3秒 | ⚡⚡ 3-5秒 |
| 依赖 | 无额外依赖 | 需要poppler ✅ |
| 准确率 | 更高（原始像素） | 略低（转换损失） |
| 倾斜校正 | ✅ 支持 | ✅ 支持 |

**建议：** 手工拍照的发票保存为JPG格式，处理更快更准！

## ⚠️ 注意事项

1. **首次运行**：PaddleOCR会自动下载模型（约200MB），只需一次
2. **处理速度**：
   - PDF文本：0.1秒/张（最快）
   - OCR识别：2-5秒/张
   - AI处理：5-10秒/张（最智能）
3. **文件备份**：自动备份到 `rename_[随机后缀]` 目录
4. **文件名冲突**：自动添加时间戳避免覆盖

## 🆘 故障排查

### 问题1：ModuleNotFoundError
```bash
pip3 install -r requirements.txt
```

### 问题2：PaddleOCR初始化失败
```bash
python3 test_paddleocr.py
```

### 问题3：API调用失败
- 检查 `.env` 文件配置
- 确认API密钥有效
- 检查网络连接

## 📞 技术支持

邮箱：esther@feedmob.com

---

**准备好了！开始处理你的437张收据吧！** 🚀
