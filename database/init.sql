-- 基于SysML模型的文档自动生成系统 数据库初始化脚本
-- Database: sysmldocgen

CREATE DATABASE IF NOT EXISTS sysmldocgen DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sysmldocgen;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) DEFAULT '',
    email VARCHAR(100) DEFAULT '',
    role ENUM('admin', 'manager', 'member') DEFAULT 'member',
    status TINYINT DEFAULT 1 COMMENT '1-active, 0-disabled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 项目表
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 模型表
CREATE TABLE IF NOT EXISTS models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    name VARCHAR(128) NOT NULL,
    version_tag VARCHAR(32) DEFAULT 'v1.0',
    file_path VARCHAR(255) NOT NULL,
    file_size INT DEFAULT 0,
    file_type VARCHAR(32) DEFAULT '',
    uploader_id INT NOT NULL,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    parse_status ENUM('pending', 'parsing', 'success', 'failed') DEFAULT 'pending',
    parse_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (uploader_id) REFERENCES users(id),
    INDEX idx_project (project_id),
    INDEX idx_parse_status (parse_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 模型元素表
CREATE TABLE IF NOT EXISTS model_elements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    element_id VARCHAR(100) NOT NULL COMMENT 'XMI唯一标识',
    element_name VARCHAR(255) DEFAULT '',
    element_type VARCHAR(50) NOT NULL COMMENT 'Block/Requirement/Package...',
    parent_element_id VARCHAR(100) DEFAULT '' COMMENT '父元素ID（树形结构）',
    description TEXT,
    attributes JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    INDEX idx_model (model_id),
    UNIQUE KEY uk_model_element (model_id, element_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 模型关系表
CREATE TABLE IF NOT EXISTS model_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    source_element_id VARCHAR(100) NOT NULL,
    target_element_id VARCHAR(100) NOT NULL,
    relationship_type VARCHAR(50) DEFAULT '',
    relationship_name VARCHAR(255) DEFAULT '',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    INDEX idx_model (model_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 模板表
CREATE TABLE IF NOT EXISTS templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    template_type VARCHAR(50) NOT NULL COMMENT '需求文档/设计文档/测试文档...',
    content TEXT COMMENT '模板正文（含Jinja2占位符）',
    file_path VARCHAR(255) DEFAULT '',
    status ENUM('active', 'inactive') DEFAULT 'active',
    creator_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 文档表
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    model_id INT NOT NULL,
    template_id INT NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    content LONGTEXT COMMENT '文档HTML内容',
    file_path VARCHAR(255) DEFAULT '' COMMENT '导出文件路径',
    export_format VARCHAR(20) DEFAULT 'docx',
    status ENUM('generating', 'success', 'failed') DEFAULT 'generating',
    generate_message TEXT,
    operator_id INT NOT NULL,
    generate_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (model_id) REFERENCES models(id),
    FOREIGN KEY (template_id) REFERENCES templates(id),
    FOREIGN KEY (operator_id) REFERENCES users(id),
    INDEX idx_project (project_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 日志表
CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_type ENUM('login', 'operation', 'error', 'system') NOT NULL,
    operator_id INT DEFAULT NULL,
    module_name VARCHAR(64) DEFAULT '',
    operation_content TEXT,
    result_status ENUM('success', 'failed', 'warning') DEFAULT 'success',
    ip_address VARCHAR(45) DEFAULT '',
    record_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES users(id),
    INDEX idx_type (log_type),
    INDEX idx_record_time (record_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入默认管理员账号（密码: admin123）
INSERT IGNORE INTO users (username, password_hash, full_name, role, status) VALUES
('admin', '$2b$12$xP15bWzwOfJ03Q2GsA3.Q.PafPEcR6FtZ/JTLSpgO.tfbQaT/agO6', 'Administrator', 'admin', 1);
