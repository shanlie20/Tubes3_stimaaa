-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: ats_db
-- ------------------------------------------------------
-- Server version	8.0.42

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
INSERT INTO `applicantprofile` VALUES (1,'Imam','Hartati','1986-05-17','Jalan Sadang Serang No. 161, Binjai, Bengkulu 53304','+62 (0179) 835-5466'),(2,'Yusuf','Budiman','1988-02-06','Jalan Pelajar Pejuang No. 977, Sawahlunto, Jawa Timur 29569','0859222834'),(3,'Jati','Permata','1991-12-08','Jl. Kapten Muslihat No. 05, Banjar, PA 64697','+62 (510) 449 6980'),(4,'Tasdik','Pudjiastuti','1993-11-25','Jalan Rawamangun No. 626, Yogyakarta, JA 87304','+62-15-053-3728'),(5,'Prayoga','Utami','1976-12-24','Jl. Ahmad Yani No. 3, Sabang, PB 26254','+62 (44) 270-3736'),(6,'Ihsan','Susanti','1999-10-14','Gang Stasiun Wonokromo No. 0, Lubuklinggau, SG 52647','+62 (574) 509-5633'),(7,'Karman','Rahmawati','1992-10-21','Gg. K.H. Wahid Hasyim No. 6, Padang, JA 67311','+62 (0535) 282 8104'),(8,'Kartika','Firgantoro','1991-05-26','Jl. Jend. Sudirman No. 782, Langsa, DI Yogyakarta 02229','(0523) 797-0012'),(9,'Umi','Namaga','1987-07-08','Gg. Jakarta No. 771, Metro, Kalimantan Utara 33780','+62 (876) 969-3357'),(10,'Arsipatra','Situmorang','2000-05-12','Jl. Gedebage Selatan No. 89, Pematangsiantar, SS 61798','+62 (77) 333 8313'),(11,'Sidiq','Gunawan','1981-08-31','Gang Abdul Muis No. 655, Tasikmalaya, KS 13830','0860814691'),(12,'Viman','Yolanda','2007-03-04','Jalan Surapati No. 805, Madiun, Sulawesi Tenggara 56198','+62 (51) 131-2056');
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

-- Dump completed on 2025-06-14 14:27:54
