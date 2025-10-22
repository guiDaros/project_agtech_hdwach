#include <dht.h>

const int pinoUmidadeSoloDigital = 8;
const int pinoUmidadeSoloAnalogico = A0;
const int pinoLuz = A1;
#define DHT11_PIN 3
#define LED_STATUS 13  

dht DHT;

void piscarLED(int vezes, int duracao) {
  for (int i = 0; i < vezes; i++) {
    digitalWrite(LED_STATUS, HIGH);
    delay(duracao);
    digitalWrite(LED_STATUS, LOW);
    delay(duracao);
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(pinoUmidadeSoloDigital, INPUT);
  pinMode(LED_STATUS, OUTPUT);
  digitalWrite(LED_STATUS, LOW);

  Serial.println(F("======================================"));
  Serial.println(F("Iniciando leitura dos sensores..."));
  Serial.println(F("Sensores conectados:"));
  Serial.println(F("- Umidade do solo (pinos 8 e A0)"));
  Serial.println(F("- Luminosidade (pino A1)"));
  Serial.println(F("- Temperatura e Umidade do ar (DHT11 - pino 3)"));
  Serial.println(F("======================================"));

  piscarLED(3, 200); 
}

void loop() {
  int valorAnalogicoSolo = analogRead(pinoUmidadeSoloAnalogico);
  int valorLuz = analogRead(pinoLuz);
  int chk = DHT.read11(DHT11_PIN);

  if (chk != 0) {
    Serial.println(F("{\"erro\":\"Falha na leitura do DHT11\"}"));
    piscarLED(3, 500); 
    delay(10000);
    return;
  }

  float temperatura = DHT.temperature;
  float umidade_ar = DHT.humidity;
  float umidade_solo = map(valorAnalogicoSolo, 1023, 0, 0, 100);
  float luminosidade = map(valorLuz, 0, 1023, 0, 100);

  Serial.print(F("{\"temperatura\":"));
  Serial.print(temperatura, 2);
  Serial.print(F(",\"umidade_ar\":"));
  Serial.print(umidade_ar, 2);
  Serial.print(F(",\"umidade_solo\":"));
  Serial.print(umidade_solo, 1);
  Serial.print(F(",\"luminosidade\":"));
  Serial.print(luminosidade, 1);
  Serial.println(F("}"));

  piscarLED(2, 100); 
  delay(10000);
}
