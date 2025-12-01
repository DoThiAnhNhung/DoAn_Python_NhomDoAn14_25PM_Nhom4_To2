create database QL_GiaoVien
on (
	name = QLNV_mdf,
	filename = 'D:\Đồ án Python\QL_GiaoVien.mdf',
	size = 10 MB,
	maxsize = 50 MB,
	filegrowth = 5 MB)
log on (
	name = QLNV_log,
	filename = 'D:\Đồ án Python\QL_GiaoVien_log.ldf',
	size = 10 MB,
	maxsize = 50 MB,
	filegrowth = 5 MB)	

use QL_GiaoVien


CREATE TABLE GiaoVien (
    MAGV VARCHAR(10) PRIMARY KEY,   -- Mã giáo viên
    HoLot NVARCHAR(50) NOT NULL,    -- Họ và tên lót
    Ten NVARCHAR(20) NOT NULL,      -- Tên
    NgaySinh DATE,                  -- Ngày sinh
    GioiTinh NVARCHAR(10),          -- Giới tính
    DiaChi NVARCHAR(200),           -- Địa chỉ
    SDT VARCHAR(15),                -- Số điện thoại
    Email VARCHAR(50),              -- Email
    TrinhDo NVARCHAR(50),           -- Trình độ (Cử nhân, Thạc sĩ, Tiến sĩ…)
    ChucVu NVARCHAR(50)             -- Chức vụ (Giáo viên, Tổ trưởng, Phó hiệu trưởng…)
);

-- Dữ liệu mẫu
INSERT INTO GiaoVien (MAGV, HoLot, Ten, NgaySinh, GioiTinh, DiaChi, SDT, Email, TrinhDo, ChucVu)
VALUES
('GV001', N'Nguyễn Văn', 'An', '1980-05-12', 'Nam', N'123 Lê Lợi, TPAG', '0912345678', 'an.nv@gmail.com', N'Thạc sĩ', N'Tổ trưởng'),
('GV002', N'Trần Thị', N'Bích', '1985-08-20', N'Nữ', N'456 Nguyễn Huệ, TPAG', '0987654321', 'bich.tt@gmail.com', N'Cử nhân', N'Giáo viên'),
('GV003', N'Lê Văn', N'Cường', '1990-02-15', 'Nam', N'789 Trần Phú, TPAG', '0911222333', 'cuong.lv@gmail.com', N'Cử nhân', N'Giáo viên');

CREATE TABLE GiangDay (
    ID INT IDENTITY(1,1) PRIMARY KEY,  -- ID tự tăng
    MAGV VARCHAR(10) NOT NULL,          -- Mã giáo viên (FK)
    MonHoc NVARCHAR(50) NOT NULL,       -- Môn giảng dạy
    LopPhuTrach NVARCHAR(20),           -- Lớp phụ trách / chủ nhiệm
    ToCongTac NVARCHAR(50),             -- Tổ công tác
    SoTietTuan INT,                      -- Số tiết dạy/tuần
    FOREIGN KEY (MAGV) REFERENCES GiaoVien(MAGV)
);

-- Dữ liệu mẫu
INSERT INTO GiangDay (MAGV, MonHoc, LopPhuTrach, ToCongTac, SoTietTuan)
VALUES
('GV001', N'Toán', '10A1', N'Toán - Tin', 18),
('GV001', N'Lý', '11A2', N'Khoa học Tự nhiên', 4),
('GV002', N'Văn', '10A2', N'Ngữ Văn', 20),
('GV002', 'Anh', '12A1', N'Ngoại ngữ', 6),
('GV003', N'Hóa', '11A3', N'Khoa học Tự nhiên', 22);

CREATE TABLE Luong (
    ID INT IDENTITY(1,1) PRIMARY KEY,   -- ID tự tăng
    MAGV VARCHAR(10) NOT NULL,          -- Mã giáo viên (FK)
    HeSoLuong DECIMAL(5,2),             -- Hệ số lương
    BacLuong INT,                        -- Bậc lương
    PhuCap DECIMAL(12,0),                -- Phụ cấp (trách nhiệm, thâm niên…)
    Thuong DECIMAL(12,0),                -- Thưởng, khen thưởng
    FOREIGN KEY (MAGV) REFERENCES GiaoVien(MAGV)
);
ALTER TABLE Luong
ADD CONSTRAINT UQ_GiaoVien_MAGV UNIQUE (MAGV);
-- Dữ liệu mẫu
INSERT INTO Luong (MAGV, HeSoLuong, BacLuong, PhuCap, Thuong)
VALUES
('GV001', 2.34, 4, 500000, 200000),
('GV002', 2.10, 3, 450000, 150000),
('GV003', 2.50, 5, 550000, 300000);


