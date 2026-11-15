import tkinter as tk
import math
from tkinter import END, messagebox


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.geometry("310x450")
        self.title("Practica 2 - Calculadora")

        # Variables de estado
        self.numero_aux = 0
        self.oper = ""
        self.ban_dec = True
        self.ban_bin = False
        self.ban_punto = False


        self.crear_display()
        self.crear_sistemas()
        self.crear_botones()

    #codigo convertir bases
    def actualizar_sistemas(self, numero):
        if self.ban_dec:
            try:
                if self.ban_punto == False:
                    self.entry_bin.config(state="normal")
                    self.entry_bin.delete(0, END)
                    # Convertir decimal a binario
                    numero = int(numero)

                    if numero == 0:
                        binario = "0"
                    else:
                        binario = ""
                        while numero > 0:
                            residuo = numero % 2
                            binario = str(residuo) + binario
                            numero = numero // 2
                    self.entry_bin.insert(0, binario)
                    self.entry_bin.config(state="disabled")
                    # Mostrar decimal
                    self.entry_dec.config(state="normal")
                    self.entry_dec.delete(0, END)
                    self.entry_dec.insert(0,self.entry_display.get())
                    self.entry_dec.config(state="disabled")
            except:
                pass


    # DISPLAY
    def crear_display(self):

        self.entry_display = tk.Entry(self,width=24,font=("Arial", 14),justify="right")

        self.entry_display.grid(row=0,column=0,columnspan=5,padx=10,pady=(10, 8))

    # SISTEMAS NUMERICOS

    def crear_sistemas(self):

        # HEX
        tk.Label(self,text="HEX:",width=4,font=("Arial", 10)).grid(row=1, column=0, padx=2, pady=2)

        self.entry_hex = tk.Entry(self,width=27,state="disabled")

        self.entry_hex.grid(row=1,column=1,columnspan=4,padx=2,pady=2)

        # DEC
        tk.Label(self,text="DEC:",width=4,font=("Arial", 10)).grid(row=2, column=0, padx=2, pady=2)

        self.entry_dec = tk.Entry(self,width=27,state="disabled")

        self.entry_dec.grid(row=2,column=1,columnspan=4,padx=2,pady=2)

        # OCT
        tk.Label(self,text="OCT:",width=4,font=("Arial", 10)).grid(row=3, column=0, padx=2, pady=2)

        self.entry_oct = tk.Entry(self,width=27,state="disabled")

        self.entry_oct.grid(row=3,column=1,columnspan=4,padx=2,pady=2)

        # BIN
        tk.Label(self,text="BIN:",width=4,font=("Arial", 10)).grid(row=4, column=0, padx=2, pady=2)

        self.entry_bin = tk.Entry(self,width=27,state="disabled")

        self.entry_bin.grid(row=4,column=1,columnspan=4,padx=2,pady=2)

    # BOTONES

    def crear_botones(self):

        botones = [
            ('A', 5, 0), ('√', 5, 1), ('%', 5, 2),('delete', 5, 3), ('Clear', 5, 4),

            ('B', 6, 0), ('n!', 6, 1), ('^', 6, 2),('Tan', 6, 3), ('/', 6, 4),

            ('C', 7, 0), ('7', 7, 1), ('8', 7, 2),('9', 7, 3), ('*', 7, 4),

            ('D', 8, 0), ('4', 8, 1), ('5', 8, 2),('6', 8, 3), ('-', 8, 4),

            ('E', 9, 0), ('1', 9, 1), ('2', 9, 2),('3', 9, 3), ('+', 9, 4),

            ('F', 10, 0), ('±', 10, 1), ('0', 10, 2),('.', 10, 3), ('=', 10, 4)
        ]

        for text, row, col in botones:

            if text in "0123456789.":
                action = lambda x=text: self.enviar_display(x)

            elif text in "+-*/":
                action = lambda x=text: self.operador(x)

            elif text == "=":
                action = self.operacion

            elif text == "delete":
                action = self.delete

            elif text == "Clear":
                action = self.Clear

            elif text in "ABCDEF":
                action = lambda: None

            elif text == "Tan":
                action = self.calculo_tangente

            elif text == "n!":
                action = self.calculo_factorial

            elif text == "^":
                action = self.calculo_potencia

            elif text == "±":
                action = self.cambiar_signo

            elif text == "√":
                action = self.calculo_raiz

            elif text == "%":
                action = self.calculo_porcentaje

            btn = tk.Button(self,text=text,width=5,height=2,command=action)

            btn.grid(row=row,column=col,padx=2,pady=2)

    # ESCRIBIR EN DISPLAY
    def enviar_display(self, numero):
        if numero == ".":
            contenido = self.entry_display.get()
            if "." in contenido:
                return

            self.ban_punto = True
        self.entry_display.insert(END,str(numero))
        if numero != ".":
            try:
                self.actualizar_sistemas(self.entry_display.get())
            except:
                pass


    # POTENCIA

    def calculo_potencia(self):

        try:

            self.numero_aux = float(self.entry_display.get())
            self.oper = "^"
            self.entry_display.delete(0,END)

        except ValueError:
            messagebox.showerror("Error","Ingresa un número válido")

    # RAIZ CUADRADA
    def calculo_raiz(self):
        try:
            numero = float(self.entry_display.get())
            if numero < 0:
                messagebox.showerror("Error","No se puede calcular la raíz de un número negativo")
                return
            if numero == 0:
                self.mostrar_resultado(0)
                return
            aproximacion = numero
            for i in range(20):
                aproximacion = (
                    aproximacion + numero / aproximacion
                ) / 2

            self.mostrar_resultado(aproximacion)

        except ValueError:
            messagebox.showerror("Error","Ingresa un número válido")

    # TANGENTE

    def calculo_tangente(self):

        try:

            angulo = float(self.entry_display.get())
            # Convertimos grados a radianes
            radianes = math.radians(angulo)
            resultado = math.tan(radianes)
            self.mostrar_resultado(resultado)

        except ValueError:
            messagebox.showerror("Error","Ingresa un número válido")

    # FACTORIAL
    
    def calculo_factorial(self):

        try:

            numero = float(self.entry_display.get())

            if numero < 0:
                messagebox.showerror("Error","El factorial no acepta números negativos")
                return

            if not numero.is_integer():
                messagebox.showerror("Error","El factorial solo acepta números enteros")
                return
            numero = int(numero)
            resultado = 1
            for i in range(1, numero + 1):
                resultado = resultado * i
            self.mostrar_resultado(resultado)

        except ValueError:

            messagebox.showerror("Error","Ingresa un número válido")

    # PORCENTAJE

    def calculo_porcentaje(self):

        try:

            numero = float(self.entry_display.get())
            resultado = numero / 100
            self.mostrar_resultado(resultado)

        except ValueError:
            messagebox.showerror("Error","Ingresa un número válido")

    # CAMBIAR SIGNO

    def cambiar_signo(self):

        try:

            numero = float(self.entry_display.get())
            resultado = numero * -1
            self.mostrar_resultado(resultado)

        except ValueError:
            messagebox.showerror("Error","Ingresa un número válido")

    # CLEAR
    
    def Clear(self):

        self.entry_display.delete(0,END)
        self.numero_aux = 0
        self.oper = ""

    # DELETE

    def delete(self):
        contenido = self.entry_display.get()
        if contenido:
            self.entry_display.delete(len(contenido) - 1,END)

    # OPERADORES

    def operador(self, op):

        try:

            self.numero_aux = float(self.entry_display.get())
            self.oper = op
            self.entry_display.delete(0,END)

        except ValueError:
            messagebox.showerror("Error","Ingresa un número válido")

    # OPERACION =

    def operacion(self):

        try:

            numero_actual = float(self.entry_display.get())
            resultado = 0
            if self.oper == "+":
                resultado = (self.numero_aux + numero_actual)

            elif self.oper == "-":
                resultado = (self.numero_aux - numero_actual)

            elif self.oper == "*":
                resultado = (self.numero_aux * numero_actual)

            elif self.oper == "/":
                if numero_actual == 0:
                    messagebox.showerror("Error","División por cero")
                    return

                resultado = (self.numero_aux / numero_actual)

            elif self.oper == "^":
                    base = self.numero_aux
                    exponente = int(numero_actual)

                    resultado = 1

                    for i in range(exponente):
                        resultado = resultado * base

            else:
                return

            self.mostrar_resultado(resultado)

            # Guardamos el resultado
            self.numero_aux = resultado
            self.oper = ""

        except ValueError:
            messagebox.showerror("Error","Ingresa un número válido")

    # MOSTRAR RESULTADO

    def mostrar_resultado(self, resultado):
        if isinstance(resultado, float):
            if resultado.is_integer():
                resultado = int(resultado)

        self.entry_display.delete(0,END)
        self.entry_display.insert(0,str(resultado))

if __name__ == "__main__":

    app = App()
    app.mainloop()