#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_AM2320.h>
#include <LiquidCrystal_I2C.h>

Adafruit_AM2320 am2320 = Adafruit_AM2320();

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);

  lcd.begin(16, 2);
  lcd.backlight();

  if (!am2320.begin()) {
    lcd.setCursor(0, 0);
    lcd.print("Sensor no detectado");
    while (1);
  }

  lcd.setCursor(0, 0);
  lcd.print("Sensor y LCD OK");
  delay(2000);
  lcd.clear();
}

void loop() {

  if (Serial.available() > 0) {
    String incomingData = Serial.readString();

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Raspberry dice:");
    lcd.setCursor(0, 1);
    lcd.print(incomingData);

    delay(2000);
  }

  float humidity = am2320.readHumidity();
  float temperature = am2320.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Error de sensor");
  } else {

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    lcd.print(temperature);
    lcd.print(" C");

    lcd.setCursor(0, 1);
    lcd.print("Hum: ");
    lcd.print(humidity);
    lcd.print(" %");
    String message = String(temperature) + "-" + String(humidity);
    Serial.println(message);
  }

  delay(2000);
}
