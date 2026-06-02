"""
fastapi веб сервер для классификации кошек и собак
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io
import os
import json
from datetime import datetime

# поднимаем приложение
app = FastAPI(title="Cat vs Dog Classifier")

# подключаем статику и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# путь к сохраненной модели
MODEL_PATH = "models/cat_dog_model.h5"

# проверяем что модель на месте, без неё никак
if not os.path.exists(MODEL_PATH):
    raise Exception(f"модель не найдена")

# грузим модель в память
model = load_model(MODEL_PATH)

# размер входного слоя, должно совпадать с тренировкой
IMG_HEIGHT, IMG_WIDTH = 224, 224

# файлик где хранится история предсказаний
HISTORY_FILE = "history.json"

def load_history():
    """тянем историю из json файла"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    """сохраняем историю обратно в json"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# подгружаем сохраненную историю при старте
history = load_history()

def predict_image(image_bytes):
    """ядро: принимает байты картинки, отдает кто это и насколько уверен"""
    img = Image.open(io.BytesIO(image_bytes))
    
    # png с альфой конвертим в rgb
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # ресайзим под ожидаемый моделью размер
    img = img.resize((IMG_WIDTH, IMG_HEIGHT))
    img_array = np.array(img) / 255.0  # нормируем пиксели
    img_array = np.expand_dims(img_array, axis=0)  # добавляем батч
    
    # инференс
    prediction = model.predict(img_array, verbose=0)
    confidence = float(prediction[0][0])  # вероятность что собака
    
    if confidence > 0.5:
        label = "Собака"
        confidence_percent = confidence * 100
    else:
        label = "Кошка"
        confidence_percent = (1 - confidence) * 100
    
    return label, round(confidence_percent, 2)

# главная страница с интерфейсом
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "history": history
    })

# эндпоинт для предсказаний
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # проверяем что загрузили именно картинку
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "загрузи изображение, бро")
        
        contents = await file.read()
        
        # не даем загружать слишком жирные файлы
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(400, "файл слишком толстый (макс 10 мб)")
        
        # получаем вердикт от модели
        label, confidence = predict_image(contents)
        
        # создаем запись для истории
        history_entry = {
            "id": len(history) + 1,
            "filename": file.filename,
            "prediction": label,
            "confidence": confidence,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_cat": label == "Кошка",
            "is_dog": label == "Собака"
        }
        
        # новые записи в начало списка
        history.insert(0, history_entry)
        
        # храним только последние 20
        if len(history) > 20:
            history.pop()
        
        save_history(history)
        
        # возвращаем результат 
        return JSONResponse({
            "success": True,
            "prediction": label,
            "confidence": confidence,
            "class": "dog" if label == "Собака" else "cat",
            "history": history
        })
    
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# отдаем всю историю
@app.get("/history")
async def get_history():
    return JSONResponse({"history": history})

# очищаем историю
@app.delete("/history/clear")
async def clear_history():
    global history
    history = []
    save_history(history)
    return JSONResponse({"success": True, "message": "история очищена"})

# проверка что сервер жив и модель загружена
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "history_size": len(history)
    }

# точка входа, запускаем сервер
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)