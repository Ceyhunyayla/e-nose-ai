import time
import serial
import numpy as np
import joblib
import json
import os
import pandas as pd
import traceback
from RPLCD.i2c import CharLCD
from scipy.stats import skew, kurtosis

try:
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
    ser.flushInput()
    print("Seri bağlantısı kuruldu.")
except Exception as e:
    print(f"Seri bağlantı hatası: {e}")
    exit()

try:
    lcd = CharLCD('PCF8574', 0x27)
    lcd.clear()
    lcd.write_string("Bekleniyor")
except Exception as e:
    print(f"LCD başlatma hatası: {e}")
    exit()

print(" RESET_OK bekleniyor")


while True:
    try:
        raw = ser.readline()
        if not raw:
            continue

        try:
            satir = raw.decode('utf-8').strip()
        except UnicodeDecodeError:
            print("hata veri atlandı.")
            continue

        print(f"Gelen satır: {satir}")

        if satir == "RESET_OK":
            print("RESET_OK Alındı")
            break
    except Exception as e:
        print(f"RESET_OK beklenirken hata: {e}")
        time.sleep(1)

def pencere_ozellik_uret(veri_listesi):
    ozellik = {}
    eşleşmeler = {
        "mq3_ppm": "mq3",
        "mq135_ppm": "mq135",
        "mq4_ppm": "mq4",
        "eco2": "eco2",
        "tvoc": "tvoc"
    }

    for eski_ad, yeni_ad in eşleşmeler.items():
        dizi = np.array([v.get(eski_ad, 0) for v in veri_listesi], dtype=float)
        if len(dizi) == 0:
            dizi = np.array([0.0])

        ozellik[f"{yeni_ad}_mean"] = np.mean(dizi)
        ozellik[f"{yeni_ad}_std"] = np.std(dizi)
        ozellik[f"{yeni_ad}_min"] = np.min(dizi)
        ozellik[f"{yeni_ad}_max"] = np.max(dizi)
        ozellik[f"{yeni_ad}_skew"] = skew(dizi, nan_policy='omit')
        ozellik[f"{yeni_ad}_kurt"] = kurtosis(dizi, nan_policy='omit')
        ozellik[f"{yeni_ad}_iqr"] = np.percentile(dizi, 75) - np.percentile(dizi, 25)
        ozellik[f"{yeni_ad}_range"] = np.max(dizi) - np.min(dizi)

    return ozellik

print("Veri toplanıyor")
veri_listesi = []
while len(veri_listesi) < 60:
    try:
        satir = ser.readline().decode('utf-8').strip()
        if satir.startswith('{') and satir.endswith('}'):
            print(f"Alınan veri: {satir}")
            veri = json.loads(satir)
            veri_listesi.append(veri)
    except Exception as e:
        print(f"Veri okuma hatası: {e}")

print(f"{len(veri_listesi)} veri alındı")

try:
    ham_df = pd.DataFrame(veri_listesi)
    ham_df["timestamp"] = pd.Timestamp.now()

    ham_csv_yolu = "/home/pi/Desktop/Model_dosyam/ham_veriler.csv"

    if not os.path.exists(ham_csv_yolu):
        ham_df.to_csv(ham_csv_yolu, mode='w', index=False)
    else:
        ham_df.to_csv(ham_csv_yolu, mode='a', header=False, index=False)

    print("veriler CSV dosyasına kaydedildi")
except Exception as e:
    print(f"veri CSV yazım hatası: {e}")

if len(veri_listesi) < 60:
    print("Yeterli veri alınamadı")
    lcd.clear()
    lcd.write_string("Veri yetersiz")
    time.sleep(3)
    exit()

print("Özellikler hesaplanıyor")
ozellik_dict = pencere_ozellik_uret(veri_listesi)
X = pd.DataFrame([ozellik_dict])
X = X.fillna(0)
print("Özellikler:")
print(X)

model_yolu = "/home/pi/Desktop/Model_dosyam/sut_modeli.pkl"
try:
    model = joblib.load(model_yolu)
    print("Model yüklendi")
except Exception as e:
    print(f"Model yükleme hatası: {e}")
    lcd.clear()
    lcd.write_string("Model hatası")
    time.sleep(3)
    exit()

try:
    X = X[model.feature_names_in_]
    tahmin = model.predict(X)[0]
    print(f"Tahmin sonucu: {tahmin}")
except Exception as e:
    print("Tahmin hatası:")
    traceback.print_exc()
    lcd.clear()
    lcd.write_string("Tahmin hatası")
    time.sleep(3)
    exit()

try:
    son_veri = veri_listesi[-1]
    temp = son_veri.get("temp", 0)
    hum = son_veri.get("hum", 0)
except:
    temp, hum = 0, 0

try:
    lcd.clear()
    lcd.write_string(f"{tahmin}")
    if temp != 0 or hum != 0:
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"{temp:.1f}C {hum:.0f}%")
    print("LCD'ye yazıldı")
except Exception as e:
    print(f"LCD yazım hatası: {e}")


print("Reset bekleniyor")


while True:
    try:
        raw = ser.readline()
        if not raw:
            continue
        satir = raw.decode('utf-8').strip()
        if satir == "RESET_OK":
            print(" Yeniden başlıyor")
            break  
    except Exception as e:
        print(f"RESET_OK hata: {e}")
    time.sleep(1)

