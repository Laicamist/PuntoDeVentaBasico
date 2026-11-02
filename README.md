# Punto de Venta Básico

Práctica de manejo de transacciones: al guardar una venta se inserta en
VENTAS, se descuenta el stock en PRODUCTOS y se insertan los renglones en
DETALLES_VENTA, todo en una sola transacción.

## Estructura

```
database/
  schema.sql            Establece la base de datos que se usara para el proyecto
  datos_prueba.sql      Productos de prueba
src/
  main.py               Punto de entrada: arma las capas y abre la pantalla
  config.py             Tasa de IVA y otros ajustes
  modelos/              Dataclasses (Producto, Venta, DetalleVenta) y excepciones
  datos/                Conexión a MySQL y DAO (único lugar con SQL)
  logica/               Cálculos de montos y reglas de la venta
  ui/                   Pantalla y tema visual
```

Cada capa solo usa a la de abajo:
`ui -> logica -> datos -> MySQL`.

## Cómo ejecutarlo

1. Instala las dependencias: `pip install -r requirements.txt`
2. En MySQL ejecuta `database/schema.sql` y luego `database/datos_prueba.sql`.
3. Copia `.env.example` como `.env` y pon tu usuario y contraseña de MySQL.
4. Desde la raíz del proyecto: `python src/main.py`
