// Variables globales
const video = document.getElementById('video');
const ctx = document.getElementById('emotionChart').getContext('2d');
const serverUrl = '/process_frame'; // URL del servidor

// Inicializar la gráfica
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Confianza de Emociones',
            data: [],
            backgroundColor: [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
            }
        },
        plugins: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: 'Emociones Detectadas',
                font: {
                    size: 16
                }
            }
        }
    }
});

// Actualizar los datos de la gráfica
function updateChart(data) {
    chart.data.labels = Object.keys(data);
    chart.data.datasets[0].data = Object.values(data);
    chart.update();
}

// Configurar acceso a la webcam
async function setupCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (error) {
        console.error('Error al acceder a la cámara:', error);
        alert('No se pudo acceder a la cámara. Verifica los permisos.');
    }
}

// Capturar un frame del video
function captureFrame() {
    if (video.videoWidth === 0 || video.videoHeight === 0) {
        console.error('El video aún no está listo.');
        return null;
    }
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas;
}

// Enviar el frame al servidor
async function sendFrameToServer() {
    const canvas = captureFrame();
    if (!canvas) return;

    canvas.toBlob(async (blob) => {
        if (!blob) {
            console.error('No se pudo convertir el canvas a Blob.');
            return;
        }

        const formData = new FormData();
        formData.append('frame', blob, 'frame.jpg');

        try {
            const response = await fetch(serverUrl, {
                method: 'POST',
                body: formData,
            });
            const emotions = await response.json();
            updateChart(emotions);
        } catch (error) {
            console.error('Error enviando frame al servidor:', error);
        }
    }, 'image/jpeg');
}

// Inicializar la aplicación
async function init() {
    await setupCamera();
    setInterval(() => {
        sendFrameToServer();
    }, 500);
}

// Ejecutar la inicialización
init();
