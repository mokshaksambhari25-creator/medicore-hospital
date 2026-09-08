Warning: A partial dump from a server that has GTIDs will by default include the GTIDs of all transactions, even those that changed suppressed parts of the database. If you don't want to restore GTIDs, pass --set-gtid-purged=OFF. To make a complete dump, pass --all-databases --triggers --routines --events. 
Warning: A dump from a server that has GTIDs enabled will by default include the GTIDs of all transactions, even those that were executed during its extraction and might not be represented in the dumped data. This might result in an inconsistent data dump. 
In order to ensure a consistent backup of the database, pass --single-transaction or --lock-all-tables or --source-data. 

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;
SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '9d9f5900-a837-11f1-991d-53eba1661a4f:1-102';
mysqldump: Error: 'SELECT command denied to user 'medicore'@'localhost' for table 'column_masking_policy'' when trying to dump masking policies
mysqldump: Error: 'Access denied; you need (at least one of) the PROCESS privilege(s) for this operation' when trying to dump tablespaces

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `medicore` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `medicore`;
DROP TABLE IF EXISTS `alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alerts` (
  `pos` int NOT NULL,
  `id` varchar(64) NOT NULL,
  `to` varchar(120) DEFAULT NULL,
  `template` varchar(120) DEFAULT NULL,
  `time` varchar(16) DEFAULT NULL,
  `date` varchar(16) DEFAULT NULL,
  `status` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `alerts` WRITE;
/*!40000 ALTER TABLE `alerts` DISABLE KEYS */;
INSERT INTO `alerts` VALUES (5,'AL-1','+91 98200 11223','Appointment Reminder','08:10','2026-08-27','Delivered'),(4,'AL-1787829531577','Nikhil Patil','Payment receipt','16:48','2026-08-27','Queued'),(3,'AL-1787829608440','','Report Ready','16:50','2026-08-27','Queued'),(2,'AL-1787829615791','IMRAN','Scan slot booked','16:50','2026-08-27','Queued'),(1,'AL-1787829624009','','Report Ready','16:50','2026-08-27','Delivered'),(0,'AL-1788483847534','+91 99870 22114','Payment receipt','12:04','2026-09-04','Queued'),(6,'AL-2','+91 98330 45671','Scan Slot Changed','08:42','2026-08-27','Delivered'),(7,'AL-3','+91 90045 77812','Payment Due','09:05','2026-08-27','Failed'),(8,'AL-4','+91 99870 22114','Report Ready','09:31','2026-08-27','Queued');
/*!40000 ALTER TABLE `alerts` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `appointments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointments` (
  `pos` int NOT NULL,
  `id` varchar(32) NOT NULL,
  `patient` varchar(120) DEFAULT NULL,
  `patientId` varchar(32) DEFAULT NULL,
  `phone` varchar(40) DEFAULT NULL,
  `doctorId` varchar(32) DEFAULT NULL,
  `department` varchar(80) DEFAULT NULL,
  `date` varchar(16) DEFAULT NULL,
  `time` varchar(24) DEFAULT NULL,
  `status` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `appointments` WRITE;
/*!40000 ALTER TABLE `appointments` DISABLE KEYS */;
INSERT INTO `appointments` VALUES (0,'AP-5512','Aarav Sharma','P-4821','+91 98200 11223','DOC-1001','Cardiology','2026-08-27','09:30 AM','Checked-in'),(1,'AP-5513','Fatima Khan','P-6402','+91 98111 33445','DOC-1002','Maternity','2026-08-27','10:15 AM','Checked-in'),(2,'AP-5514','Nikhil Patil','P-7718','+91 90045 77812','DOC-1003','Orthopaedics','2026-08-27','11:00 AM','Pending'),(3,'AP-5515','Sneha Patil','P-2196','+91 99870 22114','DOC-1004','Neurology','2026-08-27','12:30 PM','Confirmed'),(4,'AP-5516','Kabir Reddy','P-5580','+91 98765 43210','DOC-1005','Paediatrics','2026-08-27','02:00 PM','Cancelled');
/*!40000 ALTER TABLE `appointments` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `diagnostics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnostics` (
  `pos` int NOT NULL,
  `id` varchar(32) NOT NULL,
  `patient` varchar(120) DEFAULT NULL,
  `patientId` varchar(32) DEFAULT NULL,
  `test` varchar(80) DEFAULT NULL,
  `slot` varchar(24) DEFAULT NULL,
  `date` varchar(16) DEFAULT NULL,
  `status` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `diagnostics` WRITE;
/*!40000 ALTER TABLE `diagnostics` DISABLE KEYS */;
INSERT INTO `diagnostics` VALUES (1,'DX-2201','Aarav Sharma','P-4821','ECG','09:00 AM','2026-08-27','Done'),(2,'DX-2202','Ritu Verma','P-3304','CT Chest','11:30 AM','2026-08-27','Done'),(3,'DX-2203','Sneha Patil','P-2196','MRI Brain','02:00 PM','2026-08-27','Scheduled'),(4,'DX-2204','Nikhil Patil','P-7718','X-Ray Knee','04:00 PM','2026-08-27','Done'),(0,'DX-2205','IMRAN','P-9267','X-Ray','09:00 AM','2026-08-27','Done');
/*!40000 ALTER TABLE `diagnostics` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `doctors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctors` (
  `pos` int NOT NULL,
  `id` varchar(32) NOT NULL,
  `name` varchar(120) DEFAULT NULL,
  `department` varchar(80) DEFAULT NULL,
  `phone` varchar(40) DEFAULT NULL,
  `available` tinyint(1) NOT NULL DEFAULT '1',
  `login` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `doctors` WRITE;
/*!40000 ALTER TABLE `doctors` DISABLE KEYS */;
INSERT INTO `doctors` VALUES (0,'DOC-1001','Dr. Meera Nair','Cardiology','+91 98200 11001',1,1),(1,'DOC-1002','Dr. Rohan Das','General Medicine','+91 98200 11002',1,1),(2,'DOC-1004','Dr. Imran Sheikh','Neurology','+91 98200 11004',1,1),(3,'DOC-1005','Dr. Ananya Bose','Paediatrics','+91 98200 11005',1,1),(4,'DOC-1006','Dr. Arjun Menon','Oncology','+91 98200 11006',1,1),(5,'DOC-1007','Dr. IMRAN 24','Neurology','6969696969',1,1);
/*!40000 ALTER TABLE `doctors` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `pos` int NOT NULL,
  `id` varchar(32) NOT NULL,
  `patient` varchar(120) DEFAULT NULL,
  `patientId` varchar(32) DEFAULT NULL,
  `department` varchar(80) DEFAULT NULL,
  `amount` decimal(12,2) DEFAULT NULL,
  `method` varchar(40) DEFAULT NULL,
  `date` varchar(16) DEFAULT NULL,
  `status` varchar(40) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
INSERT INTO `invoices` VALUES (2,'INV-77120','Aarav Sharma','P-4821','Cardiology',42300.00,'UPI','2026-08-16','Paid',''),(3,'INV-77121','Ritu Verma','P-3304','Oncology',186500.00,'Insurance','2026-08-27','Processing','Claim #ONC-441'),(4,'INV-77122','Nikhil Patil','P-7718','Orthopaedics',78900.00,'Card','2026-08-15','Paid',''),(5,'INV-77123','Sneha Patil','P-2196','Neurology',22150.00,'Cash','2026-08-15','Due',''),(6,'INV-77124','Fatima Khan','P-6402','Maternity',56000.00,'Insurance','2026-08-14','Paid',''),(1,'INV-77125','Nikhil Patil','P-7718','General',2.00,'UPI','2026-08-27','Paid','Quick payment'),(0,'INV-77126','Nikhil Patil','P-7718','Orthopaedics',2.00,'UPI','2026-08-27','Paid','POOJA');
/*!40000 ALTER TABLE `invoices` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patients` (
  `pos` int NOT NULL,
  `id` varchar(32) NOT NULL,
  `name` varchar(120) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `phone` varchar(40) DEFAULT NULL,
  `blood` varchar(16) DEFAULT NULL,
  `department` varchar(80) DEFAULT NULL,
  `doctorId` varchar(32) DEFAULT NULL,
  `status` varchar(40) DEFAULT NULL,
  `ward` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
INSERT INTO `patients` VALUES (4,'P-2196','Sneha Patil',29,'Female','+91 99870 22114','AB+','Neurology','DOC-1004','Observation',''),(2,'P-3304','Ritu Verma',51,'Female','+91 98330 45671','O+','Oncology','DOC-1006','Admitted','ICU-01'),(1,'P-4821','Aarav Sharma',30,'Male','+91 98200 11223','B+','Cardiology','DOC-1001','Admitted','PR-210'),(6,'P-5580','Kabir Reddy',8,'Male','+91 98765 43210','O+','Paediatrics','DOC-1005','Admitted',''),(5,'P-6402','Fatima Khan',31,'Female','+91 98111 33445','B+','Maternity','DOC-1002','Admitted','MT-305'),(3,'P-7718','Nikhil Patil',36,'Male','+91 90045 77812','A+','Orthopaedics','DOC-1003','Discharged',''),(0,'P-9267','IMRAN',24,'Male','696969669','C+','General Medicine','DOC-1004','Admitted','');
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `pharmacy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pharmacy` (
  `pos` int NOT NULL,
  `id` varchar(32) NOT NULL,
  `name` varchar(120) DEFAULT NULL,
  `batch` varchar(40) DEFAULT NULL,
  `stock` int DEFAULT NULL,
  `min` int DEFAULT NULL,
  `unit` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `pharmacy` WRITE;
/*!40000 ALTER TABLE `pharmacy` DISABLE KEYS */;
INSERT INTO `pharmacy` VALUES (0,'RX-01','Paracetamol 500mg','B-8821',420,80,'strip'),(1,'RX-02','Amoxicillin 250mg','B-7740',64,60,'strip'),(2,'RX-03','Insulin Glargine','B-3302',18,25,'vial'),(3,'RX-04','ORS sachets','B-1190',210,50,'box'),(4,'RX-05','Atorvastatin 10mg','B-5518',90,40,'strip');
/*!40000 ALTER TABLE `pharmacy` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rooms` (
  `pos` int NOT NULL,
  `id` varchar(32) NOT NULL,
  `type` varchar(40) DEFAULT NULL,
  `floor` varchar(16) DEFAULT NULL,
  `beds` int DEFAULT NULL,
  `occupied` int DEFAULT NULL,
  `tariff` int DEFAULT NULL,
  `occupant` varchar(120) DEFAULT NULL,
  `status` varchar(40) DEFAULT NULL,
  `patients` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `rooms` WRITE;
/*!40000 ALTER TABLE `rooms` DISABLE KEYS */;
INSERT INTO `rooms` VALUES (2,'GW-104','General Ward','1st',6,4,1800,'4 patients','Partially Full','[\"Kiran Rao\", \"Mehul Shah\", \"Anita Das\", \"Vikram Iyer\"]'),(6,'GW-108','General Ward','1st',6,0,1800,'','Available','[]'),(0,'ICU-01','ICU','3rd',1,1,12000,'Ritu Verma','Occupied','[\"Ritu Verma\"]'),(1,'ICU-02','ICU','3rd',1,0,12000,'','Available','[]'),(5,'MT-305','Maternity','3rd',2,1,4200,'Fatima Khan','Partially Full','[\"Fatima Khan\"]'),(3,'PR-210','Private','2nd',1,1,6500,'Aarav Sharma','Occupied','[\"Aarav Sharma\"]'),(4,'PR-211','Private','2nd',1,0,6500,'','Cleaning','[]'),(7,'PR-214','Private','2nd',1,0,6500,'','Available','[]'),(8,'PR-69','Private','4th',2,1,100000,'SHUBHAM 69','Partially Full','[\"SHUBHAM 69\"]');
/*!40000 ALTER TABLE `rooms` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` varchar(32) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(16) NOT NULL DEFAULT 'staff',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('ADMIN-1000','pbkdf2:sha256:1000000$J74lNzFJ6hUA5z5x$e68eab45ec040a657aefc9c28ade47ae09a1d58e4ec5c63522fb8a03478bfbfa','admin'),('DOC-1001','pbkdf2:sha256:1000000$z9CAnSNomvk0m7cr$3c931e89ed4f84cd2611fd8c09f6b7055b886465fd53b36da2daea7232c8dc01','staff'),('DOC-1002','pbkdf2:sha256:1000000$z9CAnSNomvk0m7cr$3c931e89ed4f84cd2611fd8c09f6b7055b886465fd53b36da2daea7232c8dc01','staff'),('DOC-1004','pbkdf2:sha256:1000000$z9CAnSNomvk0m7cr$3c931e89ed4f84cd2611fd8c09f6b7055b886465fd53b36da2daea7232c8dc01','staff'),('DOC-1005','pbkdf2:sha256:1000000$z9CAnSNomvk0m7cr$3c931e89ed4f84cd2611fd8c09f6b7055b886465fd53b36da2daea7232c8dc01','staff'),('DOC-1006','pbkdf2:sha256:1000000$z9CAnSNomvk0m7cr$3c931e89ed4f84cd2611fd8c09f6b7055b886465fd53b36da2daea7232c8dc01','staff'),('DOC-1007','pbkdf2:sha256:1000000$qFcuPi8vBK8yfKnT$25daf5c6598ddf179ad442f13ee50e2e7ed2d3c68ded0b46706d1084980cb518','staff'),('P-2196','pbkdf2:sha256:1000000$0YFFxtnpvQHrqdsU$5ceafe6db2715751364dad482f7a00e1c8ec247bef8b236c13f3de2cef3ab556','patient'),('P-3304','pbkdf2:sha256:1000000$YDkNn5cztMX08Gkf$bd6dbaee7339f3f8321837dabed99c86cfbbf884210c17f58a19546474709854','patient'),('P-4821','pbkdf2:sha256:1000000$ceO5q5Uc6JZXW8ta$17ab7e22bda26164509208906ac27bc2e14154cd86ca5481b4518cb5f12732e4','patient'),('P-5580','pbkdf2:sha256:1000000$qRXXaiF71Fl4N5Nl$4d971012c64cf14bb8310ef2cbc95888a92c4c178e3b76699512003ac3179891','patient'),('P-6402','pbkdf2:sha256:1000000$mc3Wavd09gVZuq7U$a4727104a2a5f324c659cdeb61a53d7bf3c71dbfa791d6ac28fb9b47b20f3c9c','patient'),('P-7718','pbkdf2:sha256:1000000$DtQJqJNFuJhBja3O$7483fe9088f0fc5a979d1ee65e849e91d6523662ac964d70103a2bac563d3eaf','patient'),('P-9267','pbkdf2:sha256:1000000$1FcZAPgj3mXhDWRG$0c21dd0b796c395863646581f58a25ee532de479fe325b3054ea351d04d7e7fe','patient');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

