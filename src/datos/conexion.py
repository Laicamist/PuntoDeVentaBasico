import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno (.env en la raíz del proyecto)
load_dotenv(override=True)  # el .env manda sobre variables viejas de la terminal


class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT", "3306")),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
            )
            print("Conexión exitosa a MySQL.")
        except Error as e:
            print(f"Error al conectar: {e}")
            raise

    def get_connection(self):
        return self.connection

    def close(self):
        if hasattr(self, "connection") and self.connection.is_connected():
            self.connection.close()
            print("Conexión cerrada.")
