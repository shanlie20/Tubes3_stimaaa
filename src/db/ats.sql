-- MySQL dump 10.13  Distrib 9.3.0, for Win64 (x86_64)
--
-- Host: localhost    Database: ats_db
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `applicantprofile`
--

DROP TABLE IF EXISTS `applicantprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `applicantprofile` (
  `applicant_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone_number` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`applicant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `applicantprofile`
--

LOCK TABLES `applicantprofile` WRITE;
/*!40000 ALTER TABLE `applicantprofile` DISABLE KEYS */;
INSERT INTO `applicantprofile` VALUES (1,'Edi','Hassanah','1991-10-12','Gang Sadang Serang No. 481, Singkawang, DKI Jakarta 56221','+62 (65) 563 4750'),(2,'Kasim','Mulyani','1986-06-12','Gg. M.H Thamrin No. 962, Langsa, Banten 55661','+62-311-907-9642'),(3,'Darimin','Nababan','1998-05-27','Jl. Cempaka No. 871, Sabang, SG 95605','+62 (0263) 918 8712'),(4,'Elon','Manullang','1988-03-23','Jl. Gedebage Selatan No. 0, Palopo, Kepulauan Bangka Belitung 66664','(0752) 650 4528'),(5,'Melinda','Maheswara','2003-08-20','Gg. HOS. Cokroaminoto No. 983, Subulussalam, JT 76891','+62 (631) 786-0787'),(6,'Galih','Marpaung','1999-01-23','Jl. PHH. Mustofa No. 32, Padangpanjang, Sulawesi Tenggara 29934','+62 (053) 249 4619'),(7,'Kani','Suryatmi','2004-06-23','Jalan Astana Anyar No. 11, Surakarta, YO 24369','(0504) 375-8810'),(8,'Luluh','Hakim','1990-12-09','Gang Pelajar Pejuang No. 7, Padang Sidempuan, Kalimantan Utara 43333','+62 (0726) 128 5481'),(9,'Hilda','Hidayat','1990-05-11','Gg. R.E Martadinata No. 1, Batu, KU 99416','+62 (0303) 823-8158'),(10,'Pangestu','Adriansyah','1977-04-15','Gang Erlangga No. 751, Sabang, Jambi 59138','+62 (990) 403 1981'),(11,'Farhunnisa','Sitorus','2001-01-03','Gg. Cikutra Timur No. 0, Tomohon, SG 19649','(076) 969-1737'),(12,'Rama','Hasanah','1990-11-20','Jalan Otto Iskandardinata No. 740, Surakarta, Bengkulu 89303','+62-923-525-3154');
/*!40000 ALTER TABLE `applicantprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `applicationdetail`
--

DROP TABLE IF EXISTS `applicationdetail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `applicationdetail` (
  `detail_id` int NOT NULL AUTO_INCREMENT,
  `applicant_id` int NOT NULL,
  `application_role` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cv_path` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`detail_id`),
  KEY `applicant_id` (`applicant_id`),
  CONSTRAINT `applicationdetail_ibfk_1` FOREIGN KEY (`applicant_id`) REFERENCES `applicantprofile` (`applicant_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `applicationdetail`
--

LOCK TABLES `applicationdetail` WRITE;
/*!40000 ALTER TABLE `applicationdetail` DISABLE KEYS */;
INSERT INTO `applicationdetail` VALUES (1,1,'ACCOUNTANT','10001727.pdf'),(2,2,'ACCOUNTANT','10005171.pdf'),(3,3,'ACCOUNTANT','10030015.pdf'),(4,4,'ACCOUNTANT','10041713.pdf'),(5,5,'ACCOUNTANT','10062724.pdf'),(6,6,'ACCOUNTANT','10070224.pdf'),(7,7,'ACCOUNTANT','10076271.pdf'),(8,8,'ACCOUNTANT','10089434.pdf'),(9,9,'ACCOUNTANT','10100240.pdf'),(10,10,'ACCOUNTANT','10138632.pdf'),(11,11,'ACCOUNTANT','10149490.pdf'),(12,12,'ACCOUNTANT','3547447.pdf');
/*!40000 ALTER TABLE `applicationdetail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'ats_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-14 17:45:00
