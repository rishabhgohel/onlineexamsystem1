-- Active: 1744625794689@@127.0.0.1@3306@onlineexam
-- version 5.2.1
-- Host: 127.0.0.1


SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- Create the database

USE onlineexam;

CREATE TABLE IF NOT EXISTS questions (
    QuestionID INT AUTO_INCREMENT PRIMARY KEY,
    Question TEXT NOT NULL,
    QuestionType ENUM('MCQ', 'TF', 'DESC') NOT NULL,
    Option1 VARCHAR(255),
    Option2 VARCHAR(255),
    Option3 VARCHAR(255),
    Option4 VARCHAR(255),
    CorrectAnswer TEXT NOT NULL
);

ALTER TABLE questions MODIFY COLUMN CorrectAnswer VARCHAR(255);


ALTER TABLE questions ADD COLUMN Questiontype ENUM ('MCQ', 'TF', 'DESC') NOT NULL AFTER Question;

SELECT * FROM questions;

DESCRIBE questions;

-- Create the students table
CREATE TABLE IF NOT EXISTS students (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(100) NOT NULL,
    Role ENUM('STUDENT', 'ADMIN') NOT NULL
);

-- Insert sample data into students table
INSERT INTO students (Name, Email, Password, Role) VALUES
('rishabh', 'rishabh77@gmail.com', 'password123', 'ADMIN'),
('sachin kumar', 'sachin1@gmail.com', 'password123', 'STUDENT'),
('janavi khatri', 'khatri@example.com', 'studentpass', 'STUDENT');

SELECT * FROM students;

DESCRIBE students;

SELECT * FROM students WHERE Role = 'ADMIN';

CREATE TABLE IF NOT EXISTS exams (
    ExamID INT AUTO_INCREMENT PRIMARY KEY,
    SubjectID INT UNSIGNED NOT NULL,
    FOREIGN KEY (SubjectID) REFERENCES subjects(SubjectID) ON DELETE CASCADE ON UPDATE CASCADE
);

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

