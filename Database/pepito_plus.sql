-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: pepito_plus
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `busquedas`
--

DROP TABLE IF EXISTS `busquedas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `busquedas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `persona_id` int NOT NULL,
  `pais` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_inicio` datetime DEFAULT CURRENT_TIMESTAMP,
  `fecha_fin` datetime DEFAULT NULL,
  `estado` enum('EN_PROGRESO','COMPLETADA','ERROR') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'EN_PROGRESO',
  `num_workers` int DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_busqueda_persona` (`persona_id`),
  CONSTRAINT `fk_busqueda_persona` FOREIGN KEY (`persona_id`) REFERENCES `personas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `busquedas`
--

LOCK TABLES `busquedas` WRITE;
/*!40000 ALTER TABLE `busquedas` DISABLE KEYS */;
/*!40000 ALTER TABLE `busquedas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documento_analisis`
--

DROP TABLE IF EXISTS `documento_analisis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documento_analisis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `documento_id` int NOT NULL,
  `verificacion_identidad` enum('MISMA_PERSONA','POSIBLE_COINCIDENCIA','PERSONA_DIFERENTE','NO_DETERMINADO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `clasificacion_contextual` enum('POSITIVO','NEUTRO','NEGATIVO','NO_DETERMINADO') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_analisis` datetime DEFAULT CURRENT_TIMESTAMP,
  `tiempo_procesamiento_ms` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `documento_id` (`documento_id`),
  KEY `idx_analisis_verificacion` (`verificacion_identidad`),
  KEY `idx_analisis_clasificacion` (`clasificacion_contextual`),
  CONSTRAINT `fk_analisis_documento` FOREIGN KEY (`documento_id`) REFERENCES `documentos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documento_analisis`
--

LOCK TABLES `documento_analisis` WRITE;
/*!40000 ALTER TABLE `documento_analisis` DISABLE KEYS */;
/*!40000 ALTER TABLE `documento_analisis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documentos`
--

DROP TABLE IF EXISTS `documentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documentos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `url_id` int NOT NULL,
  `busqueda_id` int NOT NULL,
  `titulo` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fuente_id` int NOT NULL,
  `pais` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_publicacion` date DEFAULT NULL,
  `fecha_consulta` datetime DEFAULT CURRENT_TIMESTAMP,
  `contenido_texto` longtext COLLATE utf8mb4_unicode_ci,
  `es_relacionado` tinyint(1) NOT NULL DEFAULT '0',
  `motivo_descarte` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_doc_url` (`url_id`),
  KEY `fk_doc_busqueda` (`busqueda_id`),
  KEY `fk_doc_fuente` (`fuente_id`),
  KEY `idx_doc_relacionado` (`es_relacionado`),
  CONSTRAINT `fk_doc_busqueda` FOREIGN KEY (`busqueda_id`) REFERENCES `busquedas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_doc_fuente` FOREIGN KEY (`fuente_id`) REFERENCES `fuentes` (`id`),
  CONSTRAINT `fk_doc_url` FOREIGN KEY (`url_id`) REFERENCES `urls` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documentos`
--

LOCK TABLES `documentos` WRITE;
/*!40000 ALTER TABLE `documentos` DISABLE KEYS */;
/*!40000 ALTER TABLE `documentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuentes`
--

DROP TABLE IF EXISTS `fuentes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fuentes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `url_inicial` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pais` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` enum('ACTIVA','INACTIVA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ACTIVA',
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuentes`
--

LOCK TABLES `fuentes` WRITE;
/*!40000 ALTER TABLE `fuentes` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuentes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metricas_concurrencia`
--

DROP TABLE IF EXISTS `metricas_concurrencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metricas_concurrencia` (
  `id` int NOT NULL AUTO_INCREMENT,
  `busqueda_id` int NOT NULL,
  `fase` enum('CRAWLING','MATCHING','VERIFICACION','CLASIFICACION') COLLATE utf8mb4_unicode_ci NOT NULL,
  `num_workers` int NOT NULL,
  `tiempo_total_ms` int NOT NULL,
  `elementos_procesados` int NOT NULL,
  `fecha_ejecucion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_metrica_busqueda` (`busqueda_id`),
  CONSTRAINT `fk_metrica_busqueda` FOREIGN KEY (`busqueda_id`) REFERENCES `busquedas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metricas_concurrencia`
--

LOCK TABLES `metricas_concurrencia` WRITE;
/*!40000 ALTER TABLE `metricas_concurrencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `metricas_concurrencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `personas`
--

DROP TABLE IF EXISTS `personas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `personas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_completo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pais` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ciudad` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `profesion_cargo` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `empresa_organizacion` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `alias` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `palabras_relacionadas` text COLLATE utf8mb4_unicode_ci,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `personas`
--

LOCK TABLES `personas` WRITE;
/*!40000 ALTER TABLE `personas` DISABLE KEYS */;
/*!40000 ALTER TABLE `personas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `urls`
--

DROP TABLE IF EXISTS `urls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `urls` (
  `id` int NOT NULL AUTO_INCREMENT,
  `busqueda_id` int NOT NULL,
  `fuente_id` int NOT NULL,
  `url` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` enum('PENDIENTE','EN_PROCESAMIENTO','PROCESADA','DESCARTADA','ERROR') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDIENTE',
  `profundidad` int DEFAULT '0',
  `fecha_descubrimiento` datetime DEFAULT CURRENT_TIMESTAMP,
  `fecha_procesamiento` datetime DEFAULT NULL,
  `worker_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_url_busqueda` (`busqueda_id`,`url`(255)),
  KEY `fk_url_fuente` (`fuente_id`),
  KEY `idx_url_estado` (`estado`),
  CONSTRAINT `fk_url_busqueda` FOREIGN KEY (`busqueda_id`) REFERENCES `busquedas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_url_fuente` FOREIGN KEY (`fuente_id`) REFERENCES `fuentes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `urls`
--

LOCK TABLES `urls` WRITE;
/*!40000 ALTER TABLE `urls` DISABLE KEYS */;
/*!40000 ALTER TABLE `urls` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'pepito_plus'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-11 17:42:41
