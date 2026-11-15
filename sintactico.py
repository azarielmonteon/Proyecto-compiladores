#sintactico

from lexico import Lexico
from genera import GeneraCodigo
import sys


class Sintactico:

    def __init__(self, fuente, objeto, traza=0):
        self.lexico = Lexico(fuente, traza)
        self.generaCodigo = GeneraCodigo(objeto)

        if self.lexico.existeTraza():
            print("INICIO DE ANALISIS SINTACTICO")

        self.programa()

    def __del__(self):
        if hasattr(self, "lexico") and self.lexico.existeTraza():
            print("FIN DE ANALISIS SINTACTICO")
            print("FIN DE COMPILACION")

    # PROGRAMA
    def programa(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <PROGRAMA>")

        token = self.lexico.siguienteToken()

        if token == 'M':
            self.generaCodigo.code()
        else:
            self.errores(8)

        token = self.lexico.siguienteToken()

        if token != '{':
            self.errores(9)

        self.bloque()

        token = self.lexico.siguienteToken()

        if token == '}':
            self.generaCodigo.end()
        else:
            self.errores(2)

    # BLOQUE
    def bloque(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <BLOQUE>")

        self.sentencia()
        self.otra_sentencia()

    # OTRA SENTENCIA
    def otra_sentencia(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <OTRA_SENTENCIA>")

        token = self.lexico.siguienteToken()

        if token == ';':
            self.sentencia()
            self.otra_sentencia()
        else:
            self.lexico.devuelveToken(token)

    # SENTENCIA
    def sentencia(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <SENTENCIA>")

        token = self.lexico.siguienteToken()

        if 'a' <= token <= 'z':
            self.lexico.devuelveToken(token)
            self.asignacion()
        elif token == 'R':
            self.lectura()
        elif token == 'W':
            self.escritura()
        else:
            self.errores(6)

    # ASIGNACION
    def asignacion(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <ASIGNACION>")

        self.variable()

        token = self.lexico.siguienteToken()

        if token != '=':
            self.errores(3)

        self.expresion()
        self.generaCodigo.store()

    # VARIABLE
    def variable(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <VARIABLE>")

        token = self.lexico.siguienteToken()

        if 'a' <= token <= 'z':
            self.generaCodigo.push(token)
        else:
            self.errores(5)

    # EXPRESION
    def expresion(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <EXPRESION>")

        self.termino()
        self.mas_terminos()

    # TERMINO
    def termino(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <TERMINO>")

        self.factor()
        self.mas_factores()

    # MAS TERMINOS
    def mas_terminos(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <MAS_TERMINOS>")

        token = self.lexico.siguienteToken()

        if token == '+':
            self.termino()
            self.generaCodigo.add()
            self.mas_terminos()

        elif token == '-':
            self.termino()
            self.generaCodigo.neg()
            self.generaCodigo.add()
            self.mas_terminos()

        else:
            self.lexico.devuelveToken(token)

    # FACTOR
    def factor(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <FACTOR>")

        token = self.lexico.siguienteToken()

        if '0' <= token <= '9':
            self.lexico.devuelveToken(token)
            self.constante()

        elif token == '(':
            self.expresion()

            token = self.lexico.siguienteToken()

            if token != ')':
                self.errores(4)

        else:
            self.lexico.devuelveToken(token)
            self.variable()
            self.generaCodigo.load()

    # MAS FACTORES
    def mas_factores(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <MAS_FACTORES>")

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

    # LECTURA
    def lectura(self):
        token = self.lexico.siguienteToken()

        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <LECTURA>", token)

        if not ('a' <= token <= 'z'):
            self.errores(5)

        self.generaCodigo.input(token)

    # ESCRITURA
    def escritura(self):
        token = self.lexico.siguienteToken()

        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <ESCRITURA>", token)

        if not ('a' <= token <= 'z'):
            self.errores(5)

        self.generaCodigo.output(token)

    # CONSTANTE
    def constante(self):
        if self.lexico.existeTraza():
            print("ANALISIS SINTACTICO: <CONSTANTE>")

        token = self.lexico.siguienteToken()

        if '0' <= token <= '9':
            self.generaCodigo.pushc(token)
        else:
            self.errores(7)


    # ERRORES SINTACTICOS
    def errores(self, codigo):
        print(
            f"LINEA {self.lexico.lineaActual()} "
            f"ERROR SINTACTICO {codigo}",
            end=""
        )

        mensajes = {
            1: " :ESPERABA UN ;",
            2: " :ESPERABA UNA }",
            3: " :ESPERABA UN =",
            4: " :ESPERABA UN )",
            5: " :ESPERABA UN IDENTIFICADOR",
            6: " :INSTRUCCION DESCONOCIDA",
            7: " :ESPERABA UNA CONSTANTE",
            8: " :ESPERABA UNA M DE MAIN",
            9: " :ESPERABA UNA {"
        }

        print(mensajes.get(codigo, " :NO DOCUMENTADO"))
        sys.exit(-(codigo + 100))


if __name__ == "__main__":
    fuente = "pruebalexico.txt"
    objeto = "salida.txt"
    traza = 1

    compilador = None

    try:
        compilador = Sintactico(fuente, objeto, traza)

        print("\nAnalisis sintactico terminado.")
        print("Codigo generado en:", objeto)

    except SystemExit as error:
        print("El programa termino con codigo:", error.code)

    finally:
        if compilador is not None:
            compilador.lexico.cerrar()

            if not compilador.generaCodigo.salida.closed:
                compilador.generaCodigo.salida.close()
