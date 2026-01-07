#!/usr/bin/env python3
"""
测试Airbnb发票处理
"""
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_ai_rename import InvoiceExtractor, ImageOcrExtractor
from rename_function import get_full_text, extract_fields_from_text

def test_invoice(file_path):
    """测试单个发票文件"""
    print(f"\n{'='*60}")
    print(f"🧾 测试文件: {os.path.basename(file_path)}")
    print(f"{'='*60}")

    # 1. 尝试PDF文本提取
    print("\n1️⃣ 尝试PDF文本提取...")
    try:
        class MockTextArea:
            def insert(self, *args): pass
            def see(self, *args): pass

        text_area = MockTextArea()
        full_text = get_full_text(text_area, file_path)

        if full_text:
            print(f"   ✅ PDF文本提取成功！")
            print(f"   📄 提取文本长度: {len(full_text)} 字符")

            # 显示前200个字符
            preview = full_text[:200].replace('\n', ' ')
            print(f"   📝 文本预览: {preview}...")

            # 2. 尝试正则提取字段
            print("\n2️⃣ 尝试正则表达式提取字段...")
            fields = ["发票号码", "开票日期", "购方名称", "销方名称", "合计"]
            field_values = extract_fields_from_text(full_text, fields)

            if any(field_values.values()):
                print("   ✅ 正则提取成功！")
                for key, value in field_values.items():
                    if value:
                        print(f"   - {key}: {value}")
            else:
                print("   ⚠️  正则提取未找到有效字段")
        else:
            print("   ⚠️  PDF文本提取失败")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    # 3. 尝试OCR识别
    print("\n3️⃣ 尝试PaddleOCR识别...")
    try:
        ocr_extractor = ImageOcrExtractor()
        ocr_text = ocr_extractor.extract_from_path(file_path)

        if ocr_text and len(ocr_text.strip()) > 10:
            print(f"   ✅ OCR识别成功！")
            print(f"   📄 识别文本长度: {len(ocr_text)} 字符")

            # 显示前200个字符
            preview = ocr_text[:200].replace('\n', ' ')
            print(f"   📝 文本预览: {preview}...")

            # 4. 尝试AI提取
            print("\n4️⃣ 尝试AI智能提取...")
            try:
                ai_extractor = InvoiceExtractor(model_name='deepseek-chat')
                result = ai_extractor.extract(ocr_text)

                print("   ✅ AI提取完成！")
                print("   📊 提取结果:")
                for key, value in result.items():
                    if value:
                        print(f"   - {key}: {value}")
            except Exception as e:
                print(f"   ⚠️  AI提取失败: {e}")
        else:
            print("   ⚠️  OCR未识别到有效文本")
    except Exception as e:
        print(f"   ❌ OCR错误: {e}")

if __name__ == "__main__":
    # 测试文件列表
    test_files = [
        "/Users/esther/Downloads/consolidated_receipts/airbnb_148981.pdf",
        "/Users/esther/Downloads/consolidated_receipts/airbnb_343059.pdf"
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            test_invoice(file_path)
        else:
            print(f"\n❌ 文件不存在: {file_path}")

    print(f"\n{'='*60}")
    print("✅ 测试完成！")
    print(f"{'='*60}\n")
