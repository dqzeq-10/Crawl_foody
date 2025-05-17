-- Sử dụng database đã được tạo tự động bởi Docker
USE db_crawl;

-- Chỉ tạo bảng nếu bảng chưa tồn tại
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

