#!/usr/bin/env python3
"""
Gemini REST API 提取器 - 直接调用API，不使用SDK
支持多语言收据/发票识别（中英日文）
"""
import os
import base64
import requests
from PIL import Image
from typing import Dict
import io
import json


class GeminiRestExtractor:
    """
    Gemini REST API 提取器
    直接使用REST API，避免SDK版本问题
    """

    def __init__(self, api_key: str):
        """
        初始化 Gemini REST API

        :param api_key: Google API Key
        """
        self.api_key = api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        print(f"🔧 初始化 Gemini REST API...")
        print("   ✅ 初始化成功\n")

    def _image_to_base64(self, image_path: str) -> str:
        """将图片转换为base64编码"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')

    def extract_from_image(self, image_path: str) -> Dict:
        """
        从图片中提取收据信息

        :param image_path: 图片路径
        :return: 提取的信息字典
        """
        # 构建请求体
        prompt = """
请详细分析这张收据/发票图片，提取所有可见信息。

返回JSON格式，包含以下字段：
{
  "seller_name": "店铺或公司名称（保留原语言）",
  "issue_date": "日期（YYYY-MM-DD格式）",
  "issue_time": "时间（如果有，HH:MM格式）",
  "invoice_number": "发票或收据编号（如果有）",
  "total_amount": "总金额（仅数字）",
  "subtotal": "小计金额",
  "tax": "税额",
  "currency": "货币符号（如¥、$、€等）",
  "payment_method": "支付方式（现金/信用卡/支付宝等）",
  "items": "商品列表（如果有多个商品，用分号分隔）"
}

支持中文、英文、日文识别。如果某项信息不存在，设为null。

只返回JSON，不要其他解释文字。
"""

        # 转换图片
        img_base64 = self._image_to_base64(image_path)

        # 构建请求
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_base64
                            }
                        }
                    ]
                }
            ]
        }

        # 发送请求
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            # 提取生成的文本
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0]["content"]["parts"][0]["text"]

                # 解析JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    return json.loads(json_str)
                else:
                    return {"raw_text": content}
            else:
                return {"error": "No content in response"}

        except Exception as e:
            return {"error": str(e)}

    def extract_with_deep_structure(self, image_path: str) -> Dict:
        """
        深度结构化提取

        :param image_path: 图片路径
        :return: 详细的信息字典
        """
        return self.extract_from_image(image_path)


# 测试代码
if __name__ == "__main__":
    import sys

    # 从环境变量获取API Key
    API_KEY = os.getenv("GEMINI_API_KEY")

    if not API_KEY:
        print("❌ 请设置环境变量: GEMINI_API_KEY")
        print("   获取方式: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("使用方法: python3 gemini_rest_extractor.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]

    print(f"\n{'='*60}")
    print(f"🔍 Gemini REST API 测试")
    print(f"{'='*60}\n")

    extractor = GeminiRestExtractor(API_KEY)

    print(f"📸 正在识别: {os.path.basename(image_path)}\n")
    result = extractor.extract_from_image(image_path)

    print(f"\n{'='*60}")
    print(f"✅ 识别结果:")
    print(f"{'='*60}\n")

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"\n{'='*60}\n")
