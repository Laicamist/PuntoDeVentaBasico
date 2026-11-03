from datetime import datetime
from pathlib import Path
from config import TITULO_APP
from modelos import Venta

ANCHO = 40
CARPETA_RECIBOS = Path(__file__).resolve().parent.parent.parent / "recibos"


def _linea(izquierda, derecha):
    return f"{izquierda}{derecha:>{ANCHO - len(izquierda)}}"


def generar_recibo(venta: Venta, descripciones: dict) -> Path:
    """Crea recibos/recibo_<folio>.txt y regresa su ruta."""
    fecha = venta.fecha or datetime.now()
    separador = "-" * ANCHO

    lineas = [
        TITULO_APP.center(ANCHO),
        separador,
        _linea(f"Folio: {venta.folio}", fecha.strftime("%d/%m/%Y %H:%M")),
        f"Atendió: {venta.empleado}",
        separador,
        f"{'CANT':>4} {'DESCRIPCION':<17} {'P.U.':>8} {'IMPORTE':>8}",
    ]
    for d in venta.detalles:
        descripcion = descripciones.get(d.codigo_producto, d.codigo_producto)[:17]
        lineas.append(f"{d.cantidad:>4} {descripcion:<17} {d.precio_unitario:>8.2f} {d.importe:>8.2f}")
    lineas += [
        separador,
        _linea("", f"SUBTOTAL: {venta.subtotal:>10.2f}"),
        _linea("", f"IVA: {venta.iva:>10.2f}"),
        _linea("", f"TOTAL: {venta.total:>10.2f}"),
        separador,
        "¡GRACIAS POR SU COMPRA!".center(ANCHO),
    ]

    CARPETA_RECIBOS.mkdir(exist_ok=True)
    ruta = CARPETA_RECIBOS / f"recibo_{venta.folio}.txt"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return ruta