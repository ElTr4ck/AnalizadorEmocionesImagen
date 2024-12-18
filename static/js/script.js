document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const userImage = document.getElementById('user-image');
    const resultImage = document.getElementById('result-image');
    const emotionSpan = document.getElementById('emotion');
    const confidenceSpan = document.getElementById('confidence');
    const fileInput = document.getElementById('image-input');
    const fileNameSpan = document.getElementById('file-name');
    const fileInputLabel = document.querySelector('.file-input-label');

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            const fileName = e.target.files[0].name;
            fileNameSpan.textContent = fileName;
            fileInputLabel.classList.add('file-selected');
        } else {
            fileNameSpan.textContent = 'Seleccionar Imagen';
            fileInputLabel.classList.remove('file-selected');
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        resultDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');

        try {
            const response = await fetch('/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Error del servidor');
            }

            const result = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(result, 'text/html');

            userImage.src = doc.getElementById('user-image').src;
            resultImage.src = doc.getElementById('result-image').src;
            emotionSpan.textContent = doc.getElementById('emotion').textContent;
            confidenceSpan.textContent = doc.getElementById('confidence').textContent;

            resultDiv.classList.remove('hidden');
        } catch (error) {
            errorDiv.textContent = 'Ocurrió un error. Por favor, inténtalo de nuevo.';
            errorDiv.classList.remove('hidden');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });
});
