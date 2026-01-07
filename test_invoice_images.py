#!/usr/bin/env python3
"""
测试发票图片OCR识别
"""
import os
import sys
from paddleocr import PaddleOCR
import logging
import requests

logging.getLogger('ppocr').setLevel(logging.ERROR)

def download_and_test(url, index):
    """下载并测试图片"""
    temp_path = f"/tmp/invoice_{index}.jpg"

    print(f"\n{'='*60}")
    print(f"📥 图片 #{index}")
    print(f"{'='*60}")

    # 下载图片
    print(f"📥 下载图片...")
    try:
        response = requests.get(url, timeout=10)
        with open(temp_path, 'wb') as f:
            f.write(response.content)

        file_size = os.path.getsize(temp_path)
        print(f"   ✅ 图片已保存: {temp_path}")
        print(f"   📊 文件大小: {file_size / 1024:.2f} KB")

    except Exception as e:
        print(f"   ❌ 下载失败: {e}")
        return

    # 检查是否是有效图片
    if file_size < 100:
        with open(temp_path, 'r') as f:
            content = f.read()
        print(f"   ⚠️  错误: {content}")
        return

    # 初始化OCR
    print(f"\n🔍 初始化PaddleOCR...")
    try:
        ocr = PaddleOCR(lang='ch')
        print("   ✅ 初始化成功")
    except Exception as e:
        print(f"   ❌ 初始化失败: {e}")
        return

    # OCR识别
    print(f"\n📸 正在识别图片...")
    try:
        result = ocr.ocr(temp_path)

        if not result or not result[0]:
            print("   ⚠️  未识别到文字")
            return

        # 显示识别结果
        print(f"\n✅ 识别成功！共识别到 {len(result[0])} 行文本\n")
        print("   " + "="*56)

        text_lines = []
        for i, line in enumerate(result[0], 1):
            bbox = line[0]
            text_info = line[1]
            text = text_info[0]
            confidence = text_info[1]
            text_lines.append(text)

            # 显示文本和置信度
            conf_pct = confidence * 100
            print(f"   {i:2d}. {text:40s} (置信度: {conf_pct:5.1f}%)")

        # 合并文本
        full_text = '\n'.join(text_lines)

        print("\n   " + "="*56)
        print(f"   📊 统计信息:")
        print(f"   - 识别行数: {len(text_lines)}")
        print(f"   - 总字符数: {len(full_text)}")

        # 保存结果
        output_file = f"/tmp/invoice_{index}_result.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"   💾 文本已保存: {output_file}")

        return full_text

    except Exception as e:
        print(f"   ❌ 识别失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 图片URL
    images = [
        "https://maas-log-prod.cn-wlcb.ufileos.com/anthropic/03311557-5f8c-4724-9c1c-ef5e3795e971/9afba6f387b05baa5b552ed867b14aa9.jpg?UCloudPublicKey=TOKEN_e15ba47a-d098-4fbd-9afc-a0dcf0e4e621&Expires=1767779632&Signature=jObC26diXz7D7WVk98M8JoAgUt8=",
        "https://maas-log-prod.cn-wlcb.ufileos.com/anthropic/03311557-5f8c-4724-9c1c-ef5e3795e971/8347f1c691a49c32eaa37d78ec39ce25.jpg?UCloudPublicKey=TOKEN_e15ba47a-d098-4fbd-9afc-a0dcf0e4e621&Expires=1767779632&Signature=K2OdxackXxO4UEB4HPDeJMEuTPc="
    ]

    print("🎯 发票图片OCR测试")
    print("="*60)

    # 测试每张图片
    for i, url in enumerate(images, 1):
        download_and_test(url, i)

    print(f"\n{'='*60}")
    print("✅ 测试完成！")
    print(f"{'='*60}\n")
