
import random
import sqlite3

Opciones = ["piedra", "papel", "tijera"]

conexion = sqlite3.connect("piedra_papel_tijera.db")
cursor = conexion.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS partidas
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   eleccion TEXT,
                   resultado TEXT)''')

Eleccion = random.choice(Opciones)

print("Videojuego de piedra, papel o tijera")
opcion = input("Elige entre piedra, papel o tijera: ").lower()

if opcion not in Opciones:
    print("Opcion incorrecta")

elif opcion == Eleccion:
    resultado = "Empate"
    print("Empate")

elif (opcion == "piedra" and Eleccion == "tijera") or \
     (opcion == "papel" and Eleccion == "piedra") or \
     (opcion == "tijera" and Eleccion == "papel"):

    resultado = "Victoria"
    print("Ganaste")

else:
    resultado = "Derrota"
    print("Perdiste")

print("La computadora eligio:", Eleccion)

if opcion in Opciones:
    cursor.execute(
        "INSERT INTO partidas (eleccion, resultado) VALUES (?, ?)",
        (opcion, resultado)
    )

    conexion.commit()

conexion.close()
