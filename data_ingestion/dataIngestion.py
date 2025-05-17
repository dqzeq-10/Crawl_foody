import os
import json
import time
import requests
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

INPUT_DIR = "/app/landing_zone"
OUTPUT_FILE = "/app/landing_zone/clean_data.json"

def process_raw_data(raw_item_data):
    try:
        processed_item = {
            "BranchName": raw_item_data.get("Name"),
            "AvgRating": float(raw_item_data.get("AvgRatingOriginal",0.0)),
            "Address": raw_item_data.get("Address"),
            "City": raw_item_data.get("City"),
            "TotalReview": int(raw_item_data.get("TotalReview",0)),
            "TotalCheckins": int(raw_item_data.get("TotalCheckins",0)),
            "IsOpening": bool(raw_item_data.get("IsOpening")),
            "HasDelivery": bool(raw_item_data.get("HasDelivery"))
        }

        return processed_item
    except Exception as e:
        print(f"Lỗi khi xử lí item {raw_item_data.get('Id', 'N/A')}: {e}")
        return None
    
def ingest_data():
    all_processed_items = []

    if not os.path.exists(INPUT_DIR):
        print(f"Thư mục INPUT '{INPUT_DIR}' không tồn tại.")
        return
    
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(INPUT_DIR, filename)
            print(f"Đang xử lí file: {file_path}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                raw_items = data.get("searchItems")

                if isinstance(raw_items, list):
                    for raw_item in raw_items:
                        if isinstance(raw_item, dict):
                            processed_item = process_raw_data(raw_item)
                            if processed_item:
                                all_processed_items.append(processed_item)
                        else:
                            print(f"Cảnh báo: Item không phải dictionary trong file {filename}: {type(raw_item)}")
                elif raw_items is not None:
                    print(f"Cảnh báo: 'searchItems' trong file {filename} không phải là một danh sách ")
                else:
                    if isinstance(data, list):
                        for raw_item in data:
                            if isinstance(raw_item, dict):
                                processed_item = process_raw_data(raw_item)
                                if processed_item:
                                    all_processed_items.append(processed_item)
                            else:
                                print(f"Cảnh báo: Item không phải dictionary trong file (root list) {filename}: {type(raw_item)}")
                    else:
                        print(f"Cảnh báo: Không tìm thấy key 'searchItems' hoặc dữ liệu không phải là danh sách trong file {filename}.")
            except json.JSONDecodeError:
                print(f"Lỗi giải mã JSON trong file: {file_path}")
            except Exception as e:
                print(f"Lỗi không xác định khi xử lý file {file_path}: {e}")
    if all_processed_items: 
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
            json.dump(all_processed_items, f_out, ensure_ascii=False, indent=4)
        print(f"\nĐã xử lý và lưu tổng cộng {len(all_processed_items)} địa điểm vào file '{OUTPUT_FILE}'.")
    else:
        print("\nKhông có địa điểm nào được xử lí.")





#Gửi data tới DB

# Sử dụng địa chỉ IP thay vì tên container
# Chúng ta cũng sẽ thêm cơ chế tìm IP từ hostname
def get_host_ip():
    try:
        # Thử phân giải tên miền db_api
        host_ip = socket.gethostbyname('db-api')
        print(f"Đã phân giải được IP của db-api: {host_ip}")
        return f"http://{host_ip}:8000"
    except socket.gaierror:
        try:
            # Thử dùng docker DNS nội bộ của network
            host_ip = socket.gethostbyname('db-api.crawl_foody_foody-network')
            print(f"Đã phân giải được IP của db-api.crawl_foody_foody-network: {host_ip}")
            return f"http://{host_ip}:8000"
        except socket.gaierror:
            # Fallback đến tên gốc
            print("Không thể phân giải IP, sử dụng tên container")
            return "http://db-api:8000"

API_URL = get_host_ip()
BRANCH_ENDPOINT = f"{API_URL}/branch"

def read_clean_data():
    try:
        with open('/app/landing_zone/clean_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Không tìm thấy file clean_data.json")
        return None
    except json.JSONDecodeError:
        print(f"File clean_data.json không đúng định dạng JSON")
        return None
    
def create_session_with_retry():
    # Thiết lập session với cơ chế retry
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def send_data_to_db(data):
    success_count = 0
    fail_count = 0
    session = create_session_with_retry()

    # Thử ping API trước khi gửi dữ liệu
    max_ping_retries = 10
    ping_success = False
    
    print(f"Đang kiểm tra kết nối đến DB API ({API_URL})...")
    for i in range(max_ping_retries):
        try:
            response = session.get(API_URL, timeout=5)
            if response.status_code == 200:
                ping_success = True
                print(f"Kết nối thành công đến DB API ({API_URL})")
                break
        except requests.exceptions.RequestException:
            print(f"Lần thử {i+1}/{max_ping_retries}: Không thể kết nối đến DB API")
            time.sleep(2)
    
    if not ping_success:
        print(f"Không thể kết nối đến DB API sau {max_ping_retries} lần thử. Không thể gửi dữ liệu.")
        return 0, len(data)

    for item in data:
        branch_data = {
            "BranchName": item.get("BranchName", "Unknown"),
            "AvgRating": float(item.get("AvgRating", 0)), 
            "Address": item.get("Address", ""),
            "City": item.get("City", "Đà Nẵng"),
            "TotalReview": int(item.get("TotalReview", 0)),
            "TotalCheckins": int(item.get("TotalCheckins", 0)),
            "IsOpening": item.get("IsOpening", False),
            "HasDelivery": item.get("HasDelivery", False)
        }

        try:
            response = session.post(BRANCH_ENDPOINT, json=branch_data, timeout=10)
            
            if response.status_code == 200:
                success_count += 1
                print(f"Đã thêm thành công: {branch_data['BranchName']}")
            else:
                fail_count += 1
                print(f"Lỗi khi thêm {branch_data['BranchName']}: {response.text}")

            time.sleep(0.1)
        
        except requests.exceptions.RequestException as e:
            fail_count +=1
            print(f"Lỗi kết nối khi thêm {branch_data['BranchName']}: {str(e)}")

    return success_count, fail_count

def main():
    print("=== Bắt đầu xử lý dữ liệu và gửi vào DB ===")
    ingest_data()
    clean_data = read_clean_data()
    if not clean_data:
        print("Không có dữ liệu để gửi.")
        return
    print(f"Đã đọc {len(clean_data)} bản ghi từ clean_data.json")

    success, fail = send_data_to_db(clean_data)
    print(f"Thành công: {success},  Thất bại: {fail}")



if __name__ == "__main__":
    main()


