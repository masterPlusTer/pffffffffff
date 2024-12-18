from machine import Pin, SPI
import time

# Configuración del SPI
spi = SPI(1, baudrate=5000000, polarity=0, phase=0, sck=Pin(12), mosi=Pin(11))
cs = Pin(10, Pin.OUT)   # Chip Select
dc = Pin(8, Pin.OUT)    # Data/Command
rst = Pin(9, Pin.OUT)   # Reset

# Función para enviar comandos
def write_cmd(cmd):
    cs.value(0)
    dc.value(0)  # Modo comando
    spi.write(bytearray([cmd]))
    cs.value(1)

# Función para enviar datos
def write_data(data):
    cs.value(0)
    dc.value(1)  # Modo datos
    spi.write(bytearray([data]))
    cs.value(1)

# Inicialización del display
def init_display():
    rst.value(0)  # Reinicia el display
    time.sleep(0.1)
    rst.value(1)
    time.sleep(0.1)

    write_cmd(0x01)  # Reset por software
    time.sleep(0.15)

    write_cmd(0x11)  # Sleep Out
    time.sleep(0.12)

    write_cmd(0x3A)  # Configuración de formato de píxeles
    write_data(0x55)  # Formato RGB565

    write_cmd(0x36)  # MADCTL: Orientación y formato
    write_data(0x00)  # Orientación estándar, RGB
    write_cmd(0x21)  # Invertir polaridad de bits

    # Configuración de rango
# Configuración de rango para columnas (ancho 240 píxeles)
    write_cmd(0x2A)  # Configuración de columnas
    write_data(0x00)  # Inicio alto
    write_data(0x00)  # Inicio bajo (columna 0)
    write_data(0x00)  # Fin alto
    write_data(0xEF)  # Fin bajo (columna 239)

    # Configuración de rango para filas (alto 135 píxeles)
    write_cmd(0x2B)  # Configuración de filas
    write_data(0x00)  # Inicio alto
    write_data(0x00)  # Inicio bajo (fila 0)
    write_data(0x00)  # Fin alto
    write_data(0x86)  # Fin bajo (fila 134)

    write_cmd(0x29)  # Encender el display

# Llenar la pantalla con un color
def fill_screen(color):
    write_cmd(0x2C)  # Escribir en memoria
    for _ in range(135 * 240):  # Total de píxeles
        write_data(color >> 8)
        write_data(color & 0xFF)

# Código principal
init_display()

# Código principal
init_display()
fill_screen(0b0000000000011111)  # Rellenar pantalla con azul

