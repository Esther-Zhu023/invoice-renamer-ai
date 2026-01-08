#!/usr/bin/env python3
"""
百度OCR提取器 - 专门识别发票/收据
准确率最高，支持增值税发票、通用票据等
"""
import os
import base64
import requests
from typing import Optional, Dict, List
from PIL import Image
import io


class BaiduOcrExtractor:
    """
    百度OCR提取器
    支持：增值税发票、通用票据、行程单等复杂单据
    """

    def __init__(self, api_key: str, secret_key: str):
        """
        初始化百度OCR

        :param api_key: API Key
        :param secret_key: Secret Key
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None

        # 获取access_token
        self._get_access_token()
        print(f"   ✅ 百度OCR初始化成功\n")

    def _get_access_token(self):
        """获取百度API Access Token"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }

        response = requests.post(url, params=params)
        result = response.json()

        if "access_token" in result:
            self.access_token = result["access_token"]
        else:
            raise Exception(f"获取Access Token失败: {result}")

    def _image_to_base64(self, image_path: str) -> str:
        """将图片转换为base64编码"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')

    def extract_vat_invoice(self, image_path: str) -> Dict:
        """
        识别增值税发票（最准确）

        :param image_path: 图片路径（支持JPG/PNG/PDF）
        :return: 发票信息字典
        """
        if not self.access_token:
            raise Exception("Access Token未初始化")

        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/vat_invoice"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # 转换图片
        img_base64 = self._image_to_base64(image_path)

        # 调用API
        params = {
            "access_token": self.access_token,
            "image": img_base64
        }

        response = requests.post(url, headers=headers, data=params)
        result = response.json()

        if "error_code" in result:
            raise Exception(f"百度OCR错误: {result.get('error_msg')}")

        return self._parse_vat_invoice(result)

    def _parse_vat_invoice(self, result: Dict) -> Dict:
        """解析增值税发票结果"""
        words_result = result.get("words_result", {})

        return {
            "invoice_number": words_result.get("InvoiceNum", {}).get("word"),
            "issue_date": words_result.get("InvoiceDate", {}).get("word"),
            "seller_name": words_result.get("SellerName", {}).get("word"),
            "seller_tax_id": words_result.get("SellerRegisterNum", {}).get("word"),
            "buyer_name": words_result.get("PurchaserName", {}).get("word"),
            "buyer_tax_id": words_result.get("PurchaserRegisterNum", {}).get("word"),
            "total_amount": words_result.get("TotalAmount", {}).get("word"),
            "total_tax": words_result.get("TotalTax", {}).get("word"),
            "total_including_tax": words_result.get("AmountInFiguers", {}).get("word"),
            "total_including_tax_in_words": words_result.get("AmountInWords", {}).get("word"),
        }

    def extract_general_receipt(self, image_path: str) -> str:
        """
        识别通用票据/收据（支持复杂排版）

        :param image_path: 图片路径
        :return: 识别的完整文本
        """
        if not self.access_token:
            raise Exception("Access Token未初始化")

        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/receipt"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # 转换图片
        img_base64 = self._image_to_base64(image_path)

        # 调用API
        params = {
            "access_token": self.access_token,
            "image": img_base64,
            "return_seal_image": "false"  # 不返回印章图片
        }

        response = requests.post(url, headers=headers, data=params)
        result = response.json()

        if "error_code" in result:
            raise Exception(f"百度OCR错误: {result.get('error_msg')}")

        # 提取所有文本
        words_result = result.get("words_result", [])
        text_lines = [item.get("word", "") for item in words_result]
        return "\n".join(text_lines)

    def extract_from_path(self, file_path: str) -> str:
        """
        从文件路径提取文本（智能判断）

        :param file_path: 文件路径
        :return: 提取的文本
        """
        ext = os.path.splitext(file_path)[1].lower()

        # 优先使用增值税发票API（如果是PDF）
        if ext == '.pdf':
            try:
                result = self.extract_vat_invoice(file_path)
                # 将字典转换为文本格式
                text = "\n".join([f"{k}: {v}" for k, v in result.items() if v])
                if text.strip():
                    return text
            except:
                pass

        # 降级使用通用票据识别
        return self.extract_general_receipt(file_path)


# 测试代码
if __name__ == "__main__":
    import sys

    # 从环境变量获取API Key
    API_KEY = os.getenv("BAIDU_OCR_API_KEY")
    SECRET_KEY = os.getenv("BAIDU_OCR_SECRET_KEY")

    if not API_KEY or not SECRET_KEY:
        print("❌ 请设置环境变量:")
        print("   BAIDU_OCR_API_KEY")
        print("   BAIDU_OCR_SECRET_KEY")
        print("\n获取方式:")
        print("1. 访问 https://console.bce.baidu.com/ai/")
        print("2. 开通「文字识别」服务")
        print("3. 创建应用获取API Key和Secret Key")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("使用方法: python3 baidu_ocr_extractor.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]

    print(f"\n{'='*60}")
    print(f"🔍 百度OCR测试")
    print(f"{'='*60}\n")

    extractor = BaiduOcrExtractor(API_KEY, SECRET_KEY)

    print(f"📸 正在识别: {os.path.basename(image_path)}\n")
    text = extractor.extract_from_path(image_path)

    print(f"\n{'='*60}")
    print(f"✅ 识别结果:")
    print(f"{'='*60}\n")
    print(text)
    print(f"\n{'='*60}\n")
