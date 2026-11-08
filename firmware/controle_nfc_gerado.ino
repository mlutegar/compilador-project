// controle.ino — gerado automaticamente pelo compilador Tupã
// Dispositivo: controle
// Alvo: ESP32 DevKit v1

#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>

// ---- Pinos ----
#define LED_VERDE     16
#define LED_VERMELHO  17
#define BOTAO_1        4
#define NFC_SS         5
#define NFC_RST       22

MFRC522 leitorNFC(NFC_SS, NFC_RST);
byte UID_AUTORIZADO[4] = { 0xDE, 0xAD, 0xBE, 0xEF };

struct Cartao {
  bool valido;
};

Cartao nfcLer() {
  Cartao c; c.valido = false;
  if (!leitorNFC.PICC_IsNewCardPresent() || !leitorNFC.PICC_ReadCardSerial())
    return c;
  bool igual = (leitorNFC.uid.size == 4);
  for (byte i = 0; i < leitorNFC.uid.size && igual; i++)
    if (leitorNFC.uid.uidByte[i] != UID_AUTORIZADO[i]) igual = false;
  c.valido = igual;
  leitorNFC.PICC_HaltA();
  return c;
}

void ledVerde()    { digitalWrite(LED_VERDE, HIGH); digitalWrite(LED_VERMELHO, LOW); }
void ledVermelho() { digitalWrite(LED_VERMELHO, HIGH); digitalWrite(LED_VERDE, LOW); }
void ledApagar()   { digitalWrite(LED_VERDE, LOW); digitalWrite(LED_VERMELHO, LOW); }

int tentativas = 3;

void setup() {
  Serial.begin(115200);
  SPI.begin();
  leitorNFC.PCD_Init();
  pinMode(BOTAO_1, INPUT_PULLUP);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_VERMELHO, OUTPUT);
  ledApagar();
}

void loop() {
  // evento: ao botao(1)
  if (digitalRead(BOTAO_1) == LOW) {
    delay(30); // debounce
    Cartao cartao = nfcLer();
    if ((cartao.valido == true)) {
      ledVerde();
      delay(1500);
    } else {
      ledVermelho();
    }
    while (digitalRead(BOTAO_1) == LOW) delay(10);
  }
}
