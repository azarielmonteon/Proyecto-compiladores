import tkinter as tk
from tkinter import END, messagebox
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("240x280")
        self.title("Practica 2 - Calculadora")
        # Variables de estado
        self.numero_aux = 0
        self.oper = ""
        self.entry_display = tk.Entry(self, width=20, font=("Arial", 14),
        justify="right")
        self.entry_display.grid(row=0, column=0, columnspan=4, padx=10,
        pady=10)
        self.crear_botones()

    def crear_botones(self):
        botones = [
        ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
        ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
        ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
        ('delete', 5, 0), ('Clear', 5,1)
        ]
        for (text, row, col) in botones:
            if text in "0123456789.":
                action = lambda x=text: self.enviar_display(x)
            elif text in "+-*/":
                action = lambda x=text: self.operador(x)
            elif text == "=":
                action = self.operacion
            elif text == "delete":
                action = lambda x=text: self.delete(x)
            elif text == "Clear":
                action = lambda x=text: self.Clear(x)
                
            btn = tk.Button(self, text=text, width=5, height=2,command=action)

            btn.grid(row=row, column=col, padx=2, pady=2)
    def enviar_display(self, numero):
        self.entry_display.insert(END, str(numero))
    def Clear(self,numero):
        self.entry_display.delete(0,tk.END)
    def delete(self,numero):
        self.entry_display.delete(0)
    def operador(self, op):
        try:
            self.numero_aux = float(self.entry_display.get())
            self.oper = op
            self.entry_display.delete(0, END)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido")
    def operacion(self):
        try:
            numero_actual = float(self.entry_display.get())
            resultado = 0
            if self.oper == "+":
                resultado = self.numero_aux + numero_actual
            elif self.oper == "-":
                resultado = self.numero_aux - numero_actual
            elif self.oper == "*":
                resultado = self.numero_aux * numero_actual
            elif self.oper == "/":
                if numero_actual == 0:
                    messagebox.showerror("Error", "División por cero")
                    return
                resultado = self.numero_aux / numero_actual
            else:
                # No se seleccionó una operación
                return
                # Mostrar resultado formateado
            if resultado.is_integer():
                self.entry_display.delete(0, END)
                self.entry_display.insert(0, str(int(resultado)))
            else:
                self.entry_display.delete(0, END)
                self.entry_display.insert(0, str(resultado))
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido")

if __name__ == "__main__":
    app = App()
    app.mainloop()