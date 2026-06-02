// хватаем все нужные элементы с html страницы
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const previewArea = document.getElementById('previewArea');
const previewImg = document.getElementById('previewImg');
const resultLabel = document.getElementById('resultLabel');
const confidenceFill = document.getElementById('confidenceFill');
const confidenceText = document.getElementById('confidenceText');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');

// обработчики на дн drop зону
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');  // красим зону когда тащат файл
});
dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file);  // погнали обрабатывать
    } else {
        alert('Пожалуйста, загрузите изображение');
    }
});

// если выбрали файл через кнопку
fileInput.addEventListener('change', (e) => {
    if (e.target.files[0]) {
        handleFile(e.target.files[0]);
    }
});

// отправляем фото на сервер и показываем результат
async function handleFile(file) {
    // сначала покажем превьюшку, чтобы юзер видел что загрузил
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewArea.style.display = 'block';
    };
    reader.readAsDataURL(file);
    
    // готовим форму для отправки
    const formData = new FormData();
    formData.append('file', file);
    
    // скидываем UI в состояние загрузки
    resultLabel.textContent = '🔍 Анализирую...';
    confidenceFill.style.width = '0%';
    confidenceText.textContent = 'Уверенность: --%';
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // обновляем карточку с результатом
            resultLabel.textContent = data.prediction;
            resultLabel.className = `result-label ${data.class === 'dog' ? 'dog' : 'cat'}`;
            
            const confidencePercent = data.confidence;
            confidenceFill.style.width = `${confidencePercent}%`;
            confidenceFill.textContent = `${confidencePercent}%`;
            confidenceText.textContent = `Уверенность: ${confidencePercent}%`;
            
            // обновляем историю предсказаний
            updateHistory(data.history);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        resultLabel.textContent = '❌ Ошибка при анализе';
        resultLabel.className = 'result-label';
        alert('Ошибка при загрузке. Попробуйте другое фото.');
    }
}

// реализуем историю предсказаний
function updateHistory(history) {
    if (!historyList) return;
    
    if (history.length === 0) {
        historyList.innerHTML = '<div class="history-item">История пуста</div>';
        return;
    }
    
    // пробегаемся по массиву и генерим html
    historyList.innerHTML = history.map(item => `
        <div class="history-item">
            <div class="history-filename">${escapeHtml(item.filename)}</div>
            <div class="history-prediction ${item.prediction === 'Кошка' ? 'cat' : 'dog'}">
                ${item.prediction === 'Кошка' ? '🐱' : '🐶'} ${item.prediction}
            </div>
            <div class="history-confidence">${item.confidence}%</div>
            <div class="history-time">${item.timestamp}</div>
        </div>
    `).join('');
}

// очищаем историю по кнопке
clearHistoryBtn.addEventListener('click', async () => {
    if (confirm('Очистить всю историю?')) {
        const response = await fetch('/history/clear', { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
            updateHistory([]);
        }
    }
});

// при загрузке страницы тянем историю с бэка
async function loadHistory() {
    const response = await fetch('/history');
    const data = await response.json();
    if (data.history) {
        updateHistory(data.history);
    }
}

// защита от xss: экранируем юзерский ввод
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// все системы запущены, грузим историю
loadHistory();
