from typing import List, Optional

from modelos import (
    Producto,
    Venta,
    DetalleVenta,
    DatosVentaInvalidosError,
    SinConexionError,
)
from logica.calculos import calcular_importe, calcular_totales, Totales

MAX_EMPLEADO = 100  # VARCHAR(100) en la base de datos


class VentaServicio:
    def __init__(self, dao=None):
        self.dao = dao 

    def _dao(self):
        if self.dao is None:
            raise SinConexionError("Sin conexión a la base de datos.")
        return self.dao

    #Consultas

    def buscar_producto(self, codigo_barras: str) -> Optional[Producto]:
        codigo = codigo_barras.strip()
        if not codigo:
            return None
        return self._dao().buscar_producto(codigo)

    #Cálculo

    @staticmethod
    def totales(detalles: List[DetalleVenta]) -> Totales:
        return calcular_totales(d.importe for d in detalles)
    
    #Guardar

    def guardar_venta(self, empleado: str, detalles: List[DetalleVenta]) -> Venta:
        """Valida, calcula los totales y guarda la venta con su folio en una transacción.
        """
        empleado = (empleado or "").strip()
        if not empleado:
            raise DatosVentaInvalidosError("Captura el nombre del empleado.")
        if len(empleado) > MAX_EMPLEADO:
            raise DatosVentaInvalidosError(
                f"El nombre del empleado excede {MAX_EMPLEADO} caracteres.")
        if not detalles:
            raise DatosVentaInvalidosError("La venta no tiene productos.")

        for d in detalles:
            if not isinstance(d.cantidad, int) or d.cantidad <= 0:
                raise DatosVentaInvalidosError(
                    f"Cantidad inválida para el producto {d.codigo_producto}.")
        detalles = [
            DetalleVenta(d.codigo_producto, d.cantidad, d.precio_unitario,
                         calcular_importe(d.precio_unitario, d.cantidad))
            for d in detalles
        ]

        t = self.totales(detalles)
        venta = Venta(empleado=empleado, subtotal=t.subtotal, iva=t.iva,
                      total=t.total, detalles=detalles)
        self._dao().guardar_venta(venta)
        return venta
