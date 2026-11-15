import tkinter as tk
from tkinter import filedialog, messagebox
import os
import analizador_lexico_sintactico as analizador
#from sintactico2 import 
import re 


# COLORES

BG = "#1e1e2e"
BG_PANEL = "#313144"
FG = "#cdd6f4"
BG_SEPARADOR = "#4F577C"
BG_TERMINAL = "#11111b"


# PALABRAS RESERVADAS DEL LENGUAJE

PALABRAS_RESERVADAS = {
    "control": [
        "if", "else", "switch", "case", "default",
        "for", "while", "do", "break", "continue",
        "goto", "return"
    ],

    "tipos": [
        "void", "char", "short", "int", "long",
        "float", "double", "signed", "unsigned",
        "bool", "wchar_t", "auto"
    ],


    "modificadores": [
        "const", "static", "extern", "volatile",
        "register", "inline", "restrict",
        "constexpr", "mutable", "virtual",
        "explicit", "friend", "typename"
    ],

    "cpp": [
        "class", "public", "private", "protected",
        "namespace", "using", "new", "delete",
        "this", "operator", "template", "try",
        "catch", "throw", "nullptr", "override",
        "final", "noexcept", "decltype"
    ],

    "otros": [
        "struct", "union", "enum", "typedef",
        "sizeof", "static_assert", "alignof",
        "true", "false"
    ]
}


# VENTANA PRINCIPAL

lisp = tk.Tk()
lisp.title("Lisp Estudio")
lisp.geometry("1280x800")
lisp.configure(bg=BG)

archivo_actual = None

# ARCHIVOS TEMPORALES PARA DESHACER Y REHACER

TEMP_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "temp"
)

os.makedirs(TEMP_DIR, exist_ok=True)

for archivo in os.listdir(TEMP_DIR):

    if archivo.startswith("temp_") and archivo.endswith(".txt"):

        ruta = os.path.join(
            TEMP_DIR,
            archivo
        )

        try:
            os.remove(ruta)
        except PermissionError:
            pass

historial_temporal = []
posicion_historial = -1
ultimo_codigo = ""

# TERMINAL
def escribir_terminal(texto):
    terminal.config(state="normal")
    terminal.insert("end", texto + "\n")
    terminal.see("end")
    terminal.config(state="disabled")


def limpiar_terminal():
    terminal.config(state="normal")
    terminal.delete("1.0", "end")
    terminal.config(state="disabled")


# DESHACER
def deshacer():

    global posicion_historial
    global ultimo_codigo

    if not historial_temporal:
        return

    if posicion_historial <= 0:
        return

    posicion_historial -= 1

    archivo = historial_temporal[posicion_historial]

    try:

        with open(
            archivo,
            "r",
            encoding="utf-8"
        ) as f:

            codigo = f.read()

        ide.delete("1.0", "end")
        ide.insert("1.0", codigo)

        ultimo_codigo = codigo

        actualizar_lineas()

    except Exception:
        pass


# REHACER
def rehacer():

    global posicion_historial
    global ultimo_codigo

    if not historial_temporal:
        return

    if posicion_historial >= len(historial_temporal) - 1:
        return

    posicion_historial += 1

    archivo = historial_temporal[posicion_historial]

    try:

        with open(
            archivo,
            "r",
            encoding="utf-8"
        ) as f:

            codigo = f.read()

        ide.delete("1.0", "end")
        ide.insert("1.0", codigo)

        ultimo_codigo = codigo

        actualizar_lineas()

    except Exception:
        pass


# GUARDAR CAMBIO TEMPORAL
def guardar_temporal(event=None):

    global historial_temporal
    global posicion_historial
    global ultimo_codigo

    codigo = ide.get("1.0", "end-1c")

    # Si realmente no cambió el código, no crear otro archivo
    if codigo == ultimo_codigo:
        return

    # Si se hizo un cambio después de un deshacer,
    # eliminar los archivos que estaban después
    if posicion_historial < len(historial_temporal) - 1:

        archivos_eliminar = historial_temporal[
            posicion_historial + 1:
        ]

        for archivo in archivos_eliminar:

            try:
                os.remove(archivo)
            except FileNotFoundError:
                pass

        historial_temporal = historial_temporal[
            :posicion_historial + 1
        ]

    # Crear el estado anterior si todavía no existe historial
    if not historial_temporal:

        archivo_inicial = os.path.join(
            TEMP_DIR,
            "temp_0.txt"
        )

        with open(
            archivo_inicial,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(ultimo_codigo)

        historial_temporal.append(
            archivo_inicial
        )

        posicion_historial = 0

    # Crear archivo para el nuevo estado
    numero = len(historial_temporal)

    archivo_temporal = os.path.join(
        TEMP_DIR,
        "temp_" + str(numero) + ".txt"
    )

    with open(
        archivo_temporal,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(codigo)

    historial_temporal.append(
        archivo_temporal
    )

    posicion_historial += 1

    ultimo_codigo = codigo


# ELIMINAR ARCHIVOS TEMPORALES
def limpiar_temporales():

    global historial_temporal
    global posicion_historial

    for archivo in historial_temporal:

        try:
            os.remove(archivo)
        except FileNotFoundError:
            pass

    historial_temporal = []
    posicion_historial = -1


# NUMERACIÓN DE LÍNEAS
def actualizar_lineas(event=None):

    lineas.config(state="normal")
    lineas.delete("1.0", "end")

    cantidad = int(
        ide.index("end-1c").split(".")[0]
    )

    numeros = "\n".join(
        str(i) for i in range(1, cantidad + 1)
    )

    lineas.insert(
        "1.0",
        numeros
    )

    lineas.config(state="disabled")


# COLORES DE LAS PALABRAS RESERVADAS

COLORES_RESERVADAS = {
    "control": "#cba6f7",
    "tipos": "#89b4fa",
    "modificadores": "#f9e2af",
    "cpp": "#fab387",
    "otros": "#a6e3a1"
}


# RECONOCIMIENTO DE PALABRAS RESERVADAS

def actualizar_resaltado(event=None):

    codigo = ide.get("1.0", "end-1c")

    # Eliminar los resaltados anteriores
    for categoria in PALABRAS_RESERVADAS:
        ide.tag_remove(categoria, "1.0", "end")

    # Configurar los colores
    for categoria, color in COLORES_RESERVADAS.items():
        ide.tag_configure(
            categoria,
            foreground=color,
            font=("Consolas", 12, "bold")
        )

    # Construir el patrón para reconocer cada categoría
    patrones = [
        r'(?P<comentario>//[^\n]*|/\*[\s\S]*?\*/)',
        r'(?P<cadena>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\' )'
    ]

    # Corregir el patrón de cadenas para no incluir espacios finales
    patrones[1] = (
        r"""(?P<cadena>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')"""
    )

    for categoria, palabras in PALABRAS_RESERVADAS.items():

        if not palabras:
            continue

        palabras_regex = "|".join(
            re.escape(palabra)
            for palabra in sorted(palabras, key=len, reverse=True)
        )

        patrones.append(
            rf"(?P<{categoria}>\b(?:{palabras_regex})\b)"
        )

    patron = re.compile("|".join(patrones))

    # Buscar coincidencias en el código
    for match in patron.finditer(codigo):

        categoria = match.lastgroup

        # Ignorar comentarios y cadenas de texto
        if categoria in ("comentario", "cadena"):
            continue

        inicio_index = f"1.0 + {match.start()} chars"
        fin_index = f"1.0 + {match.end()} chars"

        ide.tag_add(
            categoria,
            inicio_index,
            fin_index
        )


# CERRAR MENU
def cerrar_menu():
    menu_archivo.place_forget()


# COMPILAR

def compilar():

    # Obtener código escrito en el IDE
    codigo = ide.get("1.0", "end-1c")

    if not codigo.strip():
        escribir_terminal("No hay código para compilar.")
        return

    limpiar_terminal()

    escribir_terminal("========== COMPILACIÓN ==========")

    # ANÁLISIS LÉXICO Y SINTÁCTICO
    escribir_terminal("\nINICIANDO ANÁLISIS LÉXICO Y SINTÁCTICO...\n")

    resultado = analizador.analizar_codigo(codigo)

    escribir_terminal(resultado)

    escribir_terminal("\n========== FIN DEL ANÁLISIS ==========")


# EJECUTAR
def ejecutar():

    codigo = ide.get("1.0", "end-1c")

    # Verificar que exista código
    if not codigo.strip():

        escribir_terminal("No hay código para ejecutar.")
        return


    try:

        # Primero verificar que el código sea válido
        resultados = analizar_codigo(codigo)

        # Revisar si existe algún error
        codigo_valido = True

        for resultado in resultados:

            if "no identificado" in resultado:

                codigo_valido = False
                break


        if not codigo_valido:

            limpiar_terminal()
            escribir_terminal("        ERROR DE EJECUCIÓN")
            escribir_terminal("")
            escribir_terminal(
                "El código contiene instrucciones no válidas."
            )
            escribir_terminal("")
            escribir_terminal(
                "Primero corrige los errores y vuelve a intentar."
            )

            return


        # Crear ventana de ejecución

        ventana_ejecucion = tk.Toplevel(lisp)

        ventana_ejecucion.title("Ejecución - Lisp Estudio")
        ventana_ejecucion.geometry("800x500")
        ventana_ejecucion.configure(bg=BG)


        # TÍTULO

        titulo = tk.Label(
            ventana_ejecucion,
            text="EJECUCIÓN DEL PROGRAMA",
            bg=BG,
            fg=FG,
            font=("Arial", 14, "bold")
        )

        titulo.pack(
            pady=10
        )


        # TERMINAL DE EJECUCIÓN

        salida = tk.Text(
            ventana_ejecucion,
            bg=BG_TERMINAL,
            fg="#a6e3a1",
            insertbackground="white",
            font=("Consolas", 11),
            relief="flat",
            bd=0
        )

        salida.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )


        # MENSAJE DE EJECUCIÓN

        salida.insert(
            "end",
            "========================================\n"
        )

        salida.insert(
            "end",
            "       PROGRAMA EN EJECUCIÓN\n"
        )

        salida.insert(
            "end",
            "========================================\n\n"
        )


        # Mostrar las instrucciones ejecutadas

        for resultado in resultados:

            salida.insert(
                "end",
                resultado + "\n"
            )


        salida.insert(
            "end",
            "\n"
        )

        salida.insert(
            "end",
            "========================================\n"
        )

        salida.insert(
            "end",
            "       EJECUCIÓN FINALIZADA\n"
        )

        salida.insert(
            "end",
            "========================================\n"
        )


        salida.config(
            state="disabled"
        )


        # BOTÓN CERRAR

        btn_cerrar = tk.Button(
            ventana_ejecucion,
            text="Cerrar",
            command=ventana_ejecucion.destroy,
            bg=BG_PANEL,
            fg=FG,
            activebackground="#45475a",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=20,
            font=("Arial", 11),
            cursor="hand2"
        )

        btn_cerrar.pack(
            pady=10
        )


    except Exception as e:

        escribir_terminal("")
        escribir_terminal("ERROR DURANTE LA EJECUCIÓN:")
        escribir_terminal(str(e))


# FUNCIONES DE ARCHIVO
def nuevo():

    global archivo_actual
    global ultimo_codigo

    cerrar_menu()

    if ide.get("1.0", "end-1c").strip():

        respuesta = messagebox.askyesnocancel(
            "Nuevo",
            "¿Deseas guardar el código actual?"
        )

        if respuesta is None:
            return

        if respuesta:

            if not guardar():
                return

    ide.delete("1.0", "end")

    archivo_actual = None

    limpiar_temporales()

    ultimo_codigo = ""

    actualizar_lineas()

    lisp.title("Lisp Estudio")


def abrir():

    global archivo_actual
    global ultimo_codigo

    cerrar_menu()

    archivo = filedialog.askopenfilename(
        title="Abrir código",
        filetypes=[
            ("Archivos de texto", "*.txt"),
            ("Todos los archivos", "*.*")
        ]
    )

    if not archivo:
        return

    try:

        with open(
            archivo,
            "r",
            encoding="utf-8"
        ) as f:

            codigo = f.read()

        ide.delete("1.0", "end")
        ide.insert("1.0", codigo)

        limpiar_temporales()

        ultimo_codigo = codigo

        actualizar_lineas()

        archivo_actual = archivo

        lisp.title(
            "Lisp Estudio - " + archivo_actual
        )

        escribir_terminal(
            "Archivo abierto: " + archivo_actual
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            "No se pudo abrir el archivo.\n" + str(e)
        )


def guardar():

    global archivo_actual
    global ultimo_codigo

    cerrar_menu()

    if archivo_actual is None:
        return guardar_como()

    try:

        codigo = ide.get(
            "1.0",
            "end-1c"
        )

        with open(
            archivo_actual,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(codigo)

        limpiar_temporales()

        ultimo_codigo = codigo

        escribir_terminal(
            "Archivo guardado: " + archivo_actual
        )

        return True

    except Exception as e:

        messagebox.showerror(
            "Error",
            "No se pudo guardar el archivo.\n" + str(e)
        )

        return False


def guardar_como():

    global archivo_actual
    global ultimo_codigo

    cerrar_menu()

    archivo = filedialog.asksaveasfilename(
        title="Guardar código",
        defaultextension=".txt",
        filetypes=[
            ("Archivos de texto", "*.txt"),
            ("Todos los archivos", "*.*")
        ]
    )

    if not archivo:
        return False

    try:

        codigo = ide.get(
            "1.0",
            "end-1c"
        )

        with open(
            archivo,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(codigo)

        limpiar_temporales()

        ultimo_codigo = codigo

        archivo_actual = archivo

        lisp.title(
            "Lisp Estudio - " + archivo_actual
        )

        escribir_terminal(
            "Archivo guardado: " + archivo_actual
        )

        return True

    except Exception as e:

        messagebox.showerror(
            "Error",
            "No se pudo guardar el archivo.\n" + str(e)
        )

        return False



# BUSCAR Y REEMPLAZAR
def buscar_reemplazar():

    ventana_buscar = tk.Toplevel(lisp)
    ventana_buscar.title("Buscar y Reemplazar")
    ventana_buscar.geometry("500x230")
    ventana_buscar.configure(bg=BG)
    ventana_buscar.resizable(False, False)

    # TÍTULO
    titulo = tk.Label(
        ventana_buscar,
        text="Buscar y Reemplazar",
        bg=BG,
        fg=FG,
        font=("Arial", 14, "bold")
    )
    titulo.pack(pady=(15, 10))

    # CONTENEDOR
    contenedor = tk.Frame(
        ventana_buscar,
        bg=BG
    )
    contenedor.pack(fill="x", padx=20)

    # BUSCAR
    etiqueta_buscar = tk.Label(
        contenedor,
        text="Buscar:",
        bg=BG,
        fg=FG,
        font=("Arial", 11)
    )
    etiqueta_buscar.grid(
        row=0,
        column=0,
        sticky="w",
        pady=5
    )

    entrada_buscar = tk.Entry(
        contenedor,
        bg=BG_PANEL,
        fg=FG,
        insertbackground="white",
        relief="flat",
        font=("Arial", 11)
    )
    entrada_buscar.grid(
        row=0,
        column=1,
        sticky="ew",
        padx=(10, 0),
        pady=5
    )

    # REEMPLAZAR
    etiqueta_reemplazar = tk.Label(
        contenedor,
        text="Reemplazar:",
        bg=BG,
        fg=FG,
        font=("Arial", 11)
    )
    etiqueta_reemplazar.grid(
        row=1,
        column=0,
        sticky="w",
        pady=5
    )

    entrada_reemplazar = tk.Entry(
        contenedor,
        bg=BG_PANEL,
        fg=FG,
        insertbackground="white",
        relief="flat",
        font=("Arial", 11)
    )
    entrada_reemplazar.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=(10, 0),
        pady=5
    )

    contenedor.columnconfigure(1, weight=1)

    # CONFIGURAR RESALTADO
    ide.tag_configure(
        "coincidencia_busqueda",
        background="#585b70",
        foreground="white"
    )

    ide.tag_configure(
        "coincidencia_actual",
        background="#89b4fa",
        foreground="#11111b"
    )

    coincidencias = []
    posicion_actual = [-1]

    def buscar_todas():

        palabra = entrada_buscar.get()

        ide.tag_remove(
            "coincidencia_busqueda",
            "1.0",
            "end"
        )

        ide.tag_remove(
            "coincidencia_actual",
            "1.0",
            "end"
        )

        coincidencias.clear()
        posicion_actual[0] = -1

        if not palabra:
            etiqueta_resultado.config(
                text="Escribe algo para buscar."
            )
            return

        inicio = "1.0"

        while True:

            posicion = ide.search(
                palabra,
                inicio,
                stopindex="end"
            )

            if not posicion:
                break

            final = f"{posicion}+{len(palabra)}c"

            coincidencias.append(
                (posicion, final)
            )

            ide.tag_add(
                "coincidencia_busqueda",
                posicion,
                final
            )

            inicio = final

        if coincidencias:

            posicion_actual[0] = 0

            inicio_actual, final_actual = coincidencias[0]

            ide.tag_remove(
                "coincidencia_busqueda",
                inicio_actual,
                final_actual
            )

            ide.tag_add(
                "coincidencia_actual",
                inicio_actual,
                final_actual
            )

            ide.see(inicio_actual)
            ide.mark_set("insert", final_actual)

            etiqueta_resultado.config(
                text=f"{len(coincidencias)} coincidencia(s) encontrada(s)."
            )

        else:

            etiqueta_resultado.config(
                text="No se encontraron coincidencias."
            )

    def buscar_siguiente():

        if not coincidencias:
            buscar_todas()

            if not coincidencias:
                return

        # Restaurar el resaltado anterior
        for inicio, final in coincidencias:
            ide.tag_remove(
                "coincidencia_actual",
                inicio,
                final
            )

            ide.tag_add(
                "coincidencia_busqueda",
                inicio,
                final
            )

        posicion_actual[0] += 1

        if posicion_actual[0] >= len(coincidencias):
            posicion_actual[0] = 0

        inicio, final = coincidencias[
            posicion_actual[0]
        ]

        ide.tag_remove(
            "coincidencia_busqueda",
            inicio,
            final
        )

        ide.tag_add(
            "coincidencia_actual",
            inicio,
            final
        )

        ide.see(inicio)
        ide.mark_set("insert", final)

        etiqueta_resultado.config(
            text=f"Coincidencia "
                 f"{posicion_actual[0] + 1} "
                 f"de {len(coincidencias)}."
        )

    def reemplazar():

        if not coincidencias:
            buscar_todas()

            if not coincidencias:
                return

        indice = posicion_actual[0]

        if indice < 0:
            indice = 0
            posicion_actual[0] = 0

        inicio, final = coincidencias[indice]

        ide.delete(
            inicio,
            final
        )

        ide.insert(
            inicio,
            entrada_reemplazar.get()
        )

        actualizar_lineas()
        guardar_temporal()

        # Volver a buscar para actualizar
        buscar_todas()

        etiqueta_resultado.config(
            text="Coincidencia reemplazada."
        )

    def reemplazar_todos():

        palabra = entrada_buscar.get()
        reemplazo = entrada_reemplazar.get()

        if not palabra:
            etiqueta_resultado.config(
                text="Escribe algo para buscar."
            )
            return

        codigo = ide.get(
            "1.0",
            "end-1c"
        )

        cantidad = codigo.count(palabra)

        if cantidad == 0:

            etiqueta_resultado.config(
                text="No se encontraron coincidencias."
            )
            return

        nuevo_codigo = codigo.replace(
            palabra,
            reemplazo
        )

        ide.delete(
            "1.0",
            "end"
        )

        ide.insert(
            "1.0",
            nuevo_codigo
        )

        actualizar_lineas()
        guardar_temporal()

        buscar_todas()

        etiqueta_resultado.config(
            text=f"{cantidad} coincidencia(s) reemplazada(s)."
        )

    # BOTONES
    botones = tk.Frame(
        ventana_buscar,
        bg=BG
    )
    botones.pack(
        pady=15
    )

    btn_buscar = tk.Button(
        botones,
        text="Buscar",
        command=buscar_todas,
        bg=BG_PANEL,
        fg=FG,
        activebackground="#45475a",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=15,
        font=("Arial", 10),
        cursor="hand2"
    )
    btn_buscar.pack(
        side="left",
        padx=4
    )

    btn_siguiente = tk.Button(
        botones,
        text="Buscar siguiente",
        command=buscar_siguiente,
        bg=BG_PANEL,
        fg=FG,
        activebackground="#45475a",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=15,
        font=("Arial", 10),
        cursor="hand2"
    )
    btn_siguiente.pack(
        side="left",
        padx=4
    )

    btn_reemplazar = tk.Button(
        botones,
        text="Reemplazar",
        command=reemplazar,
        bg=BG_PANEL,
        fg=FG,
        activebackground="#45475a",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=15,
        font=("Arial", 10),
        cursor="hand2"
    )
    btn_reemplazar.pack(
        side="left",
        padx=4
    )

    btn_reemplazar_todos = tk.Button(
        botones,
        text="Reemplazar todos",
        command=reemplazar_todos,
        bg=BG_PANEL,
        fg=FG,
        activebackground="#45475a",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=15,
        font=("Arial", 10),
        cursor="hand2"
    )
    btn_reemplazar_todos.pack(
        side="left",
        padx=4
    )

    # RESULTADO DE LA BÚSQUEDA
    etiqueta_resultado = tk.Label(
        ventana_buscar,
        text="",
        bg=BG,
        fg="#a6e3a1",
        font=("Arial", 10)
    )
    etiqueta_resultado.pack(
        pady=(0, 10)
    )

    entrada_buscar.focus_set()


# MOSTRAR / OCULTAR MENU ARCHIVO
def mostrar_archivo():

    if menu_archivo.winfo_ismapped():

        menu_archivo.place_forget()

    else:

        menu_archivo.place(
            x=0,
            y=34
        )

        menu_archivo.lift()


# BARRA DE MENU
menu_bar = tk.Frame(
    lisp,
    bg=BG_PANEL,
    height=34
)

menu_bar.pack(
    side="top",
    fill="x"
)

menu_bar.pack_propagate(False)


# BOTON DESHACER
btn_deshacer = tk.Button(
    menu_bar,
    text="ctrl z",
    command=deshacer,
    bg=BG_PANEL,
    fg=FG,
    activebackground="#45475a",
    activeforeground="white",
    relief="flat",
    bd=0,
    padx=14,
    font=("Arial", 11),
    cursor="hand2"
)

btn_deshacer.pack(side="right")


# BOTON REHACER
btn_rehacer = tk.Button(
    menu_bar,
    text="ctrl y",
    command=rehacer,
    bg=BG_PANEL,
    fg=FG,
    activebackground="#45475a",
    activeforeground="white",
    relief="flat",
    bd=0,
    padx=14,
    font=("Arial", 11),
    cursor="hand2"
)

btn_rehacer.pack(side="right")


# BOTON ARCHIVO
btn_archivo = tk.Button(
    menu_bar,
    text="Archivo",
    command=mostrar_archivo,
    bg=BG_PANEL,
    fg=FG,
    activebackground="#45475a",
    activeforeground="white",
    relief="flat",
    bd=0,
    padx=14,
    font=("Arial", 11),
    cursor="hand2"
)

btn_archivo.pack(side="left")


# BOTON COMPILAR
btn_compilar = tk.Button(
    menu_bar,
    text="Compilar",
    command=compilar,
    bg=BG_PANEL,
    fg=FG,
    activebackground="#45475a",
    activeforeground="white",
    relief="flat",
    bd=0,
    padx=14,
    font=("Arial", 11),
    cursor="hand2"
)

btn_compilar.pack(side="left")


# BOTON EJECUTAR
btn_ejecutar = tk.Button(
    menu_bar,
    text="Ejecutar",
    command=ejecutar,
    bg=BG_PANEL,
    fg=FG,
    activebackground="#45475a",
    activeforeground="white",
    relief="flat",
    bd=0,
    padx=14,
    font=("Arial", 11),
    cursor="hand2"
)

btn_ejecutar.pack(side="left")


# BOTON AYUDA
btn_ayuda = tk.Button(
    menu_bar,
    text="ayuda",
    bg=BG_PANEL,
    fg=FG,
    activebackground="#45475a",
    activeforeground="white",
    relief="flat",
    bd=0,
    padx=14,
    font=("Arial", 11),
    cursor="hand2"
)

btn_ayuda.pack(side="left")


# MENU ARCHIVO
menu_archivo = tk.Frame(
    lisp,
    bg=BG_PANEL,
    bd=1,
    relief="solid"
)


Lista_Archivo = [
    ("Nuevo", nuevo),
    ("Abrir", abrir),
    ("Guardar", guardar),
    ("Guardar como", guardar_como),
    ("Buscar y remplazar", buscar_reemplazar)
]


for item, funcion in Lista_Archivo:

    btn = tk.Button(
        menu_archivo,
        text=item,
        command=funcion,
        bg=BG_PANEL,
        fg=FG,
        activebackground="#45475a",
        activeforeground="white",
        relief="flat",
        bd=0,
        anchor="w",
        padx=14,
        font=("Arial", 11),
        cursor="hand2"
    )

    btn.pack(
        fill="x",
        ipadx=10,
        ipady=4
    )


# Prioridad del menu
menu_archivo.lift()


# IDE
ide_container = tk.Frame(
    lisp,
    bg=BG
)

ide_container.place(
    x=0,
    y=34,
    relwidth=1,
    height=466
)


lineas = tk.Text(
    ide_container,
    width=5,
    bg="#181825",
    fg="#6c7086",
    font=("Consolas", 12),
    relief="flat",
    bd=0,
    state="disabled"
)

lineas.pack(
    side="left",
    fill="y",
    padx=(10, 0),
    pady=10
)


ide = tk.Text(
    ide_container,
    bg="#181825",
    fg=FG,
    insertbackground="white",
    font=("Consolas", 12),
    relief="flat",
    bd=0,
    undo=False
)

ide.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10),
    pady=10
)
ide.bind(
    "<KeyRelease>",
    actualizar_lineas
)

ide.bind(
    "<KeyRelease>",
    guardar_temporal,
    add="+"
)


ide.bind(
    "<KeyRelease>",
    actualizar_resaltado,
    add="+"
)

actualizar_lineas()
# BARRA SEPARADORA TERMINAL
separador_bar = tk.Frame(
    lisp,
    bg=BG_SEPARADOR,
    height=25
)
separador_bar.place(
    x=0,
    y=500,
    relwidth=1
)
# TEXTO TERMINAL
texto_terminal = tk.Label(
    separador_bar,
    text="TERMINAL",
    bg=BG_SEPARADOR,
    fg="white",
    font=("Arial", 10, "bold")
)
texto_terminal.pack(
    side="left",
    padx=10
)
# CONTENEDOR TERMINAL
terminal_container = tk.Frame(
    lisp,
    bg=BG_TERMINAL
)
terminal_container.place(
    x=0,
    y=525,
    relwidth=1,
    height=275
)
terminal = tk.Text(
    terminal_container,
    bg=BG_TERMINAL,
    fg="#a6e3a1",
    insertbackground="white",
    font=("Consolas", 11),
    relief="flat",
    bd=0,
    state="disabled"
)
terminal.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

# MENSAJE INICIAL
escribir_terminal("Lisp Estudio iniciado.")
escribir_terminal("El autómata está listo para compilar.")

# EJECUTAR APLICACION
lisp.mainloop()