import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import asyncio
from mcp.server.fastmcp import FastMCP
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# --- Logging Configuration ---
project_root = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(project_root, "@logs")
os.makedirs(logs_dir, exist_ok=True)

logger = logging.getLogger("nexus-webscraper")
logger.setLevel(logging.INFO)

# 1. Stderr Handler (Standard MCP logging out-of-band of JSON RPC)
stderr_handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stderr_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)

# 2. Minimal Rotating File Handler (Max 5MB x 3 backups)
file_handler = RotatingFileHandler(
    os.path.join(logs_dir, "server.log"),
    maxBytes=1024 * 1024 * 5,
    backupCount=3
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def cleanup_old_files():
    """Automatically scrub files older than 72 hours from outputs and logs."""
    dirs_to_clean = ["@outputs", "@logs"]
    age_limit_seconds = 72 * 60 * 60
    current_time = time.time()
    deleted_count = 0
    
    for d in dirs_to_clean:
        dir_path = os.path.join(project_root, d)
        if not os.path.exists(dir_path): continue
            
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path):
                # Keep active logs safe, they rotate themselves
                if filename == "server.log":
                    continue
                    
                age = current_time - os.path.getmtime(file_path)
                if age > age_limit_seconds:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Cleanup error on {file_path}: {e}")
                        
    if deleted_count > 0:
        logger.info(f"Routine maintenance: deleted {deleted_count} stale files (>72 hrs).")

# Create a FastMCP server instance
mcp = FastMCP("nexus-webscraper")

def trim_scraped_article(markdown: str) -> str:
    """Post-processes extracted Markdown to remove related articles, footers, and PR."""
    cutoff_markers = [
        "関連記事", "関連リンク", "SpecialPR", "記事ジャンル", "RANKING", 
        "メールマガジン", "あなたにおすすめの記事", "利用規約", "メディア一覧", 
        "公式SNS", "お問い合わせ", "プライバシーポリシー", "運営会社", "採用情報", "RSS"
    ]
    remove_line_markers = [
        "Copyright ©", "続きを読むには", "会員登録が必要", "アイティメディアID"
    ]
    
    lines = markdown.splitlines()
    cleaned_lines = []
    
    for line in lines:
        # Check if we should stop parsing completely (end of article body)
        if any(marker in line for marker in cutoff_markers):
            break
            
        # Check if we should discard this specific line
        if any(marker in line for marker in remove_line_markers):
            continue
            
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines).strip()

@mcp.tool()
async def crawl_website(url: str) -> str:
    """
    Crawls a website and returns its contents in Markdown format.

    Args:
        url: The URL of the website to crawl.
    """
    logger.info(f"Incoming tool request: crawl_website for url={url}")
    # Housekeeping
    cleanup_old_files()
    
    config = CrawlerRunConfig(
        excluded_tags=["nav", "footer", "aside"],
        excluded_selector=".sidebar, .ad",
    )
    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(
            url=url,
            config=config,
            fit_markdown=True
        )
        
        # Handle different Crawl4AI version object structures for fit_markdown
        if hasattr(result.markdown, "fit_markdown") and result.markdown.fit_markdown:
            content = result.markdown.fit_markdown
        elif hasattr(result, "fit_markdown") and result.fit_markdown:
            content = result.fit_markdown
        else:
            content = result.markdown
            
        return trim_scraped_article(str(content))

if __name__ == "__main__":
    # Start the FastMCP server with standard stdio transport
    mcp.run()
