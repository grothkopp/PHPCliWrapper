CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;

DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(255), 
    email VARCHAR(255), 
    status VARCHAR(50)
);
INSERT INTO users (name, email, status) VALUES ('Test User', 'test@example.com', 'active');
INSERT INTO users (name, email, status) VALUES ('Another User', 'another@example.com', 'inactive');
INSERT INTO users (name, email, status) VALUES ('Third User', 'third@example.com', 'active');

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);
INSERT INTO products (product_name, category, price) VALUES ('Laptop', 'Electronics', 1200.00);
INSERT INTO products (product_name, category, price) VALUES ('Desk Chair', 'Furniture', 150.00);

