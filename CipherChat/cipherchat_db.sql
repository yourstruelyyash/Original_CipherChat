-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 27, 2024 at 11:41 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cipherchat_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `alembic_version`:
--

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('932566e91a7c');

-- --------------------------------------------------------

--
-- Table structure for table `message`
--

CREATE TABLE `message` (
  `id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `message`:
--   `sender_id`
--       `user` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(60) DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `date_of_birth` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- MEDIA TYPES FOR TABLE `user`:
--   `bio`
--       `Text_Plain`
--   `name`
--       `Text_Plain`
--

--
-- RELATIONSHIPS FOR TABLE `user`:
--

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `username`, `password`, `name`, `email`, `date_of_birth`) VALUES
(1, 'user1', 'user1', 'User 1', 'user1@mail.com', '0000-00-00'),
(2, 'tuser1', 'tuser1', 'test user1', 'tuser1@mail.com', '0000-00-00'),
(3, 'tuser2', 'tuser2', 'test user2', 'testuser2@mail.com', '0000-00-00'),
(4, 'tuser3', 'tuser3', 'Test user3', 'yourstruelyyash@gmail.com', '0000-00-00'),
(5, 'tuser4', 'tuser4', 'tuser4', 'tuser4@mail.com', '0000-00-00'),
(7, 'yourstruelyyash', 'scrypt:32768:8', 'Yashvardhan Mahesh Sharma', 'yashsharma7841@gmail.com', '0000-00-00'),
(8, 'vidhi', 'scrypt:32768:8', 'Vidhi Sharma', 'visha7841@gmail.com', '2005-12-20'),
(9, 'yash', 'scrypt:32768:8:1$3j5vO3r5T7EyUHW3$65c8f96783a56026fd53dc4e02', 'yash ', 'yash@mail.com', '2003-04-19'),
(10, 'omkar', 'scrypt:32768:8:1$zUlKMjUfqGMkCa6u$e26e663424ecdf575d13fd43b0', 'omkar sarswat', 'sarswatomkar009@gmail.com', '2005-02-24'),
(11, 'new', 'scrypt:32768:8:1$L3mMG9Zd2sO9dLqD$17a14ada03a995c87234f4b8d3', 'new', 'new@gmail.com', '2001-12-12'),
(12, 'new2', 'scrypt:32768:8:1$zmcoa2eaOVTmctTw$4739f5ec866aa56f2f658b0350', 'new2', 'new2@gmail.com', '2000-12-11'),
(13, 'new3', 'scrypt:32768:8:1$Svjsuhu43HPxbTf0$43c8691d412604b7d24ee8fa15', 'new3', 'new3@gmail.com', '2013-12-01'),
(14, 'new4', 'scrypt:32768:8:1$sAoDPvLUAhmXLR8F$b84c6f7be1aee97f755713142b', 'new4', 'new4@gmail.com', '2005-12-04'),
(15, 'check1', 'check1', 'check1', 'check1@gmail.com', '2001-01-01'),
(16, 'check2', 'check2', 'check2', 'check2@gmail.com', '2001-01-01'),
(17, 'check3', 'check3', 'check3', 'check3@gmail.com', '2001-01-01');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `message`
--
ALTER TABLE `message`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `message`
--
ALTER TABLE `message`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `message`
--
ALTER TABLE `message`
  ADD CONSTRAINT `message_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
