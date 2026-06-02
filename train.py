"""
обучение нейросети для распознавания кошек и собак
архитектура: mobilenetv2
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import time
import json

# гиперпараметры, которые будем тыкать
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15

# пути к датасету
BASE_DIR = "data"
TRAIN_DIR = os.path.join(BASE_DIR, "training_set")
VALIDATION_DIR = os.path.join(BASE_DIR, "test_set")

# проверяем что данные вообще есть
if not os.path.exists(TRAIN_DIR):
    raise Exception(f"папка {TRAIN_DIR} не найдена")

# аугментация чтобы модель не переобучалась
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.15,
    fill_mode='nearest'
)

# для валидации просто нормируем, без аугментации
validation_datagen = ImageDataGenerator(rescale=1./255)

# подгружаем картинки для тренировки
train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    classes=['cats', 'dogs'],
    shuffle=True
)

# подгружаем тестовые картинки
validation_generator = validation_datagen.flow_from_directory(
    VALIDATION_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    classes=['cats', 'dogs'],
    shuffle=False
)

# берем предобученную mobilenet как базу
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)

# замораживаем веса базовой модели
base_model.trainable = False

# накидываем сверху свои слои для бинарной классификации
model = keras.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),  # дропаутим 30% чтобы не переобучалась
    layers.Dense(1, activation='sigmoid')  # сигмоида на выходе для кошка/собака
])

# компилим модельку
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

start_time = time.time()

history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator,
    verbose=1
)

training_time = time.time() - start_time

# смотрим качество на тесте
test_loss, test_accuracy = model.evaluate(validation_generator, verbose=0)

# создаем папку для сохранения если её нет
os.makedirs("models", exist_ok=True)

# сохраняем модель в двух форматах (на всякий случай)
model.save("models/cat_dog_model.h5")
model.save("models/cat_dog_model.keras")

# сохраняем историю обучения чтобы потом графики рисовать
history_dict = {
    'accuracy': [float(x) for x in history.history['accuracy']],
    'val_accuracy': [float(x) for x in history.history['val_accuracy']],
    'loss': [float(x) for x in history.history['loss']],
    'val_loss': [float(x) for x in history.history['val_loss']]
}

with open('models/training_history.json', 'w') as f:
    json.dump(history_dict, f)