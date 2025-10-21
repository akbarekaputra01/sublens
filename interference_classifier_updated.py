import pickle
import cv2
import mediapipe as mp
import numpy as np
import requests
import time
from threading import Thread

# 🔹 Load model dari file pickle
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# 🔹 Inisialisasi modul MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.3)

# 🔹 Class untuk ambil stream dengan thread
class CameraStream:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        self.ret, self.frame = self.cap.read()
        self.running = True
        Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.ret, self.frame = ret, frame

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.cap.release()

# 🔹 URL stream dari ESP32-CAM
# url = "http://172.20.10.12:81/stream"
url = "http://172.20.10.3:81/stream"
stream = CameraStream(url)

# Variable untuk rate limiting
last_send_time = 0
send_interval = 1.0  # Kirim maksimal 1x per detik

frame_count = 0

while True:
    ret, frame = stream.read()
    if not ret:
        print("[WARNING] Gagal ambil frame dari ESP32.")
        continue
    
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    frame_count += 1
    if frame_count % 2 != 0:  # skip 1 frame, proses 1 frame
        continue

    data_aux = []
    x_ = []
    y_ = []

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

        expected_len = model.n_features_in_
        if len(data_aux) < expected_len:
            data_aux += [0] * (expected_len - len(data_aux))
        elif len(data_aux) > expected_len:
            data_aux = data_aux[:expected_len]

        prediction = model.predict([np.asarray(data_aux)])
        predicted_character = prediction[0]

        # Kirim ke ESP32 OLED dengan rate limiting
        current_time = time.time()
        if current_time - last_send_time >= send_interval:
            try:
                oled_url = "http://172.20.10.3/display"
                response = requests.post(oled_url, data=str(predicted_character), timeout=2)
                if response.status_code == 200:
                    print(f"[INFO] Huruf '{predicted_character}' berhasil dikirim ke OLED.")
                    last_send_time = current_time
                else:
                    print(f"[WARNING] ESP32 response: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Koneksi ke ESP32 gagal: {e}")
            except Exception as e:
                print(f"[ERROR] Kirim ke ESP32 gagal: {e}")

        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10
        x2 = int(max(x_) * W) + 10
        y2 = int(max(y_) * H) + 10

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
        cv2.putText(frame, predicted_character.upper(), (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

    cv2.imshow("Sublingo Sign Classifier", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC untuk keluar
        break

stream.stop()
cv2.destroyAllWindows()
