#!/usr/bin/env python3
"""
测试PaddleOCR是否正常工作
"""
import sys
from paddleocr import PaddleOCR
import logging

# 只显示错误日志
logging.getLogger('ppocr').setLevel(logging.ERROR)

def test_paddleocr():
    print("=" * 60)
    print("🔍 测试PaddleOCR安装...")
    print("=" * 60)

    try:
        # 初始化OCR
        print("\n1️⃣ 初始化PaddleOCR...")
        ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        print("   ✅ PaddleOCR初始化成功！")

        # 测试文本
        print("\n2️⃣ OCR引擎信息：")
        print(f"   - 语言支持: 中文 (ch)")
        print(f"   - 方向分类器: 启用 (use_angle_cls=True)")
        print(f"   - 版本: PaddleOCR 3.x")

        print("\n" + "=" * 60)
        print("✅ PaddleOCR安装测试通过！")
        print("=" * 60)

        print("\n📝 使用方法：")
        print("   from paddleocr import PaddleOCR")
        print("   ocr = PaddleOCR(use_angle_cls=True, lang='ch')")
        print("   result = ocr.ocr('image.jpg')")

        return True

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n可能的问题：")
        print("1. PaddlePaddle未正确安装")
        print("2. 依赖包版本冲突")
        print("3. 系统架构不兼容")
        return False

if __name__ == "__main__":
    success = test_paddleocr()
    sys.exit(0 if success else 1)
