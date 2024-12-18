import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from deepface import DeepFace
import matplotlib.pyplot as plt
import pandas as pd
import os

class EmotionAnalyzer:
    def __init__(self, master):
        self.master = master
        master.title("Analizador de emociones por imagen")
        master.geometry("1000x650")
        master.configure(bg="#f0f0f0")

        self.setup_ui()

    def setup_ui(self):
        # Ventana para todo el contenido
        main_frame = tk.Frame(self.master, bg="#f0f0f0")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Ventana izquierda para el sujeto a analizar
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH, expand=True)

        # Frame derecho para el resultado del análisis
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.RAISED)
        right_frame.pack(side=tk.RIGHT, padx=(10, 0), fill=tk.BOTH, expand=True)

        # Imagen del sujeto
        self.subject_image = ImageTk.PhotoImage(Image.open("CurrentGraph/user.jpg").resize((450, 450)))
        self.subject_label = tk.Label(left_frame, image=self.subject_image, bg="#ffffff")
        self.subject_label.pack(padx=10, pady=10)

        # Imagen del resultado
        self.result_image = ImageTk.PhotoImage(Image.open("CurrentGraph/sinDatos.png").resize((450, 450)))
        self.result_label = tk.Label(right_frame, image=self.result_image, bg="#ffffff")
        self.result_label.pack(padx=10, pady=10)

        # Frame del boton
        button_frame = tk.Frame(self.master, bg="#f0f0f0")
        button_frame.pack(pady=20)

        # Botón para elegir imagen
        self.choose_button = tk.Button(button_frame, text="Escoger imagen", command=self.open_image, 
                                       bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                       padx=20, pady=10)
        self.choose_button.pack()

    # Función para abrir imagen y analizarla con DeepFace
    def open_image(self):
        file_path = filedialog.askopenfilename(
            initialdir="", 
            title="Escoge la imagen a analizar", 
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            try:
                # Actualizar imagen del sujeto
                img = Image.open(file_path)
                img.thumbnail((400, 400))
                self.subject_image = ImageTk.PhotoImage(img)
                self.subject_label.config(image=self.subject_image)

                # Analizar la emoción de la imagen
                self.analyze_emotion(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Un error ocurrió: {str(e)}")

    # Función para analizar la emoción de la imagen
    def analyze_emotion(self, image_path):
        try:
            emotions = DeepFace.analyze(img_path=image_path, actions=['emotion'])
            confidence = int(emotions[0]['face_confidence'] * 100)

            # Plot emociones
            plt.figure(figsize=(8, 6))
            pd.DataFrame(emotions[0]['emotion'], index=[0]).T.plot(kind="bar")
            plt.title(f"Emocion detectada: {emotions[0]['dominant_emotion']}\nIndice de Confianza: {confidence}%")
            plt.tight_layout()
            plt.savefig('CurrentGraph/res.png')
            plt.close()

            # Actualizar imagen del resultado
            result_img = Image.open("CurrentGraph/res.png")
            result_img.thumbnail((450, 450))
            self.result_image = ImageTk.PhotoImage(result_img)
            self.result_label.config(image=self.result_image)

        except Exception as e:
            messagebox.showerror("Error de analisis", f"No se ha podido analizar la imagen: {str(e)}")
            self.result_image = ImageTk.PhotoImage(Image.open("CurrentGraph/sinDatos.png").resize((450, 450)))
            self.result_label.config(image=self.result_image)

    def on_closing(self):
        if os.path.exists("CurrentGraph/res.png"):
            os.remove("CurrentGraph/res.png")
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionAnalyzer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

