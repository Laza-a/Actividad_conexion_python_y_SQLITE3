import random
import sqlite3

jugador = input("Nombre: ")
conexion = sqlite3.connect("Piedra_Papel_tijerass.db")
cursor = conexion.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS partida (
        nombre TEXT,
        jugador TEXT,
        computadora TEXT,
        resultado TEXT
    )
''')


opciones = ["piedra", "papel", "tijera"]

computadora = random.choice(opciones)

if jugador == computadora:
    resultado = "empatado"
elif jugador == "piedra" and computadora == "tijera":
    resultado = "ganaste"
    print(resultado)

elif jugador == "tijera" and computadora == "papel":
    resultado = "ganaste"
    print(resultado)

elif jugador == "papel" and computadora == "piedra":
    resultado = "ganaste"
    print(resultado)

else:
    resultado = "perdiste"
    print(resultado)
    
while seguir.lower() == "s":

conexion.commit()
commit()
SELECT COUNT(*)