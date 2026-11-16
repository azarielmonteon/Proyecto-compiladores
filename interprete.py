from decimal import Decimal

class Interprete:

    def __init__(self):
        # Diccionario para almacenar las variables
        self.variables = {}

    # Ejecutar el programa
    def ejecutar(self, arbol):

        salida = []

        self.ejecutar_nodo(arbol, salida)

        return "\n".join(salida)

    # Recorrer los nodos del AST
    def ejecutar_nodo(self, nodo, salida):

        if nodo is None:
            return

        if nodo.tipo in {"Programa", "Funcion", "Bloque"}:

            for hijo in nodo.hijos:
                self.ejecutar_nodo(hijo, salida)

        elif nodo.tipo == "Declaracion":

            nombre = nodo.valor
            expresion = nodo.hijos[1] if len(nodo.hijos) > 1 else None

            if expresion is not None:
                valor = self.evaluar_expresion(expresion)
            else:
                valor = None

            self.variables[nombre] = valor

        elif nodo.tipo == "Impresion":

            if nodo.hijos:
                valor = self.evaluar_expresion(nodo.hijos[0])
                salida.append(str(valor))

        elif nodo.tipo == "Condicional":

            condicion = self.evaluar_expresion(nodo.hijos[0])

            # En Scheme solamente #f representa falso
            if condicion is not False:
                self.ejecutar_nodo(nodo.hijos[1], salida)
            else:
                self.ejecutar_nodo(nodo.hijos[2], salida)

        elif nodo.tipo == "CondicionalMultiple":

            for caso in nodo.hijos:

                condicion = caso.hijos[0]

                # Caso alternativo
                if condicion.tipo == "Else":
                    for expresion in caso.hijos[1:]:
                        self.ejecutar_nodo(expresion, salida)
                    break

                # Evaluar condición
                resultado = self.evaluar_expresion(condicion)

                if resultado is not False:
                    for expresion in caso.hijos[1:]:
                        self.ejecutar_nodo(expresion, salida)
                    break



        elif nodo.tipo == "CicloFor":

            nombre = nodo.valor

            inicio = self.evaluar_expresion(nodo.hijos[0])
            fin = self.evaluar_expresion(nodo.hijos[1])
            incremento = self.evaluar_expresion(nodo.hijos[2])

            cuerpo = nodo.hijos[3]

            variable_existia = nombre in self.variables

            if variable_existia:
                valor_anterior = self.variables[nombre]

            if incremento == 0:
                raise Exception(
                    "El incremento del ciclo for no puede ser cero."
                )

            if incremento > 0:

                i = inicio

                while i <= fin:

                    self.variables[nombre] = i

                    self.ejecutar_nodo(cuerpo, salida)

                    i += incremento

            else:

                i = inicio

                while i >= fin:

                    self.variables[nombre] = i

                    self.ejecutar_nodo(cuerpo, salida)

                    i += incremento

            # Restaurar el valor original de la variable
            if variable_existia:
                self.variables[nombre] = valor_anterior
            else:
                del self.variables[nombre]




        elif nodo.tipo == "CicloWhile":

            condicion = nodo.hijos[0]
            cuerpo = nodo.hijos[1]

            # Ejecutar mientras la condición sea verdadera
            while self.evaluar_expresion(condicion) is not False:

                self.ejecutar_nodo(cuerpo, salida)



        elif nodo.tipo == "Asignacion":

            nombre = nodo.valor

            if nombre not in self.variables:
                raise Exception(
                    f"La variable '{nombre}' no está definida."
                )

            if not nodo.hijos:
                raise Exception(
                    f"No se proporcionó un valor para '{nombre}'."
                )

            expresion = nodo.hijos[0]
            valor = self.evaluar_expresion(expresion)

            self.variables[nombre] = valor

    # Evaluar expresiones
    def evaluar_expresion(self, nodo):

        if nodo is None:
            return None

        if nodo.tipo == "Numero":

            if "." in nodo.valor:
                return Decimal(nodo.valor)

            return int(nodo.valor)

        elif nodo.tipo == "Variable":

            nombre = nodo.valor

            if nombre not in self.variables:
                raise Exception(
                    f"Variable {nombre!r} no declarada."
                )

            return self.variables[nombre]

        elif nodo.tipo == "Cadena":

            return nodo.valor.strip('"')

        elif nodo.tipo == "Booleano":

            return nodo.valor == "true"

        elif nodo.tipo == "Lista":

            elementos = []

            for hijo in nodo.hijos:
                valor = self.evaluar_expresion(hijo)
                elementos.append(valor)

            return elementos

        elif nodo.tipo == "LongitudLista":

            lista = self.evaluar_expresion(nodo.hijos[0])

            if not isinstance(lista, list):
                raise Exception(
                    "La función length necesita una lista."
                )

            return len(lista)

        elif nodo.tipo == "Operacion":

            izquierdo = self.evaluar_expresion(nodo.hijos[0])
            derecho = self.evaluar_expresion(nodo.hijos[1])

            operador = nodo.valor

            if operador == "+":
                return izquierdo + derecho

            elif operador == "-":
                return izquierdo - derecho

            elif operador == "*":
                return izquierdo * derecho

            elif operador == "/":
                return izquierdo / derecho

        elif nodo.tipo == "Comparacion":

            izquierdo = self.evaluar_expresion(nodo.hijos[0])
            derecho = self.evaluar_expresion(nodo.hijos[1])

            operador = nodo.valor

            if operador == "=":
                return izquierdo == derecho

            elif operador == ">":
                return izquierdo > derecho

            elif operador == "<":
                return izquierdo < derecho

            elif operador == ">=":
                return izquierdo >= derecho

            elif operador == "<=":
                return izquierdo <= derecho

        raise Exception(
            f"Expresión no reconocida: {nodo.tipo}"
        )
