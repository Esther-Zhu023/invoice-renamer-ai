#!/usr/bin/env python3
"""
测试图片发票处理（JPG/PNG）
图片处理比PDF更简单、更快！
"""
import os
import sys
from paddleocr import PaddleOCR
import logging

# 只显示错误日志
logging.getLogger('ppocr').setLevel(logging.ERROR)

def test_image_invoice(image_path):
    """测试图片发票处理"""
    print(f"\n{'='*60}")
    print(f"📸 测试图片发票: {os.path.basename(image_path)}")
    print(f"{'='*60}")

    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return

    # 1. 初始化PaddleOCR（图片处理非常简单！）
    print("\n1️⃣ 初始化PaddleOCR...")
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        print("   ✅ PaddleOCR初始化成功")
    except Exception as e:
        print(f"   ❌ 初始化失败: {e}")
        return

    # 2. 直接OCR识别图片（不需要PDF转换！）
    print("\n2️⃣ 直接OCR识别图片...")
    try:
        result = ocr.ocr(image_path, cls=True)

        if not result or not result[0]:
            print("   ⚠️  未识别到文字")
            return

        # 3. 提取所有文本
        print("\n3️⃣ 提取识别文本...")
        text_lines = []
        for line in result[0]:
            text = line[1][0]
            text_lines.append(text)

        full_text = '\n'.join(text_lines)

        print(f"   ✅ 识别成功！")
        print(f"   📄 识别到 {len(text_lines)} 行文本")
        print(f"   📝 总字符数: {len(full_text)}")

        # 4. 显示前500个字符
        print("\n4️⃣ 文本预览（前500字符）:")
        print("   " + "-"*56)
        preview = full_text[:500]
        for line in preview.split('\n')[:10]:  # 只显示前10行
            print(f"   {line}")
        if len(full_text) > 500:
            print("   ...")
        print("   " + "-"*56)

        return full_text

    except Exception as e:
        print(f"   ❌ OCR识别失败: {e}")
        return None

def compare_pdf_vs_image():
    """对比PDF和图片处理的区别"""
    print(f"\n{'='*60}")
    print("📊 PDF vs 图片发票处理对比")
    print(f"{'='*60}\n")

    comparison = """
┌─────────────────┬────────────────────┬────────────────────┐
│     特性        │      PDF处理       │     图片处理       │
├─────────────────┼────────────────────┼────────────────────┤
│ 速度            │ ⚡⚡ 3-5秒/张      │ ⚡⚡⚡ 2-3秒/张     │
│ 依赖            │ 需要poppler       │ 无额外依赖         │
│ 处理步骤        │ PDF→图片→OCR      │ 直接OCR            │
│ 准确率          │ 略低（有损转换）  │ 更高（原始像素）   │
│ 倾斜校正        │ ✅ 支持           │ ✅ 支持           │
│ 手写识别        │ ✅ 支持           │ ✅ 支持           │
└─────────────────┴────────────────────┴────────────────────┘

💡 建议：
  - 手工拍照 → 保存为JPG/PNG → 直接OCR（更快、更准）
  - 扫描件    → 保存为JPG/PNG → 直接OCR
  - 电子发票  → PDF格式        → PDF文本提取（最快）
    """
    print(comparison)

if __name__ == "__main__":
    print("🎯 图片发票处理测试")
    print("="*60)

    # 显示对比
    compare_pdf_vs_image()

    # 使用示例
    print("\n📝 使用方法：")
    print("-" * 60)
    print("""
# 方法1：直接使用PaddleOCR
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr('invoice.jpg')  # 支持 JPG, PNG, JPEG, BMP

# 方法2：使用项目的ImageOcrExtractor类
from chat_ai_rename import ImageOcrExtractor

extractor = ImageOcrExtractor()
text = extractor.extract_from_path('invoice.jpg')

# 方法3：使用完整处理流程（OCR + AI提取）
from chat_ai_rename import ImageOcrExtractor, InvoiceExtractor

ocr_extractor = ImageOcrExtractor()
ai_extractor = InvoiceExtractor(model_name='deepseek-chat')

# OCR识别
text = ocr_extractor.extract_from_path('invoice.jpg')

# AI提取字段
result = ai_extractor.extract(text)
print(result)  # 结构化数据
    """)
    print("-" * 60)

    # 如果有图片文件，可以测试
    print("\n💡 提示：")
    print("   如果你想测试实际的图片发票，请提供图片路径：")
    print("   python3 test_image_invoice.py /path/to/your/invoice.jpg")
    print("\n   支持的图片格式：JPG, PNG, JPEG, BMP")

    # 检查命令行参数
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_image_invoice(image_path)
