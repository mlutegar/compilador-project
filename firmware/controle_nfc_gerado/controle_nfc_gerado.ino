// Gerado pelo compilador Tupã a partir de controle_nfc.tupa
// Dispositivo: controle
// Placa: ESP32-WROVER-DEV (conferido em bancada em 26/10/2026) (esp32:esp32:esp32wrover)
// Não edite à mão: altere o .tupa e gere de novo.
// Os comentários // [arquivo:linha] ligam cada bloco à linha do .tupa.

#include <SPI.h>
#include <MFRC522.h>

// ---- Pinos e tempos (vêm de compilador/placas/esp32_wrover.json) ----
#define LED_VERDE      25
#define LED_VERMELHO   26
#define BOTAO_1        4
#define NFC_SS         5
#define NFC_RST        22
#define DEBOUNCE_MS    50
#define NFC_TIMEOUT_MS 3000

// ---- Estado dos botões (debounce por millis, sem delay) ----
int botao1_leitura = HIGH, botao1_estavel = HIGH;
unsigned long botao1_mudou = 0;

// ---- Variáveis do programa ----
// [controle_nfc.tupa:3] int tentativas = 3;

MFRC522 leitorNFC(NFC_SS, NFC_RST);

struct Cartao {
  bool valido = false;
  String uid = "";
};

// UIDs autorizados (vêm da placa; os demais cartões ficam negados)
struct UidAutorizado { byte tamanho; byte bytes[10]; };
const UidAutorizado UIDS_AUTORIZADOS[] = {
  { 4, { 0x33, 0x7A, 0x87, 0xF7 } },  // 33 7A 87 F7
  { 4, { 0x43, 0xA3, 0x6F, 0xF5 } },  // 43 A3 6F F5
};
const int N_UIDS = sizeof(UIDS_AUTORIZADOS) / sizeof(UIDS_AUTORIZADOS[0]);

bool uidAutorizado(byte *uid, byte tamanho) {
  for (int i = 0; i < N_UIDS; i++) {
    if (UIDS_AUTORIZADOS[i].tamanho != tamanho) continue;
    if (memcmp(UIDS_AUTORIZADOS[i].bytes, uid, tamanho) == 0) return true;
  }
  return false;
}

// Uma tentativa de leitura. Sempre encerra a comunicação com o cartão.
bool nfcTentar(Cartao &c) {
  if (!leitorNFC.PICC_IsNewCardPresent() || !leitorNFC.PICC_ReadCardSerial()) return false;
  c.uid = "";
  for (byte i = 0; i < leitorNFC.uid.size; i++) {
    if (i > 0) c.uid += ' ';
    if (leitorNFC.uid.uidByte[i] < 0x10) c.uid += '0';
    c.uid += String(leitorNFC.uid.uidByte[i], HEX);
  }
  c.uid.toUpperCase();
  c.valido = uidAutorizado(leitorNFC.uid.uidByte, leitorNFC.uid.size);
  leitorNFC.PICC_HaltA();
  leitorNFC.PCD_StopCrypto1();
  return true;
}

// nfc.ler(): espera até NFC_TIMEOUT_MS pelo cartão; sem cartão = inválido.
Cartao nfcLer() {
  Cartao c;
  unsigned long inicio = millis();
  bool lido = false;
  while (!lido && (millis() - inicio) < NFC_TIMEOUT_MS) {
    lido = nfcTentar(c);
    if (!lido) delay(20);
  }
  if (lido) {
    Serial.println("Cartao UID: " + c.uid);
  } else {
    Serial.println("Cartao: nenhum detectado em 3 s");
  }
  Serial.println(c.valido ? "acesso liberado" : "acesso negado");
  return c;
}

void ledApagar()   { digitalWrite(LED_VERDE, LOW);  digitalWrite(LED_VERMELHO, LOW); }
void ledVerde()    { digitalWrite(LED_VERMELHO, LOW); digitalWrite(LED_VERDE, HIGH); }
void ledVermelho() { digitalWrite(LED_VERDE, LOW);  digitalWrite(LED_VERMELHO, HIGH); }

void setup() {
  Serial.begin(115200);
  delay(500);  // tempo para o Monitor Serial abrir
  pinMode(BOTAO_1, INPUT_PULLUP);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_VERMELHO, OUTPUT);
  ledApagar();  // LEDs começam apagados
  SPI.begin(18, 19, 23, 5);  // SCK, MISO, MOSI, SS
  leitorNFC.PCD_Init();
  delay(50);
  byte versaoRC522 = leitorNFC.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.printf("RC522 versao: 0x%02X -> %s\n", versaoRC522,
                (versaoRC522 == 0x00 || versaoRC522 == 0xFF)
                  ? "FALHA: confira SPI, RST e 3.3V" : "OK");
}

void loop() {
  // [controle_nfc.tupa:5] ao botao(1)
  {
    int leitura = digitalRead(BOTAO_1);
    if (leitura != botao1_leitura) { botao1_leitura = leitura; botao1_mudou = millis(); }
    if ((millis() - botao1_mudou) > DEBOUNCE_MS && leitura != botao1_estavel) {
      botao1_estavel = leitura;  // borda confirmada: dispara uma vez por aperto
      if (botao1_estavel == LOW) {
        Serial.println("Botao: PRESSIONADO");
        Cartao cartao = nfcLer();
        if ((cartao.valido == true)) {
          ledVerde();
          delay(1500);
        } else {
          ledVermelho();
        }
        ledApagar();  // LEDs apagam ao fim do evento
      } else {
        Serial.println("Botao: solto");
      }
    }
  }
  delay(10);
}
