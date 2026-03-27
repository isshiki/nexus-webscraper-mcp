import asyncio
import os
import sys
from datetime import datetime
from urllib.parse import urlparse

# Add parent directory to sys.path so we can import server.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import crawl_website

async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.itmedia.co.jp/aiplus/articles/2603/26/news132.html"
    print(f"Starting crawl of {url}")
    
    # Create outputs directory relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outputs_dir = os.path.join(project_root, "@outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    
    try:
        # Crawl the website
        content = await crawl_website(url)
        
        # Parse domain for filename
        domain = urlparse(url).netloc
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_{timestamp}.md"
        filepath = os.path.join(outputs_dir, filename)
        
        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Success! Content saved to {filepath}")
        print("First 200 characters:")
        print(content[:200])
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        # Playwright requires the Proactor event loop on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Event loop is closed" not in str(e):
            raise
