#define TRIG_PIN 32             // 發出聲波腳位(ESP32 GPIO32)
#define ECHO_PIN 33             // 接收聲波腳位(ESP32 GPIO33)
#define YLED 12                 // 接收LED腳位(ESP32 GPIO12)
#define FORCE_SENSOR_PIN 35     // 壓力感測器腳位 (ESP32 GPIO35)
#define LED1 23                 // 壓力感測器控制 LED 腳位 (ESP32 GPIO23)

#include <Wire.h>               // 引入 I2C 通訊庫
#include <Adafruit_MLX90614.h>  // 引入 Adafruit MLX90614 紅外線溫度感測器庫
#include <FirebaseESP32.h>      // 引入 FirebaseESP32 函式庫
#include <WiFi.h>               // 引入 Wi-Fi 函式庫

bool ledState = LOW;         // 初始化 LED 狀態
bool pressureLedState = LOW; // 初始化壓力感測器狀態

// 初始化 Adafruit MLX90614 紅外測溫感測器物件
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// Wi-Fi credentials
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// Firebase Realtime Database URL and Secret
#define FIREBASE_HOST "YOUR_FIREBASE_HOST"
#define FIREBASE_AUTH "YOUR_FIREBASE_AUTH"

// Firebase objects
FirebaseData firebaseData;
FirebaseConfig firebaseConfig;
FirebaseAuth firebaseAuth;

// Helper to initialize Firebase
void initFirebase() {
  firebaseConfig.host = FIREBASE_HOST;
  firebaseConfig.signer.tokens.legacy_token = FIREBASE_AUTH;

  Firebase.begin(&firebaseConfig, &firebaseAuth); // 啟動 Firebase

  if (!Firebase.ready()) {
    Serial.println("Failed to initialize Firebase");
    while (true);
  }
  Serial.println("Firebase initialized successfully");
}

void setup() {
  Serial.begin(9600);           // 啟動序列埠，設置波特率為 9600

  // 設定超音波 LED 腳位為輸出
  pinMode(TRIG_PIN, OUTPUT);    // TRIG 設為輸出模式
  pinMode(ECHO_PIN, INPUT);     // ECHO 設為輸入模式

  pinMode(FORCE_SENSOR_PIN, INPUT);

  // 設置超音波 LED 的腳位模式並初始化
  pinMode(YLED, OUTPUT);        // LED 設為輸出模式
  digitalWrite(YLED, ledState); // 初始化 LED 狀態

  // 設置壓力 LED 的腳位模式並初始化
  pinMode(LED1, OUTPUT);                // LED 設為輸出模式
  digitalWrite(LED1, pressureLedState); // 初始化 LED 狀態

  // 初始化紅外測溫感測器
  Serial.println("Adafruit MLX90614 test");  // 輸出初始化訊息
  mlx.begin();                               // 啟動紅外線溫度感測器

  // Connect to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wi-Fi...");
  }
  Serial.println("Connected to Wi-Fi");

  // Initialize Firebase
  initFirebase();
}

void loop() {
  // 讀取並輸出紅外線溫度感測器的溫度數據
  Serial.print("Ambient = "); Serial.print(mlx.readAmbientTempC());
  Serial.print("*C\tObject = "); Serial.print(mlx.readObjectTempC()); Serial.println("*C");

  // 處理超音波感測器的距離測量
  unsigned long duration = ping();        // 獲取回波時間
  unsigned long distance = duration / 58; // 計算距離 (cm)

  if (distance > 0 && distance < 300) {
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
  }

  // 每次迴圈檢查 Firebase 中的 YLED 狀態並更新 LED
  if (Firebase.getInt(firebaseData, "/data/YLED")) {
    ledState = firebaseData.intData();  // 讀取 YLED 的狀態
    digitalWrite(YLED, ledState);       // 更新 LED 狀態
    Serial.print("YLED State from Firebase: ");
    Serial.println(ledState);
  }

  // 當距離 <= 30cm 且溫度 >= 28℃，切換超音波 LED 狀態並上傳到 Firebase
  if (distance > 0 && distance <= 30 && mlx.readObjectTempC() >= 28) {
    ledState = !ledState;           // 切換超音波 LED 狀態
    digitalWrite(YLED, ledState);   // 更新超音波 LED 狀態
    Firebase.setInt(firebaseData, "/data/YLED", ledState);  // 上傳到 Firebase

    delay(1000); // 延遲 1000 毫秒防止快速切換
  }

  int analogReading = analogRead(FORCE_SENSOR_PIN); // 讀取壓力感測器數值
  Serial.print("pressure: ");
  Serial.println(analogReading);

  if (analogReading > 800) {
    pressureLedState = !pressureLedState; // 切換 LED 狀態
    digitalWrite(LED1, pressureLedState); // 更新 LED 狀態
    Firebase.setInt(firebaseData, "/data/RLED", pressureLedState); // 上傳到 Firebase

    static unsigned long lastSendTime = 0;
    if (millis() - lastSendTime > 5000) { // 每隔 5 秒更新一次
      if (Firebase.setInt(firebaseData, "/data/pressure", analogReading)) {
        Serial.println("Pressure data sent successfully.");
      } else {
        Serial.println("Failed to send pressure data: ");
        Serial.println(firebaseData.errorReason());
      }
      lastSendTime = millis();
    }
    delay(500); // 防止快速切換
  }

  // 每次迴圈檢查 Firebase 中的 RLED 狀態並更新 LED
  if (Firebase.getInt(firebaseData, "/data/RLED")) {
    ledState = firebaseData.intData();  // 讀取 YLED 的狀態
    digitalWrite(LED1, ledState);       // 更新 LED 狀態
    Serial.print("LED1 State from Firebase: ");
    Serial.println(ledState);
  }

  delay(1000);  // 延遲
}

/**
 * 發送 10us 脈衝到超音波模組的 TRIG 腳位
 * 並返回回波時間（微秒）
 */
unsigned long ping() { 
  digitalWrite(TRIG_PIN, LOW);           // 確保 Trig 為低電位
  delayMicroseconds(2);                  // 等待穩定
  digitalWrite(TRIG_PIN, HIGH);          // 啟動超音波
  delayMicroseconds(10);                 // 保持至少 10us 的高電位
  digitalWrite(TRIG_PIN, LOW);           // 關閉超音波
  return pulseIn(ECHO_PIN, HIGH, 30000); // 計算傳回時間，超時為 30ms
}