import os  # Untuk mengelola file dan folder
import pickle  # Untuk menyimpan data ke file .pickle
import time  # Untuk tracking waktu

import mediapipe as mp  # Untuk deteksi tangan
import cv2  # Untuk membaca dan memproses gambar
import numpy as np  # Untuk operasi array

# Inisialisasi modul dari MediaPipe
mp_hands = mp.solutions.hands  # Modul deteksi tangan
mp_drawing = mp.solutions.drawing_utils  # Untuk menggambar hasil landmark
mp_drawing_styles = mp.solutions.drawing_styles  # Untuk style menggambar

# Inisialisasi objek deteksi tangan
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
# static_image_mode=True → karena kita proses gambar diam (bukan video)

DATA_DIR = './data/ASL_Alphabet_Dataset/asl_alphabet_train'  # Folder tempat dataset gambar disimpan

# List untuk menyimpan semua data landmark & label kelasnya
data = []
labels = []

# Target jumlah fitur (42 untuk 1 tangan: 21 landmark x 2 koordinat)
TARGET_FEATURES = 42

# Counter untuk tracking
processed_count = 0
skipped_count = 0

# Timing variables
total_start_time = time.time()
folder_times = []

# Iterasi untuk setiap folder di dalam ./data (misalnya: ./data/0, ./data/1, dst)
for dir_ in os.listdir(DATA_DIR):
    # Skip files that are not directories (like .DS_Store)
    if not os.path.isdir(os.path.join(DATA_DIR, dir_)):
        continue
        
    # Start timing for this folder
    folder_start_time = time.time()
    print(f"Processing folder: {dir_}")
    
    # Iterasi untuk setiap gambar dalam folder kelas tersebut
    for img_path in os.listdir(os.path.join(DATA_DIR, dir_)):
        data_aux = []  # List untuk simpan koordinat landmark tangan dari 1 gambar

        x_ = []  # Untuk menyimpan semua nilai x dari landmark
        y_ = []  # Untuk menyimpan semua nilai y dari landmark

        # Baca gambar dari file
        img_path_full = os.path.join(DATA_DIR, dir_, img_path)
        img = cv2.imread(img_path_full)
        
        # Periksa apakah gambar berhasil dimuat
        if img is None:
            print(f"Warning: Could not load image {img_path_full}")
            continue
            
        # Konversi BGR ke RGB untuk diproses oleh MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Proses deteksi tangan dengan MediaPipe
        results = hands.process(img_rgb)

        # Jika tangan terdeteksi dalam gambar
        if results.multi_hand_landmarks:
            # Reset data_aux untuk setiap gambar
            data_aux = []
            x_ = []
            y_ = []
            
            # Hanya proses tangan pertama (untuk konsistensi)
            if len(results.multi_hand_landmarks) > 0:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Ambil semua koordinat x dan y
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x  # Koordinat x (dalam skala relatif: 0-1)
                    y = hand_landmarks.landmark[i].y  # Koordinat y

                    x_.append(x)  # Tambahkan ke list x_
                    y_.append(y)  # Tambahkan ke list y_

                # Normalisasi koordinat: dikurangi dengan x & y terkecil supaya posisinya relatif dari kiri atas
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y

                    data_aux.append(x - min(x_))  # Normalisasi x
                    data_aux.append(y - min(y_))  # Normalisasi y

                # Cek apakah jumlah fitur sesuai target
                if len(data_aux) == TARGET_FEATURES:
                    data.append(data_aux)  # Simpan data landmark dari gambar ini
                    labels.append(dir_)  # Simpan label kelas (nama folder)
                    processed_count += 1
                else:
                    print(f"Skipped: {img_path_full} - Expected {TARGET_FEATURES} features, got {len(data_aux)}")
                    skipped_count += 1
            else:
                print(f"Warning: No hand landmarks in {img_path_full}")
                skipped_count += 1
        else:
            # print(f"Warning: No hand detected in {img_path_full}")
            skipped_count += 1
    
    # End timing for this folder
    folder_end_time = time.time()
    folder_elapsed = folder_end_time - folder_start_time
    folder_times.append((dir_, folder_elapsed))
    print(f"  ✓ Folder '{dir_}' completed in {folder_elapsed:.2f} seconds")

print(f"\nTotal samples processed: {len(data)}")
print(f"Total labels: {len(labels)}")
print(f"Successfully processed: {processed_count}")
print(f"Skipped samples: {skipped_count}")

# Calculate total time
total_end_time = time.time()
total_elapsed = total_end_time - total_start_time

# Print timing summary
print(f"\n{'='*50}")
print(f"TIMING SUMMARY")
print(f"{'='*50}")
print(f"Total processing time: {total_elapsed:.2f} seconds ({total_elapsed/60:.2f} minutes)")

# Print individual folder times
print(f"\nFolder processing times:")
for folder_name, folder_time in folder_times:
    print(f"  {folder_name}: {folder_time:.2f}s")

# Simpan data dan label ke file .pickle
with open('dataASL.pickle', 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)

print(f"\nDataset saved to dataASL.pickle")