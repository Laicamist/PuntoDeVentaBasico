from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from config import TASA_IVA, PRECIOS_INCLUYEN_IVA
from modelos import dinero


@dataclass(frozen=True)
class Totales:
    subtotal: Decimal
    iva: Decimal
    total: Decimal


def calcular_importe(precio_unitario, cantidad: int) -> Decimal:
    return dinero(dinero(precio_unitario) * cantidad)


def calcular_totales(importes: Iterable[Decimal],
                     tasa=TASA_IVA,
                     precios_incluyen_iva: bool = PRECIOS_INCLUYEN_IVA) -> Totales:
    """Subtotal, IVA y total a partir de los importes de los renglones.

    Si los precios ya incluyen IVA, la suma de importes es el total y el
    subtotal se calcula hacia atrás (total / 1.16). Si no, la suma es el
    subtotal y el IVA se agrega encima.
    """
    tasa = Decimal(tasa)
    suma = sum((dinero(i) for i in importes), Decimal("0"))
    if precios_incluyen_iva:
        total = dinero(suma)
        subtotal = dinero(total / (1 + tasa))
        iva = total - subtotal
    else:
        subtotal = dinero(suma)
        iva = dinero(subtotal * tasa)
        total = subtotal + iva
    return Totales(subtotal, iva, total)
