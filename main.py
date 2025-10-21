import pickle
import cv2
import mediapipe as mp
import numpy as np
import requests
import time
from threading import Thread
from collections import deque

# 🔹 Load model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']
expected_len = model.n_features_in_

# 🔹 Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.3)

# 🔹 Kamera Stream Threaded
class CameraStream:
    def __init__(self, url, buffer_size=2):
        self.cap = cv2.VideoCapture(url)
        self.buffer = deque(maxlen=buffer_size)
        self.running = True
        Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.buffer.append(frame)
            time.sleep(0.001)  # hemat CPU

    def read(self):
        if self.buffer:
            return True, self.buffer[-1]
        return False, None

    def stop(self):
        self.running = False
        self.cap.release()

# 🔹 Thread pengiriman ke ESP32
class ESP32Sender(Thread):
    def __init__(self, url, interval=1.0):
        super().__init__(daemon=True)
        self.url = url
        self.interval = interval
        self.session = requests.Session()
        self.last_send = 0
        self.queue = deque(maxlen=1)
        self.start()

    def run(self):
        while True:
            if self.queue and (time.time() - self.last_send >= self.interval):
                char = self.queue.pop()
                try:
                    response = self.session.post(self.url, data=str(char), timeout=1.0)
                    if response.status_code == 200:
                        print(f"[INFO] '{char}' terkirim ke OLED.")
                    else:
                        print(f"[WARNING] ESP32 response: {response.status_code}")
                except requests.RequestException as e:
                    print(f"[ERROR] ESP32 gagal: {e}")
                self.last_send = time.time()
            time.sleep(0.01)

    def send(self, char):
        self.queue.append(char)

# 🔹 Konfigurasi
url = "http://172.20.10.12:81/stream"
oled_url = "http://172.20.10.12/display"
stream = CameraStream(url)
sender = ESP32Sender(oled_url)
frame_skip = 2
frame_count = 0

try:
    while True:
        ret, frame = stream.read()
        if not ret:
            time.sleep(0.05)
            continue

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
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

                # Convert landmarks ke NumPy
                lm_array = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark])
                x_min, y_min = lm_array.min(axis=0)
                data_aux = (lm_array - [x_min, y_min]).flatten()
                data_aux = np.pad(data_aux, (0, max(0, expected_len - len(data_aux))))[:expected_len]

                # Prediksi
                predicted_character = model.predict([data_aux])[0]

                # Kirim ke ESP32 tanpa blocking
                sender.send(predicted_character)

                # Draw bbox & text
                x1, y1 = int(x_min * W) - 10, int(y_min * H) - 10
                x2, y2 = int(lm_array[:,0].max() * W) + 10, int(lm_array[:,1].max() * H) + 10
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 3)
                cv2.putText(frame, predicted_character.upper(), (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

        cv2.imshow("Sublingo Sign Classifier (Super Optimal)", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

finally:
    stream.stop()
    cv2.destroyAllWindows()
