class Automata:

    def __init__(self):
        self.estado = 'inicio'
        self.caracteres_prohibidos = {
            '$', '#', '/', '(', '@', '-', '"', '|',
            ':', ';', '.', ',', '?', '!', ')', '&',
            '<', '>'}

    def transicion(self, caracter):
        if self.estado == 'inicio':
            # Primer caracter: letra o _
            if (caracter.isalpha() or caracter == '_') and \
               caracter not in self.caracteres_prohibidos:
                self.estado = 'valido'
            else:
                self.estado = 'invalido'

        elif self.estado == 'valido':
            # Siguientes caracteres: letra, numero o _
            if (caracter.isalnum() or caracter == '_') and \
               caracter not in self.caracteres_prohibidos:
                self.estado = 'valido'
            else:
                self.estado = 'invalido'

    def es_valida(self, cadena):
        self.estado = 'inicio'
        if cadena == '':
            return False

        for caracter in cadena:
            self.transicion(caracter)
            if self.estado == 'invalido':
                return False
        return self.estado == 'valido'


class lexico:

    def __init__(self):
        self.automata = Automata()
        self.operadores = {
            '+': 'TKN OP',
            '-': 'TKN OP',
            '*': 'TKN OP',
            '=': 'TKN OP'}

        self.operadores_division = {
            '/': 'TKN OPDIV'}

        self.simbolos = {
            '(': 'TKN PARIZQ',
            ')': 'TKN PARDER',
            ';': 'TKN PUNTOCOMA',
            ',': 'TKN COMA'}

    def tokenizar(self, texto):
        tokens = []
        palabra = ''
        i = 0
        while i < len(texto):
            caracter = texto[i]
            # Espacios
            if caracter.isspace():
                if palabra:
                    self.agregar_identificador(palabra, tokens)
                    palabra = ''

                i += 1
                continue
            # Identificadores
            if caracter.isalnum() or caracter == '_':
                palabra += caracter
                i += 1
                continue

            # Terminamos palabra anterior
            if palabra:
                self.agregar_identificador(palabra, tokens)
                palabra = ''

            # Operadores
            if caracter in self.operadores:

                tokens.append(
                    f"<{self.operadores[caracter]}, {caracter}>"
                )

            # Division
            elif caracter in self.operadores_division:

                tokens.append(
                    f"<{self.operadores_division[caracter]}, {caracter}>"
                )

            # Simbolos
            elif caracter in self.simbolos:

                tokens.append(
                    f"<{self.simbolos[caracter]}, {caracter}>"
                )

            # Caracter desconocido
            else:

                tokens.append(
                    f"<TKN INVALIDO, {caracter}>"
                )

            i += 1

        # Procesar ultima palabra
        if palabra:
            self.agregar_identificador(palabra, tokens)

        return tokens

    def agregar_identificador(self, palabra, tokens):

        if self.automata.es_valida(palabra):

            tokens.append(
                f"<TKN ID, {palabra}>"
            )

        else:

            tokens.append(
                f"<TKN INVALIDO, {palabra}>")

# PRUEBA

Lexico = lexico()

texto = "a + b /return"

tokens = Lexico.tokenizar(texto)

for token in tokens:
    print(token)
