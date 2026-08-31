// ATtiny402 東日本型ゲンジボタル明滅（超スロー明滅＆5〜30秒ランダム休止）
// 物理ピン: 5ピン (PA2)

const int ledPin = PIN_PA2; // 物理5ピン (PA2)

// 明るさの上限設定（元の255に対して30：控えめな発光）
const int MAX_BRIGHTNESS = 30; 

void setup() {
  pinMode(ledPin, OUTPUT);
  
  // 未接続ピンのアナログノイズで乱数を初期化
  randomSeed(analogRead(PIN_PA1));
}

void loop() {
  // 1. じわ〜〜っと明るく（約 6.0 秒：30ステップ × 180ms）
  for (int i = 0; i <= MAX_BRIGHTNESS; i++) {
    long longI = i;
    int brightness = (int)((longI * longI) / MAX_BRIGHTNESS);
    
    analogWrite(ledPin, brightness);
    delay(180); 
  }

  // ピーク時の余韻（約 0.5 秒）
  delay(500);

  // 2. じわ〜〜っと消灯（約 7.5 秒：30ステップ × 225ms）
  for (int i = MAX_BRIGHTNESS; i >= 0; i--) {
    long longI = i;
    int brightness = (int)((longI * longI) / MAX_BRIGHTNESS);
    
    analogWrite(ledPin, brightness);
    delay(225); 
  }

  // 完全消灯（0出力）
  analogWrite(ledPin, 0);

  // 3. 完全消灯（静寂）：5秒 〜 30秒 の間でランダムに待機
  long sleepTime = random(5000, 30001);
  delay(sleepTime);
}