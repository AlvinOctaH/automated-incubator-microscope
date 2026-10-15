// ============================================================
// AUTOMATED INCUBATOR MICROSCOPE — Arduino Nano V3
// Based on: sketch_oct03a.ino
// Added: 36-well support, Raspi handshake (AT/OK),
//        stop command, status, plate toggle, custom Z step
// ============================================================

// ===== Pin Definitions =====
#define STEP_X   2
#define DIR_X  3
#define STEP_Y   4
#define DIR_Y  5
#define STEP_Z   6
#define DIR_Z  7
#define LIM_X   8
#define LIM_Y   9

// ===== Speed & Timing (sama persis dengan sketch_oct03a) =====
#define STEP_DELAY   250
#define STEP_DELAY1  250

// ===== Well Pitch =====
// 96-well: 9mm pitch × 200 steps/mm = 1800 steps (full-step, T8 leadscrew 1mm pitch)
#define STEP_PER_WELL_X_96  1800
#define STEP_PER_WELL_Y_96  1800
// 36-well: 13mm pitch × 200 = 2600 steps
#define STEP_PER_WELL_X_36  2600
#define STEP_PER_WELL_Y_36  2600

// ===== Homing Back-off =====
// Tune HOME_BACKOFF_X/Y sampai kamera tepat di center well A1
#define HOME_BACKOFF_X  400   // ← tune ini
#define HOME_BACKOFF_Y  600   // ← tune ini

// ===== Eject (Replace Wellplate) =====
// X bergerak ke arah BERLAWANAN dari limit switch (HIGH = menjauhi switch)
// Tune EJECT_STEPS sampai wellplate bebas dari bawah kamera/struktur
#define EJECT_STEPS  5000   // ← tune ini: tambah kalau belum cukup jauh

// ===== Position Trackers =====
long currentX = 0;
long currentY = 0;
long currentZ = 0;

// ===== Runtime State =====
int  plateType     = 96;
bool stopRequested = false;
bool isEjected     = false;

// ============================================================
// STEP FUNCTION (dari sketch_oct03a — X+Y simultan)
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
// HOMING
// ============================================================
void homing() {
  stopRequested = false;
  Serial.println(F("HOMING"));
  digitalWrite(DIR_X, LOW);
  digitalWrite(DIR_Y, HIGH);
  bool homeX = false, homeY = false;
  while (!(homeX && homeY)) {
    if (!homeX) homeX = digitalRead(LIM_X);
    if (!homeY) homeY = digitalRead(LIM_Y);
    stepMotors(!homeX, !homeY);
  }
  digitalWrite(DIR_X, HIGH);
  for (int i = 0; i < HOME_BACKOFF_X; i++) stepMotors(true, false);
  digitalWrite(DIR_Y, LOW);
  for (int i = 0; i < HOME_BACKOFF_Y; i++) stepMotors(false, true);
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
// SERPENTINE SCAN dengan Raspi handshake
// ============================================================
void serpentineScan() {
  stopRequested = false;
  int rows = (plateType == 96) ? 8  : 6;
  int cols = (plateType == 96) ? 12 : 6;

  Serial.print(F("SCAN_START ")); Serial.println(plateType);

  for (int row = 0; row < rows; row++) {
    for (int cIdx = 0; cIdx < cols; cIdx++) {
      if (stopRequested) { Serial.println(F("STOP")); return; }

      int col = (row % 2 == 0) ? (cIdx + 1) : (cols - cIdx);
      moveToWell(char('A' + row), col);
      if (stopRequested) { Serial.println(F("STOP")); return; }

      Serial.print(F("AT "));
      Serial.print(char('A' + row));
      Serial.println(col);

      unsigned long t0 = millis();
      while (!Serial.available()) {
        if (stopRequested) { Serial.println(F("STOP")); return; }
        if (millis() - t0 > 30000) { Serial.println(F("TIMEOUT")); return; }
      }
      String ack = Serial.readStringUntil('\n');
      ack.trim();
      if (ack.equalsIgnoreCase("stop") || ack.equalsIgnoreCase("cancel")) {
        stopRequested = true;
        Serial.println(F("STOP")); return;
      }
    }
  }
  Serial.println(F("SCAN_DONE"));
}

// ============================================================
// EJECT — geser X menjauhi limit switch agar wellplate bisa diganti
// ============================================================
void ejectPlate() {
  if (isEjected) { Serial.println(F("ALREADY_EJECTED")); return; }
  Serial.println(F("EJECTING"));
  // HIGH = arah berlawanan dari limit switch (menjauhi switch)
  digitalWrite(DIR_X, HIGH);
  for (long i = 0; i < EJECT_STEPS; i++) {
    if (stopRequested) { Serial.println(F("STOP")); return; }
    stepMotors(true, false);
  }
  currentX += EJECT_STEPS;
  isEjected = true;
  Serial.println(F("EJECTED"));
}

// RETURN — home ulang setelah ganti wellplate
void returnFromEject() {
  if (!isEjected) { Serial.println(F("NOT_EJECTED")); return; }
  isEjected = false;
  homing();   // home sudah print HOMED
}

// ============================================================
// SETUP
// ============================================================
void setup() {
  pinMode(DIR_X, OUTPUT); pinMode(STEP_X, OUTPUT);
  pinMode(DIR_Y, OUTPUT); pinMode(STEP_Y, OUTPUT);
  pinMode(DIR_Z, OUTPUT); pinMode(STEP_Z, OUTPUT);
  pinMode(LIM_X, INPUT_PULLUP);
  pinMode(LIM_Y, INPUT_PULLUP);

  Serial.begin(115200);
  Serial.println(F("READY"));
  Serial.println(F("Commands: home | scan | eject | return | A1..H12 | U <n> | D <n> | setzero | status | stop | plate 96|36"));
}

// ============================================================
// MAIN LOOP
// ============================================================
void loop() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd.length() == 0) return;

  // STOP
  if (cmd.equalsIgnoreCase("stop")) {
    stopRequested = true; Serial.println(F("STOP")); return;
  }

  // PLATE TYPE
  if (cmd.startsWith("plate ")) {
    int t = cmd.substring(6).toInt();
    if (t == 96 || t == 36) { plateType = t; Serial.print(F("PLATE ")); Serial.println(plateType); }
    else Serial.println(F("ERR:use plate 96 or plate 36"));
    return;
  }

  // HOME
  if (cmd.equalsIgnoreCase("home")) { homing(); return; }

  // EJECT — geser wellplate keluar
  if (cmd.equalsIgnoreCase("eject")) { ejectPlate(); return; }

  // RETURN — balik ke home setelah ganti wellplate
  if (cmd.equalsIgnoreCase("return")) { returnFromEject(); return; }

  // SCAN
  if (cmd.equalsIgnoreCase("scan")) { homing(); serpentineScan(); return; }

  // Z UP — "U" atau "U 500" (custom steps)
  if (cmd.startsWith("U") || cmd.startsWith("u")) {
    String arg = cmd.substring(1); arg.trim();
    long steps = arg.length() > 0 ? arg.toInt() : 100;
    if (steps <= 0) steps = 100;
    moveZSteps(steps, HIGH);
    Serial.print(F("Z=")); Serial.println(currentZ); return;
  }

  // Z DOWN — "D" atau "D 500"
  if (cmd.startsWith("D") || cmd.startsWith("d")) {
    String arg = cmd.substring(1); arg.trim();
    long steps = arg.length() > 0 ? arg.toInt() : 100;
    if (steps <= 0) steps = 100;
    moveZSteps(steps, LOW);
    Serial.print(F("Z=")); Serial.println(currentZ); return;
  }

  // SETZERO
  if (cmd.equalsIgnoreCase("setzero")) { currentZ = 0; Serial.println(F("Z=0")); return; }

  // STATUS
  if (cmd.equalsIgnoreCase("status")) {
    Serial.print(F("X=")); Serial.print(currentX);
    Serial.print(F(" Y=")); Serial.print(currentY);
    Serial.print(F(" Z=")); Serial.print(currentZ);
    Serial.print(F(" PLATE=")); Serial.print(plateType);
    Serial.print(F(" EJECTED=")); Serial.println(isEjected ? 1 : 0);
    return;
  }

  // WELL COMMAND: A1, B3, H12, F6, dll
  if (cmd.length() >= 2 && cmd.length() <= 3) {
    char rowChar = toupper(cmd.charAt(0));
    int  col     = cmd.substring(1).toInt();
    if (rowChar >= 'A' && rowChar <= 'H' && col > 0) { moveToWell(rowChar, col); return; }
  }

  Serial.print(F("ERR:unknown ")); Serial.println(cmd);
}
