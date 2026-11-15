#lexer act 7
from enum import Enum

class Token(Enum):
    NUMERO = 'NUMERO'
    SUMA = 'SUMA'
    MENOS = 'MENOS'
    DIV = 'DIV'
    MUL = 'MUL'
    END = 'END'
    INVALIDO = 'INVALIDO'


class Lexer:
    def __init__(self, text):
        self._text = text
        self._pos = 0
        self._current_char = self._text[self._pos] if self._text else '\0'

    def _siguiente(self):
        self._pos += 1

        if self._pos >= len(self._text):
            self._current_char = '\0'
        else:
            self._current_char = self._text[self._pos]

    def get_next_token(self):
        while self._current_char != '\0':

            if self._current_char.isspace():
                self._siguiente()
                continue

            if self._current_char.isdigit():
                numero = ''

                while self._current_char.isdigit():
                    numero += self._current_char
                    self._siguiente()

                return Token.NUMERO

            if self._current_char == '+':
                self._siguiente()
                return Token.SUMA

            if self._current_char == '-':
                self._siguiente()
                return Token.MENOS

            if self._current_char == '*':
                self._siguiente()
                return Token.MUL

            if self._current_char == '/':
                self._siguiente()
                return Token.DIV

            self._siguiente()
            return Token.INVALIDO

        return Token.END


class Analizador:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def gramatica(self):
        while self.current_token != Token.END:

            if self.current_token == Token.NUMERO:
                print("Número encontrado")
                self.current_token = self.lexer.get_next_token()

            elif self.current_token in (
                Token.SUMA,
                Token.MENOS,
                Token.MUL,
                Token.DIV
            ):
                print("Operador encontrado:", self.current_token.value)
                self.current_token = self.lexer.get_next_token()

            else:
                print("Token inválido")
                return

        print("Expresión analizada correctamente")


entrada = input("Ingrese una expresión: ")

lexer = Lexer(entrada)
analizador = Analizador(lexer)
analizador.gramatica()
