#token

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
        # Ignorar espacios en blanco
        while (self.index < len(self.origen)
               and self.origen[self.index].isspace()):
            self.index += 1

        # Detectar el fin de la expresión
        if self.index >= len(self.origen):
            return Token(Token.Type.Fin, "")

        entrada_actual = self.origen[self.index]

        # Identificar números enteros
        if entrada_actual.isdigit():
            num = ""

            while (self.index < len(self.origen)
                   and self.origen[self.index].isdigit()):
                num += self.origen[self.index]
                self.index += 1

            return Token(Token.Type.Numero, num)

        # Identificar operadores
        self.index += 1

        if entrada_actual == '+':
            return Token(Token.Type.Suma, "+")
        elif entrada_actual == '-':
            return Token(Token.Type.Resta, "-")
        elif entrada_actual == '*':
            return Token(Token.Type.Multiplicar, "*")
        elif entrada_actual == '/':
            return Token(Token.Type.Dividir, "/")
        else:
            return Token(Token.Type.Invalido, entrada_actual)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token_actual = lexer.next_token()

    def parse(self):
        while self.token_actual.type != Token.Type.Fin:

            if self.token_actual.type == Token.Type.Numero:
                print("Number: " + self.token_actual.value)

            elif self.token_actual.type == Token.Type.Suma:
                print("Operator: +")

            elif self.token_actual.type == Token.Type.Resta:
                print("Operator: -")

            elif self.token_actual.type == Token.Type.Multiplicar:
                print("Operator: *")

            elif self.token_actual.type == Token.Type.Dividir:
                print("Operator: /")

            elif self.token_actual.type == Token.Type.Invalido:
                print("Token inválido: " + self.token_actual.value)

            # Obtener el siguiente token
            self.token_actual = self.lexer.next_token()


if __name__ == "__main__":
    expresion = input("Introduce una expresión: ")
    lexer = Lexico(expresion)
    parser = Parser(lexer)
    parser.parse()
