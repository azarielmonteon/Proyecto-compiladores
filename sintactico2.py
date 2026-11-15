
# sintactico2.py
# Actividad 1.1 - Analizador sintactico

import sys
from lexico import Lexico
from genera import GeneraCodigo


class Sintactico:

    def __init__(self, fuente, objeto, traza=0):
        # Objeto analizador lexico
        self.lexico = Lexico(fuente, traza)

        # Objeto generador de codigo
        self.generaCodigo = GeneraCodigo(objeto)

        self.traza = traza

        try:
            if self.lexico.existeTraza():
                print("INICIO DE ANALISIS SINTACTICO")

            self.programa()

        finally:
            self.lexico.cerrar()
            if hasattr(self, "generaCodigo"):
                if hasattr(self.generaCodigo, "salida"):
                    if not self.generaCodigo.salida.closed:
                        self.generaCodigo.salida.close()

    def __del__(self):
        if hasattr(self, "lexico"):
            if self.lexico.existeTraza():
                print("FIN DE ANALISIS SINTACTICO")
                print("FIN DE COMPILACION")

    # --------------------------------------------------
    # PROGRAMA
    # --------------------------------------------------

    def programa(self):
        token = self.lexico.siguienteToken()

        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <PROGRAMA>")

        if token == 'M':
            self.generaCodigo.code()
        else:
            self.errores(8)

        token = self.lexico.siguienteToken()

        if token != '{':
            self.errores(9)

        self.bloque()

        token = self.lexico.siguienteToken()

        if token != '}':
            self.errores(2)

        # No se permiten tokens despues del programa
        token = self.lexico.siguienteToken()

        if token is not None:
            self.errores(6)

        self.generaCodigo.end()

    # --------------------------------------------------
    # BLOQUE
    # --------------------------------------------------

    def bloque(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <BLOQUE>")

        self.sentencia()
        self.otra_sentencia()

    def otra_sentencia(self):
        token = self.lexico.siguienteToken()

        if token == ';':
            # Permite cerrar el bloque despues del punto y coma
            siguiente = self.lexico.siguienteToken()

            if siguiente == '}':
                self.lexico.devuelveToken(siguiente)
                return

            self.lexico.devuelveToken(siguiente)
            self.sentencia()
            self.otra_sentencia()

        else:
            self.lexico.devuelveToken(token)

    # --------------------------------------------------
    # SENTENCIA
    # --------------------------------------------------

    def sentencia(self):
        token = self.lexico.siguienteToken()

        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <SENTENCIA>")

        if token is not None and 'a' <= token <= 'z':
            self.lexico.devuelveToken(token)
            self.asignacion()

        elif token == 'R':
            self.lectura()

        elif token == 'W':
            self.escritura()

        else:
            self.errores(6)

    # --------------------------------------------------
    # ASIGNACION
    # --------------------------------------------------

    def asignacion(self):
        self.variable()

        token = self.lexico.siguienteToken()

        if token != '=':
            self.errores(3)

        self.expresion()
        self.generaCodigo.store()

    # --------------------------------------------------
    # VARIABLE
    # --------------------------------------------------

    def variable(self):
        token = self.lexico.siguienteToken()

        if token is not None and 'a' <= token <= 'z':
            self.generaCodigo.push(token)
        else:
            self.errores(5)

    # --------------------------------------------------
    # EXPRESION
    # --------------------------------------------------

    def expresion(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <EXPRESION>")

        self.termino()
        self.mas_terminos()

    def mas_terminos(self):
        token = self.lexico.siguienteToken()

        if token == '+':
            self.termino()
            self.generaCodigo.add()
            self.mas_terminos()

        elif token == '-':
            self.termino()
            self.generaCodigo.sub()
            self.mas_terminos()

        else:
            self.lexico.devuelveToken(token)

    # --------------------------------------------------
    # TERMINO
    # --------------------------------------------------

    def termino(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <TERMINO>")

        self.factor()
        self.mas_factores()

    def mas_factores(self):
        token = self.lexico.siguienteToken()

        if token == '*':
            self.factor()
            self.generaCodigo.mul()
            self.mas_factores()

        elif token == '/':
            self.factor()
            self.generaCodigo.div()
            self.mas_factores()

        elif token == '%':
            self.factor()
            self.generaCodigo.mod()
            self.mas_factores()

        else:
            self.lexico.devuelveToken(token)

    # --------------------------------------------------
    # FACTOR
    # --------------------------------------------------

    def factor(self):
        token = self.lexico.siguienteToken()

        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <FACTOR>")

        if token is not None and '0' <= token <= '9':
            self.lexico.devuelveToken(token)
            self.constante()

        elif token == '(':
            self.expresion()

            token = self.lexico.siguienteToken()

            if token != ')':
                self.errores(4)

        elif token is not None and 'a' <= token <= 'z':
            self.lexico.devuelveToken(token)
            self.variable()
            self.generaCodigo.load()

        else:
            self.errores(7)

    # --------------------------------------------------
    # LECTURA
    # --------------------------------------------------

    def lectura(self):
        token = self.lexico.siguienteToken()

        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <LECTURA>", token)

        if token is None or not ('a' <= token <= 'z'):
            self.errores(5)

        self.generaCodigo.input(token)

    # --------------------------------------------------
    # ESCRITURA
    # --------------------------------------------------

    def escritura(self):
        token = self.lexico.siguienteToken()

        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <ESCRITURA>", token)

        if token is None or not ('a' <= token <= 'z'):
            self.errores(5)

        self.generaCodigo.output(token)

    # --------------------------------------------------
    # CONSTANTE
    # --------------------------------------------------

    def constante(self):
        token = self.lexico.siguienteToken()

        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <CONSTANTE>")

        if token is not None and '0' <= token <= '9':
            self.generaCodigo.pushc(token)
        else:
            self.errores(7)

    # --------------------------------------------------
    # ERRORES SINTACTICOS
    # --------------------------------------------------

    def errores(self, codigo):
        print(
            f"LINEA {self.lexico.lineaActual()} "
            f"ERROR SINTACTICO {codigo}"
        )

        mensajes = {
            1: ": ESPERABA UN ;",
            2: ": ESPERABA UNA }",
            3: ": ESPERABA UN =",
            4: ": ESPERABA UN )",
            5: ": ESPERABA UN IDENTIFICADOR",
            6: ": INSTRUCCION DESCONOCIDA",
            7: ": ESPERABA UNA CONSTANTE O FACTOR",
            8: ": ESPERABA UNA M DE MAIN",
            9: ": ESPERABA UNA {"
        }

        print(mensajes.get(codigo, ": ERROR NO DOCUMENTADO"))
        raise SystemExit(-(codigo + 100))


# ------------------------------------------------------
# PROGRAMA PRINCIPAL
# ------------------------------------------------------

def main():
    archivo_fuente = input(
        "Nombre del archivo fuente (.txt): "
    )

    archivo_objeto = input(
        "Nombre del archivo objeto (ej. salida.obj): "
    )

    respuesta = input("Activar traza? (s/n): ").lower()
    traza = 1 if respuesta == 's' else 0

    try:
        sintactico = Sintactico(
            archivo_fuente,
            archivo_objeto,
            traza
        )

        print("COMPILACION TERMINADA CORRECTAMENTE")

    except OSError as error:
        print("ERROR DE ARCHIVO:", error)


if __name__ == "__main__":
    main()
