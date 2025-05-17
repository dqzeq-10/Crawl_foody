#!/bin/bash
set -e

echo "=== Data Ingestion Service Starting ==="

# Xóa file clean_data.json nếu đã tồn tại
if [ -f "/app/landing_zone/clean_data.json" ]; then
    echo "Xóa file clean_data.json cũ..."
    rm -f /app/landing_zone/clean_data.json
    echo "✅ Đã xóa file clean_data.json cũ"
fi

# Kiểm tra thư mục landing_zone
echo "Kiểm tra thư mục landing_zone:"
ls -la /app/landing_zone

# Đợi crawler hoàn thành
MAX_RETRIES=30
COUNTER=0
CRAWL_COMPLETED=false

echo "Đang đợi quá trình crawl hoàn tất..."
while [ $COUNTER -lt $MAX_RETRIES ] && [ "$CRAWL_COMPLETED" = false ]; do
    echo "Kiểm tra file crawl_completed lần thứ $((COUNTER+1))..."
    if [ -f "/app/landing_zone/crawl_completed" ]; then
        CRAWL_COMPLETED=true
        echo "✅ Quá trình crawl đã hoàn tất!"
    else
        echo "⏳ Đang đợi quá trình crawl hoàn tất. Thử lại sau 10 giây..."
        # Liệt kê nội dung thư mục để debug
        echo "Nội dung hiện tại của thư mục landing_zone:"
        ls -la /app/landing_zone
        sleep 10
        COUNTER=$((COUNTER+1))
    fi
done

if [ "$CRAWL_COMPLETED" = false ]; then
    echo "❌ Crawler không hoàn tất sau $MAX_RETRIES lần thử. Data Ingestion sẽ dừng lại."
    exit 1
fi

# Kiểm tra dữ liệu đầu vào
echo "Kiểm tra dữ liệu crawl..."
JSON_COUNT=$(ls -1 /app/landing_zone/*.json 2>/dev/null | wc -l)
if [ "$JSON_COUNT" -eq 0 ]; then
    echo "❌ Không tìm thấy file JSON nào trong landing_zone. Data Ingestion sẽ dừng lại."
    exit 1
fi
echo "✅ Tìm thấy $JSON_COUNT file JSON trong landing_zone"

# Kiểm tra API đã sẵn sàng chưa
MAX_RETRIES=30
COUNTER=0
API_READY=false

echo "Đang đợi DB API sẵn sàng..."
while [ $COUNTER -lt $MAX_RETRIES ] && [ "$API_READY" = false ]; do
    if curl -s http://db-api:8000/ > /dev/null; then
        API_READY=true
        echo "✅ DB API đã sẵn sàng!"
    else
        echo "⏳ DB API chưa sẵn sàng. Thử lại sau 5 giây..."
        sleep 5
        COUNTER=$((COUNTER+1))
    fi
done

if [ "$API_READY" = false ]; then
    echo "❌ DB API không khả dụng sau $MAX_RETRIES lần thử. Data Ingestion sẽ dừng lại."
    exit 1
fi

echo "=== Bắt đầu quá trình xử lý và lưu dữ liệu ==="
python dataIngestion.py

echo "=== Data Ingestion Service đã hoàn thành nhiệm vụ ==="
# Giữ container chạy
tail -f /dev/null
