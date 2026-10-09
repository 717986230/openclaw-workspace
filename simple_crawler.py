#!/usr/bin/env python3
"""
Simple web crawler using crawl4ai for data extraction
Designed to work with crawl4ai 0.6.3 and extract content for labeling
"""

import asyncio
from crawl4ai import AsyncWebCrawler

async def crawl_and_extract(url):
    """
    Crawl a URL and extract text content
    Returns clean text suitable for data labeling tasks
    """
    print(f"🕷️  Crawling: {url}")
    
    # Configure crawler for simple text extraction
    async with AsyncWebCrawler(
        verbose=True,
        # Simple configuration that works with crawl4ai 0.6.3
    ) as crawler:
        
        # Crawl the page
        result = await crawler.arun(
            url=url,
            # Only get the cleaned text content
            word_count_threshold=10,  # Ignore very short text blocks
            exclude_external_links=True,  # Focus on main content
            process_iframes=False,  # Simplify processing
            remove_overlay_elements=True,  # Remove popups/modals
        )
        
        if result.success:
            print(f"✅ Successfully crawled {url}")
            print(f"📄 Extracted {len(result.markdown)} characters of markdown")
            print(f"📝 Extracted {len(result.cleaned_html)} characters of cleaned HTML")
            
            # Return the markdown content which is clean and ready for labeling
            return result.markdown
        else:
            print(f"❌ Failed to crawl {url}: {result.error_message}")
            return None

async def main():
    """Main function to demonstrate the crawler"""
    print("🚀 Simple Web Crawler for Data Labeling")
    print("=" * 50)
    
    # Example URLs to crawl - using stable, simple sites for demonstration
    test_urls = [
        "https://httpbin.org/html",  # Simple HTML page for testing
        "https://example.com",       # Very simple example site
    ]
    
    for url in test_urls:
        try:
            content = await crawl_and_extract(url)
            if content:
                print("\n📋 Extracted Content Preview:")
                print("-" * 30)
                # Show first 500 characters of extracted content
                preview = content[:500] + ("..." if len(content) > 500 else "")
                print(preview)
                print("-" * 30)
                print(f"📊 Content length: {len(content)} characters\n")
            else:
                print("❌ No content extracted\n")
                
        except Exception as e:
            print(f"❌ Error crawling {url}: {e}\n")
    
    print("✅ Crawling demonstration complete!")
    print("💡 The extracted content above is ready for data labeling tasks")
    print("   (NER, classification, sentiment analysis, etc.)")

if __name__ == "__main__":
    asyncio.run(main())