
import tkinter as tk
from tkinter import ttk, messagebox
import random
import sqlite3

# =====================================
# 1. BASE DE DATOS
# =====================================

conexion = sqlite3.connect("piedra_papel_tijera.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    jugador TEXT,
    computadora TEXT,
    resultado TEXT
)
""")

# Comprobar columnas para conservar bases anteriores
cursor.execute("PRAGMA table_info(partidas)")
columnas = [col[1] for col in cursor.fetchall()]

for columna in ["nombre", "jugador", "computadora", "resultado", "fecha"]:
    if columna not in columnas:
        cursor.execute(f"ALTER TABLE partidas ADD COLUMN {columna} TEXT")

# Recuperar elecciones de una version anterior
if "eleccion" in columnas:
    cursor.execute("""
    UPDATE partidas
    SET jugador = eleccion
    WHERE jugador IS NULL
    """)

conexion.commit()


# =====================================
# 2. VARIABLES
# =====================================

opciones = ["piedra", "papel", "tijera"]

victorias = 0
derrotas = 0
empates = 0

ronda = 0
jugando = False
cuenta_activa = False


# =====================================
# 3. FUNCIONES DEL JUEGO
# =====================================

def bloquear_botones(estado):
    boton_piedra.config(state=estado)
    boton_papel.config(state=estado)
    boton_tijera.config(state=estado)


# Identificador para invalidar cuentas regresivas de partidas anteriores
id_partida = 0
temporizador_id = None


def nueva_partida():
    global victorias, derrotas, empates
    global ronda, jugando, cuenta_activa
    global id_partida, temporizador_id

    # Invalida cualquier cuenta regresiva que haya quedado pendiente
    id_partida += 1
    if temporizador_id is not None:
        try:
            ventana.after_cancel(temporizador_id)
        except tk.TclError:
            pass
        temporizador_id = None

    victorias = 0
    derrotas = 0
    empates = 0
    ronda = 0

    jugando = True
    cuenta_activa = False

    cartel.config(
        text="¡QUE COMIENCE EL DESAFIO!",
        bg="#263653"
    )
    texto_elecciones.config(text="Elegí tu primera jugada")
    actualizar_marcador()

    bloquear_botones("normal")

    # El botón queda siempre visible y vuelve a su texto inicial
    boton_nueva.config(
        state="normal",
        text="🔄 NUEVA PARTIDA"
    )


def cuenta_regresiva(numero, opcion, partida):
    global temporizador_id

    # Si se inició otra partida, esta cuenta regresiva ya no sirve
    if partida != id_partida or not jugando:
        return

    if numero > 0:
        bloquear_botones("disabled")
        cartel.config(text=str(numero), bg="#263653")
        temporizador_id = ventana.after(
            800,
            lambda: cuenta_regresiva(numero - 1, opcion, partida)
        )
    else:
        cartel.config(text="¡YA!", bg="#16834a")
        temporizador_id = ventana.after(
            500,
            lambda: jugar(opcion, partida)
        )


def iniciar_jugada(opcion):
    global jugando, cuenta_activa

    if not jugando or cuenta_activa:
        return

    nombre = entrada_nombre.get().strip()
    if nombre == "":
        messagebox.showwarning(
            "Atención",
            "Primero escribí tu nombre"
        )
        return

    cuenta_activa = True
    bloquear_botones("disabled")
    cuenta_regresiva(3, opcion, id_partida)


def jugar(opcion, partida):
    global victorias, derrotas, empates
    global ronda, jugando, cuenta_activa, temporizador_id

    # Evita que una jugada vieja afecte a una partida nueva
    if partida != id_partida or not jugando:
        return

    temporizador_id = None
    cuenta_activa = False
    computadora = random.choice(opciones)

    if opcion == computadora:
        resultado = "Empate"
        empates += 1
        cartel.config(
            text="¡EMPATE! NO CUENTA COMO RONDA",
            bg="#d69e22"
        )

    elif (
        (opcion == "piedra" and computadora == "tijera") or
        (opcion == "papel" and computadora == "piedra") or
        (opcion == "tijera" and computadora == "papel")
    ):
        resultado = "Victoria"
        victorias += 1
        ronda += 1
        cartel.config(
            text="¡GANASTE LA RONDA!",
            bg="#16834a"
        )

    else:
        resultado = "Derrota"
        derrotas += 1
        ronda += 1
        cartel.config(
            text="¡PERDISTE LA RONDA!",
            bg="#b83232"
        )

    texto_elecciones.config(
        text=f"Vos: {opcion.upper()}     |     "
             f"Computadora: {computadora.upper()}"
    )

    cursor.execute(
        """
        INSERT INTO partidas
        (nombre, jugador, computadora, resultado, fecha)
        VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
        """,
        (
            entrada_nombre.get().strip(),
            opcion,
            computadora,
            resultado
        )
    )
    conexion.commit()

    actualizar_marcador()
    actualizar_ranking()
    mostrar_historial()
    actualizar_estadisticas()

    if victorias >= 3 or derrotas >= 3:
        jugando = False
        cuenta_activa = False
        bloquear_botones("disabled")
        boton_nueva.config(
            state="normal",
            text="🔄 VOLVER A JUGAR"
        )

        if victorias >= 3:
            cartel.config(
                text="¡GANASTE EL PARTIDO!",
                bg="#16834a"
            )
            messagebox.showinfo(
                "CAMPEÓN",
                "¡Felicitaciones! Ganaste el partido."
            )
        else:
            cartel.config(
                text="FIN DEL PARTIDO",
                bg="#b83232"
            )
            messagebox.showinfo(
                "Fin del partido",
                "Esta vez ganó la computadora. ¡A intentarlo otra vez!"
            )
    else:
        bloquear_botones("normal")


def actualizar_marcador():
    marcador.config(
        text=f"RONDA: {ronda} / 5\n"
             f"🏆 VOS: {victorias}     "
             f"💻 COMPUTADORA: {derrotas}     "
             f"🤝 EMPATES: {empates}"
    )


# =====================================
# 4. ESTADISTICAS
# =====================================

def actualizar_estadisticas():

    nombre = entrada_stats.get().strip()

    if nombre == "":
        return

    cursor.execute("""
        SELECT
        COUNT(*),
        SUM(CASE WHEN resultado = 'Victoria' THEN 1 ELSE 0 END),
        SUM(CASE WHEN resultado = 'Derrota' THEN 1 ELSE 0 END),
        SUM(CASE WHEN resultado = 'Empate' THEN 1 ELSE 0 END)
        FROM partidas
        WHERE LOWER(nombre) = LOWER(?)
    """, (nombre,))

    datos = cursor.fetchone()

    total = datos[0] or 0
    ganadas = datos[1] or 0
    perdidas = datos[2] or 0
    empatadas = datos[3] or 0

    porcentaje = 0

    if total > 0:
        porcentaje = (ganadas / total) * 100

    estadisticas.config(
        text=f"""
JUGADOR: {nombre.upper()}

PARTIDAS JUGADAS: {total}

VICTORIAS: {ganadas}

DERROTAS: {perdidas}

EMPATES: {empatadas}

PORCENTAJE DE VICTORIAS: {porcentaje:.1f} %
        """
    )


# =====================================
# 5. RANKING DE JUGADORES
# =====================================

def actualizar_ranking():

    for fila in tabla_ranking.get_children():
        tabla_ranking.delete(fila)

    cursor.execute("""
        SELECT
            nombre,
            COUNT(*),
            SUM(CASE WHEN resultado = 'Victoria' THEN 1 ELSE 0 END),
            SUM(CASE WHEN resultado = 'Derrota' THEN 1 ELSE 0 END),
            SUM(CASE WHEN resultado = 'Empate' THEN 1 ELSE 0 END)
        FROM partidas
        GROUP BY LOWER(nombre)
        ORDER BY 3 DESC, 2 DESC, nombre ASC
    """)

    jugadores = cursor.fetchall()

    for posicion, jugador in enumerate(jugadores, start=1):

        nombre, total, ganadas, perdidas, empatadas = jugador

        tabla_ranking.insert(
            "",
            tk.END,
            values=(
                posicion,
                nombre,
                total,
                ganadas or 0,
                perdidas or 0,
                empatadas or 0
            )
        )


# =====================================
# 6. BUSCAR PARTIDAS ANTERIORES
# =====================================

def mostrar_historial():

    for fila in tabla_historial.get_children():
        tabla_historial.delete(fila)

    busqueda = entrada_busqueda.get().strip()

    cursor.execute("""
        SELECT id, fecha, nombre, jugador, computadora, resultado
        FROM partidas
        WHERE LOWER(nombre) LIKE LOWER(?)
        ORDER BY id DESC
    """, ("%" + busqueda + "%",))

    partidas = cursor.fetchall()

    for partida in partidas:

        tabla_historial.insert(
            "",
            tk.END,
            values=partida
        )


# =====================================
# 7. VENTANA PRINCIPAL
# =====================================

ventana = tk.Tk()

ventana.title("PIEDRA, PAPEL O TIJERA")
ventana.geometry("1000x720")
ventana.minsize(850, 650)
ventana.config(bg="#17243b")


# =====================================
# 8. DISEÑO DE LAS PESTAÑAS
# =====================================

estilo = ttk.Style()

estilo.theme_use("clam")

estilo.configure(
    "TNotebook",
    background="#17243b",
    borderwidth=0
)

estilo.configure(
    "TNotebook.Tab",
    background="#263653",
    foreground="white",
    padding=[20, 12],
    font=("Arial", 11, "bold")
)

estilo.map(
    "TNotebook.Tab",
    background=[("selected", "#16834a")],
    foreground=[("selected", "white")]
)

estilo.configure(
    "Treeview",
    background="#263653",
    foreground="white",
    fieldbackground="#263653",
    rowheight=30,
    font=("Arial", 10)
)

estilo.configure(
    "Treeview.Heading",
    background="#16834a",
    foreground="white",
    font=("Arial", 10, "bold")
)


# Crear pestañas

pestanas = ttk.Notebook(ventana)
pestanas.pack(fill="both", expand=True, padx=15, pady=15)

pestana_juego = tk.Frame(pestanas, bg="#17243b")
pestana_ranking = tk.Frame(pestanas, bg="#17243b")
pestana_stats = tk.Frame(pestanas, bg="#17243b")
pestana_historial = tk.Frame(pestanas, bg="#17243b")

pestanas.add(pestana_juego, text="🎮 JUEGO")
pestanas.add(pestana_ranking, text="🏆 RANKING")
pestanas.add(pestana_stats, text="📊 ESTADISTICAS")
pestanas.add(pestana_historial, text="📋 HISTORIAL")


# =====================================
# 9. PESTAÑA JUEGO
# =====================================

tk.Label(
    pestana_juego,
    text="PIEDRA, PAPEL O TIJERA",
    font=("Arial", 25, "bold"),
    bg="#17243b",
    fg="white"
).pack(pady=20)

tk.Label(
    pestana_juego,
    text="EL DESAFIO DEFINITIVO",
    font=("Arial", 12, "bold"),
    bg="#17243b",
    fg="#d69e22"
).pack()

tk.Label(
    pestana_juego,
    text="Nombre del jugador:",
    font=("Arial", 12),
    bg="#17243b",
    fg="white"
).pack(pady=12)

entrada_nombre = tk.Entry(
    pestana_juego,
    font=("Arial", 14),
    justify="center",
    width=25
)

entrada_nombre.pack(pady=5)

tk.Label(
    pestana_juego,
    text="¡El primero en conseguir 3 victorias gana!",
    font=("Arial", 12),
    bg="#17243b",
    fg="white"
).pack(pady=15)


# Botón de reinicio: queda arriba para que siempre esté visible
boton_nueva = tk.Button(
    pestana_juego,
    text="🔄 NUEVA PARTIDA",
    font=("Arial", 12, "bold"),
    bg="#16834a",
    fg="white",
    activebackground="#20a05b",
    activeforeground="white",
    command=nueva_partida,
    state="normal"
)
boton_nueva.pack(pady=5)


# Botones de elecciones

marco_botones = tk.Frame(
    pestana_juego,
    bg="#17243b"
)

marco_botones.pack(pady=10)

boton_piedra = tk.Button(
    marco_botones,
    text="🪨\nPIEDRA",
    font=("Arial", 15, "bold"),
    width=12,
    height=3,
    bg="#d9d9d9",
    command=lambda: iniciar_jugada("piedra")
)

boton_piedra.grid(row=0, column=0, padx=10)

boton_papel = tk.Button(
    marco_botones,
    text="📄\nPAPEL",
    font=("Arial", 15, "bold"),
    width=12,
    height=3,
    bg="#d9d9d9",
    command=lambda: iniciar_jugada("papel")
)

boton_papel.grid(row=0, column=1, padx=10)

boton_tijera = tk.Button(
    marco_botones,
    text="✂️\nTIJERA",
    font=("Arial", 15, "bold"),
    width=12,
    height=3,
    bg="#d9d9d9",
    command=lambda: iniciar_jugada("tijera")
)

boton_tijera.grid(row=0, column=2, padx=10)


# Cartel del resultado

cartel = tk.Label(
    pestana_juego,
    text="¡QUE COMIENCE EL DESAFIO!",
    font=("Arial", 20, "bold"),
    bg="#263653",
    fg="white",
    width=35,
    pady=20
)

cartel.pack(pady=20)


texto_elecciones = tk.Label(
    pestana_juego,
    text="Esperando tu jugada...",
    font=("Arial", 13),
    bg="#17243b",
    fg="white"
)

texto_elecciones.pack(pady=5)


# Marcador

marcador = tk.Label(
    pestana_juego,
    text="RONDA: 0 / 5\nVOS: 0     COMPUTADORA: 0     EMPATES: 0",
    font=("Arial", 14, "bold"),
    bg="#263653",
    fg="#f5d76e",
    pady=15,
    width=55
)

marcador.pack(pady=15)


# =====================================
# 10. PESTAÑA RANKING
# =====================================

tk.Label(
    pestana_ranking,
    text="🏆 RANKING DE JUGADORES",
    font=("Arial", 22, "bold"),
    bg="#17243b",
    fg="white"
).pack(pady=25)

tabla_ranking = ttk.Treeview(
    pestana_ranking,
    columns=("Posicion", "Nombre", "Partidas", "Victorias",
             "Derrotas", "Empates"),
    show="headings"
)

for columna in ("Posicion", "Nombre", "Partidas",
                "Victorias", "Derrotas", "Empates"):

    tabla_ranking.heading(columna, text=columna)

    tabla_ranking.column(
        columna,
        width=110,
        anchor="center"
    )

tabla_ranking.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

tk.Button(
    pestana_ranking,
    text="ACTUALIZAR RANKING",
    font=("Arial", 11, "bold"),
    command=actualizar_ranking
).pack(pady=10)


# =====================================
# 11. PESTAÑA ESTADISTICAS
# =====================================

tk.Label(
    pestana_stats,
    text="📊 ESTADISTICAS DEL JUGADOR",
    font=("Arial", 22, "bold"),
    bg="#17243b",
    fg="white"
).pack(pady=25)

entrada_stats = tk.Entry(
    pestana_stats,
    font=("Arial", 13),
    justify="center"
)

entrada_stats.pack(pady=10)

entrada_stats.insert(0, "")

tk.Button(
    pestana_stats,
    text="CONSULTAR ESTADISTICAS",
    font=("Arial", 11, "bold"),
    command=actualizar_estadisticas
).pack(pady=10)

estadisticas = tk.Label(
    pestana_stats,
    text="Escribí un nombre para consultar sus datos.",
    font=("Arial", 15),
    bg="#263653",
    fg="white",
    justify="left",
    width=45,
    height=12
)

estadisticas.pack(pady=20)


# =====================================
# 12. PESTAÑA HISTORIAL
# =====================================

tk.Label(
    pestana_historial,
    text="📋 HISTORIAL DE PARTIDAS",
    font=("Arial", 22, "bold"),
    bg="#17243b",
    fg="white"
).pack(pady=20)

entrada_busqueda = tk.Entry(
    pestana_historial,
    font=("Arial", 13),
    justify="center",
    width=30
)

entrada_busqueda.pack(pady=10)

entrada_busqueda.bind(
    "<Return>",
    lambda evento: mostrar_historial()
)

tk.Button(
    pestana_historial,
    text="🔍 BUSCAR JUGADOR",
    font=("Arial", 11, "bold"),
    command=mostrar_historial
).pack(pady=5)

tabla_historial = ttk.Treeview(
    pestana_historial,
    columns=("ID", "Fecha", "Nombre", "Jugador",
             "Computadora", "Resultado"),
    show="headings"
)

for columna in ("ID", "Fecha", "Nombre", "Jugador",
                "Computadora", "Resultado"):

    tabla_historial.heading(columna, text=columna)

    tabla_historial.column(
        columna,
        width=115,
        anchor="center"
    )

tabla_historial.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)

tk.Button(
    pestana_historial,
    text="MOSTRAR TODAS LAS PARTIDAS",
    font=("Arial", 11, "bold"),
    command=lambda: (
        entrada_busqueda.delete(0, tk.END),
        mostrar_historial()
    )
).pack(pady=10)


# =====================================
# 13. CERRAR PROGRAMA
# =====================================

def cerrar():

    respuesta = messagebox.askyesno(
        "Salir",
        "¿Seguro que querés cerrar el juego?"
    )

    if respuesta:
        conexion.close()
        ventana.destroy()


tk.Button(
    ventana,
    text="❌ CERRAR JUEGO",
    font=("Arial", 11, "bold"),
    bg="#b83232",
    fg="white",
    command=cerrar
).pack(pady=8)


ventana.protocol("WM_DELETE_WINDOW", cerrar)



# =====================================
# 14. INICIAR PROGRAMA
# =====================================

actualizar_ranking()
mostrar_historial()

nueva_partida()

ventana.mainloop()