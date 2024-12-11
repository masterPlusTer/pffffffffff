// Pines para backlight
const int backlightPin = A3; // Pin para backlight

// Pines del display
const int rs = 10;  // Pin RS
const int e = 8;    // Pin Enable (E)
const int dataPins[8] = {2, 3, 4, 5, 6, 7, 11, A2}; // DB6 -> 11

void setup() {
    // Configurar el backlight
    pinMode(backlightPin, OUTPUT);
    analogWrite(backlightPin, 200); // Nivel de backlight (0-255)

    // Configurar pines del display como salida
    pinMode(rs, OUTPUT);
    pinMode(e, OUTPUT);
    for (int i = 0; i < 8; i++) {
        pinMode(dataPins[i], OUTPUT);
    }

    // Inicializar el display
    initializeDisplay();

    // Prueba de un valor binario
    testSingleBinary(); // Llama a la función para probar un binario
}

void loop() {
    // El loop queda vacío
}

// Inicializar el display en modo 8 bits
void initializeDisplay() {
    delay(50); // Espera inicial
    sendCommand(0x38); // Configuración: 8 bits, 2 líneas, 5x8 puntos
    sendCommand(0x0C); // Display ON, cursor OFF
    sendCommand(0x06); // Incrementar cursor automáticamente
    sendCommand(0x01); // Limpiar pantalla
    delay(2); // Esperar limpieza
}

// Prueba de un valor binario
void testSingleBinary() {
    byte binaryValue = 0b11111100; // Cambia este valor binario (Ejemplo: 'A')
    sendData(binaryValue);        // Enviar el valor binario al display
    delay(5000);                  // Espera para observar el resultado
}

// Enviar un comando al display
void sendCommand(byte command) {
    digitalWrite(rs, LOW); // RS = 0 para comando
    write8Bits(command);
    pulseEnable();
}

// Enviar datos al display
void sendData(byte data) {
    digitalWrite(rs, HIGH); // RS = 1 para datos
    write8Bits(data);
    pulseEnable();
}

// Escribir 8 bits en los pines de datos
void write8Bits(byte value) {
    for (int i = 0; i < 8; i++) {
        digitalWrite(dataPins[i], (value >> i) & 0x01);
        delayMicroseconds(5); // Retardo para estabilizar
    }
}

// Generar un pulso en Enable
void pulseEnable() {
    digitalWrite(e, HIGH);
    delayMicroseconds(20); // Pulso más largo
    digitalWrite(e, LOW);
    delayMicroseconds(100); // Espera para procesar
}

