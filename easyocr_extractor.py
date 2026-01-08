#!/usr/bin/env python3
"""
EasyOCR提取器 - 替代PaddleOCR
支持图片和PDF的OCR识别，支持中英日等多语言
"""
import os
from typing import Union, List
from PIL import Image
import numpy as np
import easyocr
from pdf2image import convert_from_path


class EasyOcrExtractor:
    """
    使用EasyOCR的图片/PDF文本提取器
    """

    def __init__(self, languages=['ch_sim', 'en']):
        """
        初始化EasyOCR提取器

        :param languages: 语言列表
            - 'ch_sim': 简体中文
            - 'ch_tra': 繁体中文
            - 'en': 英文
            - 'ja': 日文
            - 'ko': 韩文
        """
        print(f"🔧 初始化EasyOCR (语言: {', '.join(languages)})...")
        self.reader = easyocr.Reader(languages, gpu=False)
        print("   ✅ 初始化成功\n")

    def extract_from_image(self, image: Union[np.ndarray, Image.Image]) -> str:
        """
        从单个图像对象中提取文本

        :param image: PIL.Image 或 numpy数组
        :return: 提取出的文本字符串
        """
        # 如果是PIL图像，转换为numpy数组
        if isinstance(image, Image.Image):
            image = np.array(image)

        # 调用EasyOCR进行识别
        results = self.reader.readtext(image)

        # 提取所有文本行并合并
        text_lines = [result[1] for result in results]
        return '\n'.join(text_lines)

    def extract_from_path(self, file_path: str) -> str:
        """
        从图片文件或PDF文件的路径中提取所有文本

        :param file_path: 文件的路径
        :return: 提取出的完整文本字符串
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件未找到: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        images: List[Image.Image] = []

        # 根据文件扩展名处理
        if ext == '.pdf':
            try:
                # 将PDF转换为PIL图像列表
                images = convert_from_path(file_path, dpi=300)
            except Exception as e:
                return f"处理PDF文件时出错: {e}"
        elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            try:
                # 打开单个图片文件
                images = [Image.open(file_path)]
            except Exception as e:
                return f"打开图片文件时出错: {e}"
        else:
            return f"不支持的文件类型: {ext}"

        # 遍历所有图像页，提取文本并合并
        image_text = ''
        for i, img in enumerate(images):
            image_text += self.extract_from_image(img)
            if i < len(images) - 1:
                image_text += "\n\n"  # 在不同页面之间添加分隔

        return image_text


# 测试代码
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python3 easyocr_extractor.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]

    print(f"\n{'='*60}")
    print(f"🔍 EasyOCR测试")
    print(f"{'='*60}\n")

    extractor = EasyOcrExtractor(languages=['ch_sim', 'en'])

    print(f"📸 正在识别: {os.path.basename(image_path)}\n")
    text = extractor.extract_from_path(image_path)

    print(f"\n{'='*60}")
    print(f"✅ 识别结果:")
    print(f"{'='*60}\n")
    print(text)
    print(f"\n{'='*60}\n")
