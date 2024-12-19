from machine import Pin, SPI
import time

spi = SPI(1, baudrate=5000000, polarity=0, phase=0, sck=Pin(12), mosi=Pin(11))
cs = Pin(10, Pin.OUT)   # Chip Select
dc = Pin(8, Pin.OUT)    # Data/Command
rst = Pin(9, Pin.OUT)   # Reset

def write_cmd(cmd):
    cs.value(0)
    dc.value(0)
    spi.write(bytearray([cmd]))
    cs.value(1)

def write_data(data):
    cs.value(0)
    dc.value(1)
    spi.write(bytearray([data]))
    cs.value(1)

def init_display():
    rst.value(0)
    time.sleep(0.1)
    rst.value(1)
    time.sleep(0.1)

    write_cmd(0x01)
    time.sleep(0.15)

    write_cmd(0x11)
    time.sleep(0.12)

    write_cmd(0x3A)
    write_data(0x55)

    write_cmd(0x36)
    write_data(0x00)
    write_cmd(0x21)

    write_cmd(0x2A)
    write_data(0x00)
    write_data(0x00)
    write_data(0x00)
    write_data(0xEF)

    write_cmd(0x2B)
    write_data(0x00)
    write_data(0x00)
    write_data(0x01)
    write_data(0x3F)

    write_cmd(0x29)

def fill_screen(color):
    write_cmd(0x2C)
    for _ in range(240 * 320):
        write_data(color >> 8)
        write_data(color & 0xFF)
        
def draw_pixel(x, y, color):
    # Configurar el rango para un solo píxel
    write_cmd(0x2A)  # Configurar columnas
    write_data(x >> 8)  # Byte alto de X
    write_data(x & 0xFF)  # Byte bajo de X
    write_data(x >> 8)  # Byte alto de X (repetido)
    write_data(x & 0xFF)  # Byte bajo de X (repetido)

    write_cmd(0x2B)  # Configurar filas
    write_data(y >> 8)  # Byte alto de Y
    write_data(y & 0xFF)  # Byte bajo de Y
    write_data(y >> 8)  # Byte alto de Y (repetido)
    write_data(y & 0xFF)  # Byte bajo de Y (repetido)

    # Escribir el color del píxel
    write_cmd(0x2C)  # Escribir en memoria
    write_data(color >> 8)  # Byte alto del color
    write_data(color & 0xFF)  # Byte bajo del color

init_display()
fill_screen(0b0000000000000000) 

# Dibuja píxeles en las esquinas y el centro

# Colores en RGB565
red = 0b1111100000000000    # Rojo puro
green = 0b0000011111100000  # Verde puro
blue = 0b0000000000011111   # Azul puro
yellow = 0b1111111111100000 # Amarillo
black = 0b0000000000000000  # Negro
white = 0b1111111111111111  # Blanco

# Dibujar píxeles en diferentes colores # apartir de 60 para la x , y a partir de 50 para la Y 
#draw_pixel(120, 150, red)    # Centro (Rojo)
#draw_pixel(100, 150, green)  # Verde
#draw_pixel(140, 150, blue)   # Azul
#draw_pixel(120, 130, yellow) # Amarillo
#draw_pixel(120, 170, black)  # Negro
draw_pixel(60, 50, white)  # Blanco


