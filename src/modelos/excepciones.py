"""Errores de negocio."""


class VentaError(Exception):
    """La venta no se guardó (no quedó nada en la BD)."""


class DatosVentaInvalidosError(VentaError):
    pass


class ProductoNoEncontradoError(VentaError):
    pass


class StockInsuficienteError(VentaError):
    pass


class SinConexionError(Exception):
    """No se puedes conectar con la base de datos."""
