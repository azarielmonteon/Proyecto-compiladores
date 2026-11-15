# TIPOS DE DATOS PERMITIDOS

TIPOS_DATOS = {
    "int": "entero corto",
    "double": "entero largo",
    "str": "cadena",
    "bool": "booleano",
    "char": "caracter",
    "float": "flotante"
}

# CARACTERES QUE PUEDE RECONOCER EL AUTÓMATA

LETRAS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITOS = "0123456789"
GUION_BAJO = "_"
# Caracteres que NO forman parte de un nombre de variable
CARACTERES_PROHIBIDOS = {
    '$', '#', '/', '(', ')', '@', '-', '"', '|',
    ':', ';', '.', ',', '?', '!', '&', '<', '>',
    '+', '*', '='
}

# AUTÓMATA PARA VALIDAR UNA VARIABLE

def validar_variable(variable):
    if variable == "":
        return False
    estado = "q0"

    for caracter in variable:
        # Estado inicial
        if estado == "q0":
            # El primer carácter solamente puede ser:una letra o "_"

            if caracter in LETRAS or caracter == GUION_BAJO:
                estado = "q1"

            elif caracter in CARACTERES_PROHIBIDOS:
                estado = "qError"

            else:
                # si comienza con un número
                estado = "qError"

        elif estado == "q1":

            # Después del primer carácter se permiten:
            # letras, números y "_"

            if caracter in LETRAS:
                estado = "q2"

            elif caracter in DIGITOS:
                estado = "q2"

            elif caracter == GUION_BAJO:
                estado = "q2"

            elif caracter in CARACTERES_PROHIBIDOS:
                estado = "qError"

            else:
                estado = "qError"

        # Continuamos aceptando letras, números y "_"
        elif estado == "q2":
            if caracter in LETRAS:
                estado = "q2"
            elif caracter in DIGITOS:
                estado = "q2"
            elif caracter == GUION_BAJO:
                estado = "q2"
            elif caracter in CARACTERES_PROHIBIDOS:
                estado = "qError"
            else:
                estado = "qError"


        # ESTADO DE ERROR
        elif estado == "qError":
            return False


    # ESTADOS DE ACEPTACIÓN
    return estado == "q1" or estado == "q2"

# FUNCIÓN PARA ANALIZAR UNA LÍNEA
def analizar_linea(linea, tabla_simbolos):

    linea = linea.strip()

    # Ignorar líneas vacías
    if not linea:
        return None

    # Ignorar main y llaves
    if linea in ["main(){", "}", "{"]:
        return None

    # Separar los tokens
    tokens = linea.split()

    # Debe existir exactamente:
    # tipo_de_dato variable

    if len(tokens) != 2:
        return f"{linea} // no identificado"

    tipo = tokens[0]
    variable = tokens[1]

    # VALIDAR TIPO DE DATO

    tipo_valido = tipo in TIPOS_DATOS

    # VALIDAR VARIABLE

    variable_valida = validar_variable(variable)

    # SI ALGUNO ES INCORRECTO

    if not tipo_valido or not variable_valida:
        return f"{linea} // no identificado"

    # REVISAR AMBIGÜEDAD

    if variable in tabla_simbolos:
        tipo_anterior = tabla_simbolos[variable]
        if tipo_anterior != tipo:
            return (f"{linea} // tipo de dato {TIPOS_DATOS[tipo]}, "f"variable {variable}, "f"ambigüedad con {tipo_anterior} {variable}")

    # Guardar variable y tipo
    tabla_simbolos[variable] = tipo

    return (f"{linea} // tipo de dato {TIPOS_DATOS[tipo]}, "f"variable {variable}")

# ANALIZAR ARCHIVO TXT
def analizar_archivo(nombre_archivo):
    tabla_simbolos = {}
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            print("========== RESULTADO DEL AUTÓMATA ==========\n")
            for linea in archivo:
                resultado = analizar_linea(linea,tabla_simbolos)
                if resultado:
                    print(resultado)

    except FileNotFoundError:
        print(f"Error: no se encontró el archivo "f"'{nombre_archivo}'.")





# ANALIZAR ARCHIVO TXT
def analizar_archivo(nombre_archivo):

    tabla_simbolos = {}

    try:

        with open(
            nombre_archivo,
            "r",
            encoding="utf-8"
        ) as archivo:

            print(
                "========== RESULTADO DEL AUTÓMATA ==========\n"
            )

            for linea in archivo:

                resultado = analizar_linea(
                    linea,
                    tabla_simbolos
                )

                if resultado:
                    print(resultado)

    except FileNotFoundError:

        print(
            f"Error: no se encontró el archivo "
            f"'{nombre_archivo}'."
        )


# ANALIZAR CÓDIGO RECIBIDO DESDE EL IDE
def analizar_codigo(codigo):

    tabla_simbolos = {}
    resultados = []

    for linea in codigo.splitlines():

        resultado = analizar_linea(
            linea,
            tabla_simbolos
        )

        if resultado:
            resultados.append(resultado)

    return resultados


if __name__ == "__main__":
    archivo = r"C:\Users\micro\OneDrive\Desktop\compiladores\pruebas.txt"
    analizar_archivo(archivo)
