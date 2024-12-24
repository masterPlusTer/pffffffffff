from machine import Pin
import time


# Configuración de pines de color
G1 = Pin(2, Pin.OUT)  # Verde mitad superior
B1 = Pin(3, Pin.OUT)  # Azul mitad superior
R1 = Pin(4, Pin.OUT)  # Rojo mitad superior
G2 = Pin(5, Pin.OUT)  # Verde mitad inferior
B2 = Pin(8, Pin.OUT)  # azul mitad inferior
R2 = Pin(9, Pin.OUT)  # Rojo mitad inferior

# Configuración de pines de control
CLK = Pin(11, Pin.OUT)  # Reloj
LAT = Pin(12, Pin.OUT)  # Latch
OE = Pin(13, Pin.OUT)   # Enable (Output Enable)

# Pines de selección de filas
A = Pin(10, Pin.OUT)
B = Pin(16, Pin.OUT)
C = Pin(18, Pin.OUT)
D = Pin(20, Pin.OUT)
E = Pin(22, Pin.OUT)

# Función para apagar la salida
def clear_output():
    OE.value(1)  # Desactiva la salida para evitar parpadeo

# Función para seleccionar una fila específica usando un número en binario
def select_row(row):
    binary_row = "{:05b}".format(row)  # Convierte el número de fila a binario de 5 bits
    A.value(int(binary_row[4]))
    B.value(int(binary_row[3]))
    C.value(int(binary_row[2]))
    D.value(int(binary_row[1]))
    E.value(int(binary_row[0]))

# Función para iluminar LEDs en una fila con un color específico
def illuminate_row(color):
    if color == "red":
        R1.value(1)
        G1.value(0)
        B1.value(0)
        R2.value(1)
        G2.value(0)
        B2.value(0)
    elif color == "green":
        R1.value(0)
        G1.value(1)
        B1.value(0)
        R2.value(0)
        G2.value(1)
        B2.value(0)
    elif color == "blue":
        R1.value(0)
        G1.value(0)
        B1.value(1)
        R2.value(0)
        G2.value(0)
        B2.value(1)
    elif color == "celeste":
        R1.value(0)
        G1.value(1)
        B1.value(1)
        R2.value(0)
        G2.value(1)
        B2.value(1)
    elif color == "rosa":
        R1.value(1)
        G1.value(0)
        B1.value(1)
        R2.value(1)
        G2.value(0)
        B2.value(1)
    elif color == "yellow":
        R1.value(1)
        G1.value(1)
        B1.value(0)
        R2.value(1)
        G2.value(1)
        B2.value(0)
    elif color == "white":
        R1.value(1)
        G1.value(1)
        B1.value(1)
        R2.value(1)
        G2.value(1)
        B2.value(1)

    # Pulso de reloj para cada columna en la fila seleccionada
    for _ in range(64):  # Avanza por las 64 columnas en la fila
        CLK.value(1)
        CLK.value(0)

# Función para refrescar la pantalla fila por fila
def refresh_display(color, duration_ms):
    start_time = time.ticks_ms()  # Obtener el tiempo inicial
    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        for row in range(32):  # Controlamos las 32 filas para una matriz de 64x64
            clear_output()       # Apaga la salida mientras configuramos la fila
            select_row(row)      # Selecciona la fila actual
            illuminate_row(color) # Configura los LEDs en el color deseado para la fila seleccionada
            LAT.value(1)         # Aplica el latch para almacenar el estado actual
            LAT.value(0)
            OE.value(0)          # Activa la salida para iluminar la fila
            time.sleep_us(90)    # Reducir el tiempo para un refresco rápido
            OE.value(1)          # Desactiva la salida antes de la siguiente fila

# Ciclo principal
colors = ["red", "green", "blue", "celeste", "rosa", "yellow", "white"]
while True:
    for color in colors:
        print(f"Mostrando color: {color}")
        refresh_display(color, 2000)  # Mostrar cada color por 2000 ms (2 segundos)

