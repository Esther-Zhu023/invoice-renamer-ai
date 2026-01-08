#!/usr/bin/env python3
"""
Gemini Vision 提取器 - 支持多语言收据/发票识别
支持中文、英文、日文等多种语言
使用Google Gemini Pro Vision API
"""
import os
import google.generativeai as genai
from PIL import Image
from typing import Dict, Optional
import base64


class GeminiVisionExtractor:
    """
    Gemini Vision 提取器
    支持多语言收据/发票的直接识别和结构化提取
    """

    def __init__(self, api_key: str, model: str = "gemini-pro-vision"):
        """
        初始化 Gemini Vision

        :param api_key: Google API Key
        :param model: 模型名称（gemini-pro-vision 专门用于视觉）
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        print(f"🔧 初始化 Gemini Vision (模型: {model})...")
        print("   ✅ 初始化成功\n")

    def extract_from_image_path(self, image_path: str) -> Dict:
        """
        从图片路径提取收据/发票信息

        :param image_path: 图片路径（支持JPG/PNG/PDF转图片）
        :return: 提取的信息字典
        """
        # 加载图片
        img = Image.open(image_path)

        # 构建提示词
        prompt = """
你是一个专业的收据/发票识别助手。请从这张图片中提取信息，并以JSON格式返回。

请提取以下字段（如果图片中没有对应信息，设为null）：
- seller_name: 店铺/公司名称（保留原语言，不要翻译）
- total_amount: 总金额（仅数字）
- issue_date: 日期（YYYY-MM-DD格式）
- currency: 货币符号（如¥、$、€等）

支持语言：中文、英文、日文

只返回JSON，不要其他文字。
"""

        # 调用 Gemini Vision
        response = self.model.generate_content([prompt, img])

        # 解析结果
        result_text = response.text

        # 简单的JSON解析（提取花括号内容）
        try:
            import json
            import re

            # 提取JSON部分
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # 如果没有找到JSON，返回原始文本
                return {"raw_text": result_text}
        except Exception as e:
            # 解析失败，返回原始文本
            return {"raw_text": result_text, "error": str(e)}

    def extract_with_deep_structure(self, image_path: str) -> Dict:
        """
        深度结构化提取（使用更详细的Prompt）

        :param image_path: 图片路径
        :return: 详细的信息字典
        """
        img = Image.open(image_path)

        prompt = """
请详细分析这张收据/发票图片，提取所有可见信息。

返回JSON格式，包含以下字段：
{
  "seller_name": "店铺或公司名称（保留原语言）",
  "seller_address": "地址（如果有）",
  "seller_phone": "电话（如果有）",
  "issue_date": "日期（YYYY-MM-DD）",
  "issue_time": "时间（如果有，HH:MM格式）",
  "invoice_number": "发票或收据编号（如果有）",
  "items": [
    {
      "name": "商品名称",
      "quantity": "数量",
      "price": "单价",
      "amount": "小计"
    }
  ],
  "subtotal": "小计金额",
  "tax": "税额",
  "total_amount": "总金额",
  "payment_method": "支付方式（现金/信用卡/支付宝等）",
  "currency": "货币符号"
}

支持中文、英文、日文识别。如果某项信息不存在，设为null。

只返回JSON，不要其他解释文字。
"""

        response = self.model.generate_content([prompt, img])
        result_text = response.text

        try:
            import json
            import re

            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return {"raw_text": result_text}
        except Exception as e:
            return {"raw_text": result_text, "error": str(e)}


# 测试代码
if __name__ == "__main__":
    import sys

    # 从环境变量获取API Key
    API_KEY = os.getenv("GEMINI_API_KEY")

    if not API_KEY:
        print("❌ 请设置环境变量:")
        print("   GEMINI_API_KEY")
        print("\n获取方式:")
        print("1. 访问 https://aistudio.google.com/app/apikey")
        print("2. 创建API Key（免费）")
        print("3. 复制API Key到环境变量")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("使用方法: python3 gemini_vision_extractor.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]

    print(f"\n{'='*60}")
    print(f"🔍 Gemini Vision 测试")
    print(f"{'='*60}\n")

    extractor = GeminiVisionExtractor(API_KEY)

    print(f"📸 正在识别: {os.path.basename(image_path)}\n")

    # 使用深度提取
    result = extractor.extract_with_deep_structure(image_path)

    print(f"\n{'='*60}")
    print(f"✅ 识别结果:")
    print(f"{'='*60}\n")

    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"\n{'='*60}\n")
