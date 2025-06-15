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
-- Table structure for table `applicant_profiles`
--

DROP TABLE IF EXISTS `applicant_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `applicant_profiles` (
  `applicant_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`applicant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `applicant_profiles`
--

LOCK TABLES `applicant_profiles` WRITE;
/*!40000 ALTER TABLE `applicant_profiles` DISABLE KEYS */;
INSERT INTO `applicant_profiles` VALUES (1,'Usyi','Sihombing','1975-08-24','Jl. Stasiun Wonokromo No. 1, Cimahi, MA 17297','+62-133-578-0842'),(2,'Amalia','Hakim','1979-02-08','Jl. Tebet Barat Dalam No. 988, Pekanbaru, Sumatera Barat 54691','+62-76-541-2121'),(3,'Elisa','Purnawati','1981-12-23','Jalan Rajawali Timur No. 46, Palembang, Nusa Tenggara Timur 73158','+62-0844-454-6675'),(4,'Lega','Ramadan','2002-02-22','Gang Wonoayu No. 4, Surabaya, Nusa Tenggara Barat 91709','+62 (263) 159-3792'),(5,'Cakrawala','Simanjuntak','2007-03-21','Jalan Otto Iskandardinata No. 15, Kota Administrasi Jakarta Barat, SU 90341','+62-0310-430-6318'),(6,'Prakosa','Anggraini','1977-10-02','Gg. Rungkut Industri No. 97, Payakumbuh, ST 49419','+62-48-803-3671'),(7,'Olga','Mahendra','1998-08-10','Gang Rungkut Industri No. 16, Palu, Aceh 34060','+62 (444) 753 4368'),(8,'Tiara','Mandasari','1985-11-03','Gang Gegerkalong Hilir No. 354, Bandar Lampung, Sulawesi Tenggara 90316','+62 (78) 589-0901'),(9,'Mahmud','Firgantoro','1984-06-02','Gg. Gegerkalong Hilir No. 4, Kediri, Aceh 78770','(020) 701-9354'),(10,'Zelda','Andriani','2006-03-30','Gg. Ir. H. Djuanda No. 57, Jambi, RI 33283','(063) 420-2687'),(11,'Devi','Uyainah','1987-05-02','Jalan Laswi No. 7, Tanjungpinang, Sumatera Utara 70010','(001) 378-6950'),(12,'Cemplunk','Pratiwi','1986-10-26','Gg. Cempaka No. 85, Bandar Lampung, Jawa Barat 54203','+62-080-584-7047');
/*!40000 ALTER TABLE `applicant_profiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `application_details`
--

DROP TABLE IF EXISTS `application_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `application_details` (
  `application_id` int NOT NULL AUTO_INCREMENT,
  `applicant_id` int NOT NULL,
  `application_role` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cv_path` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cv_content` text COLLATE utf8mb4_unicode_ci,
  `extracted_skills_str` text COLLATE utf8mb4_unicode_ci,
  `extracted_job_history_str` text COLLATE utf8mb4_unicode_ci,
  `extracted_education_str` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`application_id`),
  UNIQUE KEY `applicant_id` (`applicant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application_details`
--

LOCK TABLES `application_details` WRITE;
/*!40000 ALTER TABLE `application_details` DISABLE KEYS */;
INSERT INTO `application_details` VALUES (1,1,'ACCOUNTANT','10001727.pdf',NULL,NULL,NULL,NULL),(2,2,'ACCOUNTANT','10005171.pdf',NULL,NULL,NULL,NULL),(3,3,'ACCOUNTANT','10030015.pdf',NULL,NULL,NULL,NULL),(4,4,'ACCOUNTANT','10041713.pdf',NULL,NULL,NULL,NULL),(5,5,'ACCOUNTANT','10062724.pdf',NULL,NULL,NULL,NULL),(6,6,'ACCOUNTANT','10070224.pdf',NULL,NULL,NULL,NULL),(7,7,'ACCOUNTANT','10076271.pdf',NULL,NULL,NULL,NULL),(8,8,'ACCOUNTANT','10089434.pdf',NULL,NULL,NULL,NULL),(9,9,'ACCOUNTANT','10100240.pdf',NULL,NULL,NULL,NULL),(10,10,'ACCOUNTANT','10138632.pdf',NULL,NULL,NULL,NULL),(11,11,'ACCOUNTANT','10149490.pdf',NULL,NULL,NULL,NULL),(12,12,'ACCOUNTANT','3547447.pdf',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `application_details` ENABLE KEYS */;
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

-- Dump completed on 2025-06-15 12:17:48
