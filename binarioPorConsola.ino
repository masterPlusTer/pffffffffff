// Pines para backlight y control
const int backlightPin = A3; // Backlight
const int rs = 9;           // RS
const int rw = 10;          // RW
const int e = 11;           // Enable
const int dataPins[8] = {2, 3, 4, 5, 6, 7, 8, 12}; // DB0-DB7

void setup() {
    pinMode(backlightPin, OUTPUT);
    analogWrite(backlightPin, 200); // Encender backlight
    pinMode(rs, OUTPUT);
    pinMode(rw, OUTPUT);
    pinMode(e, OUTPUT);
    for (int i = 0; i < 8; i++) {
        pinMode(dataPins[i], OUTPUT);
    }

    Serial.begin(9600);
    Serial.println("Escribe un valor binario (8 bits) para mostrar en el display.");
    Serial.println("Ejemplo: 01000001 (corresponde a 'A')");
    Serial.println("Escribe 'READ' para leer lo que está en el display.");

    // Inicializar el display
    initializeDisplay();
    Serial.println("Display inicializado.");
}

void loop() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n'); // Lee hasta un salto de línea
        input.trim(); // Elimina espacios o caracteres extras

        if (input.equalsIgnoreCase("READ")) {
            readDisplay(); // Leer y mostrar lo que está en el display
        } else if (input.length() == 8 && isBinary(input)) {
            byte value = binaryToByte(input);
            sendData(value); // Enviar el valor binario al display
            Serial.print("Mostrando en el display: ");
            Serial.println(input);
        } else {
            Serial.println("Entrada no válida. Ingresa 'READ' o un valor binario (8 bits).");
        }
    }
}

// Inicializar el display
void initializeDisplay() {
    delay(50); // Espera inicial

    sendCommand(0x30); // Modo 8 bits
    delay(5);
    sendCommand(0x30); // Repetir configuración
    delayMicroseconds(150);
    sendCommand(0x30); // Última configuración
    delayMicroseconds(150);

    sendCommand(0x38); // Modo 8 bits, 2 líneas, 5x8 puntos
    sendCommand(0x0C); // Display ON, cursor OFF
    sendCommand(0x06); // Incrementar cursor automáticamente
    sendCommand(0x01); // Limpiar pantalla
    delay(2);
}

// Validar si la entrada es binaria
bool isBinary(String input) {
    for (char c : input) {
        if (c != '0' && c != '1') {
            return false;
        }
    }
    return true;
}

// Convertir una cadena binaria a un byte
byte binaryToByte(String binary) {
    byte value = 0;
    for (int i = 0; i < 8; i++) {
        value <<= 1; // Desplazar a la izquierda
        if (binary[i] == '1') {
            value |= 1; // Establecer el bit si es '1'
        }
    }
    return value;
}

// Leer y mostrar lo que está en el display
void readDisplay() {
    Serial.println("Leyendo contenido del display:");
    pinMode(rs, OUTPUT);
    pinMode(rw, OUTPUT);

    for (int addr = 0; addr < 16; addr++) { // Suponiendo 16 caracteres por línea
        sendCommand(0x80 | addr); // Mover el cursor a la dirección DDRAM
        byte data = readData();   // Leer el carácter en esa posición
        Serial.print((char)data); // Mostrar el carácter leído
    }

    Serial.println(); // Nueva línea después de leer la línea completa
}

// Leer datos del display
byte readData() {
    pinMode(rs, OUTPUT);
    pinMode(rw, OUTPUT);
    for (int i = 0; i < 8; i++) {
        pinMode(dataPins[i], INPUT); // Configurar pines de datos como entrada
    }

    digitalWrite(rs, HIGH); // RS = 1 para datos
    digitalWrite(rw, HIGH); // RW = 1 para lectura
    digitalWrite(e, HIGH);
    delayMicroseconds(1);

    byte value = 0;
    for (int i = 0; i < 8; i++) {
        value |= (digitalRead(dataPins[i]) << i);
    }

    digitalWrite(e, LOW);
    delayMicroseconds(100);

    for (int i = 0; i < 8; i++) {
        pinMode(dataPins[i], OUTPUT); // Restaurar pines como salida
    }

    return value;
}

// Enviar un comando al display
void sendCommand(byte command) {
    delay(2);
    digitalWrite(rs, LOW); // RS = 0 para comando
    digitalWrite(rw, LOW); // RW = 0 para escritura
    write8Bits(command);
    pulseEnable();
}

// Enviar datos al display
void sendData(byte data) {
    delay(2);
    digitalWrite(rs, HIGH); // RS = 1 para datos
    digitalWrite(rw, LOW);  // RW = 0 para escritura
    write8Bits(data);
    pulseEnable();
}

// Escribir 8 bits en el display
void write8Bits(byte value) {
    for (int i = 0; i < 8; i++) {
        digitalWrite(dataPins[i], (value >> i) & 0x01);
    }
}

// Generar un pulso en Enable
void pulseEnable() {
    digitalWrite(e, HIGH);
    delayMicroseconds(1);
    digitalWrite(e, LOW);
    delayMicroseconds(100);
}
