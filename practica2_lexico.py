class Token:
    class Type:
        Numero = "Numero"
        Suma = "Suma"
        Resta = "Resta"
        Multiplicar = "Multiplicar"
        Dividir = "Dividir"
        Fin = "Fin"
        Invalido = "Invalido"

    def __init__(self, type, value):
        self.type = type
        self.value = value


class Lexico:
    def __init__(self, origen):
        self.origen = origen
        self.index = 0

    def next_token(self):

        # Ignorar espacios
        while (self.index < len(self.origen)
               and self.origen[self.index].isspace()):
            self.index += 1

        # Fin de la expresión
        if self.index >= len(self.origen):
            return Token(Token.Type.Fin, "")

        ch = self.origen[self.index]
        # Número
        if ch.isdigit():
            num = ""

            while (self.index < len(self.origen)
                   and self.origen[self.index].isdigit()):
                num += self.origen[self.index]
                self.index += 1

            return Token(Token.Type.Numero, num)

        # Suma
        elif ch == '+':
            self.index += 1
            return Token(Token.Type.Suma, '+')

        # Resta
        elif ch == '-':
            self.index += 1
            return Token(Token.Type.Resta, '-')

        # Multiplicación
        elif ch == '*':
            self.index += 1
            return Token(Token.Type.Multiplicar, '*')

        # División
        elif ch == '/':
            self.index += 1
            return Token(Token.Type.Dividir, '/')

        # Carácter no reconocido
        else:
            self.index += 1
            return Token(Token.Type.Invalido, ch)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token_actual = lexer.next_token()

    def parse(self):

        while self.token_actual.type != Token.Type.Fin:

            if self.token_actual.type == Token.Type.Numero:
                print("Numero:", self.token_actual.value)

            elif self.token_actual.type == Token.Type.Suma:
                print("Operador: +")

            elif self.token_actual.type == Token.Type.Resta:
                print("Operador: -")

            elif self.token_actual.type == Token.Type.Multiplicar:
                print("Operador: *")

            elif self.token_actual.type == Token.Type.Dividir:
                print("Operador: /")

            elif self.token_actual.type == Token.Type.Invalido:
                print("Invalido:", self.token_actual.value)

            # Obtener el siguiente token
            self.token_actual = self.lexer.next_token()


if __name__ == "__main__":

    expresion = input("Introduce una expresión: ")
    lexer = Lexico(expresion)
    parser = Parser(lexer)
    parser.parse()
