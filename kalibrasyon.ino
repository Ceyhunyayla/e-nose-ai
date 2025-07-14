#include <SPIFFS.h>
#include <Adafruit_SGP30.h>
#include <DHT.h>  

#define MQ3_PIN 32
#define MQ135_PIN 33
#define MQ4_PIN 35
#define DHT_PIN 25
#define DHTTYPE DHT11

#define VREF 3.3
#define ADC_BITS 13
#define ADC_MAX 8191

const float RL_MQ3 = 40000.0, RATIO_MQ3 = 1.4;
const float RL_MQ135 = 3000.0, RATIO_MQ135 = 2.1;
const float RL_MQ4 = 1000.0, RATIO_MQ4 = 5;

const float M_MQ3 = -1.2, B_MQ3 = 3.1, OFFSET_MQ3 = 870.0;
const float M_MQ135 = -1.0, B_MQ135 = 3.07, OFFSET_MQ135 = 30.0;
const float M_MQ4 = -1.0, B_MQ4 = 2.28, OFFSET_MQ4 = 40.0;

float R0_MQ3, R0_MQ135, R0_MQ4;

Adafruit_SGP30 sgp;
DHT dht(DHT_PIN, DHTTYPE);  

float getVoltage(int pin) {
  float sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(pin);
    delay(2);
  }
  return (sum / 10) * (VREF / ADC_MAX);
}

float calculateR0(float voltage, float RL, float ratio) {
  float rs = (VREF - voltage) * RL / voltage;
  return rs / ratio;
}

float getPPM(float voltage, float RL, float R0, float M, float B, float offset) {
  float rs = (VREF - voltage) * RL / voltage;
  float ratio = rs / R0;
  return constrain(pow(10, (M * log10(ratio) + B)) - offset, 0.0, 10000.0);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(ADC_BITS);
  pinMode(MQ3_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);
  pinMode(MQ4_PIN, INPUT);

  SPIFFS.begin(true);
  sgp.begin();
  sgp.IAQinit();
  dht.begin();  

  delay(1000);
  Serial.println("RESET_OK");

  R0_MQ3 = calculateR0(getVoltage(MQ3_PIN), RL_MQ3, RATIO_MQ3);
  R0_MQ135 = calculateR0(getVoltage(MQ135_PIN), RL_MQ135, RATIO_MQ135);
  R0_MQ4 = calculateR0(getVoltage(MQ4_PIN), RL_MQ4, RATIO_MQ4);
}

void loop() {
  float v_mq3 = getVoltage(MQ3_PIN);
  float v_mq135 = getVoltage(MQ135_PIN);
  float v_mq4 = getVoltage(MQ4_PIN);

  float ppm_mq3 = getPPM(v_mq3, RL_MQ3, R0_MQ3, M_MQ3, B_MQ3, OFFSET_MQ3);
  float ppm_mq135 = getPPM(v_mq135, RL_MQ135, R0_MQ135, M_MQ135, B_MQ135, OFFSET_MQ135);
  float ppm_mq4 = getPPM(v_mq4, RL_MQ4, R0_MQ4, M_MQ4, B_MQ4, OFFSET_MQ4);

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (sgp.IAQmeasure()) {
    Serial.print("{\"mq3_ppm\":");
    Serial.print((int)ppm_mq3);
    Serial.print(",\"mq135_ppm\":");
    Serial.print((int)ppm_mq135);
    Serial.print(",\"mq4_ppm\":");
    Serial.print((int)ppm_mq4);
    Serial.print(",\"eco2\":");
    Serial.print(sgp.eCO2);
    Serial.print(",\"tvoc\":");
    Serial.print(sgp.TVOC);
    Serial.print(",\"temp\":");
    Serial.print(temp);
    Serial.print(",\"hum\":");
    Serial.print(hum);
    Serial.println("}");
  }

  delay(1000);
}
