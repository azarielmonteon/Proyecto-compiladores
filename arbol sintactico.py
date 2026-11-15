#arbol sintactico 
class Token:
    class Type:
        Numero = "Numero"
        Suma = "Suma"
        Resta = "Resta"
        Multiplica = "Multiplica"
        Divide = "Divide"
        Fin = "Fin"
        Invalido = "Invalido"

    def __init__(self, type, value):
        self.type = type
        self.value = value


class Lexer:
    def __init__(self, origen):
        self.origen = origen
        self.index = 0

    def next_token(self):
        while self.index < len(self.origen) and self.origen[self.index].isspace():
            self.index += 1

        if self.index >= len(self.origen):
            return Token(Token.Type.Fin, "")

        entrada_actual = self.origen[self.index]

        if entrada_actual.isdigit():
            num = ""

            while self.index < len(self.origen) and self.origen[self.index].isdigit():
                num += self.origen[self.index]
                self.index += 1

            return Token(Token.Type.Numero, num)

        self.index += 1

        if entrada_actual == '+':
            return Token(Token.Type.Suma, "+")
        elif entrada_actual == '-':
            return Token(Token.Type.Resta, "-")
        elif entrada_actual == '*':
            return Token(Token.Type.Multiplica, "*")
        elif entrada_actual == '/':
            return Token(Token.Type.Divide, "/")
        else:
            return Token(Token.Type.Invalido, entrada_actual)


class TreeNode:
    def __init__(self, token):
        self.token = token
        self.left = None
        self.right = None

    def __repr__(self):
        return f"Tree Node({self.token.type}, {self.token.value})"

    def print_tree(self, level=0):
        indent = " " * level

        if self.token.type == Token.Type.Numero:
            print(f"{indent}Numero: {self.token.value}")

        elif self.token.type == Token.Type.Suma:
            print(f"{indent}Suma: {self.token.value}")

        elif self.token.type == Token.Type.Resta:
            print(f"{indent}Resta: {self.token.value}")

        elif self.token.type == Token.Type.Multiplica:
            print(f"{indent}Multiplica: {self.token.value}")

        elif self.token.type == Token.Type.Divide:
            print(f"{indent}Divide: {self.token.value}")

        elif self.token.type == Token.Type.Invalido:
            print(f"{indent}Invalido: {self.token.value}")

        if self.left is not None:
            self.left.print_tree(level + 4)

        if self.right is not None:
            self.right.print_tree(level + 4)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token_actual = lexer.next_token()

    def parse(self):
        return self.expr()

    def expr(self):
        node = self.termino()

        while self.token_actual.type in (Token.Type.Suma, Token.Type.Resta):
            token = self.token_actual
            self.eat(token.type)

            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = self.termino()

            node = new_node

        return node

    def termino(self):
        node = self.factor()

        while self.token_actual.type in (Token.Type.Multiplica, Token.Type.Divide):
            token = self.token_actual
            self.eat(token.type)

            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = self.factor()

            node = new_node

        return node

    def factor(self):
        token = self.token_actual

        if token.type == Token.Type.Numero:
            self.eat(Token.Type.Numero)
            return TreeNode(token)

        raise SyntaxError(f"Token inesperado: {token.value}")

    def eat(self, token_type):
        if self.token_actual.type == token_type:
            self.token_actual = self.lexer.next_token()
        else:
            raise SyntaxError(
                f"Se esperaba {token_type}, pero se encontró {self.token_actual.type}"
            )


if __name__ == "__main__":
    expresion = input("Introduce una expresión: ")

    lexer = Lexer(expresion)
    parser = Parser(lexer)

    try:
        result = parser.parse()

        if parser.token_actual.type != Token.Type.Fin:
            raise SyntaxError(
                f"Entrada inválida: {parser.token_actual.value}"
            )

        print("\nÁrbol Sintáctico:")
        result.print_tree()

    except SyntaxError as error:
        print(f"\nError: {error}")