import os
import logging
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, url_for
import matplotlib.pyplot as plt
import pandas as pd
from deepface import DeepFace

# Comfigurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["RESULT_FOLDER"] = "static/results"
UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]
RESULT_FOLDER = app.config["RESULT_FOLDER"]

# Asegurarse de que las carpetas de subida y resultados existan
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'image' not in request.files:
            logger.warning("No file part in the request")
            return render_template("index.html", error="No se seleccionó ningún archivo")
        
        file = request.files["image"]
        
        if file.filename == '':
            logger.warning("No file selected")
            return render_template("index.html", error="No se seleccionó ningún archivo")
        
        if file:
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
                logger.info(f"File saved: {file_path}")

                emotions = DeepFace.analyze(img_path=file_path, actions=['emotion'])
                confidence = int(emotions[0]['face_confidence'] * 100)

                # Plot emociones
                plt.figure(figsize=(8, 6))
                pd.DataFrame(emotions[0]['emotion'], index=[0]).T.plot(kind="bar")
                plt.title(f"Emoción detectada: {emotions[0]['dominant_emotion']}\nÍndice de Confianza: {confidence}%")
                plt.tight_layout()

                result_path = os.path.join(app.config["RESULT_FOLDER"], f"result_{filename}.png")
                plt.savefig(result_path)
                plt.close()

                # Generar la página con datos
                return render_template("index.html", 
                                       user_image=f"{app.config['UPLOAD_FOLDER']}/{filename}", 
                                       result_image=f"{app.config['RESULT_FOLDER']}/result_{filename}.png", 
                                       emotion=emotions[0]['dominant_emotion'], 
                                       confidence=confidence)
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return render_template("index.html", error=f"Error al procesar la imagen: {str(e)}")

    # Si es un GET, renderizar sin datos
    return render_template("index.html", user_image=None, result_image=None, emotion=None, confidence=None)


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return render_template("index.html", error="Ha ocurrido un error inesperado. Por favor, inténtelo de nuevo más tarde."), 500

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")

