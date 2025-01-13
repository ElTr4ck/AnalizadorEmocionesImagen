import cv2
from flask import Flask, render_template, Response, jsonify
from deepface import DeepFace
import threading
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

# Variables globales
current_emotions = {}
lock = threading.Lock()

""" Function: analyze_frame
    Analiza un frame de video para analizar emociones usando la libreria de DeepFace
    Args:
        frame (numpy.ndarray): El frame de video a analizar, convertido en formato RGB
    Raises:
        Exception: Si hay un error durante el analisis del frame
"""
def analyze_frame(frame):
    
    global current_emotions
    try:
        # Convertir el frame de BGR a RGB (DeepFace usa RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detected_face = DeepFace.extract_faces(img_path=rgb_frame, detector_backend='opencv')
        numberOfFaces = len(detected_face)

        for face_obj in detected_face:
            img = face_obj['face']
            img = img * 255
            cv2.imwrite("CurrentGraph/face.jpg", img)
            imgrdt = plt.imread("CurrentGraph/face.jpg")

            analysis = DeepFace.analyze(img_path=imgrdt, actions=['emotion'], enforce_detection=False)

            with lock:
                temp_current_emotions = analysis[0]['emotion']

                # Convertir el np.float32 a np.float64
                for keys in temp_current_emotions:
                    current_emotions[keys] = 0 # Resetear current_emotions
                    a = temp_current_emotions[keys]
                    b = np.array([a], dtype=np.float32)
                    c = b.astype(np.float64)
                    d = c[0]
                    current_emotions[keys] += d # Sumar los valores                    
        
        for keys in current_emotions:
            current_emotions[keys] /= numberOfFaces # Obtiene promedio de emocion con respecto al num de rostros

    except Exception as e:
        print(f"Error analyzing frame: {e}")


"""
    Function: generate_frames
    Captura frames de video desdela cámara predeterminada, analiza cada frma ene un hilo separado,
    y codifica los frames para su transimión en formato JPEG.
    Yields:
        bytes: Frame de video codificado en bits, con encabezados pertinentes para transmisión.
"""
def generate_frames():
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        success, frame = cap.read()
        if not success:
            print("Error reading frame")
            break
        
        # Enviar el frame para análisis en un hilo separado
        threading.Thread(target=analyze_frame, args=(frame,)).start()
        
        # Codificar el frame para transmisión
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/emotions')
def emotions():
    global current_emotions
    with lock:
        return jsonify(current_emotions)

if __name__ == "__main__":
    app.run(debug=True)
