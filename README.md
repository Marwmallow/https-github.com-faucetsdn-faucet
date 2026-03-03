# 🎬 YouTube Content Automation System

Профессиональная система для автоматизации создания и публикации контента на YouTube с рандомизацией качества.

## 🌟 Возможности

- **🎯 Генерация контента**: Автоматическое создание скриптов для видео различных типов
- **🎲 Рандомизация качества**: Создание вариативного контента для избежания паттернов
- **🎬 Обработка видео**: Создание видео из скриптов с различными настройками качества
- **📤 YouTube API**: Автоматическая загрузка и планирование публикаций
- **📅 Планировщик**: Распределение контента по времени с оптимизацией
- **📊 Статистика**: Отслеживание производительности и успешности

## 📋 Требования

- Python 3.8+
- FFmpeg (для обработки видео)
- YouTube Data API v3 credentials

## 🚀 Быстрый старт

### 1. Установка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd youtube-automation

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка

```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env и добавьте ваши API ключи
nano .env
```

### 3. YouTube API Credentials

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект
3. Включите **YouTube Data API v3**
4. Создайте OAuth 2.0 credentials
5. Скачайте JSON файл и сохраните как `client_secrets.json`

### 4. Первый запуск

```bash
# Авторизация в YouTube
python main.py auth

# Генерация скрипта
python main.py generate -t "Python для начинающих"

# Создание профилей качества
python main.py quality -q medium -v 0.3 -c 5

# Планирование задач
python main.py schedule -t "Обучение Python" -c 5 -d 7
```

## 💻 Использование CLI

### Генерация скрипта

```bash
python main.py generate \
  --topic "Тема видео" \
  --type tutorial \
  --duration 300 \
  --quality random
```

**Типы видео:**
- `tutorial` - Обучающие видео
- `review` - Обзоры
- `listicle` - ТОП-листы
- `story` - Истории
- `news` - Новости

### Профили качества

```bash
# Генерация одного профиля
python main.py quality -q high -v 0.2

# Батч профилей
python main.py quality -q medium -v 0.4 -c 10
```

**Уровни качества:**
- `low` - 720p, 24-30fps
- `medium` - 720p-1080p, 30-60fps
- `high` - 1080p-4k, 60fps

**Вариативность** (0.0 - 1.0):
- `0.0-0.2` - Минимальная вариативность
- `0.3-0.5` - Средняя вариативность
- `0.6-1.0` - Высокая вариативность

### Планирование контента

```bash
# Одна задача
python main.py schedule -t "Название видео"

# Серия видео
python main.py schedule \
  -t "Курс Python" \
  -c 10 \
  -d 14 \
  --type tutorial
```

### Просмотр задач

```bash
# Задачи на ближайшие 24 часа
python main.py upcoming

# Задачи на неделю
python main.py upcoming -h 168

# Статистика
python main.py stats
```

### Создание видео

```bash
# Полный цикл: генерация + рендеринг
python main.py create -t "Python для начинающих" -o ./output
```

### Загрузка на YouTube

```bash
python main.py upload \
  -v ./output/video.mp4 \
  -t "Заголовок видео" \
  -d "Описание видео"
```

## 📁 Структура проекта

```
.
├── main.py                 # Главный CLI интерфейс
├── requirements.txt        # Зависимости
├── .env.example           # Пример конфигурации
├── config/                # Конфигурационные файлы
│   └── schedule.json      # Расписание задач
├── src/
│   ├── content_generator/ # Генерация контента
│   │   ├── script_generator.py
│   │   └── quality_randomizer.py
│   ├── video_processor/   # Обработка видео
│   │   └── video_creator.py
│   ├── youtube_api/       # YouTube API
│   │   └── uploader.py
│   └── scheduler/         # Планировщик
│       └── content_scheduler.py
├── templates/             # Шаблоны контента
├── examples/              # Примеры использования
└── output/                # Готовые видео
```

## 🎲 Система рандомизации

Система рандомизации создаёт вариативность в контенте для:

### Качество видео
- Разрешение: 720p, 1080p, 4K
- FPS: 24, 30, 60
- Битрейт: low, medium, high

### Качество аудио
- Битрейт: 96k, 192k, 320k
- Форматы: MP3, AAC

### Метаданные
- Количество тегов: 5-30
- Длина описания: short, medium, long
- Стиль заголовка: simple, engaging, clickbait

### Расписание
- Время публикации: 9:00 - 21:00
- Интервалы: 1-7 дней
- Случайные минуты

## 🔧 Программное использование

```python
from src.content_generator.script_generator import ScriptGenerator
from src.content_generator.quality_randomizer import QualityRandomizer
from src.video_processor.video_creator import VideoCreator

# Генерация скрипта
generator = ScriptGenerator()
script = generator.generate_script(
    topic="Python для начинающих",
    video_type="tutorial",
    duration=300,
    quality_level="random"
)

# Генерация профиля качества
randomizer = QualityRandomizer(base_quality="medium", variance=0.3)
profile = randomizer.generate_profile()

# Создание видео
creator = VideoCreator(output_dir="./output")
config = creator.apply_quality_profile(profile)
video_path = creator.create_video_from_script(
    script=script.script,
    title=script.title,
    config=config
)
```

## 📊 Примеры профилей качества

### Низкое качество (экономичный режим)
```python
{
    "resolution": "720p",
    "fps": 24,
    "bitrate": "low",
    "audio_quality": "low",
    "tags_count": 5-10
}
```

### Среднее качество (баланс)
```python
{
    "resolution": "1080p",
    "fps": 30,
    "bitrate": "medium",
    "audio_quality": "medium",
    "tags_count": 10-20
}
```

### Высокое качество (премиум)
```python
{
    "resolution": "4k",
    "fps": 60,
    "bitrate": "high",
    "audio_quality": "high",
    "tags_count": 15-25
}
```

## 🤝 Интеграция с вашими скриптами

Если у вас уже есть Python скрипты для YouTube, вы можете легко их интегрировать:

### Добавление своего генератора контента

```python
# src/content_generator/custom_generator.py
from src.content_generator.script_generator import ScriptGenerator

class CustomGenerator(ScriptGenerator):
    def generate_script(self, topic, **kwargs):
        # Ваша логика
        return super().generate_script(topic, **kwargs)
```

### Добавление своего обработчика видео

```python
# src/video_processor/custom_processor.py
from src.video_processor.video_creator import VideoCreator

class CustomProcessor(VideoCreator):
    def create_video_from_script(self, script, **kwargs):
        # Ваша логика
        return super().create_video_from_script(script, **kwargs)
```

## ⚙️ Конфигурация

### Файл .env

```bash
# YouTube API
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_API_KEY=your_api_key

# OpenAI (опционально)
OPENAI_API_KEY=your_openai_key

# Anthropic Claude (опционально)
ANTHROPIC_API_KEY=your_anthropic_key

# Настройки
OUTPUT_DIR=./output
UPLOAD_SCHEDULE=daily
BASE_QUALITY=medium
VARIANCE=0.3
```

## 📈 Квоты YouTube API

- **Дневной лимит**: 10,000 единиц
- **Загрузка видео**: ~1600 единиц
- **Максимум видео в день**: ~6 видео

Система автоматически отслеживает квоты и предупреждает о превышении.

## 🐛 Отладка

```bash
# Включите подробные логи
export DEBUG=1

# Запуск с логированием
python main.py generate -t "Test" 2>&1 | tee debug.log
```

## 📝 TODO / Roadmap

- [ ] Интеграция с OpenAI для генерации скриптов
- [ ] Интеграция с moviepy для реального создания видео
- [ ] Поддержка TTS (Text-to-Speech)
- [ ] Автоматическая генерация миниатюр
- [ ] Поддержка субтитров
- [ ] Web-интерфейс для управления
- [ ] Telegram-бот для уведомлений
- [ ] Аналитика YouTube (просмотры, лайки)
- [ ] A/B тестирование заголовков
- [ ] Интеграция с Shorts

## 🤝 Вклад в проект

Если у вас есть идеи или улучшения:

1. Форкните репозиторий
2. Создайте feature branch
3. Внесите изменения
4. Отправьте Pull Request

## 📄 Лицензия

MIT License - свободное использование для личных и коммерческих проектов.

## 📧 Контакты

Если у вас есть вопросы или предложения - создайте Issue в репозитории.

---

**Сделано с ❤️ для автоматизации YouTube контента**
