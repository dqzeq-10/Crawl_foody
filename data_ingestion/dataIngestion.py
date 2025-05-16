import json
from opcode import opname
import os

INPUT_DIR = "landing_zone"
OUTPUT_FILE = "data_ingestion/clean_data.json"

def process_raw_data(raw_item_data):
    try:
        processed_item = {
            "BrandName": raw_item_data.get("Name"),
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
        print(f"Lỗi khi xử lí item {raw_item_data.get('Id', 'N/A'): {e}}")
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

if __name__ == "__main__":
    ingest_data()


