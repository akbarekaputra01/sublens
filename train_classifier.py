import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load data
with open('dataASL.pickle', 'rb') as f:
    data_dict = pickle.load(f)

# Ambil data & label
raw_data = data_dict['data']
labels = np.asarray(data_dict['labels'])

# Cari panjang maksimum dari semua data (landmark)
max_len = max(len(row) for row in raw_data)
print(f"Maksimal panjang data: {max_len}")

# Buat fungsi padding
def pad_sequence(row, target_len):
    return row + [0] * (target_len - len(row)) if len(row) < target_len else row

# Lakukan padding ke semua data agar panjangnya sama
data = np.asarray([pad_sequence(row, max_len) for row in raw_data])

# Bagi dataset jadi train-test
x_train, x_test, y_train, y_test = train_test_split(
    data, labels, test_size=0.2, shuffle=True, stratify=labels
)

# Buat dan latih model
model = RandomForestClassifier()
model.fit(x_train, y_train)

# Prediksi & evaluasi
y_predict = model.predict(x_test)
score = accuracy_score(y_predict, y_test)
print(f"{score * 100:.2f}% of samples were classified correctly!")

# Simpan model
with open('model.p', 'wb') as f:
    pickle.dump({'model': model}, f)

print("✅ Model telah disimpan sebagai 'model.p'")