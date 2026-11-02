USE punto_venta;

INSERT INTO productos (codigo_barras, descripcion, precio, stock) VALUES
('7622202825682', 'COCA 600', 23.00, 50),
('7501295600614', 'DORITOS', 20.00, 30),
('7500810049686', 'PRODUCTO DE PRUEBA', 15.00, 10)
ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion), precio = VALUES(precio), stock = VALUES(stock);
