#main.py

from genera import GeneraCodigo

archivo = "salida.txt"

codigo = GeneraCodigo(archivo)

codigo.code()
codigo.pushc('5')
codigo.pushc('3')
codigo.add()
codigo.output('A')
codigo.end()

codigo.salida.close()
