from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import dataCrawling
import os
import subprocess
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Foody Crawler API")

# Track crawling status
crawling_status = {
    "is_crawling": False,
    "last_crawl": None,
    "total_items_found": 0,
    "pages_crawled": 0,
    "error": None
}

def run_crawler(pages: int = None):
    """Background task to run the crawler"""
    global crawling_status
    
    try:
        # Reset status
        crawling_status["is_crawling"] = True
        crawling_status["error"] = None
        crawling_status["total_items_found"] = 0
        crawling_status["pages_crawled"] = 0
        
        # Clean up previous data
        logger.info("Cleaning up previous data...")
        landing_zone = "/app/landing_zone"
        for file in os.listdir(landing_zone):
            if file.endswith(".json") or file == "crawl_completed":
                os.remove(os.path.join(landing_zone, file))
        
        # Set max pages parameter if provided
        if pages:
            os.environ["MAX_PAGES_TO_CRAWL"] = str(pages)
            dataCrawling.MAX_PAGES_TO_CRAWL = pages
            
        # Run crawler
        logger.info(f"Starting crawling process (max pages: {dataCrawling.MAX_PAGES_TO_CRAWL})...")
        
        item_count = 0
        for i in range(dataCrawling.MAX_PAGES_TO_CRAWL):
            current_page = i + 1
            result = dataCrawling.crawl_page(current_page)
            
            if result is None:
                logger.warning(f"Error or no data on page {current_page}")
                break
                
            if result == "NO_MORE_ITEMS":
                logger.info(f"No more items found after page {current_page-1}")
                break
            
            # Count items
            if "searchItems" in result and isinstance(result["searchItems"], list):
                item_count += len(result["searchItems"])
            
            crawling_status["pages_crawled"] = current_page
            time.sleep(2)
        
        # Create completion marker
        with open(os.path.join(landing_zone, "crawl_completed"), "w") as f:
            f.write("Crawling completed at " + time.strftime("%Y-%m-%d %H:%M:%S"))
        
        crawling_status["total_items_found"] = item_count
        crawling_status["last_crawl"] = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Crawling completed. Found {item_count} items across {crawling_status['pages_crawled']} pages.")
            
    except Exception as e:
        error_msg = f"Error during crawling: {str(e)}"
        logger.error(error_msg)
        crawling_status["error"] = error_msg
    finally:
        crawling_status["is_crawling"] = False

@app.get("/")
def read_root():
    return {"message": "Foody Crawler API is running"}

@app.get("/status")
def get_status():
    """Get current crawler status"""
    return crawling_status

@app.post("/crawl")
async def start_crawl(background_tasks: BackgroundTasks, pages: int = None):
    """Start a new crawling job"""
    if crawling_status["is_crawling"]:
        return JSONResponse(
            status_code=409,
            content={"message": "A crawling job is already in progress"}
        )
    
    # Validate pages parameter
    if pages is not None and (not isinstance(pages, int) or pages <= 0):
        raise HTTPException(status_code=400, detail="Pages must be a positive integer")
        
    # Start background crawling task
    background_tasks.add_task(run_crawler, pages)
    
    return {"message": "Crawling started", "pages_requested": pages or dataCrawling.MAX_PAGES_TO_CRAWL}

@app.post("/reset")
def reset_crawler():
    """Reset crawler status (for debugging/testing)"""
    if crawling_status["is_crawling"]:
        return JSONResponse(
            status_code=409,
            content={"message": "Cannot reset while a crawling job is in progress"}
        )
    
    # Reset the status dictionary values
    crawling_status["is_crawling"] = False
    crawling_status["last_crawl"] = None
    crawling_status["total_items_found"] = 0
    crawling_status["pages_crawled"] = 0
    crawling_status["error"] = None
    
    return {"message": "Crawler status has been reset"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("crawler_api:app", host="0.0.0.0", port=8000, reload=True)