# ARBOL DE SINTAXIS ABSTRACTA (AST)

class NodoAST:

    def __init__(self, tipo, valor=None, hijos=None):

        self.tipo = tipo
        self.valor = valor

        # Lista de nodos hijos
        self.hijos = hijos if hijos is not None else []

    # Agregar un hijo al nodo
    def agregar_hijo(self, hijo):

        if hijo is not None:
            self.hijos.append(hijo)

    # Representacion del nodo
    def __repr__(self):

        return f"NodoAST({self.tipo}, {self.valor})"

    # Imprimir el arbol en consola
    def imprimir(self, nivel=0):

        indentacion = "    " * nivel

        if self.valor is not None:
            print(f"{indentacion}{self.tipo}: {self.valor}")
        else:
            print(f"{indentacion}{self.tipo}")

        for hijo in self.hijos:
            hijo.imprimir(nivel + 1)

    # Obtener el arbol como una cadena de texto
    def como_texto(self, nivel=0):

        indentacion = "    " * nivel

        if self.valor is not None:
            resultado = f"{indentacion}{self.tipo}: {self.valor}"
        else:
            resultado = f"{indentacion}{self.tipo}"

        for hijo in self.hijos:
            resultado += "\n" + hijo.como_texto(nivel + 1)

        return resultado


# ==========================================
# FUNCIONES AUXILIARES PARA CREAR NODOS
# ==========================================

def crear_nodo(tipo, valor=None, *hijos):

    return NodoAST(
        tipo,
        valor,
        list(hijos)
    )


# ==========================================
# PRUEBA INDEPENDIENTE DEL AST
# ==========================================

if __name__ == "__main__":

    # Crear nodo principal
    raiz = NodoAST("Programa")

    # Crear una declaracion
    declaracion = NodoAST(
        "Declaracion",
        "int edad"
    )

    # Crear una expresion matematica
    suma = NodoAST("Operacion", "+")

    numero1 = NodoAST("Numero", "10")
    numero2 = NodoAST("Numero", "20")

    suma.agregar_hijo(numero1)
    suma.agregar_hijo(numero2)

    # Agregar expresion a declaracion
    declaracion.agregar_hijo(suma)

    # Agregar declaracion al programa
    raiz.agregar_hijo(declaracion)

    # Mostrar AST
    print("========== ARBOL AST ==========\n")

    raiz.imprimir()
