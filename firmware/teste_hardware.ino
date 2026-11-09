// Teste de hardware do protótipo Tupã — ESP32-WROVER-DEV
// Placa na Arduino IDE: "ESP32 Wrover Module" · Serial Monitor em 115200
// Biblioteca: MFRC522 (GithubCommunity)
// Escrito à mão. Validado em bancada em 26/10/2026 (ver artigo/figuras/).

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN   5
#define RST_PIN  22
#define BTN      4
#define LED_G    25
#define LED_R    26
#define IR_PIN   34

MFRC522 rfid(SS_PIN, RST_PIN);
int lastBtn = -1, lastIr = -1;

void setup() {
  Serial.begin(115200);
  delay(500);
  pinMode(BTN, INPUT_PULLUP);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_R, OUTPUT);
  pinMode(IR_PIN, INPUT);

  Serial.println("\n== Teste de hardware Tupa ==");

  Serial.println("LED verde...");
  digitalWrite(LED_G, HIGH); delay(700); digitalWrite(LED_G, LOW);
  Serial.println("LED vermelho...");
  digitalWrite(LED_R, HIGH); delay(700); digitalWrite(LED_R, LOW);

  SPI.begin(18, 19, 23, SS_PIN);   // SCK, MISO, MOSI, SS
  rfid.PCD_Init();
  delay(50);
  byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.printf("RC522 versao: 0x%02X -> %s\n", v,
                (v == 0x00 || v == 0xFF) ? "FALHA: confira SPI, RST e 3.3V" : "OK");

  Serial.println("Aperte o botao, passe a mao no IR e aproxime um cartao.");
}

void loop() {
  int b = digitalRead(BTN);
  int ir = digitalRead(IR_PIN);

  if (b != lastBtn) {
    Serial.println(b == LOW ? "Botao: PRESSIONADO" : "Botao: solto");
    lastBtn = b;
  }
  if (ir != lastIr) {
    Serial.println(ir == LOW ? "IR: obstaculo detectado" : "IR: livre");
    lastIr = ir;
  }

  digitalWrite(LED_R, b == LOW);   // vermelho acende enquanto aperta o botao

  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    Serial.print("Cartao UID:");
    for (byte i = 0; i < rfid.uid.size; i++) Serial.printf(" %02X", rfid.uid.uidByte[i]);
    Serial.println();
    digitalWrite(LED_G, HIGH); delay(800); digitalWrite(LED_G, LOW);
    rfid.PICC_HaltA();
  }
  delay(20);
}
