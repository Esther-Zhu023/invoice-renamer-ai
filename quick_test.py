#!/usr/bin/env python3
"""
快速测试图片OCR
"""
import sys
import os
from paddleocr import PaddleOCR
import logging
import requests
from PIL import Image
from io import BytesIO

logging.getLogger('ppocr').setLevel(logging.ERROR)

def download_image(url, save_path):
    """下载图片"""
    print(f"📥 下载图片: {url}")
    try:
        response = requests.get(url, timeout=10)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"   ✅ 图片已保存: {save_path}")
        return save_path
    except Exception as e:
        print(f"   ❌ 下载失败: {e}")
        return None

def test_ocr(image_path):
    """测试OCR"""
    print(f"\n{'='*60}")
    print(f"🔍 PaddleOCR测试")
    print(f"{'='*60}")

    # 初始化OCR
    print("\n1️⃣ 初始化PaddleOCR...")
    ocr = PaddleOCR(lang='ch')
    print("   ✅ 初始化成功")

    # OCR识别
    print(f"\n2️⃣ 识别图片: {os.path.basename(image_path)}")
    print("   正在识别...")
    result = ocr.ocr(image_path)

    if not result or not result[0]:
        print("   ⚠️  未识别到文字")
        return

    # 提取文本
    print(f"\n3️⃣ 识别结果:")
    print("   " + "="*56)
    text_lines = []
    for i, line in enumerate(result[0], 1):
        text = line[1][0]
        confidence = line[1][1]
        text_lines.append(text)
        print(f"   {i}. {text} (置信度: {confidence:.2f})")

    # 合并文本
    full_text = '\n'.join(text_lines)

    print("\n   " + "="*56)
    print(f"   📊 统计:")
    print(f"   - 识别行数: {len(text_lines)}")
    print(f"   - 总字符数: {len(full_text)}")

    return full_text

if __name__ == "__main__":
    # Discord图片URL
    image_url = "https://cdn.discordapp.com/attachments/1300283278950051910/1300283340308361266/image_0.jpg"

    # 下载图片
    temp_path = "/tmp/test_invoice.jpg"
    downloaded = download_image(image_url, temp_path)

    if downloaded:
        # 测试OCR
        text = test_ocr(temp_path)

        # 保存文本
        if text:
            output_file = "/tmp/ocr_result.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n   💾 文本已保存到: {output_file}")
