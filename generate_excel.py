#!/usr/bin/env python3
"""
对账神器 - 批量处理发票/收据并生成Excel对账单
支持：中文、日文、英文等多语言收据
"""
import os
import pandas as pd
from tqdm import tqdm
from chat_ai_rename import InvoiceExtractor, ImageOcrExtractor
import pdfplumber
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# --- 配置区 ---
INPUT_FOLDER = "/Users/esther/Downloads/consolidated_receipts"  # 输入文件夹
OUTPUT_EXCEL = "我的对账单.xlsx"  # 输出Excel文件名
AI_MODEL_NAME = "deepseek-chat"  # AI模型（与.env保持一致）


def get_text_content(file_path):
    """
    智能判断：如果是PDF尝试提取文本，如果是图片或扫描件用OCR
    """
    ext = os.path.splitext(file_path)[1].lower()
    full_text = ""

    # 1. 尝试直接提取 PDF 文本
    if ext == '.pdf':
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt:
                        full_text += txt + "\n"
        except Exception as e:
            print(f"  ⚠️ PDF文本提取失败: {e}")

    # 2. 如果文本太少（说明是扫描件/图片），或者是图片格式，启动 OCR
    if len(full_text.strip()) < 50 or ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        try:
            ocr = ImageOcrExtractor()  # 复用现有的 OCR 类
            full_text = ocr.extract_from_path(file_path)
        except Exception as e:
            print(f"  ⚠️ OCR识别失败: {e}")
            full_text = ""

    return full_text


def main():
    """主处理流程"""
    # 1. 初始化 AI (复用现有的类)
    print("🔧 初始化AI模型...")
    extractor = InvoiceExtractor(model_name=AI_MODEL_NAME)
    print("   ✅ 初始化成功\n")

    # 2. 获取所有支持的文件
    supported_extensions = ('.pdf', '.jpg', '.png', '.jpeg', '.bmp')
    files = [f for f in os.listdir(INPUT_FOLDER)
             if f.lower().endswith(supported_extensions)]

    if not files:
        print(f"❌ 在 {INPUT_FOLDER} 中没有找到支持的文件")
        return

    print(f"📂 找到 {len(files)} 个文件\n")
    print("="*60)

    results = []

    # 3. 遍历处理每个文件
    for filename in tqdm(files, desc="处理进度"):
        file_path = os.path.join(INPUT_FOLDER, filename)

        try:
            # A. 获取文字 (OCR 或 PDF解析)
            text_content = get_text_content(file_path)

            if not text_content.strip():
                print(f"\n⚠️ 跳过 {filename}: 无法提取内容")
                continue

            # B. 呼叫 AI 提取结构化数据 (复用核心功能)
            # data 是一个字典，包含 seller_name, total_amount 等
            data = extractor.extract(text_content)

            # C. 补充原文件名，方便核对
            data['OriginalFileName'] = filename

            # D. 加入列表
            results.append(data)

        except Exception as e:
            print(f"\n❌ 处理 {filename} 失败: {e}")

    # 4. 生成 Excel
    if results:
        print("\n" + "="*60)
        print(f"📊 成功处理 {len(results)} 个文件，正在生成Excel...")

        df = pd.DataFrame(results)

        # 列名映射（英文→中文）
        col_map = {
            "seller_name": "店铺/公司名称",
            "total_amount": "金额(不含税)",
            "total_tax": "税额",
            "total_including_tax": "价税合计",
            "total_including_tax_in_words": "价税合计(大写)",
            "issue_date": "日期",
            "invoice_number": "发票号码",
            "buyer_name": "购买方",
            "buyer_tax_id": "购买方税号",
            "seller_tax_id": "销售方税号",
            "preparer": "开票人",
            "OriginalFileName": "源文件名"
        }
        df.rename(columns=col_map, inplace=True)

        # 调整列顺序（把重要的放前面）
        priority_cols = [
            "日期", "店铺/公司名称", "价税合计",
            "金额(不含税)", "税额", "发票号码", "源文件名"
        ]

        # 确保列存在才排序
        existing_cols = [c for c in priority_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_cols]
        df = df[existing_cols + other_cols]

        # 保存Excel
        output_path = os.path.join(INPUT_FOLDER, OUTPUT_EXCEL)
        df.to_excel(output_path, index=False, engine='openpyxl')

        print(f"✅ Excel已生成: {output_path}")
        print(f"📄 共 {len(results)} 行数据\n")

        # 显示前5行预览
        print("="*60)
        print("📋 数据预览（前5行）:")
        print("="*60)
        print(df.head().to_string(index=False))
        print("="*60)

    else:
        print("❌ 没有提取到任何数据")


if __name__ == "__main__":
    main()
