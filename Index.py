import random 
import sqlite3
Opciones=["piedra","papel","tijera"]

conexion = sqlite3.connect("piedra_papel_tijera.db")

cursor = conexion.cursor()

CREATE TABLE IF NOT EXISTS partidas

Eleccion = random.choice(Opciones)

print ("Videojuego de piedra, papel o tijera")
opcion =input("elije entre piedra, papel o tijera").lower

if opcion == Eleccion:
    print("empate")
elif
