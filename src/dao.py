from dataclasses import dataclass
from mysql.connector import Error, IntegrityError
from typing import List, Optional
import os
from dotenv import load_dotenv
# Cargar varibles de entorno
load_dotenv()

@dataclass
class Usuario:
    test: str


class DAO:
    def test(self):
        return "test"