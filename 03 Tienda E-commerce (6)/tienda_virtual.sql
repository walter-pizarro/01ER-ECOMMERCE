-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 26-03-2023 a las 17:52:53
-- Versión del servidor: 10.4.27-MariaDB
-- Versión de PHP: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `tienda_virtual`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `calificaciones`
--

CREATE TABLE `calificaciones` (
  `id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `id_cliente` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id` int(11) NOT NULL,
  `categoria` varchar(100) NOT NULL,
  `imagen` varchar(150) NOT NULL,
  `estado` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id`, `categoria`, `imagen`, `estado`) VALUES
(1, 'SISTEMAS', 'assets/images/categorias/20220805093011.jpg', 1),
(2, 'DISEÑO WEB', 'assets/images/categorias/20220805093028.jpg', 1),
(3, 'FASHON', 'assets/images/categorias/20230116112856.jpg', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id` int(11) NOT NULL,
  `nombre` varchar(150) DEFAULT NULL,
  `apellido` varchar(100) NOT NULL,
  `correo` varchar(80) NOT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `direccion` varchar(150) DEFAULT NULL,
  `clave` varchar(100) DEFAULT NULL,
  `perfil` varchar(100) NOT NULL DEFAULT 'default.png',
  `token` varchar(100) DEFAULT NULL,
  `verify` int(11) NOT NULL DEFAULT 0,
  `estado` int(11) NOT NULL DEFAULT 1,
  `accion` varchar(20) NOT NULL DEFAULT 'PRINCIPAL',
  `metodo` varchar(30) NOT NULL DEFAULT 'directo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`id`, `nombre`, `apellido`, `correo`, `telefono`, `direccion`, `clave`, `perfil`, `token`, `verify`, `estado`, `accion`, `metodo`) VALUES
(1, 'Homer', 'tmre', 'hvannoni0@ebay.co.uk', '9008975370', '<p>LIMA - PERU</p>', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/134x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(2, 'Giulio', 'santander', 'gdaenen1@samsung.com', '900897538', '<p>LIMA - PERU - prinicpal</p>', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/132x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(3, 'Julian', 'dfsfsddf', 'jcroutear2@arizona.edu', '9008975', '<p>LIMA - PERU</p>', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/241x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(4, 'Ivar', '', 'ipitson3@storify.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/127x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(5, 'Neel', '', 'nswaile4@squarespace.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/105x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(6, 'Mala', '', 'mleitch5@umn.edu', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/118x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(7, 'Donelle', '', 'dshirrell6@edublogs.org', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/144x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(8, 'Marianne', '', 'mbarajas7@naver.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/249x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(9, 'Liva', '', 'lrhymer8@google.co.uk', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/123x100.png/dddddd/000000', NULL, 1, 1, '', 'directo'),
(10, 'Margy', '', 'mshann9@macromedia.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/163x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(11, 'Pieter', '', 'pwingrovea@pinterest.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/174x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(12, 'Valeria', '', 'vlaidelb@artisteer.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/115x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(13, 'Adriane', '', 'aschindlerc@moonfruit.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/134x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(14, 'Ricki', '', 'rpurveyd@networksolutions.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/200x100.png/dddddd/000000', NULL, 1, 1, '', 'directo'),
(15, 'Osbert', '', 'oayrse@dion.ne.jp', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/210x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(16, 'Brewer', '', 'btalksf@artisteer.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/181x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(17, 'Caroline', '', 'ccarrickg@php.net', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/182x100.png/dddddd/000000', NULL, 1, 1, '', 'directo'),
(18, 'Mac', '', 'mskeenh@tumblr.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/206x100.png/dddddd/000000', NULL, 1, 1, '', 'directo'),
(19, 'Henrik', '', 'hwasoni@soup.io', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/246x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(20, 'Colene', '', 'cwainscoatj@opensource.org', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/206x100.png/dddddd/000000', NULL, 1, 1, '', 'directo'),
(21, 'Irina', '', 'ipeelek@so-net.ne.jp', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/209x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(22, 'Carlota', '', 'cheselwoodl@intel.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/139x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(23, 'Curtis', '', 'cpeadenm@yahoo.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/122x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(24, 'Clarine', '', 'clotwichn@uiuc.edu', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/104x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(25, 'Loraine', '', 'lbudiko@yelp.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/110x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(26, 'Roxy', '', 'rbiaggip@tuttocitta.it', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/240x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(27, 'Natassia', '', 'nalfordq@ustream.tv', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/159x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(28, 'Eugenie', '', 'ebroaderr@smh.com.au', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/138x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(29, 'Charyl', '', 'cfontess@intel.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/191x100.png/dddddd/000000', NULL, 1, 1, '', 'directo'),
(30, 'Jessee', '', 'jgetclifft@sourceforge.net', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/109x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(31, 'Paulita', '', 'peloiu@hud.gov', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/101x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(32, 'Randell', '', 'rjachimczakv@themeforest.net', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/160x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(33, 'Elizabeth', '', 'ewortmanw@geocities.jp', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/238x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(34, 'Cheri', '', 'cconaghanx@timesonline.co.uk', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/174x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(35, 'Vassili', '', 'vmehargy@bizjournals.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/213x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(36, 'Marybeth', '', 'malexsandrowiczz@upenn.edu', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/141x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(37, 'Sherwin', '', 'sfulkes10@plala.or.jp', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/124x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(38, 'Xymenes', '', 'xchin11@salon.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/143x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(39, 'Helyn', '', 'hstandall12@wordpress.org', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/218x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(40, 'Robin', '', 'rmiddler13@senate.gov', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/211x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(41, 'Nelli', '', 'ncousins14@shareasale.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/136x100.png/dddddd/000000', NULL, 1, 1, '', 'directo'),
(42, 'Rubin', '', 'rbassford15@webeden.co.uk', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/132x100.png/dddddd/000000', NULL, 1, 1, '', 'directo'),
(43, 'Myra', '', 'mdrife16@privacy.gov.au', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/166x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(44, 'Spence', '', 'sfrudd17@engadget.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/206x100.png/dddddd/000000', NULL, 1, 0, '', 'directo'),
(45, 'Devi', '', 'dpudsall18@ask.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/229x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(46, 'Hannie', '', 'hconisbee19@nps.gov', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/228x100.png/5fa2dd/ffffff', NULL, 1, 1, '', 'directo'),
(47, 'Adrian', '', 'acaines1a@geocities.jp', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/233x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(48, 'Karlis', '', 'kgrayling1b@sohu.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/168x100.png/cc0000/ffffff', NULL, 1, 1, '', 'directo'),
(49, 'Latia', '', 'lzucker1c@dell.com', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/149x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(50, 'Munmro', '', 'mtaberer1d@creativecommons.org', '900897537', 'LIMA - PERU', '$2y$10$wPMk8XAk6F09e/5nWCjjLu2zJpAVn5nQmzcrGHaXIP7rmejhmLiHe', 'http://dummyimage.com/123x100.png/ff4444/ffffff', NULL, 1, 1, '', 'directo'),
(62, 'Vida', 'Informatico', 'angelsifuentes2580@gmail.com', NULL, NULL, NULL, 'default.png', NULL, 1, 1, 'PRINCIPAL', 'directo'),
(65, 'ANGEL', 'SIFUENTES', 'lovenaju2@gmail.com', '900897530', '<p>PERU</p>', '$2y$10$TlQRmEf1HexsKMxTRoovnuUGX8IGY3EVrKZ.8bXar1By6GhycIbgW', 'http://localhost/shop/assets/images/clientes/default.png', '21a66551b83c814b108081b292dc65d2', 1, 1, 'PRINCIPAL', 'directo'),
(68, 'Ángel Sifuentes', 'Sifuentes', 'ana.info1999@gmail.com', NULL, NULL, NULL, 'https://platform-lookaside.fbsbx.com/platform/profilepic/?asid=1341154316665750&height=200&width=200', NULL, 1, 1, 'PRINCIPAL', 'facebook');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `colores`
--

CREATE TABLE `colores` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `color` varchar(15) NOT NULL,
  `estado` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `colores`
--

INSERT INTO `colores` (`id`, `nombre`, `color`, `estado`) VALUES
(1, 'ROJO', '#FF0000', 1),
(2, 'AZUL', '#003AFF', 1),
(3, 'NEGRO', '#000000', 1),
(4, 'GRIS', '#999999', 1),
(5, 'AMARILLO', '#ffea00', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `configuracion`
--

CREATE TABLE `configuracion` (
  `id` int(11) NOT NULL,
  `ruc` varchar(15) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `telefono` varchar(15) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `mensaje` text NOT NULL,
  `whatsapp` varchar(15) DEFAULT NULL,
  `facebook` varchar(200) DEFAULT NULL,
  `twitter` varchar(200) DEFAULT NULL,
  `instagram` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `configuracion`
--

INSERT INTO `configuracion` (`id`, `ruc`, `nombre`, `telefono`, `correo`, `direccion`, `mensaje`, `whatsapp`, `facebook`, `twitter`, `instagram`) VALUES
(1, '342234342', 'VIDA INFORMATICO', '9878977', 'info@angelsifuentes.net', 'AV. SIN NUMERO, EN TU CORAZON', 'GRACIAS POR LA PREFERENCIA', '51900897537', 'http://localhost/tienda-virtual/principal/shop', 'http://localhost/tienda-virtual/principal/shop', 'http://localhost/tienda-virtual/principal/shop');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `descargables`
--

CREATE TABLE `descargables` (
  `id` int(11) NOT NULL,
  `ruta` text NOT NULL,
  `id_producto` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_pedidos`
--

CREATE TABLE `detalle_pedidos` (
  `id` int(11) NOT NULL,
  `producto` varchar(255) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `atributos` longtext DEFAULT NULL,
  `id_pedido` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL,
  `id_transaccion` varchar(80) NOT NULL,
  `metodo` varchar(50) DEFAULT NULL,
  `monto` decimal(10,2) NOT NULL,
  `estado` varchar(30) NOT NULL,
  `fecha` datetime NOT NULL,
  `email` varchar(80) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `ciudad` varchar(50) DEFAULT NULL,
  `id_cliente` int(11) NOT NULL,
  `proceso` enum('1','2','3') NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` longtext NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 0,
  `ventas` int(11) NOT NULL DEFAULT 0,
  `imagen` varchar(150) NOT NULL,
  `descargable` tinyint(1) NOT NULL,
  `estado` int(11) NOT NULL DEFAULT 1,
  `id_categoria` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sliders`
--

CREATE TABLE `sliders` (
  `id` int(11) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `subtitulo` text NOT NULL,
  `imagen` varchar(150) NOT NULL,
  `estado` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sliders`
--

INSERT INTO `sliders` (`id`, `titulo`, `subtitulo`, `imagen`, `estado`) VALUES
(1, 'Zapatillas Fashión', 'Lorem ipsum dolor sit amet.\nLorem ipsum dolor sit amet consectetur adipisicing elit. Quia, ex, repellat quas eaque facere dignissimos error sapiente quis nisi reprehenderit nostrum excepturi totam numquam, doloremque alias quaerat voluptates repellendus necessitatibus.', 'assets/images/carrusel/1.jpg', 1),
(2, 'Cartera Fashión', 'Lorem ipsum dolor sit amet.\nLorem ipsum dolor sit amet consectetur adipisicing elit. Quia, ex, repellat quas eaque facere dignissimos error sapiente quis nisi reprehenderit nostrum excepturi totam numquam, doloremque alias quaerat voluptates repellendus necessitatibus.', 'assets/images/carrusel/2.jpg', 1),
(3, 'Tienda Online Php y Mysql', 'Código Fuente y Base de Datos\nOferta especial con soporte incluido en la configuración local o hosting. Tambien se hace un ajuste a su necesidad por un costo adicional', 'assets/images/carrusel/3.jpg', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `suscripciones`
--

CREATE TABLE `suscripciones` (
  `id` int(11) NOT NULL,
  `correo` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `suscripciones`
--

INSERT INTO `suscripciones` (`id`, `correo`) VALUES
(1, 'angelsifuentes2580@gmail.com');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tallas`
--

CREATE TABLE `tallas` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `nombre_corto` varchar(50) NOT NULL,
  `estado` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tallas`
--

INSERT INTO `tallas` (`id`, `nombre`, `nombre_corto`, `estado`) VALUES
(1, 'SMALL', 'S', 1),
(2, 'MEDIANA', 'M', 1),
(3, 'LARGE', 'L', 1),
(4, 'EXTRA LARGE', 'XL', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tallas_colores`
--

CREATE TABLE `tallas_colores` (
  `id` int(11) NOT NULL,
  `id_talla` int(11) NOT NULL,
  `id_color` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
  `id_producto` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tallas_colores`
--

INSERT INTO `tallas_colores` (`id`, `id_talla`, `id_color`, `cantidad`, `precio`, `id_producto`) VALUES
(1, 2, 3, 15, '20.00', 25),
(2, 3, 1, 14, '10.00', 25),
(3, 1, 1, 9, '20.00', 26),
(4, 1, 2, 10, '20.00', 26),
(5, 1, 5, 10, '20.00', 26),
(6, 3, 3, 9, '20.00', 26);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `testimonial`
--

CREATE TABLE `testimonial` (
  `id` int(11) NOT NULL,
  `mensaje` text NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `id_cliente` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `clave` varchar(100) NOT NULL,
  `perfil` varchar(50) DEFAULT NULL,
  `estado` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombres`, `apellidos`, `correo`, `clave`, `perfil`, `estado`) VALUES
(1, 'JUAN ANGEL', 'SIFUENTES', 'angelsifuentes2580@gmail.com', '$2y$10$rdZI4KwCTlG0ERv9TTd0BuJzw3kB74H5NWBisLS4nV.3martitd/6', 'assets/images/perfil/20230326174601.jpg', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `id` int(11) NOT NULL,
  `productos` longtext NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `fecha` datetime NOT NULL,
  `estado` int(11) NOT NULL DEFAULT 1,
  `id_cliente` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `calificaciones`
--
ALTER TABLE `calificaciones`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `colores`
--
ALTER TABLE `colores`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `configuracion`
--
ALTER TABLE `configuracion`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `descargables`
--
ALTER TABLE `descargables`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `detalle_pedidos`
--
ALTER TABLE `detalle_pedidos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_pedido` (`id_pedido`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_categoria` (`id_categoria`);

--
-- Indices de la tabla `sliders`
--
ALTER TABLE `sliders`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `suscripciones`
--
ALTER TABLE `suscripciones`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `tallas`
--
ALTER TABLE `tallas`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `tallas_colores`
--
ALTER TABLE `tallas_colores`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `testimonial`
--
ALTER TABLE `testimonial`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `calificaciones`
--
ALTER TABLE `calificaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- AUTO_INCREMENT de la tabla `colores`
--
ALTER TABLE `colores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `configuracion`
--
ALTER TABLE `configuracion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `descargables`
--
ALTER TABLE `descargables`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_pedidos`
--
ALTER TABLE `detalle_pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sliders`
--
ALTER TABLE `sliders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `suscripciones`
--
ALTER TABLE `suscripciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `tallas`
--
ALTER TABLE `tallas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `tallas_colores`
--
ALTER TABLE `tallas_colores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `testimonial`
--
ALTER TABLE `testimonial`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `detalle_pedidos`
--
ALTER TABLE `detalle_pedidos`
  ADD CONSTRAINT `detalle_pedidos_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id`);

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
