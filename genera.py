
# genera

class GeneraCodigo:
    def __init__(self, unNombreFichero):
        # Nombre del fichero objeto de salida
        self.nombreFichero = unNombreFichero

        # Fichero objeto de salida
        try:
            self.salida = open(unNombreFichero, "w", encoding="utf-8")
        except OSError:
            print("No se puede crear el fichero", unNombreFichero)
            raise SystemExit(-3)

    def __del__(self):
        if hasattr(self, "salida") and not self.salida.closed:
            self.salida.close()

    def code(self):
        print(".CODE")
        self.salida.write(".CODE\n")

    def pushc(self, constante):
        print("PUSHC", constante)
        self.salida.write("PUSHC " + str(constante) + "\n")

    def push(self, direccion):
        print("PUSHA", direccion)
        self.salida.write("PUSHA " + str(direccion) + "\n")

    def load(self):
        print("LOAD")
        self.salida.write("LOAD\n")

    def store(self):
        print("STORE")
        self.salida.write("STORE\n")

    def neg(self):
        print("NEG")
        self.salida.write("NEG\n")

    def add(self):
        print("ADD")
        self.salida.write("ADD\n")

    def sub(self):
        print("SUB")
        self.salida.write("SUB\n")

    def mul(self):
        print("MUL")
        self.salida.write("MUL\n")

    def div(self):
        print("DIV")
        self.salida.write("DIV\n")

    def mod(self):
        print("MOD")
        self.salida.write("MOD\n")

    def input(self, direccion):
        print("INPUT", direccion)
        self.salida.write("INPUT " + str(direccion) + "\n")

    def output(self, direccion):
        print("OUTPUT", direccion)
        self.salida.write("OUTPUT " + str(direccion) + "\n")

    def end(self):
        print("END")
        self.salida.write("END\n")
