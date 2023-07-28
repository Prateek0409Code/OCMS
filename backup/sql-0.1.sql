-- phpMyAdmin SQL Dump
-- version 4.7.1
-- https://www.phpmyadmin.net/
--
-- Host: sql6.freesqldatabase.com
-- Generation Time: Mar 05, 2022 at 10:00 AM
-- Server version: 5.5.62-0ubuntu0.14.04.1
-- PHP Version: 7.0.33-0ubuntu0.16.04.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sql6473966`
--

-- --------------------------------------------------------

--
-- Table structure for table `classes`
--

CREATE TABLE `classes` (
  `class_name` varchar(20) NOT NULL,
  `class_id` varchar(30) NOT NULL,
  `date_from` varchar(20) NOT NULL,
  `date_to` varchar(20) NOT NULL,
  `email` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `login`
--

CREATE TABLE `login` (
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `login`
--

INSERT INTO `login` (`name`, `email`, `password`) VALUES
('Admin', 'admin@admin.com', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `register`
--

CREATE TABLE `register` (
  `classid` varchar(30) NOT NULL,
  `name` varchar(20) NOT NULL,
  `email` varchar(30) NOT NULL,
  `regid` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

CREATE TABLE `sessions` (
  `sessionID` varchar(40) NOT NULL,
  `totalstudents` int(100) NOT NULL,
  `starttime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `endtime` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
