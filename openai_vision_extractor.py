#!/usr/bin/env python3
"""
OpenAI GPT-4o Vision 提取器
支持多语言收据/发票识别（中英日文）
"""
import os
import base64
from openai import OpenAI
from PIL import Image
from typing import Dict
import io
import json


class OpenAIVisionExtractor:
    """
    OpenAI GPT-4o Vision 提取器
    直接理解图片并提取结构化数据
    """

    def __init__(self, api_key: str):
        """
        初始化 OpenAI Vision

        :param api_key: OpenAI API Key
        """
        self.client = OpenAI(api_key=api_key)
        print(f"🔧 初始化 OpenAI GPT-4o Vision...")
        print("   ✅ 初始化成功\n")

    def _encode_image(self, image_path: str) -> str:
        """将图片转换为base64编码"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def extract_from_image(self, image_path: str) -> Dict:
        """
        从图片中提取收据信息（支持多收据）

        :param image_path: 图片路径
        :return: 提取的信息字典或字典列表
        """
        # 构建提示词 - 支持多收据识别
        prompt = """
请详细分析这张图片，识别其中的收据/发票信息。

**重要说明：**
- 如果图片中有多个收据/发票，请返回JSON数组格式：[{收据1}, {收据2}, ...]
- 如果只有一个收据/发票，返回单个JSON对象：{收据信息}

返回JSON格式，每个收据包含以下字段：
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

**示例：**
单个收据：{"seller_name": "星巴克", "total_amount": "50", ...}
多个收据：[{"seller_name": "星巴克", ...}, {"seller_name": "7-11", ...}]

只返回JSON，不要其他解释文字。
"""

        # 编码图片
        base64_image = self._encode_image(image_path)

        try:
            # 调用 GPT-4o Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4o支持视觉
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000  # 增加token以支持多收据
            )

            # 提取响应
            content = response.choices[0].message.content

            # 解析JSON（支持数组或对象）
            import re
            json_match = re.search(r'\[.*\]|\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)

                # 如果是单个对象，转换为数组
                if isinstance(result, dict):
                    return [result]
                elif isinstance(result, list):
                    return result
                else:
                    return [{"raw_text": content}]
            else:
                return [{"raw_text": content}]

        except Exception as e:
            return [{"error": str(e)}]

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
    API_KEY = os.getenv("OPENAI_API_KEY")

    if not API_KEY:
        print("❌ 请设置环境变量: OPENAI_API_KEY")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("使用方法: python3 openai_vision_extractor.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]

    print(f"\n{'='*60}")
    print(f"🔍 OpenAI GPT-4o Vision 测试")
    print(f"{'='*60}\n")

    extractor = OpenAIVisionExtractor(API_KEY)

    print(f"📸 正在识别: {os.path.basename(image_path)}\n")
    result = extractor.extract_from_image(image_path)

    print(f"\n{'='*60}")
    print(f"✅ 识别结果:")
    print(f"{'='*60}\n")

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"\n{'='*60}\n")
