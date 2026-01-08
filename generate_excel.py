#!/usr/bin/env python3
"""
对账神器 - 批量处理发票/收据并生成Excel对账单
支持：中文、日文、英文等多语言收据
使用OpenAI GPT-4o Vision API
"""
import os
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai_vision_extractor import OpenAIVisionExtractor

# 加载环境变量
load_dotenv()

# --- 配置区 ---
INPUT_FOLDER = "/Users/esther/Downloads/consolidated_receipts"  # 输入文件夹
OUTPUT_EXCEL = "我的对账单.xlsx"  # 输出Excel文件名
OPENAI_VISION_API_KEY = os.getenv("OPENAI_VISION_API_KEY")  # OpenAI Vision API Key


def extract_from_image(file_path: str, extractor: OpenAIVisionExtractor) -> dict:
    """
    使用OpenAI Vision从图片/收据中提取结构化信息

    :param file_path: 图片路径
    :param extractor: OpenAI Vision提取器
    :return: 提取的信息字典
    """
    try:
        # 使用OpenAI Vision提取
        result = extractor.extract_from_image(file_path)

        # 调试：打印原始结果
        if "error" in result:
            print(f"  ❌ API错误: {result['error']}")
        else:
            print(f"  ✅ 提取成功")

        # 转换为标准格式
        return {
            "店铺/公司名称": result.get("seller_name"),
            "日期": result.get("issue_date"),
            "时间": result.get("issue_time"),
            "发票号码": result.get("invoice_number"),
            "价税合计": result.get("total_amount"),
            "小计": result.get("subtotal"),
            "税额": result.get("tax"),
            "货币": result.get("currency"),
            "支付方式": result.get("payment_method"),
            "商品列表": result.get("items"),
            "源文件名": os.path.basename(file_path),
        }
    except Exception as e:
        print(f"  ⚠️ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return {"源文件名": os.path.basename(file_path), "错误": str(e)}


def main():
    """主处理流程"""
    if not OPENAI_VISION_API_KEY:
        print("❌ 请设置环境变量: OPENAI_VISION_API_KEY")
        print("   获取方式: https://platform.openai.com/api-keys")
        return

    # 初始化 OpenAI Vision
    extractor = OpenAIVisionExtractor(OPENAI_VISION_API_KEY)

    # 获取所有支持的文件
    supported_extensions = ('.jpg', '.png', '.jpeg', '.bmp')
    files = [f for f in os.listdir(INPUT_FOLDER)
             if f.lower().endswith(supported_extensions)]

    if not files:
        print(f"❌ 在 {INPUT_FOLDER} 中没有找到支持的文件")
        return

    # 🧪 测试模式：只处理前3个文件
    TEST_MODE = True
    if TEST_MODE:
        files = files[:3]
        print(f"🧪 测试模式：只处理前 {len(files)} 个文件\n")
    else:
        print(f"📂 找到 {len(files)} 个文件\n")
    print("="*60)

    results = []

    # 遍历处理每个文件
    for filename in tqdm(files, desc="处理进度"):
        file_path = os.path.join(INPUT_FOLDER, filename)

        # 使用OpenAI Vision提取
        data = extract_from_image(file_path, extractor)
        results.append(data)

    # 生成 Excel
    if results:
        print("\n" + "="*60)
        print(f"📊 成功处理 {len(results)} 个文件，正在生成Excel...")

        df = pd.DataFrame(results)

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
