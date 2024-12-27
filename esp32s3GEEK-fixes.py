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

def fill_screen(color):
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
    
def draw_line(x0, y0, x1, y1, color):
    """Dibuja una línea entre los puntos (x0, y0) y (x1, y1) con el color especificado."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        draw_pixel(x0, y0, color)  # Dibuja el píxel en las coordenadas actuales
        if x0 == x1 and y0 == y1:  # Si hemos llegado al final
            break
        err2 = err * 2
        if err2 > -dy:
            err -= dy
            x0 += sx
        if err2 < dx:
            err += dx
            y0 += sy    
    
  
def draw_rectangle(x0, y0, x1, y1, color, filled=False):
    """Dibuja un rectángulo entre los puntos (x0, y0) y (x1, y1) con el color especificado.
    Si 'filled' es True, el rectángulo estará relleno."""
    if filled:
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                draw_pixel(x, y, color)
    else:
        for x in range(min(x0, x1), max(x0, x1) + 1):
            draw_pixel(x, y0, color)  # Línea superior
            draw_pixel(x, y1, color)  # Línea inferior
        for y in range(min(y0, y1), max(y0, y1) + 1):
            draw_pixel(x0, y, color)  # Línea izquierda
            draw_pixel(x1, y, color)  # Línea derecha


def draw_circle(x0, y0, radius, color, filled=False):
    """Dibuja un círculo con centro en (x0, y0) y un radio 'radius'.
    Si 'filled' es True, el círculo estará relleno."""
    x = radius
    y = 0
    err = 0

    while x >= y:
        if filled:
            # Dibuja líneas horizontales entre los extremos del círculo
            for i in range(x0 - x, x0 + x + 1):
                draw_pixel(i, y0 + y, color)  # Parte superior
                draw_pixel(i, y0 - y, color)  # Parte inferior
            for i in range(x0 - y, x0 + y + 1):
                draw_pixel(i, y0 + x, color)  # Lados arriba
                draw_pixel(i, y0 - x, color)  # Lados abajo

        # Dibuja el contorno del círculo en los octantes
        draw_pixel(x0 + x, y0 + y, color)
        draw_pixel(x0 - x, y0 + y, color)
        draw_pixel(x0 + x, y0 - y, color)
        draw_pixel(x0 - x, y0 - y, color)
        draw_pixel(x0 + y, y0 + x, color)
        draw_pixel(x0 - y, y0 + x, color)
        draw_pixel(x0 + y, y0 - x, color)
        draw_pixel(x0 - y, y0 - x, color)

        y += 1
        err += 1 + 2 * y
        if 2 * (err - x) + 1 > 0:
            x -= 1
            err += 1 - 2 * x
            
            
def draw_polygon(color, filled=False, *vertices):
    """
    Dibuja un polígono basado en una lista de vértices.
    
    :param color: Color en formato RGB565.
    :param filled: Si es True, rellena el polígono.
    :param vertices: Vértices del polígono como argumentos separados ((x1, y1), (x2, y2), ...).
    """
    if len(vertices) < 3:
        raise ValueError("Un polígono debe tener al menos 3 vértices.")
    
    if filled:
        # Algoritmo de llenado básico: escaneo horizontal
        min_y = min(y for _, y in vertices)
        max_y = max(y for _, y in vertices)
        
        for y in range(min_y, max_y + 1):
            intersections = []
            for i in range(len(vertices)):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i + 1) % len(vertices)]
                
                if y1 < y2:
                    x_start, y_start = x1, y1
                    x_end, y_end = x2, y2
                else:
                    x_start, y_start = x2, y2
                    x_end, y_end = x1, y1
                
                if y_start <= y < y_end:
                    x = int(x_start + (y - y_start) * (x_end - x_start) / (y_end - y_start))
                    intersections.append(x)
            
            intersections.sort()
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    draw_line(intersections[i], y, intersections[i + 1], y, color)
    else:
        # Dibuja el contorno del polígono conectando los vértices
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]  # Conecta con el siguiente vértice
            draw_line(x1, y1, x2, y2, color)
            
def draw_char(x, y, char, color, bg_color):
    """Dibuja un carácter en el display usando una fuente de 8x8 píxeles."""
    if char not in font_8x8:
        return  # Salta si el carácter no está en la fuente

    bitmap = font_8x8[char]
    for row_index, row in enumerate(bitmap):
        for col_index in range(8):
            if row & (1 << (7 - col_index)):  # Verifica cada bit
                draw_pixel(x + col_index, y + row_index, color)  # Pixel encendido
            else:
                draw_pixel(x + col_index, y + row_index, bg_color)  # Pixel apagado
def draw_text(x, y, text, color, bg_color):
    """Dibuja una cadena de texto comenzando en la posición (x, y)."""
    for i, char in enumerate(text):
        draw_char(x + i * 8, y, char, color, bg_color)  # Avanza 8 píxeles por carácter

font_8x8 = {
    'A': [
        0b00011000,
        0b00100100,
        0b01000010,
        0b01000010,
        0b01111110,
        0b01000010,
        0b01000010,
        0b00000000
    ],
    'B': [
        0b01111100,
        0b01000010,
        0b01000010,
        0b01111100,
        0b01000010,
        0b01000010,
        0b01111100,
        0b00000000
    ],
    # Añade más caracteres según sea necesario
}


  #//////////////////////////////////////////////////

# Inicializar el display
init_display()
fill_screen(0b0000000000000000)  # Llenar la pantalla con azul

# Colores en formato RGB565
red = 0b1111100000000000    # Rojo puro
green = 0b0000011111100000  # Verde puro
blue = 0b0000000000011111   # Azul puro
yellow = 0b1111111111100000 # Amarillo
black = 0b0000000000000000  # Negro
white = 0b1111111111111111  # Blanco

# Dibujar píxeles en diferentes posiciones y colores
#draw_pixel(0, 0, red)       # Esquina superior izquierda
#draw_pixel(134, 0, red)       # Esquina superior derecha

#draw_pixel(120, 150, blue)

#draw_pixel(0, 239, blue) # Esquina inferior izquierda

#draw_pixel(134, 239, green) # Esquina inferior derecha

#draw_line(134, 239,10, 10, green) # linea verde
#draw_line(134, 239,50, 50, red) # linea roja
#draw_line(134, 239,100,100, blue) # linea azul


# Dibuja un rectángulo sin relleno
#draw_rectangle(10, 10, 50, 30, color=0b0000011111100000)  # Color verde

# Dibuja un rectángulo con relleno
#draw_rectangle(60, 10, 100, 30, color=0b0000000000011111, filled=True)  # Color azul

# Dibuja un círculo sin relleno
#draw_circle(95, 95, radius=30, color=0b1111100000000000)  # Color rojo

# Dibuja un círculo relleno
#draw_circle(50, 150, radius=30, color=0xFFFF00, filled=True)  # Color amarillo


# Dibuja un polígono sin relleno
#draw_polygon(0b0000011111100000, False, (10, 10), (20, 50), (80, 60), (50, 10), (9, 10))

# Dibuja un polígono relleno
#draw_polygon(0b1111100000000000, True, (60, 60), (120, 50), (180, 60), (150, 100), (90, 100))



# Escribir texto en el display
draw_text(10, 20, "AB", 0b1111100000000000, 0b0000000000000000)  # Texto rojo sobre fondo negro



