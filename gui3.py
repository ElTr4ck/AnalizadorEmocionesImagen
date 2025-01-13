import cv2
from flask import Flask, render_template, Response, jsonify, request
from deepface import DeepFace
import threading
import numpy as np

app = Flask(__name__)

# Variables globales
current_emotions = {}
smoothed_emotions = {}
lock = threading.Lock()

# Factor de suavización para exponencial moving average (entre 0 y 1)
SMOOTHING_FACTOR = 0.3


def analyze_frame(frame):
    """
    Analiza un frame para detectar emociones usando DeepFace y aplica suavización
    """
    global current_emotions, smoothed_emotions
    try:
        # Convertir el frame a formato RGB para DeepFace
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detectar y analizar emociones
        analysis = DeepFace.analyze(img_path=rgb_frame, actions=['emotion'], enforce_detection=False)

        # Procesar las emociones detectadas
        detected_emotions = analysis[0]['emotion']
        with lock:
            for emotion, value in detected_emotions.items():
                if emotion not in smoothed_emotions:
                    smoothed_emotions[emotion] = value
                else:
                    # Aplicar suavización exponencial
                    smoothed_emotions[emotion] = (
                        SMOOTHING_FACTOR * value + (1 - SMOOTHING_FACTOR) * smoothed_emotions[emotion]
                    )

            # Actualizar las emociones actuales con las suavizadas
            current_emotions = smoothed_emotions.copy()

    except Exception as e:
        print(f"Error analyzing frame: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/emotions')
def emotions():
    with lock:
        return jsonify(current_emotions)


@app.route('/process_frame', methods=['POST'])
def process_frame():
    """
    Procesa un frame enviado por el cliente para analizar emociones
    """
    try:
        file = request.files['frame']
        img_array = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Analizar el frame recibido
        analyze_frame(frame)

        # Responder con las emociones detectadas
        with lock:
            return jsonify(current_emotions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False)
