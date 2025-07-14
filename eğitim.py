import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

df = pd.read_csv("hazir_veri_seti.csv")

X = df.drop("label", axis=1)
y = df["label"]

# Veriyi eğitim ve test olarak ayır (örneğin %80 eğitim, %20 test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, stratify=y, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Dogruluk: ", accuracy_score(y_test, y_pred))
print("\n Sınıflandırma Raporu:\n", classification_report(y_test, y_pred))
print("Karısıklık Matrisi:\n", confusion_matrix(y_test, y_pred))

joblib.dump(model, "sut_modeli.pkl")
print("Model 'sut_modeli.pkl' olarak kaydedildi.")