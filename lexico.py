#lexico
import sys
TAM_BUFFER = 100

class Lexico:
    def __init__(self, nombre_fichero, una_traza=0):
        self.nombre_fichero = nombre_fichero
        self.nl = 1
        self.traza = 1 if una_traza else 0
        self.buffer = []
        self.pBuffer = 0

        try:
            self.entrada = open(nombre_fichero, "r", encoding="utf-8")
        except OSError:
            print("No se puede abrir el fichero", nombre_fichero)
            sys.exit(-2)

    def cerrar(self):
        if not self.entrada.closed:
            self.entrada.close()


    def siguienteToken(self):
        # Recuperar primero los tokens devueltos al buffer
        if self.pBuffer > 0:
            self.pBuffer -= 1
            car = self.buffer[self.pBuffer]
            if self.existeTraza():
                print("ANALIZADOR LEXICO: Recupera del buffer el token", car)
            return car

        # Si no hay tokens en el buffer, leer del archivo
        while True:
            car = self.entrada.read(1)

            if car == "":
                return None

            if car == "\x00":
                continue

            if car == "\n":
                self.nl += 1
                continue

            if car.isspace():
                continue

            break

        if self.existeTraza():
            print("ANALIZADOR LEXICO: Lee el token", car)

        tokens_especiales = [
            "M", "R", "W", "=", "(", ")", ";",
            "{", "}", ".", "+", "-", "*", "/", "&", "%"
        ]

        if car in tokens_especiales:
            return car

        if car.isascii() and car.islower() and car.isalpha():
            return car

        if car.isdigit() and car.isascii():
            return car

        print(
            f"ERROR LEXICO: TOKEN DESCONOCIDO '{car}' "
            f"en la linea {self.nl}"
        )
        sys.exit(-4)


    def devuelveToken(self, token):
        if token is None:
            return

        if self.pBuffer >= TAM_BUFFER:
            print("ERROR: DESBORDAMIENTO DEL BUFFER DEL ANALIZADOR LEXICO")
            sys.exit(-5)

        if self.pBuffer < len(self.buffer):
            self.buffer[self.pBuffer] = token
        else:
            self.buffer.append(token)

        self.pBuffer += 1

        if self.existeTraza():
            print("ANALIZADOR LEXICO: Recibe en buffer el token", token)

    def lineaActual(self):
        return self.nl

    def existeTraza(self):
        return 1 if self.traza else 0


if __name__ == "__main__":
    nombre = input("Nombre del archivo fuente: ")
    traza = input("¿Activar traza? (s/n): ").lower() == "s"

    lexico = Lexico(nombre, traza)

    try:
        print("\nTokens encontrados:")

        while True:
            token = lexico.siguienteToken()

            if token is None:
                break

            print("Token:", token)

        print("\nAnalisis lexico terminado.")
        print("Numero de linea:", lexico.lineaActual())

    finally:
        lexico.cerrar()
