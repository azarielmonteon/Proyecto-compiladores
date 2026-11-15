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
    # Tipos básicos que utilizaremos en nuestro subconjunto de C
    TIPOS_DATO = {
        "void",
        "char",
        "short",
        "int",
        "long",
        "float",
        "double",
        "_Bool"
    }

    # Palabras reservadas de C que iremos incorporando al parser
    PALABRAS_RESERVADAS = {
        "if", "else",
        "while", "do", "for",
        "switch", "case", "default",
        "break", "continue",
        "return",
        "sizeof",
        "const", "static",
        "struct", "typedef",
        "enum", "union",
        "extern", "register",
        "signed", "unsigned",
        "volatile", "auto"
    }

    # Ordenados para reconocer primero los operadores más largos
    OPERADORES = (
        ">>=", "<<=",
        "++", "--",
        "+=", "-=", "*=", "/=", "%=",
        "==", "!=", "<=", ">=",
        "&&", "||",
        "<<", ">>",
        "&=", "|=", "^=",
        "+", "-", "*", "/", "%",
        "=", "<", ">", "!",
        "&", "|", "^", "~",
        "?", ":", "."
    )

    DELIMITADORES = {
        "(", ")", "{", "}",
        "[", "]", ";", ","
    }


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

        def es_identificador(caracter):
            return caracter.isalnum() or caracter == "_"

        while i < len(codigo):

            inicio_linea = linea
            inicio_columna = columna
            caracter = codigo[i]

            # ESPACIOS, TABULACIONES Y SALTOS DE LINEA
            if caracter.isspace():
                avanzar()
                continue

            # COMENTARIOS
            if caracter == "/" and i + 1 < len(codigo):

                siguiente = codigo[i + 1]

                # Comentario de una linea //
                if siguiente == "/":
                    while i < len(codigo) and codigo[i] != "\n":
                        avanzar()
                    continue

                # Comentario de varias lineas /*
                elif siguiente == "*":
                    inicio = i
                    fin = codigo.find("*/", i + 2)

                    if fin == -1:
                        errores.append(
                            f"Error léxico línea {linea}: "
                            "comentario /* sin cerrar."
                        )
                        avanzar(len(codigo) - i)
                        continue

                    avanzar(fin + 2 - inicio)
                    continue

            # BIBLIOTECAS #include <...>
            if caracter == "#":

                j = i + 1

                while j < len(codigo) and codigo[j].isspace():
                    j += 1

                if codigo.startswith("include", j):
                    j += 7

                    while j < len(codigo) and codigo[j].isspace():
                        j += 1

                    if j < len(codigo) and codigo[j] == "<":
                        fin = codigo.find(">", j + 1)
                        salto = codigo.find("\n", j + 1)

                        if (fin != -1 and
                                (salto == -1 or fin < salto) and
                                fin > j + 1):

                            valor = codigo[i:fin + 1]

                            tokens.append(Token(
                                "BIBLIOTECA", valor,
                                inicio_linea, inicio_columna
                            ))

                            avanzar(fin + 1 - i)
                            continue

                # Si no es una biblioteca valida
                tokens.append(Token(
                    "DESCONOCIDO", caracter,
                    inicio_linea, inicio_columna
                ))

                errores.append(
                    f"Error léxico línea {linea}, columna {columna}: "
                    f"carácter no reconocido {caracter!r}."
                )

                avanzar()
                continue

            # CADENAS ENTRE COMILLAS DOBLES
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
                        "CADENA", valor,
                        inicio_linea, inicio_columna
                    ))

                    avanzar(j + 1 - i)

                else:
                    tokens.append(Token(
                        "DESCONOCIDO", caracter,
                        inicio_linea, inicio_columna
                    ))

                    errores.append(
                        f"Error léxico línea {linea}, columna {columna}: "
                        "cadena sin cerrar."
                    )

                    avanzar()

                continue

            # CARACTERES ENTRE COMILLAS SIMPLES
            if caracter == "'":
                j = i + 1

                while j < len(codigo):
                    if codigo[j] == "\\":
                        j += 2
                    elif codigo[j] == "'":
                        break
                    else:
                        j += 1

                if j < len(codigo) and codigo[j] == "'":
                    valor = codigo[i:j + 1]

                    tokens.append(Token(
                        "CARACTER", valor,
                        inicio_linea, inicio_columna
                    ))

                    avanzar(j + 1 - i)

                else:
                    tokens.append(Token(
                        "DESCONOCIDO", caracter,
                        inicio_linea, inicio_columna
                    ))

                    errores.append(
                        f"Error léxico línea {linea}, columna {columna}: "
                        "carácter sin cerrar."
                    )

                    avanzar()

                continue

            # NUMEROS E IDENTIFICADORES INVALIDOS
            if caracter.isdigit():

                j = i

                while j < len(codigo) and codigo[j].isdigit():
                    j += 1

                # Identificador que comienza con numero
                if j < len(codigo) and (
                    codigo[j].isalpha() or codigo[j] == "_"
                ):

                    while j < len(codigo) and es_identificador(codigo[j]):
                        j += 1

                    valor = codigo[i:j]

                    tokens.append(Token(
                        "ID_INVALIDO", valor,
                        inicio_linea, inicio_columna
                    ))

                    errores.append(
                        f"Error léxico línea {linea}: "
                        f"identificador inválido {valor!r}; "
                        "no puede comenzar con un número."
                    )

                    avanzar(j - i)
                    continue

                # Numero decimal
                if (j + 1 < len(codigo) and
                        codigo[j] == "." and
                        codigo[j + 1].isdigit()):

                    j += 1

                    while j < len(codigo) and codigo[j].isdigit():
                        j += 1

                valor = codigo[i:j]

                tokens.append(Token(
                    "NUMERO", valor,
                    inicio_linea, inicio_columna
                ))

                avanzar(j - i)
                continue

            # IDENTIFICADORES

            if caracter.isalpha() or caracter == "_":

                j = i + 1

                while j < len(codigo) and es_identificador(codigo[j]):
                    j += 1

                valor = codigo[i:j]

                if valor in self.TIPOS_DATO:
                    tipo_token = "TIPO_DATO"

                elif valor in self.PALABRAS_RESERVADAS:
                    tipo_token = "PALABRA_RESERVADA"

                else:
                    tipo_token = "ID"

                tokens.append(Token(
                    tipo_token, valor,
                    inicio_linea, inicio_columna
                ))

                avanzar(j - i)
                continue


            # OPERADORES: reconocer primero los más largos
            operador_encontrado = None

            for operador in self.OPERADORES:
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


            # DELIMITADORES
            if caracter in self.DELIMITADORES:

                tokens.append(Token(
                    "DELIMITADOR", caracter,
                    inicio_linea, inicio_columna
                ))

                avanzar()
                continue

            # CARACTERES DESCONOCIDOS
            tokens.append(Token(
                "DESCONOCIDO", caracter,
                inicio_linea, inicio_columna
            ))

            errores.append(
                f"Error léxico línea {linea}, columna {columna}: "
                f"carácter no reconocido {caracter!r}."
            )

            avanzar()

        # FIN DEL ARCHIVO
        tokens.append(Token("EOF", "", linea, columna))

        return tokens, errores


class AnalizadorSintactico:
    TIPOS = {"int", "double", "str", "string", "char", "bool"}

    
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

        self.advertencias = []
        self.errores = []

        # Pila de ámbitos
        self.ambitos = [{}]

        # Tabla de símbolos
        self.tabla = []

        # Árbol sintáctico AST
        self.arbol = NodoAST("Programa")

    def entrar_ambito(self):
        self.ambitos.append({})

    def salir_ambito(self):
        if len(self.ambitos) > 1:
            self.ambitos.pop()

    def buscar_variable(self, nombre):
        # Buscar desde el ámbito más interno hacia el exterior
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]

        return None

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
            f"Error sintáctico línea {t.linea}: se esperaba {descripcion}; "
            f"se encontró {t.valor!r}."
        )
        return False


    def analizar(self):

        # Buscar la función main
        while self.actual().tipo != "EOF":

            t = self.actual()

            # Ignorar bibliotecas
            if t.tipo == "BIBLIOTECA":
                self.avanzar()
                continue

            # Reconocer el tipo de retorno de main
            if t.tipo == "TIPO_DATO":

                # Guardar posición actual
                posicion = self.i

                tipo = self.avanzar()

                # Comprobar si después del tipo viene main
                if (
                    self.actual().tipo == "ID"
                    and self.actual().valor == "main"
                ):
                    break

                # No es la declaración de main
                self.i = posicion

            # Reconocer main
            if t.tipo == "ID" and t.valor == "main":
                break

            self.advertencias.append(
                f"Advertencia línea {t.linea}: "
                f"contenido fuera de main: {t.valor!r}."
            )

            self.avanzar()

        # Comprobar que se encontró main
        if self.actual().tipo == "EOF":
            self.errores.append(
                "Error sintáctico: no se encontró main()."
            )

            return self.advertencias, self.errores, self.tabla

        # Consumir el tipo de retorno si existe
        if self.actual().tipo == "TIPO_DATO":
            self.avanzar()

        # Consumir main
        self.esperar("ID", "main", "main")

        self.esperar(
            "DELIMITADOR", "(", "'(' después de main"
        )

        self.esperar(
            "DELIMITADOR", ")", "')' después de main"
        )

        # Crear nodo de función
        nodo_main = NodoAST("Funcion", "main")

        # Analizar cuerpo de main
        bloque_main = self.bloque()

        nodo_main.agregar_hijo(bloque_main)

        self.arbol.agregar_hijo(nodo_main)

        # Revisar contenido posterior a main
        while self.actual().tipo != "EOF":

            t = self.avanzar()

            self.advertencias.append(
                f"Advertencia línea {t.linea}: "
                f"contenido fuera de main: {t.valor!r}."
            )

        return self.advertencias, self.errores, self.tabla


        # Buscar main en cualquier posición
        while self.actual().tipo != "EOF":

            t = self.actual()

            if t.valor == "main" and t.tipo == "ID":
                break

            if t.tipo == "BIBLIOTECA":
                self.avanzar()
                continue

            self.advertencias.append(
                f"Advertencia línea {t.linea}: "
                f"contenido fuera de main: {t.valor!r}."
            )

            self.avanzar()

        if self.actual().tipo == "EOF":
            self.errores.append(
                "Error sintáctico: no se encontró main()."
            )

            return self.advertencias, self.errores, self.tabla

        # Reconocer main
        self.avanzar()

        self.esperar(
            "DELIMITADOR", "(", "'(' después de main"
        )

        self.esperar(
            "DELIMITADOR", ")", "')' después de main"
        )

        # Crear nodo de función
        nodo_main = NodoAST("Funcion", "main")

        # Obtener bloque
        bloque_main = self.bloque()

        nodo_main.agregar_hijo(bloque_main)

        self.arbol.agregar_hijo(nodo_main)

        while self.actual().tipo != "EOF":

            t = self.avanzar()

            self.advertencias.append(
                f"Advertencia línea {t.linea}: "
                f"contenido fuera de main: {t.valor!r}."
            )

        return self.advertencias, self.errores, self.tabla
  
    def bloque(self):

        apertura = self.aceptar("DELIMITADOR", "{")

        if not apertura:
            t = self.actual()

            self.errores.append(
                f"Error sintáctico línea {t.linea}: "
                "se esperaba '{'."
            )

            return None

        nodo_bloque = NodoAST("Bloque")

        self.entrar_ambito()

        while (
            self.actual().tipo != "EOF"
            and self.actual().valor != "}"
        ):

            antes = self.i
            t = self.actual()

            nodo = None

            if t.tipo == "TIPO_DATO":
                nodo = self.declaracion()

            elif t.tipo == "ID" and t.valor in {"print", "printf"}:
                nodo = self.impresion()

            elif t.tipo == "PALABRA_RESERVADA" and t.valor == "if":
                nodo = self.condicional()

            elif t.tipo == "PALABRA_RESERVADA" and t.valor == "return":
                nodo = self.retorno()

            elif t.tipo == "ID":
                nodo = self.asignacion()

            elif t.valor == "{":
                nodo = self.bloque()

            else:
                self.avanzar()

                self.errores.append(
                    f"Error sintáctico línea {t.linea}: "
                    f"token inesperado {t.valor!r}."
                )

            if nodo is not None:
                nodo_bloque.agregar_hijo(nodo)

            if self.i == antes:
                self.avanzar()

        if not self.aceptar("DELIMITADOR", "}"):
            self.errores.append(
                "Error sintáctico: falta '}' para cerrar el bloque."
            )

        self.salir_ambito()

        return nodo_bloque

   
    def condicional(self):
        # Consumir la palabra reservada if
        self.avanzar()

        # Comprobar apertura de paréntesis
        if not self.esperar("DELIMITADOR", "(", "'(' después de if"):
            return

        # Por ahora solamente avanzamos por la condición.
        # En el siguiente paso implementaremos su análisis.
        profundidad = 0

        while self.actual().tipo != "EOF":

            t = self.actual()

            if t.valor == "(":
                profundidad += 1

            elif t.valor == ")":
                if profundidad == 0:
                    break
                profundidad -= 1

            self.avanzar()

        # Comprobar cierre de paréntesis
        if not self.esperar("DELIMITADOR", ")", "')' después de la condición"):
            return

        # Analizar el bloque del if
        self.bloque()

    
    def retorno(self):
        # Consumir la palabra reservada return
        self.avanzar()

        # Si no hay un punto y coma, analizar el valor de retorno
        if self.actual().valor != ";":
            self.expresion()

        self.punto_coma("return")


    def declaracion(self):
        tipo = self.avanzar()
        nombre = self.actual()

        if nombre.tipo == "ID_INVALIDO":
            self.avanzar()
            self.errores.append(
                f"Error léxico/sintáctico línea {nombre.linea}: "
                f"nombre de variable inválido {nombre.valor!r}."
            )
            self.recuperar()
            return

        if nombre.tipo != "ID":
            self.errores.append(
                f"Error sintáctico línea {nombre.linea}: se esperaba un identificador "
                "después del tipo de dato."
            )
            self.recuperar()
            return

        self.avanzar()

        ambito_actual = self.ambitos[-1]
        if nombre.valor in ambito_actual:
            previo = ambito_actual[nombre.valor]

            self.advertencias.append(
                f"Warning línea {nombre.linea}: variable "
                f"{nombre.valor!r} declarada más de una vez "
                f"en el mismo ámbito (línea {previo['linea']})."
            )

        else:
            informacion = {
                "nombre": nombre.valor,
                "tipo": tipo.valor,
                "linea": nombre.linea,
                "ambito": len(self.ambitos) - 1
            }
            ambito_actual[nombre.valor] = informacion
            # Registrar todas las declaraciones
            self.tabla.append(informacion)
            
        if self.aceptar("OPERADOR", "="):
            tipo_valor = self.expresion()
            self.comprobar_tipo(tipo.valor, tipo_valor, nombre.valor, tipo.linea)
        self.punto_coma("declaración")


    def asignacion(self):
        nombre = self.avanzar()

        operadores_asignacion = {
            "=", "+=", "-=", "*=", "/=", "%="
        }

        operador = self.actual()

        if operador.tipo != "OPERADOR" or operador.valor not in operadores_asignacion:
            self.errores.append(
                f"Error sintáctico línea {nombre.linea}: "
                f"se esperaba un operador de asignación después de {nombre.valor!r}."
            )
            self.recuperar()
            return

        self.avanzar()

        tipo_valor = self.expresion()

        
        variable = self.buscar_variable(nombre.valor)

        if variable is None:
            self.advertencias.append(
                f"Warning undefined variable línea {nombre.linea}: "
                f"la variable {nombre.valor!r} no ha sido declarada."
            )
        else:
            tipo_variable = variable["tipo"]

            self.comprobar_tipo(
                tipo_variable,
                tipo_valor,
                nombre.valor,
                nombre.linea
            )

        self.punto_coma("asignación")

    def impresion(self):
        funcion = self.avanzar()
        self.esperar("DELIMITADOR", "(", "'(' después de print")
        if self.actual().valor != ")":
            self.expresion()
        self.esperar("DELIMITADOR", ")", "')' para cerrar print")
        self.punto_coma(funcion.valor)

    def expresion(self, minimo=0):
        tipo_izq = self.primario()
        prioridad = {"+": 1, "-": 1, "*": 2, "/": 2}

        while self.actual().tipo == "OPERADOR":
            op = self.actual().valor
            p = prioridad.get(op, -1)
            if p < minimo:
                break
            self.avanzar()
            tipo_der = self.expresion(p + 1)
            if "double" in {tipo_izq, tipo_der}:
                tipo_izq = "double"
            elif tipo_izq is None:
                tipo_izq = tipo_der
        return tipo_izq

    def primario(self):
        t = self.actual()
        if t.tipo == "NUMERO":
            self.avanzar()
            return "double" if "." in t.valor else "int"
        if t.tipo == "CADENA":
            self.avanzar()
            return "str"
        if t.tipo == "CARACTER":
            self.avanzar()
            return "char"
        if t.valor in {"true", "false"}:
            self.avanzar()
            return "bool"
        if t.tipo == "ID":
            self.avanzar()
            variable = self.buscar_variable(t.valor)
            if variable is not None:
                return variable["tipo"]
            self.advertencias.append(
                f"Warning undefined variable línea {t.linea}: "
                f"{t.valor!r} se utiliza sin declaración."
            )
            return None
        if self.aceptar("DELIMITADOR", "("):
            tipo = self.expresion()
            self.esperar("DELIMITADOR", ")", "')' para cerrar expresión")
            return tipo

        self.errores.append(
            f"Error sintáctico línea {t.linea}: se esperaba constante, "
            f"variable o expresión; se encontró {t.valor!r}."
        )
        if t.tipo != "EOF" and t.valor not in {";", ")", "}"}:
            self.avanzar()
        return None
    
    def comprobar_tipo(self, declarado, recibido, nombre, linea):
        if recibido is None:
            return

        compatibles = {
            "int": {"int"},
            "double": {"int", "double"},
            "float": {"int", "float"},
            "str": {"str", "string"},
            "string": {"str", "string"},
            "char": {"char"},
            "bool": {"bool", "int"},
        }

        if recibido not in compatibles.get(declarado, {declarado}):
            self.errores.append(
                f"Error semántico línea {linea}: valor de tipo {recibido!r} "
                f"asignado a {nombre!r}, declarado como {declarado!r}."
            )

    def punto_coma(self, instruccion):
        if not self.aceptar("DELIMITADOR", ";"):
            t = self.actual()
            self.advertencias.append(
                f"Warning end instruction línea {t.linea}: falta ';' "
                f"al final de {instruccion}."
            )

    def recuperar(self):
        while self.actual().tipo != "EOF" and self.actual().valor not in {";", "}"}:
            self.avanzar()
        self.aceptar("DELIMITADOR", ";")


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

def analizar_codigo(codigo):

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

    return "\n".join(salida)


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
