// ============================================================
// AUTOMATED INCUBATOR MICROSCOPE — Arduino Nano V3
// Komunikasi: Hardware UART (pin 0=RX, pin 1=TX) → Raspberry Pi
//
// WIRING NANO ↔ RASPBERRY PI:
//   Nano pin 1 (TX) ──[1kΩ]──┬── RasPi RX (GPIO15)
//                             └──[2kΩ]── GND
//   Nano pin 0 (RX) ────────── RasPi TX (GPIO14)
//   Nano GND        ────────── RasPi GND
//
//   ⚠ WAJIB voltage divider di jalur Nano TX → RasPi RX
//      karena Nano = 5V logic, RasPi GPIO = 3.3V max!
//      (1kΩ + 2kΩ membagi 5V → ~3.3V)
//
//   ⚠ Jangan colok USB Nano ke PC saat terhubung ke RasPi
//      (USB & pin 0/1 share UART yang sama di Nano V3)
//
// Raspberry Pi setup (/boot/config.txt atau raspi-config):
//   enable_uart=1
//   Disable serial console: sudo raspi-config → Interface → Serial
//     → "login shell = No", "serial port hardware = Yes"
//   Python: serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
//
// Protokol AT/OK (handshake saat scan):
//   Arduino kirim : "AT A1"  (sudah sampai di well)
//   RasPi balas   : "OK"     (foto sudah diambil, lanjut)
//   RasPi bisa kirim "stop" kapan saja untuk hentikan scan
// ============================================================

// ===== Pin Definitions =====
#define STEP_X   2
#define DIR_X    3
#define STEP_Y   4
#define DIR_Y    5
#define STEP_Z   6
#define DIR_Z    7
#define LIM_X    8
#define LIM_Y    9
// Pin 0 (RX) dan Pin 1 (TX) = Hardware UART → Raspberry Pi
// JANGAN pakai pin 0/1 untuk hal lain

// ===== Speed & Timing =====
#define STEP_DELAY   250
#define STEP_DELAY1  250

// ===== Well Pitch =====
#define STEP_PER_WELL_X_96  1800
#define STEP_PER_WELL_Y_96  1800
#define STEP_PER_WELL_X_36  2600
#define STEP_PER_WELL_Y_36  2600

// ===== Homing Back-off =====
#define HOME_BACKOFF_X  400   // ← tune ini
#define HOME_BACKOFF_Y  600   // ← tune ini

// ===== Eject =====
#define EJECT_STEPS  5000     // ← tune ini

// ===== Position Trackers =====
long currentX = 0;
long currentY = 0;
long currentZ = 0;

// ===== Runtime State =====
int  plateType     = 96;
bool stopRequested = false;
bool isEjected     = false;

// ============================================================
// STEP FUNCTION
// ============================================================
void stepMotors(bool stepX, bool stepY, bool stepZ = false) {
  if (stepX) digitalWrite(STEP_X, HIGH);
  if (stepY) digitalWrite(STEP_Y, HIGH);
  if (stepZ) digitalWrite(STEP_Z, HIGH);
  delayMicroseconds(STEP_DELAY);
  if (stepY) digitalWrite(STEP_Y, LOW);
  if (stepZ) digitalWrite(STEP_Z, LOW);
  delayMicroseconds(STEP_DELAY);
  delayMicroseconds(STEP_DELAY1);
  if (stepX) digitalWrite(STEP_X, LOW);
  delayMicroseconds(STEP_DELAY1);
}

// ============================================================
// MOVE X+Y SIMULTAN
// ============================================================
void moveSteps(long stepX, long stepY, bool dirX, bool dirY) {
  digitalWrite(DIR_X, dirX);
  digitalWrite(DIR_Y, dirY);
  long maxSteps = max(abs(stepX), abs(stepY));
  for (long i = 0; i < maxSteps; i++) {
    if (stopRequested) return;
    stepMotors(i < abs(stepX), i < abs(stepY));
  }
}

// ============================================================
// MOVE Z
// ============================================================
void moveZSteps(long steps, bool dirZ) {
  digitalWrite(DIR_Z, dirZ);
  for (long i = 0; i < steps; i++) {
    if (stopRequested) return;
    stepMotors(false, false, true);
  }
  currentZ += dirZ ? steps : -steps;
}

// ============================================================
// CEK INCOMING STOP — dipanggil di dalam loop panjang
// Baca karakter dari UART tanpa blocking; set stopRequested
// jika RasPi kirim "stop" atau "cancel"
// ============================================================
void checkStop() {
  if (Serial.available()) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();
    if (incoming.equalsIgnoreCase("stop") ||
        incoming.equalsIgnoreCase("cancel")) {
      stopRequested = true;
    }
  }
}

// ============================================================
// HOMING
// ============================================================
void homing() {
  stopRequested = false;
  Serial.println(F("HOMING"));
  digitalWrite(DIR_X, LOW);
  digitalWrite(DIR_Y, HIGH);
  bool homeX = false, homeY = false;
  while (!(homeX && homeY)) {
    checkStop();
    if (stopRequested) { Serial.println(F("STOP")); return; }
    if (!homeX) homeX = digitalRead(LIM_X);
    if (!homeY) homeY = digitalRead(LIM_Y);
    stepMotors(!homeX, !homeY);
  }
  digitalWrite(DIR_X, HIGH);
  for (int i = 0; i < HOME_BACKOFF_X; i++) {
    checkStop();
    if (stopRequested) { Serial.println(F("STOP")); return; }
    stepMotors(true, false);
  }
  digitalWrite(DIR_Y, LOW);
  for (int i = 0; i < HOME_BACKOFF_Y; i++) {
    checkStop();
    if (stopRequested) { Serial.println(F("STOP")); return; }
    stepMotors(false, true);
  }
  currentX = currentY = 0;
  Serial.println(F("HOMED"));
}

// ============================================================
// MOVE TO WELL
// ============================================================
void moveToWell(char rowChar, int col) {
  int rowIndex = rowChar - 'A';
  int maxRow   = (plateType == 96) ? 8  : 6;
  int maxCol   = (plateType == 96) ? 12 : 6;
  int pitchX   = (plateType == 96) ? STEP_PER_WELL_X_96 : STEP_PER_WELL_X_36;
  int pitchY   = (plateType == 96) ? STEP_PER_WELL_Y_96 : STEP_PER_WELL_Y_36;

  if (rowIndex < 0 || rowIndex >= maxRow) { Serial.println(F("ERR:invalid_row")); return; }
  if (col < 1    || col > maxCol)         { Serial.println(F("ERR:invalid_col")); return; }

  long targetX = (long)(col - 1) * pitchX;
  long targetY = (long)rowIndex  * pitchY;
  bool dirX    = (targetX - currentX >= 0) ? HIGH : LOW;
  bool dirY    = (targetY - currentY >= 0) ? LOW  : HIGH;

  moveSteps(abs(targetX - currentX), abs(targetY - currentY), dirX, dirY);
  currentX = targetX;
  currentY = targetY;

  Serial.print(F("MOVED "));
  Serial.print(rowChar);
  Serial.println(col);
}

// ============================================================
// SERPENTINE SCAN dengan Raspi handshake AT/OK
//
// Alur per well:
//   1. Nano bergerak ke well
//   2. Nano kirim  → "AT A1\n"
//   3. RasPi ambil foto
//   4. RasPi balas → "OK\n"   (atau "stop" untuk batal)
//   5. Nano lanjut ke well berikutnya
// ============================================================
void serpentineScan() {
  stopRequested = false;
  int rows = (plateType == 96) ? 8  : 6;
  int cols = (plateType == 96) ? 12 : 6;

  Serial.print(F("SCAN_START "));
  Serial.println(plateType);

  for (int row = 0; row < rows; row++) {
    for (int cIdx = 0; cIdx < cols; cIdx++) {
      if (stopRequested) { Serial.println(F("STOP")); return; }

      int col = (row % 2 == 0) ? (cIdx + 1) : (cols - cIdx);
      moveToWell(char('A' + row), col);
      if (stopRequested) { Serial.println(F("STOP")); return; }

      // Kirim AT ke RasPi
      Serial.print(F("AT "));
      Serial.print(char('A' + row));
      Serial.println(col);

      // Tunggu OK dari RasPi (timeout 30 detik)
      unsigned long t0 = millis();
      bool ackReceived = false;
      while (!ackReceived) {
        if (millis() - t0 > 30000UL) {
          Serial.println(F("TIMEOUT"));
          return;
        }
        if (Serial.available()) {
          String ack = Serial.readStringUntil('\n');
          ack.trim();
          if (ack.equalsIgnoreCase("stop") ||
              ack.equalsIgnoreCase("cancel")) {
            stopRequested = true;
            Serial.println(F("STOP"));
            return;
          }
          if (ack.equalsIgnoreCase("ok")) {
            ackReceived = true;  // lanjut ke well berikutnya
          }
          // Balasan lain diabaikan, tetap tunggu OK
        }
      }
    }
  }
  Serial.println(F("SCAN_DONE"));
}

// ============================================================
// EJECT
// ============================================================
void ejectPlate() {
  if (isEjected) { Serial.println(F("ALREADY_EJECTED")); return; }
  Serial.println(F("EJECTING"));
  digitalWrite(DIR_X, HIGH);
  for (long i = 0; i < EJECT_STEPS; i++) {
    checkStop();
    if (stopRequested) { Serial.println(F("STOP")); return; }
    stepMotors(true, false);
  }
  currentX += EJECT_STEPS;
  isEjected = true;
  Serial.println(F("EJECTED"));
}

// ============================================================
// RETURN FROM EJECT
// ============================================================
void returnFromEject() {
  if (!isEjected) { Serial.println(F("NOT_EJECTED")); return; }
  isEjected = false;
  homing();
}

// ============================================================
// SETUP
// ============================================================
void setup() {
  pinMode(DIR_X,  OUTPUT); pinMode(STEP_X, OUTPUT);
  pinMode(DIR_Y,  OUTPUT); pinMode(STEP_Y, OUTPUT);
  pinMode(DIR_Z,  OUTPUT); pinMode(STEP_Z, OUTPUT);
  pinMode(LIM_X,  INPUT_PULLUP);
  pinMode(LIM_Y,  INPUT_PULLUP);

  // Hardware UART — pin 0 (RX), pin 1 (TX) — terhubung ke Raspberry Pi
  Serial.begin(115200);

  // Flush buffer sisa boot
  while (Serial.available()) Serial.read();

  Serial.println(F("READY"));
  Serial.println(F("Commands: home|scan|eject|return|A1..H12|U<n>|D<n>|setzero|status|stop|plate 96|36"));
}

// ============================================================
// MAIN LOOP — baca perintah dari Raspberry Pi via UART
// ============================================================
void loop() {
  if (!Serial.available()) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd.length() == 0) return;

  // STOP
  if (cmd.equalsIgnoreCase("stop")) {
    stopRequested = true;
    Serial.println(F("STOP"));
    return;
  }

  // Reset stop flag saat terima perintah baru yang valid
  stopRequested = false;

  // PLATE TYPE
  if (cmd.startsWith("plate ")) {
    int t = cmd.substring(6).toInt();
    if (t == 96 || t == 36) {
      plateType = t;
      Serial.print(F("PLATE "));
      Serial.println(plateType);
    } else {
      Serial.println(F("ERR:use plate 96 or plate 36"));
    }
    return;
  }

  // HOME
  if (cmd.equalsIgnoreCase("home"))   { homing(); return; }

  // EJECT
  if (cmd.equalsIgnoreCase("eject"))  { ejectPlate(); return; }

  // RETURN
  if (cmd.equalsIgnoreCase("return")) { returnFromEject(); return; }

  // SCAN
  if (cmd.equalsIgnoreCase("scan"))   { homing(); serpentineScan(); return; }

  // Z UP — "U" atau "U 500"
  if (cmd.startsWith("U") || cmd.startsWith("u")) {
    String arg = cmd.substring(1); arg.trim();
    long steps = (arg.length() > 0) ? arg.toInt() : 100;
    if (steps <= 0) steps = 100;
    moveZSteps(steps, HIGH);
    Serial.print(F("Z=")); Serial.println(currentZ);
    return;
  }

  // Z DOWN — "D" atau "D 500"
  if (cmd.startsWith("D") || cmd.startsWith("d")) {
    String arg = cmd.substring(1); arg.trim();
    long steps = (arg.length() > 0) ? arg.toInt() : 100;
    if (steps <= 0) steps = 100;
    moveZSteps(steps, LOW);
    Serial.print(F("Z=")); Serial.println(currentZ);
    return;
  }

  // SETZERO
  if (cmd.equalsIgnoreCase("setzero")) {
    currentZ = 0;
    Serial.println(F("Z=0"));
    return;
  }

  // STATUS
  if (cmd.equalsIgnoreCase("status")) {
    Serial.print(F("X="));       Serial.print(currentX);
    Serial.print(F(" Y="));      Serial.print(currentY);
    Serial.print(F(" Z="));      Serial.print(currentZ);
    Serial.print(F(" PLATE="));  Serial.print(plateType);
    Serial.print(F(" EJECTED=")); Serial.println(isEjected ? 1 : 0);
    return;
  }

  // WELL COMMAND: A1, B3, H12, F6, dll
  if (cmd.length() >= 2 && cmd.length() <= 3) {
    char rowChar = toupper(cmd.charAt(0));
    int  col     = cmd.substring(1).toInt();
    if (rowChar >= 'A' && rowChar <= 'H' && col > 0) {
      moveToWell(rowChar, col);
      return;
    }
  }

  Serial.print(F("ERR:unknown "));
  Serial.println(cmd);
}
