// ATtiny402 ゲンジボタル（省電力スリープ＆過放電保護版）
// 物理3ピン (PA7) : A7 として指定
// 物理5ピン (PA2) : PWM LED

#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <megaTinyCore.h>

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
  const int LIGHT_THRESHOLD = 640;

  // 3.7V時は電流制限抵抗(4.7kΩ)によりLED電流が減るため、最大輝度を255(フル)にして光量を確保
  const int ABSOLUTE_MAX_BRIGHTNESS = 255;

  // 過放電保護: 3.0V (3000mV) を切ったら強制シャットダウンして電池を保護
  const int LOW_BATTERY_VOLTAGE_MV = 3000;

#else
  // ----------------------------------------------------
  // 5V（USB / 5Vバッテリー）駆動時
  // ----------------------------------------------------
  // 暗所判定: 4.0V 以上 (ADC 819) で「夜」と判定
  const int DARK_THRESHOLD = 819;

  // 光検知判定: ユーザー検証済みの 720 (約3.52V以下で検知)
  const int LIGHT_THRESHOLD = 720;

  // 5V時の最大輝度
  const int ABSOLUTE_MAX_BRIGHTNESS = 200;

  // 5V電源時は過放電保護無効
  const int LOW_BATTERY_VOLTAGE_MV = 0;
#endif

// ==========================================
// 省電力タイマー（PIT: Periodic Interrupt Timer）設定
// ==========================================
// 125ms ごとにスリープから復帰するための割り込み
ISR(RTC_PIT_vect) {
  RTC.PITINTFLAGS = RTC_PI_bm; // 割り込みフラグクリア
}

void initPIT() {
  while (RTC.PITSTATUS & RTC_CTRLBUSY_bm); // ビジー解除待ち
  RTC.CLKSEL = RTC_CLKSEL_INT32K_gc;     // 内部超低消費電力 32.768kHz 発振器
  RTC.PITINTCTRL = RTC_PI_bm;             // PIT割り込み有効化
  RTC.PITCTRLA = RTC_PERIOD_CYC4096_gc | RTC_PITEN_bm; // 4096周期 = 125ms (8Hz)
}

// 約125msのPower Downディープスリープ（CPU停止・消費電流約1μA）
void sleep125ms() {
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_enable();
  sleep_cpu();
  sleep_disable();
}

// 指定ミリ秒を 125ms 単位のスリープで待機
void sleepMsDuration(unsigned long ms) {
  unsigned int steps = ms / 125;
  for (unsigned int i = 0; i < steps; i++) {
    sleep125ms();
  }
}

// ==========================================
// 過放電保護チェック（3.0V未満で完全停止）
// ==========================================
void checkBatteryProtection() {
#if USE_BATTERY_3V7
  uint16_t vdd = readSupplyVoltage(); // 電源電圧(mV)を取得
  if (vdd > 0 && vdd < LOW_BATTERY_VOLTAGE_MV) {
    // 電池切れサイン: LEDを短く2回点滅
    for (int i = 0; i < 2; i++) {
      analogWrite(ledPin, 30);
      delay(30);
      analogWrite(ledPin, 0);
      delay(100);
    }

    // 全ペリフェラル停止
    RTC.PITCTRLA = 0;             // PITタイマー停止
    RTC.PITINTCTRL = 0;
    ADC0.CTRLA &= ~ADC_ENABLE_bm; // ADC停止
    digitalWrite(ledPin, LOW);

    // 永久ディープスリープ（電池交換・再充電まで完全停止、消費電流 ~0.1μA）
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    cli(); // 全割り込み禁止
    while (1) {
      sleep_cpu();
    }
  }
#endif
}

void setup() {
  // ADCの基準電圧を電源電圧（VDD）に明示的に設定
#if defined(VDD)
  analogReference(VDD);
#endif

  pinMode(ledPin, OUTPUT);
  randomSeed(analogRead(PIN_PA1));

  initPIT(); // 超低消費電力PITタイマー開始
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
  // バッテリー電圧チェック（3.0V未満なら過放電防止で自動シャットダウン）
  checkBatteryProtection();

  int currentVal = analogRead(sensorPin);

  // 暗所判定（DARK_THRESHOLD以上の場合のみ「夜」と判定）
  if (currentVal >= DARK_THRESHOLD) {

    flashFirefly();

    // 自己受光ガード（自発光直後の誤反応を防止: 2000ms間スリープ）
    sleepMsDuration(2000);

    // 休止期間（4〜10秒間）
    // 125ms間隔でスリープしながら受光センサをチェック（平均待機電流を数十μAに抑制）
    int totalSteps = random(32, 81); // 32*125ms=4000ms 〜 80*125ms=10000ms

    for (int step = 0; step < totalSteps; step++) {
      sleep125ms(); // 125ms間はCPU完全停止（消費電流 約1μA）

      int sensorVal = analogRead(sensorPin);

      // 他のホタルの光を検知（sensorVal < LIGHT_THRESHOLD）したら協調発光
      if (sensorVal < LIGHT_THRESHOLD) {
        delay(random(300, 1201)); // 同期発光までのわずかな応答揺らぎ
        break; 
      }
    }

  } else {
    // 昼間・明かりありの場合は1秒間スリープして待機
    digitalWrite(ledPin, LOW);
    sleepMsDuration(1000); 
  }
}