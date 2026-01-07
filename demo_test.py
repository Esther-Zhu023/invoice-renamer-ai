#!/usr/bin/env python3
"""
测试用户的收据图片
"""
import os
import sys
from paddleocr import PaddleOCR
import logging

logging.getLogger('ppocr').setLevel(logging.ERROR)

def test_receipt(image_path):
    """测试收据图片"""
    print(f"\n{'='*60}")
    print(f"🧾 测试收据: {os.path.basename(image_path)}")
    print(f"文件大小: {os.path.getsize(image_path) / 1024:.1f} KB")
    print(f"{'='*60}")

    # 初始化OCR
    print("\n1️⃣ 初始化PaddleOCR...")
    ocr = PaddleOCR(lang='ch')
    print("   ✅ 初始化成功")

    # OCR识别
    print("\n2️⃣ 正在识别...")
    result = ocr.ocr(image_path)

    if not result or not result[0]:
        print("   ⚠️  未识别到文字")
        return None

    # 提取文本
    lines = result[0] if result else []
    print(f"\n3️⃣ 识别结果 (共{len(lines)}行):")
    print("   " + "-"*56)

    text_lines = []
    for i, line in enumerate(lines[:20], 1):  # 只显示前20行
        text_info = line[1]
        text = text_info[0]
        confidence = text_info[1]
        text_lines.append(text)

        conf_pct = confidence * 100
        print(f"   {i:2d}. {text}")

    if len(lines) > 20:
        print(f"   ... (还有{len(lines) - 20}行)")

    # 合并文本
    full_text = '\n'.join(text_lines)

    print("\n   " + "-"*56)
    print(f"   📊 统计: {len(result[0])}行, {len(full_text)}字符")

    return full_text

if __name__ == "__main__":
    # 测试目录
    receipt_dir = "/Users/esther/Downloads/consolidated_receipts"

    # 选择几个有代表性的文件测试
    test_files = [
        "misc_153678.png",           # PNG杂项收据
        "other receipts_108465.jpg",  # JPG收据
        "misc_181593.jpg",            # 大文件JPG
    ]

    print("🎯 测试用户的收据图片")
    print("="*60)

    for filename in test_files:
        file_path = os.path.join(receipt_dir, filename)

        if os.path.exists(file_path):
            test_receipt(file_path)
        else:
            print(f"\n⚠️  文件不存在: {filename}")

    print(f"\n{'='*60}")
    print("✅ 测试完成！")
    print(f"{'='*60}\n")
