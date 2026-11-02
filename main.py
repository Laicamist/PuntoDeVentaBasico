import customtkinter as ctk
from dao import DAO
from mysql_conection import Database
# tema
ctk.set_appearance_mode("White")
ctk.set_default_color_theme("Purple")


class AuthApp(ctk.CTk):

    def __init__(self):
        super().__init__()



if __name__ == "__main__":
    app = AuthApp()
    app.mainloop()