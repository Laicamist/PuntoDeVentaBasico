from typing import List, Optional
from mysql.connector import Error, IntegrityError
from modelos import (
    Producto,
    Venta,
    DetalleVenta,
    VentaError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
)
from datos.conexion import Database
"""
No calcula montos ni valida reglas de negocio (eso es de logica/).
Solo lee y escribe en la base de datos, y garantiza que guardar una venta sea
una transacción sobre VENTAS, PRODUCTOS y DETALLES_VENTA.
"""

class DAO:
    def __init__(self, conexion=None):
        self._db = None
        if conexion is None:
            self._db = Database()
            conexion = self._db.get_connection()
        self.conn = conexion
        # Las consultas sueltas no dejan transacciones abiertas;
        # guardar_venta() abre la suya de forma explícita.
        self.conn.autocommit = True

    def cerrar(self):
        if self._db is not None:
            self._db.close()

    #Productos

    def buscar_producto(self, codigo_barras: str) -> Optional[Producto]:
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT codigo_barras, descripcion, precio, stock "
                "FROM productos WHERE codigo_barras = %s",
                (codigo_barras,),
            )
            fila = cur.fetchone()
            return Producto(**fila) if fila else None
        finally:
            cur.close()

    def listar_productos(self) -> List[Producto]:
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT codigo_barras, descripcion, precio, stock "
                "FROM productos ORDER BY descripcion"
            )
            return [Producto(**fila) for fila in cur.fetchall()]
        finally:
            cur.close()

    #Ventas

    def guardar_venta(self, venta: Venta) -> int:
        """Guarda la venta en UNA transacción y regresa el folio.
        PASOS:
          1. INSERT en ventas                  (1 registro)
          2. UPDATE del stock en productos     (n productos)
          3. INSERT en detalles_venta          (n detalles)
        Si cualquier paso falla se hace ROLLBACK y no queda nada guardado.
        """
        cur = self.conn.cursor()
        try:
            self.conn.start_transaction()
            # 1) Encabezado de la venta
            cur.execute(
                "INSERT INTO ventas (empleado, subtotal, iva, total) "
                "VALUES (%s, %s, %s, %s)",
                (venta.empleado, venta.subtotal, venta.iva, venta.total),
            )
            folio = cur.lastrowid
            for d in venta.detalles:
                # 2) Descontar stock. "stock >= cantidad" revisa y descuenta
                cur.execute(
                    "UPDATE productos SET stock = stock - %s "
                    "WHERE codigo_barras = %s AND stock >= %s",
                    (d.cantidad, d.codigo_producto, d.cantidad),
                )
                if cur.rowcount == 0:
                    self._explicar_fallo_stock(cur, d)
                # 3) Renglón del detalle
                cur.execute(
                    "INSERT INTO detalles_venta "
                    "(folio_venta, codigo_producto, cantidad, precio_unitario, importe) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (folio, d.codigo_producto, d.cantidad, d.precio_unitario, d.importe),
                )
                d.id_detalle = cur.lastrowid
                d.folio_venta = folio
            self.conn.commit()
            venta.folio = folio
            return folio
        except IntegrityError as e:
            self.conn.rollback()
            raise VentaError(f"La BD rechazó la venta: {getattr(e, 'msg', e)}") from e
        except (Error, VentaError):
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def obtener_venta(self, folio: int) -> Optional[Venta]:
        """Regresa la venta con sus detalles, o nada(None) si el folio no existe."""
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT folio, fecha, empleado, subtotal, iva, total "
                "FROM ventas WHERE folio = %s",
                (folio,),
            )
            fila = cur.fetchone()
            if fila is None:
                return None
            venta = Venta(**fila)

            cur.execute(
                "SELECT id_detalle, folio_venta, codigo_producto, cantidad, "
                "precio_unitario, importe "
                "FROM detalles_venta WHERE folio_venta = %s ORDER BY id_detalle",
                (folio,),
            )
            venta.detalles = [DetalleVenta(**f) for f in cur.fetchall()]
            return venta
        finally:
            cur.close()

    @staticmethod
    def _explicar_fallo_stock(cur, d: DetalleVenta):
        """El UPDATE no afectó filas: averigua si el producto no existe o no alcanza."""
        cur.execute("SELECT stock FROM productos WHERE codigo_barras = %s", (d.codigo_producto,))
        fila = cur.fetchone()
        if fila is None:
            raise ProductoNoEncontradoError(f"El producto {d.codigo_producto} no existe.")
        raise StockInsuficienteError(
            f"Stock insuficiente para {d.codigo_producto}: "
            f"disponible {fila[0]}, solicitado {d.cantidad}.")