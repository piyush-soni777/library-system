-- ╔══════════════════════════════════════════╗
-- ║   LIBRARY MANAGEMENT SYSTEM - DATABASE  ║
-- ║   Run this file FIRST in MySQL          ║
-- ╚══════════════════════════════════════════╝

CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- ── BOOKS TABLE ──
CREATE TABLE IF NOT EXISTS books (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    author      VARCHAR(150) NOT NULL,
    genre       VARCHAR(80),
    isbn        VARCHAR(20) UNIQUE,
    total_copies INT DEFAULT 1,
    available   INT DEFAULT 1,
    added_on    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── MEMBERS TABLE ── piyushSoni   
CREATE TABLE IF NOT EXISTS members (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    phone       VARCHAR(20),
    joined_on   DATETIME DEFAULT CURRENT_TIMESTAMP,
    active      TINYINT(1) DEFAULT 1
);
  -- piyushsoni
-- ── ISSUED BOOKS TABLE ── piyush SOni
CREATE TABLE IF NOT EXISTS issued_books (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    book_id     INT NOT NULL,
    member_id   INT NOT NULL,
    issue_date  DATE NOT NULL,
    due_date    DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    fine        DECIMAL(8,2) DEFAULT 0.00,
    status      ENUM('issued','returned','overdue') DEFAULT 'issued',
    FOREIGN KEY (book_id)   REFERENCES books(id),
    FOREIGN KEY (member_id) REFERENCES members(id)
);

-- ── SAMPLE BOOKS ── piyush Soni
INSERT INTO books (title, author, genre, isbn, total_copies, available) VALUES
('The Alchemist',           'Paulo Coelho',       'Fiction',     '9780061122415', 3, 3),
('Harry Potter & Stone',    'J.K. Rowling',        'Fantasy',     '9780439708180', 5, 5),
('Clean Code',              'Robert C. Martin',    'Technology',  '9780132350884', 2, 2),
('Atomic Habits',           'James Clear',         'Self-Help',   '9780735211292', 4, 4),
('To Kill a Mockingbird',   'Harper Lee',          'Classic',     '9780061935466', 3, 3),
('The Great Gatsby',        'F. Scott Fitzgerald', 'Classic',     '9780743273565', 2, 2),
('Python Crash Course',     'Eric Matthes',        'Technology',  '9781593276034', 3, 3),
('Wings of Fire',           'A.P.J. Abdul Kalam',  'Biography',   '9788123704456', 4, 4),
('Rich Dad Poor Dad',       'Robert Kiyosaki',     'Finance',     '9781612680194', 3, 3),
('The Immortals of Meluha', 'Amish Tripathi',      'Mythology',   '9789380658742', 2, 2);

-- ── SAMPLE MEMBERS ── piyushSoni
INSERT INTO members (name, email, phone) VALUES
('Aarav Sharma',  'aarav@email.com',  '9876543210'),
('Priya Patel',   'priya@email.com',  '9812345678'),
('Rahul Verma',   'rahul@email.com',  '9823456789'),
('Sneha Gupta',   'sneha@email.com',  '9834567890'),
('Karan Mehta',   'karan@email.com',  '9845678901');

SELECT 'Database setup complete!' AS Status;
