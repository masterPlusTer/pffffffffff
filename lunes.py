import time
from machine import Pin, freq
import _thread  # Módulo para manejar los dos núcleos

# Overclocking opcional para mejorar el rendimiento
freq(250_000_000)

# Configuración de pines de color
R1 = Pin(4, Pin.OUT)
G1 = Pin(2, Pin.OUT)
B1 = Pin(3, Pin.OUT)
R2 = Pin(9, Pin.OUT)
G2 = Pin(5, Pin.OUT)
B2 = Pin(8, Pin.OUT)

# Configuración de pines de control
CLK = Pin(11, Pin.OUT)
LAT = Pin(12, Pin.OUT)
OE = Pin(13, Pin.OUT)

# Pines de selección de filas
A = Pin(10, Pin.OUT)
B = Pin(16, Pin.OUT)
C = Pin(18, Pin.OUT)
D = Pin(20, Pin.OUT)
E = Pin(22, Pin.OUT)

# Buffer para el patrón (bitmap)
bitmap = [
    0b1111111111111111000000000000000000000000000000001111111111111111,  # Ejemplo: borde superior
    0b0000000000000000111111111111111111111111111111110000000000000000,  # Ejemplo: borde central
    0b0000000000000000111111111111111111111111111111110000000000000000,  # Ejemplo: relleno
    0b1111111111111111000000000000000000000000000000001111111111111111,  # Ejemplo: borde inferior
    0b0000000000000000000000000000000000000000000000000000000000000000,  # Vacío
    0b0000000000000000000000000000000000000000000000000000000000000000,  # Vacío
    0b0000000000000000000000000000000000000000000000000000000000000000,  # Vacío
    0b0000000000000000000000000000000000000000000000000000000000000000,  # Vacío
    0b1111000000000000000000000000000000000000000000000000000000001111,  # Ejemplo: marco adicional
    0b0000111111111111111111111111111111111111111111111111111111110000,  # Ejemplo: centro lleno
    0b0000111111111111111111111111111111111111111111111111111111110000,  # Ejemplo: relleno
    0b1111000000000000000000000000000000000000000000000000000000001111,  # Ejemplo: borde adicional
    0b0000000000000000000000000000000000000000000000000000000000000000,  # Vacío
    0b0000000000000000000000000000000000000000000000000000000000000000,  # Vacío
    0b0000000000000000000000000000000000000000000000000000000000000000,  # Vacío
    0b1111111111111111000000000000000000000000000000001111111111111111,  # Ejemplo: borde inferior
] * 2  # Se repite para parte superior e inferior

# Función para seleccionar una fila específica
def select_row(row):
    binary_row = row & 0b11111
    A.value(binary_row & 0b1)
    B.value((binary_row >> 1) & 0b1)
    C.value((binary_row >> 2) & 0b1)
    D.value((binary_row >> 3) & 0b1)
    E.value((binary_row >> 4) & 0b1)

# Función para enviar datos RGB
def send_color_data(r1, g1, b1, r2, g2, b2):
    R1.value(r1)
    G1.value(g1)
    B1.value(b1)
    R2.value(r2)
    G2.value(g2)
    B2.value(b2)
    CLK.value(1)
    CLK.value(0)

# Dibujar una fila completa (superior e inferior)
def draw_pattern_row(row_pattern_upper, row_pattern_lower):
    for col in range(64):  # 64 columnas
        bit_upper = (row_pattern_upper >> (63 - col)) & 1
        bit_lower = (row_pattern_lower >> (63 - col)) & 1
        send_color_data(bit_upper, 0, 0, bit_lower, 0, 0)

# Refrescar la matriz usando el bitmap
def refresh_display():
    while True:
        for row in range(16):  # Multiplexado 1/16
            OE.value(1)  # Apagar salida mientras configuramos
            select_row(row)  # Seleccionar fila activa
            draw_pattern_row(bitmap[row], bitmap[row + 16])  # Enviar datos
            LAT.value(1)  # Actualizar latch
            LAT.value(0)
            OE.value(0)  # Encender salida
            time.sleep_us(800)  # Incrementar tiempo activo para reducir parpadeo

# Iniciar el refresco en un hilo
_thread.start_new_thread(refresh_display, ())

# Función principal
def main():
    while True:
        time.sleep(1)  # Mantener el patrón estático

# Ejecutar función principal
main()
