class Automata:
    def __init__(self):
        self.estado = 'inicio'  # Estado inicial

    def transicion(self, caracter):
        if self.estado == 'inicio':
            # La variable debe comenzar con una letra o con el caracter _
            if caracter.isalpha() or caracter == '_':
                self.estado = 'valido'
            else:
                self.estado = 'invalido'

        elif self.estado == 'valido':
            # Después del primer carácter se permiten letras, números y _ segun yo
            if caracter.isalnum() or caracter == '_':
                self.estado = 'valido'
            else:
                self.estado = 'invalido'

    def aceptar(self):
        return self.estado == 'valido'

    def validar(self, variable):
        # Reiniciar el autómata
        self.estado = 'inicio'

        # Recorrer cada carácter de la variable
        for caracter in variable:
            self.transicion(caracter)

            # Si llega encuentra un invalido se detiene el proceso, regresa error 
            if self.estado == 'invalido':
                return False

        return self.aceptar()

automata = Automata()

#variable = input("Ingresa el nombre de una variable: ")

#pruebas
variables = ['variable','nombre', 'nombreUsuario', 'nombre_usuario', 'usuario1','1variable','123nombre','nombre/usuario','nombre@usuario','@variable'
            ,'/variable','%variable','+variable','nombre&usuario','nombre?usuario']

for variable in variables:
    if automata.validar(variable):
        print(variable, "-> Variable válida")
    else:
        print(variable, "-> Variable inválida")