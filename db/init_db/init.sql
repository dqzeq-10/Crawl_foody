-- Nếu database đã tồn tại, sử dụng nó
CREATE DATABASE db_crawl CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_crawl;

-- Xóa bảng nếu đã tồn tại
DROP TABLE IF EXISTS foody_branches;

-- Tạo bảng mới
CREATE TABLE foody_branches (
    Id INT(10) NOT NULL AUTO_INCREMENT,
    BranchName VARCHAR(255) NOT NULL DEFAULT '',
    AvgRating DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    Address VARCHAR(255) NOT NULL DEFAULT '',
    City VARCHAR(100) NOT NULL DEFAULT '',
    TotalReview INT(10) NOT NULL DEFAULT 0 CHECK (TotalReview BETWEEN 0 AND 10),
    TotalCheckins INT(10) NOT NULL DEFAULT 0,
    IsOpening BOOLEAN NOT NULL DEFAULT TRUE,
    HasDelivery BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (Id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


