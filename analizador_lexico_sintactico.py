from pathlib import Path
import sys
from arbo_sintactico import NodoAST

class Archivo:

    def leer_archivo(self, ruta):
        return Path(ruta).read_text(encoding="utf-8")

    def escribir_archivo(self, ruta, texto):
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")

class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna




class AnalizadorLexico:

    # Palabras reservadas de Scheme
    PALABRAS_RESERVADAS = {
        "if",
        "define",
        "set!",
        "begin",
        "lambda",
        "cond",
        "else"
    }
    # Operadores matemáticos y relacionales
    OPERADORES = {
        "+", "-", "*", "/",
        "=", ">", "<", ">=", "<="
    }

    DELIMITADORES = {"(", ")"}

    def analizar(self, codigo):

        tokens = []
        errores = []

        i = 0
        linea = 1
        columna = 1

        def avanzar(cantidad=1):
            nonlocal i, linea, columna

            texto = codigo[i:i + cantidad]

            for caracter in texto:
                if caracter == "\n":
                    linea += 1
                    columna = 1
                else:
                    columna += 1

            i += cantidad

        while i < len(codigo):

            caracter = codigo[i]

            inicio_linea = linea
            inicio_columna = columna

            # ESPACIOS Y SALTOS DE LINEA
            if caracter.isspace():
                avanzar()
                continue

            # COMENTARIOS DE UNA LINEA
            if caracter == ";":
                while i < len(codigo) and codigo[i] != "\n":
                    avanzar()
                continue

            # COMENTARIOS DE VARIAS LINEAS
            if codigo.startswith("#|", i):

                fin = codigo.find("|#", i + 2)

                if fin == -1:
                    errores.append(
                        f"Error léxico línea {linea}: "
                        "comentario sin cerrar."
                    )
                    avanzar(len(codigo) - i)
                    continue

                avanzar(fin + 2 - i)
                continue

            # CADENAS DE TEXTO
            if caracter == '"':

                j = i + 1

                while j < len(codigo):

                    if codigo[j] == "\\":
                        j += 2

                    elif codigo[j] == '"':
                        break

                    else:
                        j += 1

                if j < len(codigo) and codigo[j] == '"':

                    valor = codigo[i:j + 1]

                    tokens.append(Token(
                        "CADENA",
                        valor,
                        inicio_linea,
                        inicio_columna
                    ))

                    avanzar(j + 1 - i)

                else:

                    errores.append(
                        f"Error léxico línea {linea}: "
                        "cadena sin cerrar."
                    )

                    avanzar()

                continue

            # VALORES BOOLEANOS
            if codigo.startswith("#t", i) or codigo.startswith("#f", i):

                valor = codigo[i:i + 2]

                tokens.append(Token(
                    "BOOLEANO",
                    valor,
                    inicio_linea,
                    inicio_columna
                ))

                avanzar(2)
                continue

            # DELIMITADORES
            if caracter in self.DELIMITADORES:

                tokens.append(Token(
                    "DELIMITADOR",
                    caracter,
                    inicio_linea,
                    inicio_columna
                ))

                avanzar()
                continue

            # NÚMEROS POSITIVOS, NEGATIVOS Y DECIMALES
            inicio_numero = (
                caracter.isdigit()
                or (
                    caracter in "+-"
                    and i + 1 < len(codigo)
                    and codigo[i + 1].isdigit()
                )
            )

            if inicio_numero:

                j = i

                if codigo[j] in "+-":
                    j += 1

                while j < len(codigo) and codigo[j].isdigit():
                    j += 1

                if (
                    j + 1 < len(codigo)
                    and codigo[j] == "."
                    and codigo[j + 1].isdigit()
                ):

                    j += 1

                    while j < len(codigo) and codigo[j].isdigit():
                        j += 1

                # Comprobar que el número no esté unido a un identificador
                if (
                    j < len(codigo)
                    and (
                        codigo[j].isalpha()
                        or codigo[j] in "_?!"
                    )
                ):

                    while (
                        j < len(codigo)
                        and not codigo[j].isspace()
                        and codigo[j] not in "()"
                    ):
                        j += 1

                    valor = codigo[i:j]

                    errores.append(
                        f"Error léxico línea {linea}: "
                        f"número o identificador inválido {valor!r}."
                    )

                    avanzar(j - i)
                    continue

                valor = codigo[i:j]

                tokens.append(Token(
                    "NUMERO",
                    valor,
                    inicio_linea,
                    inicio_columna
                ))

                avanzar(j - i)
                continue

            # OPERADORES
            operador_encontrado = None

            for operador in sorted(
                self.OPERADORES,
                key=len,
                reverse=True
            ):

                if codigo.startswith(operador, i):
                    operador_encontrado = operador
                    break

            if operador_encontrado is not None:

                tokens.append(Token(
                    "OPERADOR",
                    operador_encontrado,
                    inicio_linea,
                    inicio_columna
                ))

                avanzar(len(operador_encontrado))
                continue

            # IDENTIFICADORES Y PALABRAS RESERVADAS
            if (
                caracter.isalpha()
                or caracter in "_?!"
            ):

                j = i + 1

                while (
                    j < len(codigo)
                    and not codigo[j].isspace()
                    and codigo[j] not in "()"
                    and codigo[j] != ";"
                ):
                    j += 1

                valor = codigo[i:j]

                if valor in self.PALABRAS_RESERVADAS:
                    tipo_token = "PALABRA_RESERVADA"

                elif valor in self.OPERADORES:
                    tipo_token = "OPERADOR"

                else:
                    tipo_token = "ID"

                tokens.append(Token(
                    tipo_token,
                    valor,
                    inicio_linea,
                    inicio_columna
                ))

                avanzar(j - i)
                continue

            # CARACTERES DESCONOCIDOS
            errores.append(
                f"Error léxico línea {linea}, columna {columna}: "
                f"carácter no reconocido {caracter!r}."
            )

            avanzar()

        # FIN DEL ARCHIVO
        tokens.append(Token(
            "EOF",
            "",
            linea,
            columna
        ))

        return tokens, errores





class AnalizadorSintactico:

    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

        self.advertencias = []
        self.errores = []

        # Pila de ámbitos
        self.ambitos = [{}]

        # Tabla de símbolos
        self.tabla = []

        # Árbol sintáctico
        self.arbol = NodoAST("Programa")

    def actual(self):
        return self.tokens[self.i]

    def avanzar(self):
        t = self.actual()

        if t.tipo != "EOF":
            self.i += 1

        return t

    def aceptar(self, tipo=None, valor=None):
        t = self.actual()

        if tipo is not None and t.tipo != tipo:
            return None

        if valor is not None and t.valor != valor:
            return None

        return self.avanzar()

    def esperar(self, tipo, valor, descripcion):
        if self.aceptar(tipo, valor):
            return True

        t = self.actual()

        self.errores.append(
            f"Error sintáctico línea {t.linea}: "
            f"se esperaba {descripcion}; "
            f"se encontró {t.valor!r}."
        )

        return False

    def buscar_variable(self, nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]

        return None

    def inferir_tipo(self, nodo):
        if nodo is None:
            return None

        if nodo.tipo == "Numero":
            return "double" if "." in nodo.valor else "int"

        if nodo.tipo == "Cadena":
            return "str"

        if nodo.tipo == "Booleano":
            return "bool"

        if nodo.tipo == "Comparacion":
            return "bool"

        if nodo.tipo == "Variable":
            variable = self.buscar_variable(nodo.valor)
            return variable["tipo"] if variable else None

        if nodo.tipo == "Operacion":
            tipos = [
                self.inferir_tipo(hijo)
                for hijo in nodo.hijos
            ]

            if "double" in tipos:
                return "double"

            return "int"

        return None

    def analizar(self):

        while self.actual().tipo != "EOF":

            antes = self.i

            nodo = self.expresion()

            if nodo is not None:
                self.arbol.agregar_hijo(nodo)

            if self.i == antes:
                self.avanzar()

        return self.advertencias, self.errores, self.tabla

    def expresion(self):

        t = self.actual()

        # Expresiones entre paréntesis
        if self.aceptar("DELIMITADOR", "("):

            funcion = self.actual()

            if funcion.tipo == "EOF":
                self.errores.append(
                    f"Error sintáctico línea {funcion.linea}: "
                    "expresión sin cerrar."
                )
                return None

            self.avanzar()

            # DEFINICIÓN DE VARIABLES
            if funcion.valor == "define":
                return self.definicion(funcion)
            if funcion.valor == "cond":
                return self.condicional_multiple(funcion)
            if funcion.valor == "set!":
                return self.asignacion(funcion)
            # CONDICIONAL IF
            if funcion.valor == "if":
                return self.condicional(funcion)

            # BLOQUE BEGIN
            if funcion.valor == "begin":
                return self.bloque_begin(funcion)

            # IMPRESIÓN DISPLAY
            if funcion.valor == "display":
                return self.impresion(funcion)

            # OPERACIONES MATEMÁTICAS Y COMPARACIONES
            if funcion.valor in {
                "+", "-", "*", "/", "=", ">", "<", ">=", "<="
            }:
                return self.operacion(funcion)

            self.errores.append(
                f"Error sintáctico línea {funcion.linea}: "
                f"función no reconocida {funcion.valor!r}."
            )

            self.recuperar_parentesis()
            return None

        # NÚMEROS
        if t.tipo == "NUMERO":
            self.avanzar()
            return NodoAST("Numero", t.valor)

        # CADENAS
        if t.tipo == "CADENA":
            self.avanzar()
            return NodoAST("Cadena", t.valor)

        # BOOLEANOS
        if t.tipo == "BOOLEANO":
            self.avanzar()

            valor = "true" if t.valor == "#t" else "false"

            return NodoAST("Booleano", valor)

        # VARIABLES
        if t.tipo == "ID":
            self.avanzar()

            if self.buscar_variable(t.valor) is None:
                self.advertencias.append(
                    f"Advertencia línea {t.linea}: "
                    f"variable {t.valor!r} no declarada."
                )

            return NodoAST("Variable", t.valor)

        self.errores.append(
            f"Error sintáctico línea {t.linea}: "
            f"expresión inesperada {t.valor!r}."
        )

        if t.tipo != "EOF":
            self.avanzar()

        return None

    def definicion(self, token):

        nombre = self.actual()

        if nombre.tipo != "ID":
            self.errores.append(
                f"Error sintáctico línea {nombre.linea}: "
                "se esperaba un nombre de variable después de define."
            )

            self.recuperar_parentesis()
            return None

        self.avanzar()

        expresion = self.expresion()

        if not self.esperar(
            "DELIMITADOR", ")", "')' para cerrar define"
        ):
            return None

        tipo = self.inferir_tipo(expresion)

        ambito_actual = self.ambitos[-1]

        if nombre.valor in ambito_actual:
            self.advertencias.append(
                f"Advertencia línea {nombre.linea}: "
                f"la variable {nombre.valor!r} ya fue definida."
            )
        else:
            informacion = {
                "nombre": nombre.valor,
                "tipo": tipo or "desconocido",
                "linea": nombre.linea,
                "ambito": len(self.ambitos) - 1
            }

            ambito_actual[nombre.valor] = informacion
            self.tabla.append(informacion)

        nodo = NodoAST("Declaracion", nombre.valor)

        nodo.agregar_hijo(
            NodoAST("Tipo", tipo or "desconocido")
        )

        nodo.agregar_hijo(expresion)

        return nodo


    def asignacion(self, token):
        nombre = self.actual()

        if nombre.tipo != "ID":
            self.errores.append(
                f"Error sintáctico línea {nombre.linea}: "
                "se esperaba una variable después de set!."
            )
            self.recuperar_parentesis()
            return None

        self.avanzar()

        expresion = self.expresion()

        if not self.esperar(
            "DELIMITADOR", ")", "')' para cerrar set!"
        ):
            return None

        if self.buscar_variable(nombre.valor) is None:
            self.errores.append(
                f"Error semántico línea {nombre.linea}: "
                f"la variable {nombre.valor!r} no está definida."
            )
            return None

        nodo = NodoAST("Asignacion", nombre.valor)
        nodo.agregar_hijo(expresion)

        return nodo

    def condicional(self, token):

        condicion = self.expresion()
        verdadero = self.expresion()
        falso = self.expresion()

        if not self.esperar(
            "DELIMITADOR", ")", "')' para cerrar if"
        ):
            return None

        nodo = NodoAST("Condicional", "if")

        nodo.agregar_hijo(condicion)
        nodo.agregar_hijo(verdadero)
        nodo.agregar_hijo(falso)

        return nodo
    
    def condicional_multiple(self, token):

        nodo = NodoAST("CondicionalMultiple", "cond")

        while (
            self.actual().tipo != "EOF"
            and self.actual().valor == "("
        ):

            self.avanzar()

            condicion = self.actual()

            if condicion.valor == "else":
                self.avanzar()
                condicion_nodo = NodoAST("Else", "else")
            else:
                condicion_nodo = self.expresion()

            bloque = NodoAST("Caso")

            bloque.agregar_hijo(condicion_nodo)

            while (
                self.actual().tipo != "EOF"
                and self.actual().valor != ")"
            ):
                antes = self.i
                expresion = self.expresion()

                if expresion is not None:
                    bloque.agregar_hijo(expresion)

                if self.i == antes:
                    self.avanzar()

            self.esperar(
                "DELIMITADOR", ")", "')' para cerrar caso"
            )

            nodo.agregar_hijo(bloque)

        self.esperar(
            "DELIMITADOR", ")", "')' para cerrar cond"
        )

        return nodo

    def bloque_begin(self, token):

        nodo = NodoAST("Bloque", "begin")

        while (
            self.actual().tipo != "EOF"
            and self.actual().valor != ")"
        ):

            antes = self.i
            expresion = self.expresion()

            if expresion is not None:
                nodo.agregar_hijo(expresion)

            if self.i == antes:
                self.avanzar()

        self.esperar(
            "DELIMITADOR", ")", "')' para cerrar begin"
        )

        return nodo

    def impresion(self, token):

        expresion = self.expresion()

        if not self.esperar(
            "DELIMITADOR", ")", "')' para cerrar display"
        ):
            return None

        nodo = NodoAST("Impresion", "display")
        nodo.agregar_hijo(expresion)

        return nodo

    def operacion(self, token):

        operador = token.valor

        izquierdo = self.expresion()
        derecho = self.expresion()

        if not self.esperar(
            "DELIMITADOR", ")", "')' para cerrar operación"
        ):
            return None

        if operador in {">", "<", ">=", "<=", "="}:
            tipo_nodo = "Comparacion"
        else:
            tipo_nodo = "Operacion"

        nodo = NodoAST(tipo_nodo, operador)

        nodo.agregar_hijo(izquierdo)
        nodo.agregar_hijo(derecho)

        return nodo

    def recuperar_parentesis(self):

        profundidad = 1

        while self.actual().tipo != "EOF":

            t = self.avanzar()

            if t.valor == "(":
                profundidad += 1

            elif t.valor == ")":
                profundidad -= 1

                if profundidad == 0:
                    break


""" este ejecuta ensenando todo el analisis, el otro solo el warning
def ejecutar(ruta_entrada, ruta_salida=None):
    ruta_entrada = Path(ruta_entrada)
    ruta_salida = Path(ruta_salida) if ruta_salida else (
        ruta_entrada.parent / "resultado_analisis.txt"
    )

    archivo = Archivo()
    codigo = archivo.leer_archivo(ruta_entrada)

    tokens, errores_lexicos = AnalizadorLexico().analizar(codigo)
    sintactico = AnalizadorSintactico(tokens)

    advertencias, errores_sintacticos, tabla = sintactico.analizar()

    salida = [
        "ANÁLISIS LÉXICO Y SINTÁCTICO",
        "\n1. TOKENS IDENTIFICADOS",
    ]

    salida.extend(f"{t.tipo:<18} {t.valor!r:<20} línea {t.linea}, columna {t.columna}"
        for t in tokens if t.tipo != "EOF"
    )

    salida += ["\n2. TABLA DE SÍMBOLOS", ]

    if tabla:
        for info in tabla:
            salida.append(
                f"{info['nombre']:<15} "
                f"tipo={info['tipo']:<10} "
                f"línea={info['linea']:<5} "
                f"ámbito={info['ambito']}"
            )
    else:
        salida.append("No se registraron variables.")

    salida += ["\n3. ADVERTENCIAS", "-"]

    todas_advertencias = advertencias + errores_lexicos + errores_sintacticos

    if todas_advertencias:
        salida.extend(todas_advertencias)
    else:
        salida.append("Sin advertencias.")


    if errores_lexicos or errores_sintacticos:
        salida.append("ANÁLISIS FINALIZADO CON ERRORES.")
    elif advertencias:
        salida.append("ANÁLISIS FINALIZADO CON ADVERTENCIAS.")
    else:
        salida.append("ANÁLISIS FINALIZADO CORRECTAMENTE.")


    reporte = "\n".join(salida)

    print(reporte)

    archivo.escribir_archivo(ruta_salida, reporte)


    return reporte
"""


#"""
def ejecutar(ruta_entrada, ruta_salida=None):

    ruta_entrada = Path(ruta_entrada)

    ruta_salida = Path(ruta_salida) if ruta_salida else (
        ruta_entrada.parent / "resultado_analisis.txt"
    )

    archivo = Archivo()

    codigo = archivo.leer_archivo(ruta_entrada)

    reporte = analizar_codigo(codigo)

    print(reporte)

    archivo.escribir_archivo(ruta_salida, reporte)

    return reporte
#"""


def analizar_codigo(codigo, devolver_ast=False):

    # 1. ANÁLISIS LÉXICO
    tokens, errores_lexicos = AnalizadorLexico().analizar(codigo)

    # 2. ANÁLISIS SINTÁCTICO
    sintactico = AnalizadorSintactico(tokens)

    advertencias, errores_sintacticos, tabla = sintactico.analizar()

    # 3. GENERAR REPORTE
    salida = [
        "ADVERTENCIAS Y ERRORES",
        "----------------------------------------"
    ]

    todos_los_mensajes = (
        errores_lexicos +
        errores_sintacticos +
        advertencias
    )

    if todos_los_mensajes:
        salida.extend(todos_los_mensajes)
    else:
        salida.append("Sin advertencias.")

    # 4. RESULTADO FINAL
    if errores_lexicos or errores_sintacticos:
        salida.append("\nANÁLISIS FINALIZADO CON ERRORES.")

    elif advertencias:
        salida.append("\nANÁLISIS FINALIZADO CON ADVERTENCIAS.")

    else:
        salida.append("\nANÁLISIS FINALIZADO CORRECTAMENTE.")

    reporte = "\n".join(salida)

    # 5. DEVOLVER REPORTE Y AST SI SE SOLICITA
    if devolver_ast:
        return reporte, sintactico.arbol

    return reporte


if __name__ == "__main__":
    entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).with_name("prueba.txt")
    )
    try:
        ejecutar(entrada)
    except (FileNotFoundError, OSError) as e:
        print(f"Error de archivo: {e}")
        print(
            "Coloca prueba.txt junto al programa o ejecuta: "
            "python analizador_lexico_sintactico.py ruta\\archivo.txt"
        )
