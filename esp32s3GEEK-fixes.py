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
    write_data(x0 >> 8)
    write_data(x0 & 0xFF)
    write_data(x1 >> 8)
    write_data(x1 & 0xFF)

    write_cmd(0x2B)  # Configurar filas
    write_data(y0 >> 8)
    write_data(y0 & 0xFF)
    write_data(y1 >> 8)
    write_data(y1 & 0xFF)
def set_rotation(rotation):
    """
    Configura la orientación del display.
    :param rotation: 0, 1, 2, o 3 (0: normal, 1: 90°, 2: 180°, 3: 270°)
    """
    madctl_values = [0x00, 0x60, 0xC0, 0xA0]
    if rotation < 0 or rotation > 3:
        raise ValueError("La rotación debe ser 0, 1, 2 o 3")
    
    write_cmd(0x36)  # Comando MADCTL
    write_data(madctl_values[rotation])

    global WIDTH, HEIGHT, OFFSET_X, OFFSET_Y
    if rotation % 2 == 0:
        WIDTH, HEIGHT = 240, 320
        OFFSET_X, OFFSET_Y = 52, 40
    else:
        WIDTH, HEIGHT = 320, 240
        OFFSET_X, OFFSET_Y = 40, 52
            

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
    """
    Dibuja un rectángulo entre los puntos (x0, y0) y (x1, y1) con el color especificado.
    Si 'filled' es True, el rectángulo estará relleno.
    """
    if filled:
        # Optimización para rectángulos rellenos usando ventanas y buffers
        x_start = min(x0, x1)
        x_end = max(x0, x1)
        y_start = min(y0, y1)
        y_end = max(y0, y1)
        
        set_active_window(x_start, y_start, x_end, y_end)  # Configurar la ventana activa
        write_cmd(0x2C)  # Comando para escribir en memoria
        
        # Crear un buffer para una línea completa
        line_length = x_end - x_start + 1
        line_buffer = bytearray([color >> 8, color & 0xFF] * line_length)
        
        # Enviar líneas al display
        for _ in range(y_start, y_end + 1):
            cs.value(0)
            dc.value(1)
            spi.write(line_buffer)
            cs.value(1)
    else:
        # Contorno del rectángulo (no relleno)
        # Líneas horizontales superior e inferior
        for x in range(min(x0, x1), max(x0, x1) + 1):
            draw_pixel(x, min(y0, y1), color)  # Línea superior
            draw_pixel(x, max(y0, y1), color)  # Línea inferior
        
        # Líneas verticales izquierda y derecha
        for y in range(min(y0, y1), max(y0, y1) + 1):
            draw_pixel(min(x0, x1), y, color)  # Línea izquierda
            draw_pixel(max(x0, x1), y, color)  # Línea derecha


def draw_circle(x0, y0, radius, color, filled=False):
    """
    Dibuja un círculo con centro en (x0, y0) y un radio 'radius'.
    Si 'filled' es True, el círculo estará relleno.
    """
    x = radius
    y = 0
    err = 0

    while x >= y:
        if filled:
            # Dibuja líneas horizontales para rellenar el círculo
            set_active_window(x0 - x, y0 + y, x0 + x, y0 + y)
            write_cmd(0x2C)
            line_color = bytearray([color >> 8, color & 0xFF] * (2 * x + 1))
            cs.value(0)
            dc.value(1)
            spi.write(line_color)
            cs.value(1)

            set_active_window(x0 - x, y0 - y, x0 + x, y0 - y)
            write_cmd(0x2C)
            cs.value(0)
            dc.value(1)
            spi.write(line_color)
            cs.value(1)

            set_active_window(x0 - y, y0 + x, x0 + y, y0 + x)
            write_cmd(0x2C)
            line_color = bytearray([color >> 8, color & 0xFF] * (2 * y + 1))
            cs.value(0)
            dc.value(1)
            spi.write(line_color)
            cs.value(1)

            set_active_window(x0 - y, y0 - x, x0 + y, y0 - x)
            write_cmd(0x2C)
            cs.value(0)
            dc.value(1)
            spi.write(line_color)
            cs.value(1)
        else:
            # Dibuja solo el contorno del círculo
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
    :param vertices: Vértices del polígono como argumentos ((x1, y1), (x2, y2), ...).
    """
    if len(vertices) < 3:
        raise ValueError("Un polígono debe tener al menos 3 vértices.")
    
    if filled:
        # Escaneo horizontal para llenar el polígono
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
                    set_active_window(intersections[i], y, intersections[i + 1], y)
                    write_cmd(0x2C)  # Comando para escribir en memoria
                    line_color = bytearray([color >> 8, color & 0xFF] * (intersections[i + 1] - intersections[i] + 1))
                    cs.value(0)
                    dc.value(1)
                    spi.write(line_color)
                    cs.value(1)
    else:
        # Dibuja el contorno del polígono
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
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
def text(x, y, text, color, bg_color):
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

def show_bmp(file_path, x_offset=0, y_offset=0):
    """
    Muestra un archivo BMP en el display reflejado horizontalmente.
    :param file_path: Ruta del archivo BMP.
    :param x_offset: Desplazamiento horizontal para dibujar la imagen.
    :param y_offset: Desplazamiento vertical para dibujar la imagen.
    """
    with open(file_path, "rb") as bmp_file:
        # Leer el encabezado BMP
        bmp_file.seek(10)
        pixel_data_offset = int.from_bytes(bmp_file.read(4), "little")

        bmp_file.seek(18)
        width = int.from_bytes(bmp_file.read(4), "little")
        height = int.from_bytes(bmp_file.read(4), "little")

        bmp_file.seek(28)
        bits_per_pixel = int.from_bytes(bmp_file.read(2), "little")

        if bits_per_pixel != 24:
            raise ValueError("Solo se admiten BMP de 24 bits.")

        # Configurar la ventana activa en el display
        set_active_window(x_offset, y_offset, x_offset + width - 1, y_offset + height - 1)
        write_cmd(0x2C)  # Comando para escribir en memoria

        # Mover a los datos de píxeles
        bmp_file.seek(pixel_data_offset)

        # Buffer para procesar una línea completa
        line_buffer = bytearray(width * 3)  # Buffer para la línea en formato RGB888
        mirrored_line = bytearray(width * 2)  # Buffer para la línea reflejada en RGB565

        # Procesar línea por línea
        for y in range(height):
            # Leer una línea completa en formato RGB888
            bmp_file.readinto(line_buffer)

            # Convertir y reflejar la línea
            for x in range(width):
                b = line_buffer[3 * x]
                g = line_buffer[3 * x + 1]
                r = line_buffer[3 * x + 2]

                # Convertir a RGB565
                color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

                # Insertar el color reflejado
                mirrored_x = width - x - 1
                mirrored_line[2 * mirrored_x] = color >> 8
                mirrored_line[2 * mirrored_x + 1] = color & 0xFF

            # Enviar la línea reflejada al display
            cs.value(0)
            dc.value(1)
            spi.write(mirrored_line)
            cs.value(1)


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


set_rotation(3)  # Apaisado (90 grados)



# Dibujar píxeles en diferentes posiciones y colores
#draw_pixel(0, 0, red)       # Esquina superior izquierda
draw_pixel(134, 0, red)       # Esquina superior derecha

draw_pixel(120, 150, blue)

#draw_pixel(0, 239, blue) # Esquina inferior izquierda

#draw_pixel(134, 239, green) # Esquina inferior derecha

draw_line(134, 239,10, 10, green) # linea verde
draw_line(134, 239,50, 50, red) # linea roja
draw_line(134, 239,100,100, blue) # linea azul


# Dibuja un rectángulo sin relleno
#draw_rectangle(10, 10, 50, 30, color=0b0000011111100000)  # Color verde

# Dibuja un rectángulo con relleno
draw_rectangle(60, 10, 100, 30, color=0b0000000000011111, filled=True)  # Color azul

 #Dibuja un círculo sin relleno
draw_circle(95, 95, radius=30, color=0b1111100000000000)  # Color rojo

# Dibuja un círculo relleno
draw_circle(50, 50, radius=30, color=0xFFFF00, filled=True)  # Color amarillo


# Dibuja un polígono sin relleno
#draw_polygon(0b0000011111100000, False, (10, 10), (20, 50), (80, 60), (50, 10), (9, 10))

# Dibuja un polígono relleno
draw_polygon(0b1111100000000000, True, (60, 60), (120, 50), (180, 60), (150, 100), (90, 100))



# Escribir texto en el display
text(10, 20, "AB", 0b1111100000000000, 0b0000001111111111)  # Texto rojo sobre fondo negro

show_bmp("/ESP32-S3-GEEK.bmp", x_offset=0, y_offset=0)


