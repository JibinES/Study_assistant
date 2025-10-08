#!/usr/bin/env python3
"""Test script to verify Playwright can convert Mermaid to image"""

from playwright.sync_api import sync_playwright

mermaid_code = """
graph TD
    A[Start] --> B[Process]
    B --> C[End]
"""

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: white;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .mermaid {{
            background: white;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
"""

print("🎨 Testing Playwright Mermaid conversion...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1200, 'height': 800})
    
    page.set_content(html_content)
    page.wait_for_timeout(2000)
    
    screenshot_bytes = page.locator('.mermaid').screenshot(type='png')
    
    # Save test image
    with open('test_mermaid.png', 'wb') as f:
        f.write(screenshot_bytes)
    
    browser.close()

print(f"✓ Success! Generated {len(screenshot_bytes)} bytes")
print("✓ Test image saved as: test_mermaid.png")
