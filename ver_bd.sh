#!/bin/bash
# Muestra el contenido de la base de datos StockOps desde la terminal
docker exec -e MYSQL_PWD=stockops123 stockops-db \
  mysql --default-character-set=utf8mb4 -ustockops stockops -t -e "
SELECT 'categorias' AS tabla, COUNT(*) AS registros FROM categorias
UNION ALL SELECT 'proveedores', COUNT(*) FROM proveedores
UNION ALL SELECT 'productos', COUNT(*) FROM productos;
SELECT * FROM categorias;
SELECT * FROM proveedores;
SELECT p.id, p.nombre AS producto, p.precio, p.cantidad,
       c.nombre AS categoria, v.nombre AS proveedor
FROM productos p
JOIN categorias c ON p.categoria_id = c.id
JOIN proveedores v ON p.proveedor_id = v.id
ORDER BY p.id;"
