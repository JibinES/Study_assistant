#!/usr/bin/env python3
"""
Test script to verify Gemini API streaming is working correctly
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

print("Testing Gemini API Streaming...")
print("-" * 50)
print("\nNon-streaming response:")
print("-" * 50)

# Test non-streaming
response = model.generate_content("Say hello in 3 words")
print(response.text)

print("\n" + "-" * 50)
print("Streaming response (watch tokens appear one by one):")
print("-" * 50)

# Test streaming
response = model.generate_content("Count from 1 to 10 slowly, one number per line", stream=True)
for chunk in response:
    if chunk.text:
        print(chunk.text, end='', flush=True)

print("\n" + "-" * 50)
print("✅ Streaming test complete!")
print("If you saw the numbers appear one at a time, streaming is working!")
