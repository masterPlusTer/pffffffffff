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

    // Inicia la comunicación Serial
    Serial.begin(9600);
    Serial.println("Arduino LCD Controller Ready");
    Serial.println("Send commands like:");
    Serial.println("TXT:Hello World");
    Serial.println("CLR");
    Serial.println("CUR:2,5");
}

void loop() {
    // Revisa si hay datos en el puerto Serial
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n'); // Lee el comando completo
        processCommand(command); // Procesa el comando recibido
    }
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

// Procesar comandos recibidos
void processCommand(String command) {
    // Dividir comando y datos
    int separatorIndex = command.indexOf(':');
    String cmd = command.substring(0, separatorIndex);
    String data = command.substring(separatorIndex + 1);

    // Procesar diferentes tipos de comandos
    if (cmd == "TXT") {
        // Escribir texto
        writeText(data.c_str());
        Serial.println("Text written: " + data);
    } else if (cmd == "CLR") {
        // Limpiar pantalla
        sendCommand(0x01);
        delay(2);
        Serial.println("Screen cleared");
    } else if (cmd == "CUR") {
        // Mover cursor
        int commaIndex = data.indexOf(',');
        if (commaIndex != -1) {
            int line = data.substring(0, commaIndex).toInt();
            int column = data.substring(commaIndex + 1).toInt();
            setCursor(line, column);
            Serial.println("Cursor moved to: Line " + String(line) + ", Column " + String(column));
        } else {
            Serial.println("Invalid CUR format. Use CUR:line,column");
        }
    } else {
        Serial.println("Unknown Command");
    }
}

// Escribir texto en el display
void writeText(const char* text) {
    while (*text) {
        sendData(*text++);
    }
}

// Posicionar el cursor en una línea y columna
void setCursor(int line, int column) {
    byte address;
    switch (line) {
        case 1: address = 0x00 + column; break; // Línea 1
        case 2: address = 0x40 + column; break; // Línea 2
        case 3: address = 0x14 + column; break; // Línea 3
        case 4: address = 0x54 + column; break; // Línea 4
        default: return; // Salir si la línea no es válida
    }
    sendCommand(0x80 | address); // Mover el cursor
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
        digitalWrite(dataPins[i], (value >> i) & 0x01); // Enviar cada bit
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
