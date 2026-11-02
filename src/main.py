from datos.dao import DAO
from logica.venta_servicio import VentaServicio
from ui.pantalla_venta import PantallaVenta


def main():
    dao = None
    error = None
    try:
        dao = DAO()
    except Exception as e:
        error = ("No se pudo conectar a MySQL.\n"
                 "Revisa tu archivo .env o que el servidor esté encendido o exista.\n\n"
                 f"{e}")

    servicio = VentaServicio(dao)
    app = PantallaVenta(servicio, error_inicial=error)
    app.mainloop()

    if dao is not None:
        dao.cerrar()


if __name__ == "__main__":
    main()
