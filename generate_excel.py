#!/usr/bin/env python3
"""
对账神器 - 批量处理发票/收据并生成Excel对账单
支持：中文、日文、英文等多语言收据
支持：PDF、图片、单收据、多收据
使用OpenAI GPT-4o Vision API
"""
import os
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai_vision_extractor import OpenAIVisionExtractor
from pdf2image import convert_from_path
import tempfile

# 加载环境变量
load_dotenv()

# --- 配置区 ---
INPUT_FOLDER = "/Users/esther/Downloads/consolidated_receipts"  # 输入文件夹
OUTPUT_EXCEL = "我的对账单.xlsx"  # 输出Excel文件名
OPENAI_VISION_API_KEY = os.getenv("OPENAI_VISION_API_KEY")  # OpenAI Vision API Key


def process_file(file_path: str, extractor: OpenAIVisionExtractor) -> list:
    """
    处理单个文件（支持PDF、图片、单收据、多收据）

    :param file_path: 文件路径
    :param extractor: OpenAI Vision提取器
    :return: 收据列表（支持多个收据）
    """
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    try:
        # PDF处理：转换为图片后识别
        if ext == '.pdf':
            print(f"  📄 PDF文件，转换为图片...")
            with tempfile.TemporaryDirectory() as temp_dir:
                # 转换PDF为图片
                images = convert_from_path(file_path, dpi=200)

                all_receipts = []
                for page_num, image in enumerate(images, 1):
                    # 保存为临时文件
                    temp_image_path = os.path.join(temp_dir, f"page_{page_num}.jpg")
                    image.save(temp_image_path, 'JPEG')

                    # 识别这一页
                    print(f"    📖 第{page_num}页识别中...")
                    receipts = extractor.extract_from_image(temp_image_path)

                    # 为每个收据添加源文件信息
                    for receipt in receipts:
                        receipt['源文件名'] = f"{filename} (第{page_num}页)"

                    all_receipts.extend(receipts)

                print(f"  ✅ PDF识别完成：{len(all_receipts)}个收据")
                return all_receipts

        # 图片处理：直接识别
        elif ext in ['.jpg', '.png', '.jpeg', '.bmp']:
            print(f"  🖼️ 图片文件识别中...")
            receipts = extractor.extract_from_image(file_path)

            # 为每个收据添加源文件信息
            for receipt in receipts:
                receipt['源文件名'] = filename

            if len(receipts) > 1:
                print(f"  ✅ 识别到{len(receipts)}个收据")
            else:
                print(f"  ✅ 提取成功")

            return receipts

        else:
            print(f"  ⚠️ 不支持的文件格式: {ext}")
            return [{"源文件名": filename, "错误": f"不支持的文件格式: {ext}"}]

    except Exception as e:
        print(f"  ❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return [{"源文件名": filename, "错误": str(e)}]


def convert_receipt_to_row(receipt: dict) -> dict:
    """
    将收据字典转换为Excel行格式

    :param receipt: 收据信息字典
    :return: Excel行字典
    """
    return {
        "店铺/公司名称": receipt.get("seller_name"),
        "日期": receipt.get("issue_date"),
        "时间": receipt.get("issue_time"),
        "发票号码": receipt.get("invoice_number"),
        "价税合计": receipt.get("total_amount"),
        "小计": receipt.get("subtotal"),
        "税额": receipt.get("tax"),
        "货币": receipt.get("currency"),
        "支付方式": receipt.get("payment_method"),
        "商品列表": receipt.get("items"),
        "源文件名": receipt.get("源文件名"),
    }


def main():
    """主处理流程"""
    if not OPENAI_VISION_API_KEY:
        print("❌ 请设置环境变量: OPENAI_VISION_API_KEY")
        print("   获取方式: https://platform.openai.com/api-keys")
        return

    # 初始化 OpenAI Vision
    extractor = OpenAIVisionExtractor(OPENAI_VISION_API_KEY)

    # 获取所有支持的文件（图片 + PDF）
    supported_extensions = ('.jpg', '.png', '.jpeg', '.bmp', '.pdf')
    files = [f for f in os.listdir(INPUT_FOLDER)
             if f.lower().endswith(supported_extensions)]

    if not files:
        print(f"❌ 在 {INPUT_FOLDER} 中没有找到支持的文件")
        return

    # 🧪 测试模式：只处理前3个文件
    TEST_MODE = True
    # 测试PDF过滤：只测试PDF文件
    TEST_PDF_ONLY = True  # 改为True测试PDF

    if TEST_MODE:
        if TEST_PDF_ONLY:
            files = [f for f in files if f.lower().endswith('.pdf')][:3]
            if not files:
                print("❌ 没有找到PDF文件")
                return
        else:
            files = files[:3]
        print(f"🧪 测试模式：只处理前 {len(files)} 个文件\n")
    else:
        print(f"📂 找到 {len(files)} 个文件\n")
    print("="*60)

    all_results = []

    # 遍历处理每个文件
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(INPUT_FOLDER, filename)
        print(f"\n[{i}/{len(files)}] 处理: {filename}")

        # 处理文件（支持PDF、多收据）
        receipts = process_file(file_path, extractor)

        # 转换为Excel行格式
        for receipt in receipts:
            row = convert_receipt_to_row(receipt)
            all_results.append(row)

    # 生成 Excel
    if all_results:
        print("\n" + "="*60)
        print(f"📊 成功处理 {len(all_results)} 条收据记录，正在生成Excel...")

        df = pd.DataFrame(all_results)

        # 调整列顺序（把重要的放前面）
        priority_cols = [
            "日期", "时间", "店铺/公司名称", "价税合计",
            "小计", "税额", "发票号码", "支付方式", "源文件名"
        ]

        # 确保列存在才排序
        existing_cols = [c for c in priority_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_cols]
        df = df[existing_cols + other_cols]

        # 保存Excel
        output_path = os.path.join(INPUT_FOLDER, OUTPUT_EXCEL)
        df.to_excel(output_path, index=False, engine='openpyxl')

        print(f"✅ Excel已生成: {output_path}")
        print(f"📄 共 {len(all_results)} 行数据\n")

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
