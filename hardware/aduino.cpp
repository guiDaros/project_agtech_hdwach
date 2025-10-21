#include <dht.h>

const int pinoUmidadeSoloDigital = 8;
const int pinoUmidadeSoloAnalogico = A0;
const int pinoLuz = A1;
#define DHT11_PIN 3

dht DHT;

void setup() {
  Serial.begin(9600);
  pinMode(pinoUmidadeSoloDigital, INPUT);

  Serial.println("======================================");
  Serial.println("Iniciando leitura dos sensores...");
  Serial.println("Sensores conectados:");
  Serial.println("- Umidade do solo (pinos 8 e A0)");
  Serial.println("- Luminosidade (pino A1)");
  Serial.println("- Temperatura e Umidade do ar (DHT11 - pino 3)");
  Serial.println("======================================");
}

void loop() {
  int valorAnalogicoSolo = analogRead(pinoUmidadeSoloAnalogico);
  int valorLuz = analogRead(pinoLuz);

  int chk = DHT.read11(DHT11_PIN);
  float temperatura = DHT.temperature;
  float umidade_ar = DHT.humidity;

  // JSON CORRIGIDO COM ESCAPE CORRETO
  Serial.print("{");
  Serial.print("\"temperatura\":");
  Serial.print(temperatura, 2);
  Serial.print(",\"umidade_ar\":");
  Serial.print(umidade_ar, 2);
  Serial.print(",\"umidade_solo\":");
  Serial.print(valorAnalogicoSolo);
  Serial.print(",\"luminosidade\":");
  Serial.print(valorLuz);
  Serial.println("}");

  delay(10000);
}