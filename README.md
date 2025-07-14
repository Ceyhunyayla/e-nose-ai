# e-nose-ai
Gaz sensörleri ve makine öğrenmesi ile gıda bozulmasını tespit eden yapay zekâ destekli elektronik burun sistemi

## Proje Hakkında

Bu proje, gaz sensörleri kullanarak süt gibi gıdaların bozulma durumunu tespit etmeyi amaçlayan yapay zekâ destekli bir elektronik burun (E-Nose) sistemidir. ESP32 mikrodenetleyicisi, çeşitli gaz sensörlerinden verileri toplar ve bu veriler Raspberry Pi üzerinde çalışan makine öğrenmesi modeli ile analiz edilerek gıdanın taze, bozulmakta veya bozuk olduğu sınıflandırılır.

Projede kullanılan sensörler arasında MQ-3, MQ-4, MQ-135 ve SPG30 gibi farklı gazları algılayabilen sensörler yer alır. Sonuçlar hem LCD ekranda gösterilir hem de ThingsBoard IoT platformu üzerinden izlenebilir. Sistem, düşük maliyetli donanım ile gerçek zamanlı gıda izleme imkânı sunar.

# AI-Based Electronic Nose System for Food Spoilage Detection

This project focuses on developing an **AI-powered electronic nose (E-nose)** system to monitor and detect **food spoilage**, specifically for perishable products like milk. The system uses **gas sensors** to collect data and a machine learning model to classify spoilage levels.

## Project Overview

- **Goal:** To detect food spoilage in real-time using gas sensor data and machine learning algorithms.
- **Target Gases:** VOCs, CO₂, CH₄, NH₃
- **Platform:** Embedded system using ESP32 and Raspberry Pi 3
- **Model Type:** Random Forest Classifier trained on extracted statistical features
- **UI Output:** LCD screen & ThingsBoard IoT dashboard

## Hardware Used

| Component          | Description                                     |
|--------------------|-------------------------------------------------|
| ESP32              | Microcontroller for sensor data acquisition     |
| Raspberry Pi 3     | Local processing and model prediction           |
| MQ-3               | Alcohol, ethanol, and organic vapor detection   |
| MQ-135             | Air quality & CO₂ sensing                       |
| MQ-4               | Methane and natural gas detection               |
| SPG30              | VOC and environmental data (CO₂, IAQ)           |
| DHT11              | Temperature and humidity sensor                 |
| I2C LCD Display    | To display spoilage result                      |

---

## Software Architecture

- **ESP32 (Arduino):**
  - Reads gas sensor values every 3 seconds
  - Sends them as JSON via serial port
  - Collects data continuously; sends trigger signal when RESET button is pressed

- **Raspberry Pi 3 (Python):**
  - Waits for "RESET_OK" signal to start inference
  - Collects 1-minute window of sensor data
  - Computes statistical features (mean, std, min, max, skew, kurtosis, etc.)
  - Feeds features to pretrained Random Forest model
  - Displays prediction result on I2C LCD
  - Logs results to CSV

---

## Machine Learning Model

- **Features Used:**
  - Mean, Std Dev, Min, Max, Skewness, Kurtosis, IQR, Trend
- **Target Classes:**
  - Fresh, Spoiling, Spoiled
- **Model:** Random Forest Classifier (Scikit-learn)
- **Training Data:** Labeled sensor logs from real food samples

---

## Dashboard Integration

- Integrated with [ThingsBoard](https://thingsboard.io/) to visualize real-time sensor data
- Each experiment session is separated by unique tags or time windows

---

## Folder Structure


