CREATE DATABASE IF NOT EXISTS campus_book_trade
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE campus_book_trade;


CREATE TABLE user (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_no VARCHAR(20) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    credit_score INT NOT NULL DEFAULT 100,
    role VARCHAR(20) NOT NULL DEFAULT 'USER',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_credit_score CHECK (credit_score >= 0),
    CONSTRAINT chk_user_role CHECK (role IN ('USER', 'ADMIN')),
    CONSTRAINT chk_user_status CHECK (status IN ('ACTIVE', 'DISABLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE book_category (
    category_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    parent_id BIGINT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_category_parent
        FOREIGN KEY (parent_id) REFERENCES book_category(category_id),
    CONSTRAINT chk_category_status CHECK (status IN ('ACTIVE', 'DISABLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE book_condition (
    condition_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    condition_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE book (
    book_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    category_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    isbn VARCHAR(20) NULL,
    author VARCHAR(100) NOT NULL,
    publisher VARCHAR(100) NOT NULL,
    course_name VARCHAR(100) NULL,
    original_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    edition VARCHAR(50) NULL,
    publish_year INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_book_category
        FOREIGN KEY (category_id) REFERENCES book_category(category_id),
    CONSTRAINT chk_book_original_price CHECK (original_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE pickup_point (
    pickup_point_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20) NULL,
    open_time VARCHAR(100) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_pickup_point_status CHECK (status IN ('ACTIVE', 'DISABLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE listing (
    listing_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    seller_id BIGINT NOT NULL,
    book_id BIGINT NOT NULL,
    condition_id BIGINT NOT NULL,
    listing_type VARCHAR(20) NOT NULL DEFAULT 'SALE',
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 1,
    description VARCHAR(500) NULL,
    donation_note VARCHAR(255) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ON_SALE',
    published_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_listing_seller
        FOREIGN KEY (seller_id) REFERENCES user(user_id),
    CONSTRAINT fk_listing_book
        FOREIGN KEY (book_id) REFERENCES book(book_id),
    CONSTRAINT fk_listing_condition
        FOREIGN KEY (condition_id) REFERENCES book_condition(condition_id),
    CONSTRAINT chk_listing_type CHECK (listing_type IN ('SALE', 'DONATION')),
    CONSTRAINT chk_listing_price CHECK (
        (listing_type = 'SALE' AND price >= 0) OR
        (listing_type = 'DONATION' AND price = 0)
    ),
    CONSTRAINT chk_listing_stock CHECK (stock >= 0),
    CONSTRAINT chk_listing_status CHECK (status IN ('ON_SALE', 'LOCKED', 'SOLD', 'OFF_SHELF'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    listing_id BIGINT NOT NULL,
    buyer_id BIGINT NOT NULL,
    seller_id BIGINT NOT NULL,
    order_type VARCHAR(20) NOT NULL DEFAULT 'SALE',
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at DATETIME NULL,
    completed_at DATETIME NULL,
    cancelled_at DATETIME NULL,
    remark VARCHAR(255) NULL,
    CONSTRAINT fk_orders_listing
        FOREIGN KEY (listing_id) REFERENCES listing(listing_id),
    CONSTRAINT fk_orders_buyer
        FOREIGN KEY (buyer_id) REFERENCES user(user_id),
    CONSTRAINT fk_orders_seller
        FOREIGN KEY (seller_id) REFERENCES user(user_id),
    CONSTRAINT chk_order_type CHECK (order_type IN ('SALE', 'DONATION')),
    CONSTRAINT chk_orders_amount CHECK (
        (order_type = 'SALE' AND total_amount >= 0) OR
        (order_type = 'DONATION' AND total_amount = 0)
    ),
    CONSTRAINT chk_orders_status CHECK (status IN ('PENDING', 'LOCKED', 'PICKUP_PENDING', 'COMPLETED', 'CANCELLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE pickup_record (
    pickup_record_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL UNIQUE,
    pickup_point_id BIGINT NOT NULL,
    pickup_code VARCHAR(20) NOT NULL UNIQUE,
    scheduled_time DATETIME NULL,
    picked_time DATETIME NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'WAITING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pickup_record_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_pickup_record_point
        FOREIGN KEY (pickup_point_id) REFERENCES pickup_point(pickup_point_id),
    CONSTRAINT chk_pickup_record_status CHECK (status IN ('WAITING', 'FINISHED', 'EXPIRED', 'CANCELLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE review (
    review_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL UNIQUE,
    reviewer_id BIGINT NOT NULL,
    reviewee_id BIGINT NOT NULL,
    rating INT NOT NULL,
    content VARCHAR(500) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_review_reviewer
        FOREIGN KEY (reviewer_id) REFERENCES user(user_id),
    CONSTRAINT fk_review_reviewee
        FOREIGN KEY (reviewee_id) REFERENCES user(user_id),
    CONSTRAINT chk_review_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE audit_log (
    audit_log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NULL,
    operator_id BIGINT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_detail VARCHAR(500) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_log_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_audit_log_operator
        FOREIGN KEY (operator_id) REFERENCES user(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


