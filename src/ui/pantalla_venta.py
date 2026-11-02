from datetime import datetime
from tkinter import ttk
import customtkinter as ctk
from config import TITULO_APP
from logica.calculos import calcular_importe
from modelos import DetalleVenta, Producto, VentaError, SinConexionError
from ui.tema import (FONDO, PANEL, CIAN, MAGENTA, AZUL, AMARILLO, VERDE, ROJO, FUENTE,
                     MENSAJE_INICIAL, fuente)


class PantallaVenta(ctk.CTk):
    def __init__(self, servicio, error_inicial=None):
        super().__init__(fg_color=FONDO)
        ctk.set_appearance_mode("dark")

        self.servicio = servicio
        self.carrito = {}        # codigo_barras -> DetalleVenta
        self.descripciones = {}  # codigo_barras -> descripción (solo para mostrar)
        self._parpadeo_visible = True

        self.title(TITULO_APP)
        self.geometry("1050x740")
        self.minsize(950, 650)

        self.var_folio = ctk.StringVar(value="NUEVO")
        self.var_fecha = ctk.StringVar()
        self.var_empleado = ctk.StringVar()
        self.var_codigo = ctk.StringVar()
        self.var_cantidad = ctk.StringVar(value="1")
        self.var_subtotal = ctk.StringVar(value="0.00")
        self.var_iva = ctk.StringVar(value="0.00")
        self.var_total = ctk.StringVar(value="0.00")

        self._crear_titulo()
        self._crear_encabezado()
        self._crear_captura()
        self._crear_grid()
        self._crear_totales()
        self._crear_estado()

        self._actualizar_reloj()
        self._parpadear()
        self.bind("<F12>", lambda e: self.guardar())
        self.bind("<Escape>", lambda e: self.cancelar_venta())
        self.entry_codigo.focus_set()

        if error_inicial:
            self.after(300, lambda: self._dialogo("ERROR DE CONEXIÓN", error_inicial, ROJO))

    # ------------------------------------------------------------------ UI
    def _crear_titulo(self):
        ctk.CTkLabel(self, text=f"★ {TITULO_APP} ★", font=fuente(34),
                     text_color=MAGENTA).pack(pady=(12, 0))
        ctk.CTkLabel(self, text="- - - PLAYER 1 READY - - -", font=fuente(13),
                     text_color=CIAN).pack(pady=(0, 6))

    def _entrada(self, padre, variable, ancho, color=CIAN, solo_lectura=False, tam=14):
        e = ctk.CTkEntry(padre, textvariable=variable, width=ancho, height=36, font=fuente(tam),
                         fg_color=FONDO, border_color=color, border_width=2,
                         text_color=color, corner_radius=0)
        if solo_lectura:
            e.configure(state="readonly")
        return e

    def _crear_encabezado(self):
        marco = ctk.CTkFrame(self, fg_color=PANEL, border_color=AZUL, border_width=2, corner_radius=0)
        marco.pack(fill="x", padx=15, pady=6)

        ctk.CTkLabel(marco, text="FOLIO", font=fuente(14), text_color=AMARILLO).grid(
            row=0, column=0, padx=(12, 6), pady=10)
        self._entrada(marco, self.var_folio, 120, AMARILLO, True).grid(row=0, column=1)

        ctk.CTkLabel(marco, text="FECHA", font=fuente(14), text_color=AMARILLO).grid(
            row=0, column=2, padx=(25, 6))
        self._entrada(marco, self.var_fecha, 200, AMARILLO, True).grid(row=0, column=3)

        ctk.CTkLabel(marco, text="EMPLEADO", font=fuente(14), text_color=AMARILLO).grid(
            row=0, column=4, padx=(25, 6))
        self._entrada(marco, self.var_empleado, 230, CIAN).grid(row=0, column=5, padx=(0, 12))

    def _crear_captura(self):
        marco = ctk.CTkFrame(self, fg_color=PANEL, border_color=CIAN, border_width=2, corner_radius=0)
        marco.pack(fill="x", padx=15, pady=6)

        ctk.CTkLabel(marco, text="CÓDIGO", font=fuente(16), text_color=VERDE).pack(
            side="left", padx=(12, 6), pady=10)
        self.entry_codigo = self._entrada(marco, self.var_codigo, 300, VERDE, tam=18)
        self.entry_codigo.pack(side="left")
        self.entry_codigo.bind("<Return>", self._al_escanear)  # el lector manda Enter al final

        ctk.CTkLabel(marco, text="CANT", font=fuente(16), text_color=VERDE).pack(side="left", padx=(20, 6))
        self._entrada(marco, self.var_cantidad, 70, VERDE, tam=18).pack(side="left")

        ctk.CTkButton(marco, text="QUITAR [SUPR]", font=fuente(13), width=150, height=36, corner_radius=0,
                      fg_color=FONDO, border_color=ROJO, border_width=2, text_color=ROJO,
                      hover_color="#3a0a0a", command=self.quitar_seleccionado).pack(side="right", padx=12)

    def _crear_grid(self):
        marco = ctk.CTkFrame(self, fg_color=PANEL, border_color=AZUL, border_width=2, corner_radius=0)
        marco.pack(fill="both", expand=True, padx=15, pady=6)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Arcade.Treeview", background=FONDO, fieldbackground=FONDO, foreground=CIAN,
                         rowheight=34, font=(FUENTE, 13, "bold"), borderwidth=0)
        estilo.configure("Arcade.Treeview.Heading", background="#2a0050", foreground=AMARILLO,
                         font=(FUENTE, 13, "bold"), relief="flat")
        estilo.map("Arcade.Treeview", background=[("selected", MAGENTA)], foreground=[("selected", FONDO)])
        estilo.map("Arcade.Treeview.Heading", background=[("active", "#3d0073")])

        columnas = ("clave", "producto", "precio", "cantidad", "importe")
        self.grid_ventas = ttk.Treeview(marco, columns=columnas, show="headings",
                                        selectmode="browse", style="Arcade.Treeview")
        config = {
            "clave": ("CLAVE", 170, "w"),
            "producto": ("PRODUCTO", 340, "w"),
            "precio": ("PRECIO", 110, "e"),
            "cantidad": ("CANTIDAD", 110, "center"),
            "importe": ("IMPORTE", 130, "e"),
        }
        for col, (texto, ancho, ancla) in config.items():
            self.grid_ventas.heading(col, text=texto)
            self.grid_ventas.column(col, width=ancho, anchor=ancla)

        scroll = ctk.CTkScrollbar(marco, command=self.grid_ventas.yview, button_color=AZUL,
                                  button_hover_color=CIAN, fg_color=PANEL)
        self.grid_ventas.configure(yscrollcommand=scroll.set)
        self.grid_ventas.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        scroll.pack(side="right", fill="y", padx=4, pady=6)
        self.grid_ventas.bind("<Delete>", lambda e: self.quitar_seleccionado())

    def _crear_totales(self):
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.pack(fill="x", padx=15, pady=6)

        botones = ctk.CTkFrame(marco, fg_color="transparent")
        botones.pack(side="left", anchor="s")
        ctk.CTkButton(botones, text="GUARDAR [F12]", font=fuente(18), width=220, height=60, corner_radius=0,
                      fg_color=FONDO, border_color=VERDE, border_width=3, text_color=VERDE,
                      hover_color="#0b3a05", command=self.guardar).pack(side="left")
        ctk.CTkButton(botones, text="CANCELAR [ESC]", font=fuente(14), width=170, height=60, corner_radius=0,
                      fg_color=FONDO, border_color=MAGENTA, border_width=3, text_color=MAGENTA,
                      hover_color="#3a0a33", command=self.cancelar_venta).pack(side="left", padx=12)

        totales = ctk.CTkFrame(marco, fg_color=PANEL, border_color=AMARILLO, border_width=2, corner_radius=0)
        totales.pack(side="right")
        filas = (("SUBTOTAL", self.var_subtotal, 16, CIAN),
                 ("IVA", self.var_iva, 16, CIAN),
                 ("TOTAL", self.var_total, 34, AMARILLO))
        for i, (texto, var, tam, color) in enumerate(filas):
            ctk.CTkLabel(totales, text=texto, font=fuente(tam), text_color=color).grid(
                row=i, column=0, sticky="e", padx=(14, 10), pady=2)
            ctk.CTkLabel(totales, textvariable=var, font=fuente(tam), text_color=color,
                         width=200, anchor="e").grid(row=i, column=1, padx=(0, 14))

    def _crear_estado(self):
        self.lbl_estado = ctk.CTkLabel(self, text=MENSAJE_INICIAL, font=fuente(14), text_color=VERDE,
                                       anchor="center", fg_color=PANEL, height=34, corner_radius=0)
        self.lbl_estado.pack(fill="x", side="bottom")
        self._estado_color = VERDE
        self._estado_parpadea = True

    # ------------------------------------------------------ Mensajes / animaciones
    def _mensaje(self, texto, color=VERDE, parpadea=False):
        self._estado_color = color
        self._estado_parpadea = parpadea
        self.lbl_estado.configure(text=texto, text_color=color)

    def _parpadear(self):
        if self._estado_parpadea:
            self._parpadeo_visible = not self._parpadeo_visible
            self.lbl_estado.configure(text_color=self._estado_color if self._parpadeo_visible else PANEL)
        else:
            self.lbl_estado.configure(text_color=self._estado_color)
        self.after(600, self._parpadear)

    def _actualizar_reloj(self):
        self.var_fecha.set(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.after(1000, self._actualizar_reloj)

    def _dialogo(self, titulo, texto, color, confirmar=False):
        """Ventana modal estilo arcade. Regresa True si se presionó el botón principal."""
        top = ctk.CTkToplevel(self, fg_color=FONDO)
        top.title(titulo)
        top.geometry("480x230")
        top.resizable(False, False)
        top.transient(self)
        resultado = {"ok": False}

        def cerrar(ok):
            resultado["ok"] = ok
            top.destroy()

        ctk.CTkLabel(top, text=titulo, font=fuente(20), text_color=color).pack(pady=(20, 8))
        ctk.CTkLabel(top, text=texto, font=fuente(14), text_color=CIAN, wraplength=430).pack(pady=6)
        fila = ctk.CTkFrame(top, fg_color="transparent")
        fila.pack(pady=18)
        ctk.CTkButton(fila, text="SÍ" if confirmar else "OK", width=130, height=40, corner_radius=0,
                      font=fuente(15), fg_color=FONDO, border_color=color, border_width=2, text_color=color,
                      command=lambda: cerrar(True)).pack(side="left", padx=8)
        if confirmar:
            ctk.CTkButton(fila, text="NO", width=130, height=40, corner_radius=0, font=fuente(15),
                          fg_color=FONDO, border_color=AZUL, border_width=2, text_color=MAGENTA,
                          command=lambda: cerrar(False)).pack(side="left", padx=8)

        top.bind("<Return>", lambda e: cerrar(True))
        top.after(100, lambda: (top.grab_set(), top.focus_force()))
        self.wait_window(top)
        self.entry_codigo.focus_set()
        return resultado["ok"]

    # ------------------------------------------------------------ Eventos
    def _al_escanear(self, _evento=None):
        codigo = self.var_codigo.get().strip()
        self.var_codigo.set("")
        if not codigo:
            return
        try:
            cantidad = int(self.var_cantidad.get())
            if cantidad < 1:
                raise ValueError
        except ValueError:
            self._mensaje("!! LA CANTIDAD DEBE SER UN ENTERO MAYOR A CERO !!", ROJO)
            self.var_cantidad.set("1")
            return

        try:
            producto = self.servicio.buscar_producto(codigo)
        except Exception as error:
            self._dialogo("ERROR", f"No se pudo consultar el producto:\n{error}", ROJO)
            return

        if producto is None:
            self._mensaje(f"!! PRODUCTO NO ENCONTRADO: {codigo} !!", ROJO)
            self.bell()
            return

        self.agregar_producto(producto, cantidad)
        self.var_cantidad.set("1")

    # ------------------------------------------------------- Lógica de UI
    def agregar_producto(self, producto: Producto, cantidad=1):
        codigo = producto.codigo_barras
        actual = self.carrito.get(codigo)
        nueva = (actual.cantidad if actual else 0) + cantidad

        if nueva > producto.stock:
            self._mensaje(f"!! STOCK INSUFICIENTE: {producto.descripcion} "
                          f"(DISPONIBLE: {producto.stock}) !!", ROJO)
            self.bell()
            return

        self.carrito[codigo] = DetalleVenta(
            codigo_producto=codigo,
            cantidad=nueva,
            precio_unitario=producto.precio,
            importe=calcular_importe(producto.precio, nueva),
        )
        self.descripciones[codigo] = producto.descripcion
        self._refrescar_fila(codigo)
        self._calcular_totales()
        self._mensaje(f"+{cantidad} AGREGADO: {producto.descripcion}", VERDE)

    def _refrescar_fila(self, codigo):
        d = self.carrito[codigo]
        valores = (codigo, self.descripciones[codigo], f"{d.precio_unitario:.2f}",
                   d.cantidad, f"{d.importe:.2f}")
        if self.grid_ventas.exists(codigo):
            self.grid_ventas.item(codigo, values=valores)
        else:
            self.grid_ventas.insert("", "end", iid=codigo, values=valores)
        self.grid_ventas.see(codigo)

    def quitar_seleccionado(self):
        seleccion = self.grid_ventas.selection()
        if not seleccion:
            return
        codigo = seleccion[0]
        self.grid_ventas.delete(codigo)
        self.carrito.pop(codigo, None)
        self.descripciones.pop(codigo, None)
        self._calcular_totales()
        self._mensaje("PRODUCTO ELIMINADO", AMARILLO)
        self.entry_codigo.focus_set()

    def _calcular_totales(self):
        t = self.servicio.totales(list(self.carrito.values()))
        self.var_subtotal.set(f"{t.subtotal:.2f}")
        self.var_iva.set(f"{t.iva:.2f}")
        self.var_total.set(f"{t.total:.2f}")

    def guardar(self):
        if not self.carrito:
            self._mensaje("!! NO HAY PRODUCTOS EN LA VENTA !!", ROJO)
            return
        empleado = self.var_empleado.get().strip()
        if not empleado:
            self._mensaje("!! CAPTURA EL NOMBRE DEL EMPLEADO !!", ROJO)
            return

        try:
            venta = self.servicio.guardar_venta(empleado, list(self.carrito.values()))
        except (VentaError, SinConexionError) as error:
            self._dialogo("NO SE GUARDÓ LA VENTA", str(error), ROJO)
            return
        except Exception as error:
            self._dialogo("ERROR AL GUARDAR", f"No se guardó la venta (se hizo rollback):\n{error}", ROJO)
            return

        self.var_folio.set(str(venta.folio))
        self._dialogo("¡VENTA GUARDADA!", f"FOLIO: {venta.folio}\nTOTAL: ${venta.total:.2f}", VERDE)
        self._limpiar()

    def cancelar_venta(self):
        if self.carrito and not self._dialogo("CANCELAR", "¿Descartar la venta actual?", AMARILLO, confirmar=True):
            return
        self._limpiar()

    def _limpiar(self):
        self.carrito.clear()
        self.descripciones.clear()
        self.grid_ventas.delete(*self.grid_ventas.get_children())
        self._calcular_totales()
        self.var_folio.set("NUEVO")
        self._mensaje(MENSAJE_INICIAL, VERDE, parpadea=True)
        self.entry_codigo.focus_set()
