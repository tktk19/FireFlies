// ATtiny402 ゲンジボタル（ADC基準電圧明示・ピン定義修正版）
// 物理3ピン (PA7) : A7 として指定

// ==========================================
// 電源設定の切り替え
// ==========================================
// 3.7V 充電池 (LIR2032 等) を使用する場合は true、
// 5V (USB / モバイルバッテリー等) を使用する場合は false に設定してください。
#define USE_BATTERY_3V7 true

const int sensorPin = A7;     // PA7 は アナログチャンネル A7 (物理3ピン)
const int ledPin = PIN_PA2;   // 物理5ピン (PA2)

#if USE_BATTERY_3V7
  // ----------------------------------------------------
  // 3.7V 充電池（LIR2032: 3.4V〜4.2V）駆動時
  // ----------------------------------------------------
  // 暗所判定: 約 2.9V 以上 (ADC 800) で「夜」と判定
  const int DARK_THRESHOLD = 800;

  // 光検知判定: 5V時の720(ΔV≒1.48V相当)を3.7V基準に換算すると約614〜650。
  // 相手のホタルも3.7V駆動でLEDが暗めになることを考慮し、やや高感度な640に設定。
  // （もし反応しにくければ 680〜700 へ、誤検知するなら 600 へ微調整）
  const int LIGHT_THRESHOLD = 640;

  // 3.7V時は電流制限抵抗(4.7kΩ)によりLED電流が減るため、最大輝度を255(フル)にして光量を確保
  const int ABSOLUTE_MAX_BRIGHTNESS = 255;

#else
  // ----------------------------------------------------
  // 5V（USB / 5Vバッテリー）駆動時
  // ----------------------------------------------------
  // 暗所判定: 4.0V 以上 (ADC 819) で「夜」と判定
  const int DARK_THRESHOLD = 819;

  // 光検知判定: ユーザー検証済みの 720 (約3.52V以下で検知)
  // 他のホタルの緑色LEDによる微小な受光変化を確実に捉える閾値
  const int LIGHT_THRESHOLD = 720;

  // 5V時の最大輝度
  const int ABSOLUTE_MAX_BRIGHTNESS = 200;
#endif

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

  // 暗所判定（設定したDARK_THRESHOLD以上の場合のみ「夜」と判定）
  if (currentVal >= DARK_THRESHOLD) {

    flashFirefly();
    delay(200); // 自己受光ガード（自発光直後の誤反応を防止）

    unsigned long sleepMs = random(4000, 10001);
    unsigned long startSleep = millis();

    while (millis() - startSleep < sleepMs) {
      int sensorVal = analogRead(sensorPin);

      // 休止中に光を検知（sensorVal < LIGHT_THRESHOLD）したら協調発光
      if (sensorVal < LIGHT_THRESHOLD) {
        delay(random(300, 1201)); // 同期発光までのわずかな応答揺らぎ
        break; 
      }

      delay(50); 
    }

  } else {
    // 昼間・明かりありの場合は消灯待機
    digitalWrite(ledPin, LOW);
    delay(1000); 
  }
}