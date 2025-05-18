from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import os
import time
import json
import logging
import requests
from typing import Optional, List

import dataIngestion

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Foody Data Ingestion API")

# Theo dõi trạng thái ingestion
ingestion_status = {
    "is_processing": False,
    "last_processed": None,
    "total_items_processed": 0,
    "total_items_saved": 0,
    "error": None,
    "step": None
}

def run_ingestion(force: bool = False):
    """Background task to run data ingestion process"""
    global ingestion_status

    try:
        # Thiết lập trạng thái ban đầu
        ingestion_status["is_processing"] = True
        ingestion_status["error"] = None
        ingestion_status["total_items_processed"] = 0
        ingestion_status["total_items_saved"] = 0
        ingestion_status["step"] = "starting"
        
        # Xóa file clean_data.json cũ nếu có
        if os.path.exists("/app/landing_zone/clean_data.json"):
            os.remove("/app/landing_zone/clean_data.json")
            logger.info("Đã xóa file clean_data.json cũ")
        
        # Kiểm tra xem có file crawl_completed chưa
        if not force and not os.path.exists("/app/landing_zone/crawl_completed"):
            logger.warning("Chưa có dữ liệu crawl hoàn chỉnh. Vui lòng chạy crawler trước.")
            ingestion_status["error"] = "Chưa có dữ liệu crawl hoàn chỉnh. Vui lòng chạy crawler trước."
            return
        # Kiểm tra có file JSON nào không
        json_files = [f for f in os.listdir("/app/landing_zone") if f.endswith('.json') and f != "clean_data.json"]
        if not json_files and not force:
            logger.warning("Không tìm thấy file JSON nào trong landing_zone để xử lý.")
            ingestion_status["error"] = "Không tìm thấy file JSON nào trong landing_zone để xử lý."
            return

        logger.info(f"Bắt đầu xử lý {len(json_files)} file JSON từ landing_zone")
        ingestion_status["step"] = "processing_data"

         # Chạy quá trình ingestion
        dataIngestion.ingest_data()


        # Đọc dữ liệu đã xử lý
        clean_data = []
        try:
            with open('/app/landing_zone/clean_data.json', 'r', encoding='utf-8') as f:
                clean_data = json.load(f)
        except Exception as e:
            logger.error(f"Lỗi khi đọc file clean_data.json: {str(e)}")
            ingestion_status["error"] = f"Lỗi khi đọc file clean_data.json: {str(e)}"
            return
        
        ingestion_status["total_items_processed"] = len(clean_data)
        logger.info(f"Đã xử lý thành công {len(clean_data)} items")
        
        # Gửi dữ liệu vào database
        if clean_data:
            ingestion_status["step"] = "saving_to_database"
            success, fail = dataIngestion.send_data_to_db(clean_data)
            ingestion_status["total_items_saved"] = success
            
            if fail > 0:
                logger.warning(f"Có {fail} items không thể lưu vào database")
                if ingestion_status["error"] is None:
                    ingestion_status["error"] = f"Có {fail} items không thể lưu vào database"
            
            logger.info(f"Đã lưu thành công {success} items vào database")
        
        ingestion_status["last_processed"] = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Quá trình xử lý dữ liệu đã hoàn tất")

    except Exception as e:
        error_msg = f"Lỗi trong quá trình xử lý dữ liệu: {str(e)}"
        logger.error(error_msg)
        ingestion_status["error"] = error_msg
    finally:
        ingestion_status["is_processing"] = False
        ingestion_status["step"] = "completed"


@app.get("/")
def read_root():
    return {"message": "Foody Data Ingestion API is running"}


@app.get("/status")
def get_status():
    """Lấy trạng thái hiện tại của quá trình ingestion"""
    return ingestion_status



@app.post("/process")
async def start_ingestion(background_tasks: BackgroundTasks, force: bool = False):
    """Bắt đầu quá trình xử lý dữ liệu mới"""
    if ingestion_status["is_processing"]:
        return JSONResponse(
            status_code=409,
            content={"message": "Một quá trình xử lý dữ liệu đang diễn ra"}
        )
    
    # Bắt đầu task xử lý dữ liệu trong background
    background_tasks.add_task(run_ingestion, force)
    
    return {"message": "Đã bắt đầu quá trình xử lý dữ liệu", "force": force}


@app.post("/reset")
def reset_ingestion():
    """Reset trạng thái ingestion (cho debug/testing)"""
    if ingestion_status["is_processing"]:
        return JSONResponse(
            status_code=409,
            content={"message": "Không thể reset khi đang có quá trình xử lý dữ liệu"}
        )
    
    # Reset dictionary trạng thái
    ingestion_status["is_processing"] = False
    ingestion_status["last_processed"] = None
    ingestion_status["total_items_processed"] = 0
    ingestion_status["total_items_saved"] = 0
    ingestion_status["error"] = None
    ingestion_status["step"] = None
    
    return {"message": "Đã reset trạng thái data ingestion"}

@app.get("/preview")
def preview_data(limit: int = 10):
    """Xem trước dữ liệu đã xử lý"""
    try:
        with open('/app/landing_zone/clean_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {"total": len(data), "preview": data[:limit]}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chưa có dữ liệu đã xử lý. Vui lòng chạy data ingestion trước.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="File dữ liệu không hợp lệ")


@app.get("/db/check")
def check_database_connection():
    """Kiểm tra kết nối đến database API"""
    try:
        # Thử lấy IP của db-api
        api_url = dataIngestion.get_host_ip()
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            return {"message": "Kết nối đến DB API thành công", "api_url": api_url}
        else:
            return {"message": f"DB API trả về status code {response.status_code}", "api_url": api_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể kết nối đến DB API: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("data_ingestion_api:app", host="0.0.0.0", port=8000, reload=True)