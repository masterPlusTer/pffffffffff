from machine import Pin, SPI
import time

# Configuración de SPI y pines
spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(12), mosi=Pin(11))  # SPI optimizado
cs = Pin(10, Pin.OUT)   # Chip Select
dc = Pin(8, Pin.OUT)    # Data/Command
rst = Pin(9, Pin.OUT)   # Reset

# Offset para coordenadas (ajustar según el hardware)
OFFSET_X = 52  # Offset horizontal
OFFSET_Y = 40  # Offset vertical

def write_cmd(cmd):
    """Escribir un comando al controlador del display."""
    cs.value(0)
    dc.value(0)
    spi.write(bytearray([cmd]))
    cs.value(1)

def write_data(data):
    """Escribir datos al controlador del display."""
    cs.value(0)
    dc.value(1)
    spi.write(bytearray([data]))
    cs.value(1)

def init_display():
    """Inicializar el display."""
    rst.value(0)
    time.sleep(0.1)
    rst.value(1)
    time.sleep(0.1)

    write_cmd(0x01)  # Software reset
    time.sleep(0.15)

    write_cmd(0x11)  # Salir del modo de reposo
    time.sleep(0.12)

    write_cmd(0x3A)  # Formato de píxel: RGB565
    write_data(0x55)

    write_cmd(0x36)  # Configuración de memoria
    write_data(0x00)  # Ajuste de orientación
    write_cmd(0x21)  # Inversión de color activada

    write_cmd(0x2A)  # Rango de columnas
    write_data(0x00)
    write_data(0x00)
    write_data(0x00)
    write_data(0xEF)  # 239 columnas

    write_cmd(0x2B)  # Rango de filas
    write_data(0x00)
    write_data(0x00)
    write_data(0x01)
    write_data(0x3F)  # 319 filas

    write_cmd(0x29)  # Encender display

def set_active_window(x0, y0, x1, y1):
    """Configura la ventana activa del display."""
    x0 += OFFSET_X
    x1 += OFFSET_X
    y0 += OFFSET_Y
    y1 += OFFSET_Y
    write_cmd(0x2A)  # Configurar columnas
    write_data(x0 >> 8)  # Byte alto de x0
    write_data(x0 & 0xFF)  # Byte bajo de x0
    write_data(x1 >> 8)  # Byte alto de x1
    write_data(x1 & 0xFF)  # Byte bajo de x1

    write_cmd(0x2B)  # Configurar filas
    write_data(y0 >> 8)  # Byte alto de y0
    write_data(y0 & 0xFF)  # Byte bajo de y0
    write_data(y1 >> 8)  # Byte alto de y1
    write_data(y1 & 0xFF)  # Byte bajo de y1

def fill_screen_fast(color):
    """Llena toda la pantalla con un color usando un buffer por líneas."""
    set_active_window(0, 0, 239, 319)  # Toda la pantalla
    write_cmd(0x2C)  # Comando para escribir en memoria

    # Crear un buffer para una línea completa (240 píxeles)
    high_byte = color >> 8
    low_byte = color & 0xFF
    line_buffer = bytearray([high_byte, low_byte] * 240)

    # Enviar el buffer 320 veces (una vez por línea)
    for _ in range(320):
        cs.value(0)
        dc.value(1)
        spi.write(line_buffer)
        cs.value(1)

def draw_pixel(x, y, color):
    """Dibuja un píxel en las coordenadas especificadas."""
    set_active_window(x, y, x, y)  # Configurar para un solo píxel
    write_cmd(0x2C)
    write_data(color >> 8)  # Byte alto del color
    write_data(color & 0xFF)  # Byte bajo del color

# Inicializar el display
init_display()
fill_screen_fast(0b0000000000000000)  # Llenar la pantalla con negro

# Colores en formato RGB565
red = 0b1111100000000000    # Rojo puro
green = 0b0000011111100000  # Verde puro
blue = 0b0000000000011111   # Azul puro
yellow = 0b1111111111100000 # Amarillo
black = 0b0000000000000000  # Negro
white = 0b1111111111111111  # Blanco

# Dibujar píxeles en diferentes posiciones y colores
draw_pixel(0, 0, red)       # Esquina superior izquierda
draw_pixel(134, 0, red)       # Esquina superior derecha

draw_pixel(120, 150, blue)

draw_pixel(0, 239, blue) # Esquina inferior izquierda

draw_pixel(134, 239, green) # Esquina inferior derecha

