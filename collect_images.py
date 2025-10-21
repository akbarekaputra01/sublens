import os  # Untuk mengelola file dan folder
import cv2  # Untuk menggunakan OpenCV (kamera, gambar, dll)

DATA_DIR = './data'  # Folder tempat menyimpan data

# Jika folder data belum ada, buat foldernya
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

numbers_of_classes = 3  # Jumlah kelas data yang akan diambil
dataset_size = 100  # Jumlah gambar per kelas
cap = cv2.VideoCapture(0)  # Mengaktifkan kamera default (biasanya webcam laptop)

# Loop untuk setiap kelas
for j in range(numbers_of_classes):
    # Buat folder untuk masing-masing kelas jika belum ada
    if not os.path.exists(os.path.join(DATA_DIR, str(j))):
        os.makedirs(os.path.join(DATA_DIR, str(j)))
    
    print(f"Collecting data for class {j}")  # Tampilkan info kelas yang sedang dikumpulkan
    
    done = False  # Tidak digunakan, bisa dihapus
    
    while True:  # Loop sampai user tekan 'q'
        ret, frame = cap.read()  # Baca frame dari kamera
        # Tampilkan teks petunjuk pada frame
        cv2.putText(frame, 'Ready? press "Q" ! :)', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
        cv2.imshow('frame', frame)  # Tampilkan frame ke jendela
        
        if cv2.waitKey(25) == ord('q'):  # Jika user tekan 'q', keluar dari loop
            break

        counter = 0  # Mulai hitung gambar dari 0
        
    # Loop untuk ambil dan simpan gambar sebanyak dataset_size
    while counter < dataset_size:
        ret, frame = cap.read()  # Ambil frame lagi dari kamera
        cv2.imshow('frame', frame)  # Tampilkan frame
        cv2.waitKey(25)  # Tunggu 25 milidetik
        # Simpan frame sebagai gambar di folder sesuai kelas dan nomor gambar
        cv2.imwrite(os.path.join(DATA_DIR, str(j), f'{counter}.jpg'), frame)
        counter += 1  # Tambah hitungan gambar

# Setelah semua kelas selesai, matikan kamera dan tutup semua jendela
cap.release()
cv2.destroyAllWindows()