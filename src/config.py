"""Configuración general del punto de venta (un solo lugar para estos valores)."""
from decimal import Decimal

# IVA
TASA_IVA = Decimal("0.16")
PRECIOS_INCLUYEN_IVA = True   # True: el precio del producto ya trae IVA

# Interfaz
TITULO_APP = "SUPER POS ARCADE"
