from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

CENTAVO = Decimal("0.01")


def dinero(valor) -> Decimal:
    """Convierte a Decimal con 2 decimales."""
    if isinstance(valor, float):
        valor = str(valor)
    return Decimal(valor).quantize(CENTAVO, ROUND_HALF_UP)


@dataclass
class Producto:
    """Tabla productos."""
    codigo_barras: str
    descripcion: str
    precio: Decimal
    stock: int = 0

    def __post_init__(self):
        self.precio = dinero(self.precio)


@dataclass
class DetalleVenta:
    """Tabla detalles_venta."""
    codigo_producto: str
    cantidad: int
    precio_unitario: Decimal
    importe: Optional[Decimal] = None
    folio_venta: Optional[int] = None
    id_detalle: Optional[int] = None

    def __post_init__(self):
        self.precio_unitario = dinero(self.precio_unitario)
        if self.importe is None:
            self.importe = dinero(self.precio_unitario * self.cantidad)
        else:
            self.importe = dinero(self.importe)


@dataclass
class Venta:
    """Tabla ventas, con una lista de detalles."""
    empleado: str
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    detalles: List[DetalleVenta] = field(default_factory=list)
    folio: Optional[int] = None
    fecha: Optional[datetime] = None

    def __post_init__(self):
        self.subtotal = dinero(self.subtotal)
        self.iva = dinero(self.iva)
        self.total = dinero(self.total)
