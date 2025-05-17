#!/bin/bash

# Script này sẽ được thực thi bởi data-ingestion service
# Thêm vào một cơ chế fallback để đảm bảo db-api có thể được truy cập

# Xóa file clean_data.json nếu đã tồn tại
if [ -f "/app/landing_zone/clean_data.json" ]; then
    echo "Xóa file clean_data.json cũ từ entrypoint..."
    rm -f /app/landing_zone/clean_data.json
    echo "✅ Đã xóa file clean_data.json cũ"
fi

# Thêm db-api vào /etc/hosts để đảm bảo nó luôn có thể phân giải được
echo "Looking up db-api IP address..."
getent hosts db-api

if [ $? -ne 0 ]; then
    echo "db-api not found in DNS. Will try ping to find IP..."
    # Thử ping để tìm IP
    ping -c 1 db-api
    
    if [ $? -ne 0 ]; then
        echo "Cannot ping db-api. Using network scan..."
        
        # Nếu ping không hoạt động, thử quét mạng để tìm IP
        apt-get update && apt-get install -y iputils-ping dnsutils net-tools iproute2
        
        # Tìm gateway
        GATEWAY=$(ip route | grep default | awk '{print $3}')
        echo "Gateway: $GATEWAY"
        
        # Tìm mạng
        NETWORK=$(ip -o -f inet addr show | awk '/scope global/ {print $4}' | head -1)
        echo "Network: $NETWORK"
        
        # Thêm db-api vào /etc/hosts với địa chỉ gateway
        echo "$GATEWAY db-api" >> /etc/hosts
        echo "Added $GATEWAY db-api to /etc/hosts"
    fi
else
    echo "db-api found in DNS lookup."
fi

# Hiển thị mạng để debug
echo "Network configuration:"
ip a
echo "--------------------"
cat /etc/hosts
echo "--------------------"
echo "DNS servers:"
cat /etc/resolv.conf
echo "--------------------"
echo "Routes:"
ip route
echo "--------------------"

# Tiếp tục với script chính
./start.sh
