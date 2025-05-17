#!/bin/bash
set -e

echo "=== Crawler Service Starting ==="

# Xóa tất cả các file JSON cũ trong landing_zone
echo "Xóa dữ liệu cũ trong landing_zone..."
rm -f /app/landing_zone/*.json
rm -f /app/landing_zone/crawl_completed
echo "✅ Đã xóa dữ liệu cũ"

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
    echo "❌ DB API không khả dụng sau $MAX_RETRIES lần thử. Crawler sẽ dừng lại."
    exit 1
fi

echo "=== Bắt đầu quá trình crawl dữ liệu ==="
python dataCrawling.py

echo "=== Quá trình crawl đã hoàn tất ==="

# Đảm bảo thư mục landing_zone tồn tại
mkdir -p /app/landing_zone

# Tạo file flag để báo hiệu cho data_ingestion
echo "Tạo file flag crawl_completed tại /app/landing_zone/"
touch /app/landing_zone/crawl_completed
ls -la /app/landing_zone/

echo "=== Crawler Service đã hoàn thành nhiệm vụ ==="
# Giữ container chạy
tail -f /dev/null