import pickle  # Untuk memuat model yang sudah dilatih
import cv2  # Untuk akses webcam dan manipulasi gambar
import mediapipe as mp  # Untuk deteksi tangan dan landmark
import numpy as np  # Untuk manipulasi array numerik

# 🔹 Load model dari file pickle
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']  # Ambil objek model dari dictionary

# 🔹 Aktifkan kamera
cap = cv2.VideoCapture("http://172.20.10.12:81/stream")

# 🔹 Inisialisasi modul MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# 🔁 Loop utama: proses video frame-by-frame
while True:
    data_aux = []  # Untuk menyimpan fitur landmark yang sudah dinormalisasi
    x_ = []
    y_ = []

    ret, frame = cap.read()
    if not ret:
        break

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                x_.append(lm.x)
                y_.append(lm.y)

            for lm in hand_landmarks.landmark:
                data_aux.append(lm.x - min(x_))
                data_aux.append(lm.y - min(y_))

        # 🔧 Padding jika jumlah fitur tidak sesuai
        expected_len = model.n_features_in_
        if len(data_aux) < expected_len:
            data_aux += [0] * (expected_len - len(data_aux))
        elif len(data_aux) > expected_len:
            data_aux = data_aux[:expected_len]

        # 🔮 Prediksi gesture
        prediction = model.predict([np.asarray(data_aux)])
        predicted_character = prediction[0]  # Sudah berupa huruf 'a' - 'z'

        # Bounding box
        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10
        x2 = int(max(x_) * W) + 10
        y2 = int(max(y_) * H) + 10

        # Gambar bounding box & label huruf kapital
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
        cv2.putText(frame, predicted_character.upper(), (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

    # Tampilkan frame ke layar
    cv2.imshow('Sublingo Sign Classifier', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Tekan ESC untuk keluar
        break

# 🔚 Bersihkan
cap.release()
cv2.destroyAllWindows()
