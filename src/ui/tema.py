import customtkinter as ctk
"""Colores y fuentes de la interfaz (estilo arcade)."""
FONDO = "#0a0a1f"
PANEL = "#14052b"
CIAN = "#00fff7"
MAGENTA = "#ff2bd6"
AZUL = "#1e90ff"
AMARILLO = "#ffe600"
VERDE = "#39ff14"
ROJO = "#ff3131"
FUENTE = "Courier New"

MENSAJE_INICIAL = ">> INSERT COIN: ESCANEA UN PRODUCTO <<"


def fuente(tam, negrita=True):
    return ctk.CTkFont(family=FUENTE, size=tam, weight="bold" if negrita else "normal")
