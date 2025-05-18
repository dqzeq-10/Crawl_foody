from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import os
import subprocess
import time
import logging
from datetime import datetime
from typing import Optional, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from pydantic import BaseModel, validator
import json
from dateutil.parser import parse as parse_date
import requests

import dataCrawling

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo scheduler
scheduler = BackgroundScheduler()
scheduler.add_jobstore(MemoryJobStore(), 'default')
scheduler.start()

app = FastAPI(title="Foody Crawler API")

# Model cho lập lịch
class ScheduleModel(BaseModel):
    name: str
    cron_expression: str
    pages: Optional[int] = 1
    description: Optional[str] = None
    active: bool = True
    
    @validator('cron_expression')
    def validate_cron(cls, v):
        # Check valid cron expression
        try:
            CronTrigger.from_crontab(v)
            return v
        except Exception as e:
            raise ValueError(f"Biểu thức cron không hợp lệ: {str(e)}")

# Track crawling status
crawling_status = {
    "is_crawling": False,
    "last_crawl": None,
    "total_items_found": 0,
    "pages_crawled": 0,
    "error": None
}

# Track schedules
schedules = []
schedule_file_path = "/app/landing_zone/schedules.json"


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


# SCHEDULER ENDPOINTS

@app.get("/schedule")
def get_schedules():
    """Get all crawl schedules"""
    # Show next run time for each schedule
    result = []
    for schedule in schedules:
        schedule_copy = schedule.copy()
        job = scheduler.get_job(f"crawler_{schedule['name']}")
        if job:
            schedule_copy["next_run"] = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None
        else:
            schedule_copy["next_run"] = None
        result.append(schedule_copy)
    return result

@app.post("/schedule")
def create_schedule(schedule: ScheduleModel):
    """Create a new crawl schedule"""
    global schedules
    
    # Check if schedule with this name already exists
    for existing in schedules:
        if existing["name"] == schedule.name:
            raise HTTPException(status_code=400, detail=f"Lịch trình với tên '{schedule.name}' đã tồn tại")
    
    # Create schedule dict
    schedule_dict = {
        "name": schedule.name,
        "cron_expression": schedule.cron_expression,
        "pages": schedule.pages,
        "description": schedule.description,
        "active": schedule.active,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to scheduler
    if add_schedule_job(schedule_dict):
        # Add to list and save
        schedules.append(schedule_dict)
        save_schedules()
        return {"message": f"Đã tạo lịch trình '{schedule.name}'", "schedule": schedule_dict}
    else:
        raise HTTPException(status_code=500, detail="Không thể đăng ký lịch trình")

@app.put("/schedule/{name}")
def update_schedule(name: str, schedule: ScheduleModel):
    """Update an existing crawl schedule"""
    global schedules
    
    # Find schedule
    found = False
    for i, existing in enumerate(schedules):
        if existing["name"] == name:
            found = True
            
            # Update schedule
            schedule_dict = {
                "name": schedule.name,
                "cron_expression": schedule.cron_expression,
                "pages": schedule.pages,
                "description": schedule.description,
                "active": schedule.active,
                "created_at": existing.get("created_at"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Update in scheduler
            if add_schedule_job(schedule_dict):
                # Update in list and save
                schedules[i] = schedule_dict
                save_schedules()
                return {"message": f"Đã cập nhật lịch trình '{name}'", "schedule": schedule_dict}
            else:
                raise HTTPException(status_code=500, detail="Không thể cập nhật lịch trình")
    
    if not found:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy lịch trình '{name}'")

@app.delete("/schedule/{name}")
def delete_schedule(name: str):
    """Delete a crawl schedule"""
    global schedules
    
    # Find schedule
    found = False
    for i, existing in enumerate(schedules):
        if existing["name"] == name:
            found = True
            
            # Remove from scheduler
            job_id = f"crawler_{name}"
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            
            # Remove from list and save
            schedules.pop(i)
            save_schedules()
            return {"message": f"Đã xóa lịch trình '{name}'"}
    
    if not found:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy lịch trình '{name}'")

@app.post("/schedule/{name}/toggle")
def toggle_schedule(name: str):
    """Enable or disable a schedule"""
    global schedules
    
    # Find schedule
    for i, existing in enumerate(schedules):
        if existing["name"] == name:
            # Toggle active status
            existing["active"] = not existing["active"]
            existing["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update scheduler
            if add_schedule_job(existing):
                save_schedules()
                status = "kích hoạt" if existing["active"] else "tạm dừng"
                return {"message": f"Đã {status} lịch trình '{name}'", "active": existing["active"]}
            else:
                raise HTTPException(status_code=500, detail=f"Không thể {status} lịch trình")
    
    raise HTTPException(status_code=404, detail=f"Không tìm thấy lịch trình '{name}'")

# Load schedules at startup
@app.on_event("startup")
def startup_event():
    global schedules
    schedules = load_schedules()

# Shutdown scheduler when app stops
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("crawler_api:app", host="0.0.0.0", port=8000, reload=True)