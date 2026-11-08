// controle.ino — equivalente manual em C++/Arduino do exemplo controle.tupa
// Gerado para a comparacao "12 linhas de Tupa x N linhas de C++" do pitch.
// Alvo: ESP32 DevKit v1 + leitor NFC MFRC522 + LEDs + botao.

#include <SPI.h>
#include <MFRC522.h>

// ---- Mapeamento de pinos ----
#define PIN_SS      5
#define PIN_RST     22
#define PIN_BOTAO_1 4
#define PIN_LED_VERDE    16
#define PIN_LED_VERMELHO 17

// UID de um cartao autorizado (exemplo)
byte UID_AUTORIZADO[4] = { 0xDE, 0xAD, 0xBE, 0xEF };

MFRC522 leitor(PIN_SS, PIN_RST);

int tentativas = 3;

struct Cartao {
  bool valido;
};

// Le um cartao NFC e diz se e valido
Cartao nfcLer() {
  Cartao cartao;
  cartao.valido = false;

  if (!leitor.PICC_IsNewCardPresent() || !leitor.PICC_ReadCardSerial()) {
    return cartao;
  }

  bool igual = (leitor.uid.size == 4);
  for (byte i = 0; i < leitor.uid.size && igual; i++) {
    if (leitor.uid.uidByte[i] != UID_AUTORIZADO[i]) {
      igual = false;
    }
  }

  cartao.valido = igual;
  leitor.PICC_HaltA();
  return cartao;
}

void ledVerde() {
  digitalWrite(PIN_LED_VERDE, HIGH);
  digitalWrite(PIN_LED_VERMELHO, LOW);
}

void ledVermelho() {
  digitalWrite(PIN_LED_VERMELHO, HIGH);
  digitalWrite(PIN_LED_VERDE, LOW);
}

void ledApagar() {
  digitalWrite(PIN_LED_VERDE, LOW);
  digitalWrite(PIN_LED_VERMELHO, LOW);
}

void setup() {
  Serial.begin(115200);
  SPI.begin();
  leitor.PCD_Init();

  pinMode(PIN_BOTAO_1, INPUT_PULLUP);
  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_VERMELHO, OUTPUT);
  ledApagar();
}

void loop() {
  // evento: ao botao(1)
  if (digitalRead(PIN_BOTAO_1) == LOW) {
    delay(30); // debounce

    Cartao cartao = nfcLer();

    if (cartao.valido == true) {
      ledVerde();
      delay(1500);
      ledApagar();
    } else {
      ledVermelho();
      delay(1500);
      ledApagar();
    }

    while (digitalRead(PIN_BOTAO_1) == LOW) {
      delay(10);
    }
  }
}
