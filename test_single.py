#!/usr/bin/env python3
from openai_vision_extractor import OpenAIVisionExtractor
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_VISION_API_KEY")

extractor = OpenAIVisionExtractor(api_key)
result = extractor.extract_from_image("/tmp/test_receipt.jpg")

import json
print("="*80)
print("🔍 OpenAI Vision 识别结果：")
print("="*80)
print(json.dumps(result, indent=2, ensure_ascii=False))
print("="*80)
