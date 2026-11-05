
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

seguir = "s"

while seguir.lower() == "s":

    eleccion = input("Elige piedra, papel o tijera: ").lower()

    if eleccion not in opciones:
        print("Opcion incorrecta")
        continue

    computadora = random.choice(opciones)

    print("La computadora eligio:", computadora)

    if eleccion == computadora:
        resultado = "empatado"

    elif eleccion == "piedra" and computadora == "tijera":
        resultado = "ganaste"

    elif eleccion == "tijera" and computadora == "papel":
        resultado = "ganaste"

    elif eleccion == "papel" and computadora == "piedra":
        resultado = "ganaste"

    else:
        resultado = "perdiste"

    print(resultado)

    cursor.execute('''
        INSERT INTO partida (nombre, jugador, computadora, resultado)
        VALUES (?, ?, ?, ?)
    ''', (jugador, eleccion, computadora, resultado))

    conexion.commit()

    seguir = input("¿Desea jugar otra vez? (s/n): ")

print("Gracias por jugar", jugador)

cursor.execute("SELECT COUNT(*) FROM partida WHERE nombre = ? AND resultado = 'ganaste'", (jugador,))
victorias = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM partida WHERE nombre = ? AND resultado = 'perdiste'", (jugador,))
derrotas = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM partida WHERE nombre = ? AND resultado = 'empatado'", (jugador,))
empates = cursor.fetchone()[0]

print("Victorias:", victorias)
print("Derrotas:", derrotas)
print("Empates:", empates)

conexion.close()
