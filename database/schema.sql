-- Esquema de la base de datos del punto de venta.
-- Ejecutar primero. Se puede volver a ejecutar sin error.
CREATE DATABASE IF NOT EXISTS punto_venta;
USE punto_venta;

CREATE TABLE IF NOT EXISTS productos (
    codigo_barras VARCHAR(13) PRIMARY KEY,
    descripcion VARCHAR(150) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ventas (
    folio INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    empleado VARCHAR(100) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    iva DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalles_venta (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    folio_venta INT NOT NULL,
    codigo_producto VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    importe DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (folio_venta) REFERENCES ventas(folio) ON DELETE CASCADE,
    FOREIGN KEY (codigo_producto) REFERENCES productos(codigo_barras)
) ENGINE=InnoDB;
