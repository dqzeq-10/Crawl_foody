from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import mysql.connector
import time
import uvicorn
from pydantic import BaseModel, validator
import logging
import os
from fastapi.middleware.cors import CORSMiddleware



# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Đợi database sẵn sàng
if os.environ.get('WAIT_FOR_DB', '0') == '1':
    logger.info("Đợi MySQL khởi động và thực thi script init...")
    time.sleep(15)  # Đợi 15 giây để đảm bảo MySQL hoàn tất initialization

app = FastAPI()
# Thiết lập CORS cho phép truy cập từ localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],  # hoặc ["*"] để cho phép tất cả
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model cho dữ liệu chi nhánh
class Branch(BaseModel):
    BranchName: str
    AvgRating: float
    Address: str
    City: str
    TotalReview: int
    TotalCheckins: int
    IsOpening: bool = True
    HasDelivery: bool = False
    
    @validator('AvgRating')
    def validate_avg_rating(cls, v):
        if not 0 <= v <= 10:
            raise ValueError('AvgRating phải có giá trị từ 0 đến 10')
        return v

# Model cho update chi nhánh
class BranchUpdate(BaseModel):
    BranchName: str = None
    AvgRating: float = None
    Address: str = None
    City: str = None
    TotalReview: int = None
    TotalCheckins: int = None
    IsOpening: bool = None
    HasDelivery: bool = None
    
    @validator('AvgRating')
    def validate_avg_rating(cls, v):
        if v is not None and not 0 <= v <= 10:
            raise ValueError('AvgRating phải có giá trị từ 0 đến 10')
        return v

def get_db_connection():
    # Đợi MySQL khởi động (nếu cần)
    retry_count = 0
    max_retries = 10
    retry_delay = 5  # seconds
    
    while retry_count < max_retries:
        try:
            logger.info(f"Đang thử kết nối MySQL, lần thử {retry_count + 1}/{max_retries}")
            connection = mysql.connector.connect(
                host='db',  # Tên service của container MySQL
                user='root',
                password='root',
                database='db_crawl',
                port=3306,
                connect_timeout=30,
                charset='utf8mb4',
                use_unicode=True,
                collation='utf8mb4_unicode_ci'
            )
            logger.info("Kết nối MySQL thành công")
            return connection
        except mysql.connector.Error as err:
            retry_count += 1
            logger.error(f"MySQL connection error: {err}")
            if retry_count < max_retries:
                logger.info(f"Thử lại sau {retry_delay} giây...")
                time.sleep(retry_delay)
    
    logger.error("Không thể kết nối đến MySQL sau nhiều lần thử")
    raise Exception("Không thể kết nối đến MySQL sau nhiều lần thử. Chi tiết lỗi đã được ghi vào log.")

@app.get('/')
def root():
    return {"message": "API đang hoạt động. Truy cập /docs để xem tài liệu API."}

@app.get('/branches')
def get_branches():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM foody_branches')
        branches = [
            {
                'Id': row[0], 
                'BranchName': row[1], 
                'AvgRating': float(row[2]), 
                'Address': row[3],
                'City': row[4],
                'TotalReview': row[5],
                'TotalCheckins': row[6],
                'IsOpening': bool(row[7]),
                'HasDelivery': bool(row[8])
            } 
            for row in cursor.fetchall()
        ]
        conn.close()
        return branches
    except Exception as e:
        logger.error(f"Error in get_branches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get('/branch/{branch_id}')
def get_branch_by_id(branch_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM foody_branches WHERE Id = %s', (branch_id,))
    branch = cursor.fetchone()
    conn.close()
    
    if branch:
        return {
            'Id': branch[0], 
            'BranchName': branch[1], 
            'AvgRating': float(branch[2]), 
            'Address': branch[3],
            'City': branch[4],
            'TotalReview': branch[5],
            'TotalCheckins': branch[6],
            'IsOpening': bool(branch[7]),
            'HasDelivery': bool(branch[8])
        }
    raise HTTPException(status_code=404, detail=f'Branch with id {branch_id} not found')

@app.post('/branch')
def create_branch(branch: Branch):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO foody_branches (BranchName, AvgRating, Address, City, TotalReview, TotalCheckins, IsOpening, HasDelivery) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
            (branch.BranchName, branch.AvgRating, branch.Address, branch.City, branch.TotalReview, branch.TotalCheckins, branch.IsOpening, branch.HasDelivery)
        )
        conn.commit()
        branch_id = cursor.lastrowid
        return {
            'Id': branch_id,
            'BranchName': branch.BranchName,
            'AvgRating': branch.AvgRating,
            'Address': branch.Address,
            'City': branch.City,
            'TotalReview': branch.TotalReview,
            'TotalCheckins': branch.TotalCheckins,
            'IsOpening': branch.IsOpening,
            'HasDelivery': branch.HasDelivery
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.put('/branch/{branch_id}')
def update_branch(branch_id: int, branch: BranchUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Lấy dữ liệu hiện tại
        cursor.execute('SELECT * FROM foody_branches WHERE Id = %s', (branch_id,))
        current = cursor.fetchone()
        if not current:
            raise HTTPException(status_code=404, detail=f'Branch with id {branch_id} not found')
        
        # Cập nhật với các giá trị mới
        cursor.execute(
            'UPDATE foody_branches SET BranchName = %s, AvgRating = %s, Address = %s, City = %s, TotalReview = %s, TotalCheckins = %s, IsOpening = %s, HasDelivery = %s WHERE Id = %s', 
            (
                branch.BranchName if branch.BranchName is not None else current[1],
                branch.AvgRating if branch.AvgRating is not None else current[2],
                branch.Address if branch.Address is not None else current[3],
                branch.City if branch.City is not None else current[4],
                branch.TotalReview if branch.TotalReview is not None else current[5],
                branch.TotalCheckins if branch.TotalCheckins is not None else current[6],
                branch.IsOpening if branch.IsOpening is not None else current[7],
                branch.HasDelivery if branch.HasDelivery is not None else current[8],
                branch_id
            )
        )
        conn.commit()
        
        # Trả về dữ liệu đã cập nhật
        cursor.execute('SELECT * FROM foody_branches WHERE Id = %s', (branch_id,))
        updated = cursor.fetchone()
        return {
            'Id': updated[0], 
            'BranchName': updated[1], 
            'AvgRating': float(updated[2]), 
            'Address': updated[3],
            'City': updated[4],
            'TotalReview': updated[5],
            'TotalCheckins': updated[6],
            'IsOpening': bool(updated[7]),
            'HasDelivery': bool(updated[8])
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete('/branch/{branch_id}')
def delete_branch(branch_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM foody_branches WHERE Id = %s', (branch_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f'Branch with id {branch_id} not found')
        conn.commit()
        return {'message': f'Branch with id {branch_id} deleted successfully'}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get('/branch/search/')
def search_branch_by_name(q: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tìm gần đúng, không phân biệt hoa thường
    query = "SELECT * FROM foody_branches WHERE LOWER(BranchName) LIKE %s"
    like_pattern = f"%{q.lower()}%"
    cursor.execute(query, (like_pattern,))
    results = cursor.fetchall()
    conn.close()
    
    branches = [
        {
            'Id': row[0],
            'BranchName': row[1],
            'AvgRating': float(row[2]),
            'Address': row[3],
            'City': row[4],
            'TotalReview': row[5],
            'TotalCheckins': row[6],
            'IsOpening': bool(row[7]),
            'HasDelivery': bool(row[8])
        }
        for row in results
    ]
    return branches

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
