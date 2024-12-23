import machine
import utime

# Overclock a 280 MHz
machine.freq(280_000_000)

# Configuración de pines
pins = {
    "R1": machine.Pin(2, machine.Pin.OUT),
    "G1": machine.Pin(3, machine.Pin.OUT),
    "B1": machine.Pin(4, machine.Pin.OUT),
    "R2": machine.Pin(5, machine.Pin.OUT),
    "G2": machine.Pin(8, machine.Pin.OUT),
    "B2": machine.Pin(9, machine.Pin.OUT),
    "CLK": machine.Pin(11, machine.Pin.OUT),
    "LAT": machine.Pin(12, machine.Pin.OUT),
    "OE": machine.Pin(13, machine.Pin.OUT),
    "A": machine.Pin(10, machine.Pin.OUT),
    "B": machine.Pin(16, machine.Pin.OUT),
    "C": machine.Pin(18, machine.Pin.OUT),
    "D": machine.Pin(20, machine.Pin.OUT),
    "E": machine.Pin(22, machine.Pin.OUT),
}

def refresh_display(buffer):
    for row in range(32):
        clear_output()
        select_row(row)
        illuminate_row(row, buffer)
        pins["LAT"].value(1)
        pins["LAT"].value(0)
        pins["OE"].value(0)
        utime.sleep_us(100)

# Apaga los LEDs
def clear_output():
    pins["OE"].value(1)  # Apaga todas las filas

# Selecciona la fila específica
def select_row(row):
    binary = "{:05b}".format(row)
    pins["A"].value(int(binary[4]))
    pins["B"].value(int(binary[3]))
    pins["C"].value(int(binary[2]))
    pins["D"].value(int(binary[1]))
    pins["E"].value(int(binary[0]))

# Enciende los LEDs según el buffer
def illuminate_row(row, buffer):
    for col in range(64):
        pins["R1"].value(buffer[row][col])       # R1 (Arriba)
        pins["R2"].value(buffer[row + 32][col]) # R2 (Abajo)
        pins["CLK"].value(1)
        pins["CLK"].value(0)

# Conversión de formato hexadecimal a matriz de 64x64
def hex_to_buffer(hex_data):
    """
    Convierte una lista de valores hexadecimales en un buffer de bits (64x64).
    """
    buffer = [[0 for _ in range(64)] for _ in range(64)]
    for row, hex_value in enumerate(hex_data):
        try:
            if isinstance(hex_value, str) and hex_value.startswith("0x"):
                int_value = int(hex_value, 16)
            elif isinstance(hex_value, int):
                int_value = hex_value
            else:
                raise ValueError(f"Valor inválido en fila {row}: {hex_value}")

            # Alternativa manual a zfill()
            binary_string = bin(int_value)[2:]  # Quita '0b'
            binary_string = "0" * (64 - len(binary_string)) + binary_string  # Rellenar con ceros
            for col, bit in enumerate(binary_string):
                buffer[row][col] = int(bit)
        except Exception as e:
            print(f"Error al procesar la fila {row}: {e}")
            raise
    return buffer

# Datos en formato hexadecimal (ejemplo)
hex_data = [
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10000000000000, 0x10, 0x120400000000,
    0x0, 0x200000000, 0x100000000000, 0x0, 0x1000000, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x2000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x800, 0x0, 0x8, 0x80000, 0x0, 0x0, 0x4, 0x800, 0x0
]

# Convertimos los datos hexadecimales al buffer
buffer = hex_to_buffer(hex_data)

# Ciclo principal
while True:
    refresh_display(buffer)

