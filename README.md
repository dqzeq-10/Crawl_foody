# Dự án Foody Crawler

## Giới thiệu
Dự án này là một hệ thống crawl dữ liệu từ website Foody.vn, bao gồm các thông tin về địa điểm đồ uống, đánh giá và bình luận của người dùng.

## Cấu trúc dự án

```
.
├── api_gateway/                 # API Gateway service
│   ├── Dockerfile
│   ├── health_check.sh         # Health check script
│   ├── nginx.conf              # Nginx configuration
│   └── html/
│       ├── index.html          # API documentation page
│       └── scheduler.html      # Crawler scheduler interface
│
├── crawler/                    # Web Crawler service
│   ├── Dockerfile
│   ├── crawler_api.py         # Crawler API endpoints
│   ├── dataCrawling.py        # Main crawling logic
│   ├── requirements.txt       # Python dependencies
│   └── start.sh              # Service startup script
│
├── data_ingestion/            # Data Processing service
│   ├── Dockerfile
│   ├── data_ingestion_api.py  # Data ingestion API
│   ├── dataIngestion.py       # Data processing logic
│   ├── requirements.txt       # Python dependencies
│   ├── start.sh              # Service startup script
│   ├── entrypoint.sh         # Docker entrypoint script
│   └── health_check.sh       # Health check script
│
├── db/                        # Database service
│   ├── Dockerfile
│   ├── init_db/              # Database initialization scripts
│   │   └── init.sql
│   └── mysql_data/          # MySQL data directory
│       ├── db_crawl/        # Application database
│       ├── mysql/           # MySQL system database
│       ├── performance_schema/
│       └── sys/
│
├── db_api/                    # Database API service
│   ├── Dockerfile
│   ├── db_api.py             # Database API endpoints
│   ├── health_check.py       # Health check script
│   └── requirements.txt      # Python dependencies
│
├── landing_zone/             # Shared data storage
│
├── web_page/                 # Frontend web application
│   ├── Dockerfile
│   ├── server.js            # Node.js server
│   ├── package.json         # Node.js dependencies
│   ├── start.sh            # Service startup script
│   └── public/
│       ├── foody.html      # Main webpage
│       ├── script.js       # Frontend JavaScript
│       ├── style.css       # Main styles
│       ├── dynamic-items.css
│       ├── loading-styles.css
│       ├── pagination-styles.css
│       ├── search-suggestions.css
│       └── images/         # Image assets directory
│
└── docker-compose.yml        # Docker compose configuration

```

## Các Thành Phần Dịch Vụ

### 1. API Gateway
- API Gateway dựa trên Nginx
- Định tuyến yêu cầu đến các dịch vụ thích hợp

### 2. Dịch Vụ Crawler
- Crawler thu thập dữ liệu từ Foody
- Triển khai crawler dựa trên Python
- API RESTful để điều khiển crawler

### 3. Dịch Vụ Xử Lý Dữ Liệu
- Xử lý và xác thực dữ liệu đã thu thập
- Xử lý chuyển đổi dữ liệu
- Quản lý luồng dữ liệu đến cơ sở dữ liệu

### 4. Dịch Vụ Cơ Sở Dữ Liệu
- Cơ sở dữ liệu MySQL
- Lưu trữ dữ liệu có cấu trúc
- Duy trì tính bền vững của dữ liệu

### 5. Dịch Vụ API Cơ Sở Dữ Liệu
- API RESTful cho các thao tác cơ sở dữ liệu
- Xử lý truy vấn và cập nhật dữ liệu
- Cung cấp lớp truy cập dữ liệu

### 6. Giao Diện Web
- Hiển thị dữ liệu tương tác
- Khả năng tìm kiếm và lọc

## Công nghệ sử dụng

- **Frontend**: 
  - HTML, CSS, JavaScript
  - Node.js (Express)
  - Bootstrap cho giao diện

- **Backend**: 
  - Python (FastAPI)
  - Nginx làm API Gateway

- **Database**: 
  - MySQL 8.0
  - Volume cho persistent data

- **Công cụ & Container**: 
  - Docker
  - Docker Compose
  - Shell scripts

- **Kiến trúc**: 
  - Microservices
  - RESTful APIs

## Hướng dẫn Cài đặt và Chạy

### Yêu cầu hệ thống
- Docker Engine: phiên bản 24.0.0 trở lên
- Docker Compose: phiên bản 2.17.0 trở lên
- Git (tùy chọn)
- Port trống: 8080, 3000, 3306, 8000-8002

### Các bước cài đặt

1. Lấy source code và vào thư mục dự án:
```bash
git clone <repository_url>
cd Crawl_foody
```

2. Khởi động hệ thống:
```bash
docker-compose up -d
```

4. Kiểm tra trạng thái các service:
```bash
docker-compose ps
```

### Thông tin Port và Endpoint

1. **Web Frontend** (NodeJS + Express)
   - Port: 3000
   - URL: http://localhost:3000
   - File chính: `/web_page/public/index.html`
   - Tính năng:
     - Tìm kiếm nhà hàng
     - Lọc theo đánh giá
     - Phân trang kết quả

2. **API Gateway** (Nginx)
   - Port: 8080:8080
   - URL: http://localhost:8080
   - Endpoints:
     - `/`: Web Frontend
     - `/api/crawler/`: Crawler Service
     - `/api/ingestion/`: Data Ingestion Service
     - `/api/db/`: Database API
     - `/scheduler`: Giao diện quản lý crawler
     - `/web`: Giao diện trang chủ tìm kiếm

3. **Crawler Service** (FastAPI)
   - Port: 8001:8000
   - Endpoints:
     - GET /status
     - POST /crawl
     - POST /reset
     - GET /schedule
     - POST /schedule
     - PUT /schedule/{name}
     - DELETE /schedule/{name}
     - POST /schedule/{name}/toggle


4. **Data Ingestion Service**
   - Port: 8002:8000
   - Endpoints:
     - GET /status
     - POST /process
     - POST /reset
     - GET /preview
     - GET /db/check

5. **Database API Service**
   - Port: 8000:8000 
   - Endpoints:
     - GET /branches
     - GET /branch/{branch_id}
     - PUT /branch/{branch_id}
     - DELETE /branch/{branch_id}
     - POST /branch/
     - GET /branch/search

6. **MySQL Database**
   - Port: 3307:3306
   - Host: localhost
   - Database: db_crawl
   - Schema:
     ```sql
     CREATE TABLE IF NOT EXISTS foody_branches (
         Id INT(10) NOT NULL AUTO_INCREMENT,
         BranchName VARCHAR(255) NOT NULL DEFAULT '',
         AvgRating DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (AvgRating BETWEEN 0 AND 10),
         Address VARCHAR(255) NOT NULL DEFAULT '',
         City VARCHAR(100) NOT NULL DEFAULT '',
         TotalReview INT(10) NOT NULL DEFAULT 0,
         TotalCheckins INT(10) NOT NULL DEFAULT 0,
         IsOpening BOOLEAN NOT NULL DEFAULT TRUE,
         HasDelivery BOOLEAN NOT NULL DEFAULT FALSE,
         PRIMARY KEY (Id)
     ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```

### Hướng dẫn Sử dụng Chi tiết

1. Khởi động hệ thống:
```bash
docker-compose up -d
```

2. Kiểm tra các service đã hoạt động:
```bash
docker-compose ps
```
Đảm bảo tất cả các service đều ở trạng thái "Up"

3. Truy cập giao diện web:
   - URL: http://localhost:3000
   - Các tính năng:
     - Tìm kiếm nhà hàng theo tên
     - Lọc theo thành phố
     - Sắp xếp theo đánh giá

4. Quản lý crawler (http://localhost:8080/scheduler):
   - Lập lịch crawl tự động:
     - Cấu hình theo cron expression
     - Theo dõi trạng thái crawl
     - Xem lịch sử crawl

3. Xem logs:
```bash
docker-compose logs -f [tên_service]
```

### Xử lý sự cố

1. Kiểm tra logs của service gặp vấn đề:
```bash
docker-compose logs [tên_service]
```

2. Khởi động lại service:
```bash
docker-compose restart [tên_service]
```

3. Khởi động lại toàn bộ hệ thống:
```bash
docker-compose down
docker-compose up -d
```

## Quan hệ giữa các Service

- Web Frontend → API Gateway
- API Gateway → All Services
- Crawler → Data Ingestion
- Data Ingestion → Database API
- Database API → Database


# Nhóm [Nicetry]