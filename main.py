from mysql_conection import Database
from pantalla_venta import PantallaVenta


def main():
    db = None
    error = None
    try:
        db = Database()
        conn = db.get_connection()
        conn.autocommit = True  # las consultas sueltas no dejan transacciones abiertas
    except Exception as e:
        conn = None
        error = f"No se pudo conectar a MySQL.\nRevisa tu archivo .env y que el servidor esté encendido.\n\n{e}"

    def buscar_producto(codigo_barras):
        if conn is None:
            raise RuntimeError("Sin conexión a MySQL")
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT codigo_barras, descripcion, precio, stock "
                "FROM productos WHERE codigo_barras = %s",
                (codigo_barras,),
            )
            return cur.fetchone()
        finally:
            cur.close()

    def guardar_venta(empleado, items, subtotal, iva, total):
        if conn is None:
            raise RuntimeError("Sin conexión a MySQL")
        cur = conn.cursor()
        try:
            conn.start_transaction()

            cur.execute(
                "INSERT INTO ventas (empleado, subtotal, iva, total) VALUES (%s, %s, %s, %s)",
                (empleado, subtotal, iva, total),
            )
            folio = cur.lastrowid

            for it in items:
                # WHERE stock >= cantidad evita dejar el stock en negativo
                cur.execute(
                    "UPDATE productos SET stock = stock - %s "
                    "WHERE codigo_barras = %s AND stock >= %s",
                    (it["cantidad"], it["codigo_barras"], it["cantidad"]),
                )
                if cur.rowcount == 0:
                    raise ValueError(f"Stock insuficiente para el producto {it['codigo_barras']}")

                cur.execute(
                    "INSERT INTO detalles_venta "
                    "(folio_venta, codigo_producto, cantidad, precio_unitario, importe) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (folio, it["codigo_barras"], it["cantidad"], it["precio_unitario"], it["importe"]),
                )

            conn.commit()
            return folio
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()

    app = PantallaVenta(buscar_producto, guardar_venta, error_inicial=error)
    app.mainloop()

    if db is not None:
        db.close()


if __name__ == "__main__":
    main()
