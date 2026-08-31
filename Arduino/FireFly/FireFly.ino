// ATtiny402 ゲンジボタル（ADC基準電圧明示・ピン定義修正版）
// 物理3ピン (PA7) : A7 として指定

const int sensorPin = A7;     // PA7 は アナログチャンネル A7
const int ledPin = PIN_PA2;   // 物理5ピン (PA2)

// 基準電圧を5Vにするため、電圧（V）から直接ADC値を計算する定数
// 4.0V ≒ 819 / 1.5V ≒ 307
const int DARK_THRESHOLD = 819;  // 4.0V以上で「暗い」と判定
const int LIGHT_THRESHOLD = 512; // 2.5V以下で「他の光を検知」と判定

const int ABSOLUTE_MAX_BRIGHTNESS = 25; 

void setup() {
  // ★重要：ADCの基準電圧を電源電圧（VDD/5V）に明示的に設定
#if defined(VDD)
  analogReference(VDD);
#endif

  pinMode(ledPin, OUTPUT);
  randomSeed(analogRead(PIN_PA1));
}

void flashFirefly() {
  int maxLimit = random(10, ABSOLUTE_MAX_BRIGHTNESS + 1);
  int upDelay = random(5, 7);
  int downDelay = random(8, 12);

  for (int i = 0; i <= 255; i++) {
    long iSquared = (long)i * i;
    int pwmVal = (int)((iSquared * maxLimit) / 65025);
    analogWrite(ledPin, pwmVal);
    delay(upDelay); 
  }

  delay(random(2000, 4000));

  for (int i = 255; i >= 0; i--) {
    long iSquared = (long)i * i;
    int pwmVal = (int)((iSquared * maxLimit) / 65025);
    analogWrite(ledPin, pwmVal);
    delay(downDelay); 
  }

  analogWrite(ledPin, 0);
}

void loop() {
  int currentVal = analogRead(sensorPin);

  // 4.0V (ADC 819) 以上の場合のみ「夜」と判定
  if (currentVal >= DARK_THRESHOLD) {

    flashFirefly();
    delay(2000); // 自己受光ガード

    unsigned long sleepMs = random(4000, 10001);
    unsigned long startSleep = millis();

    while (millis() - startSleep < sleepMs) {
      int sensorVal = analogRead(sensorPin);

      // 休止中に 2.5V (ADC 512) 以下に落ちたら光検知
      if (sensorVal < LIGHT_THRESHOLD) {
        delay(random(300, 1201));
        break; 
      }

      delay(50); 
    }

  } else {
    // 4.0V未満（昼間・明かりあり）は消灯待機
    digitalWrite(ledPin, LOW);
    delay(1000); 
  }
}