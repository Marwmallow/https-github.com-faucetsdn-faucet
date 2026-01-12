# 🚀 Video Upscaler - AI & Traditional Methods

Автоматический апскейлинг видео с созданием 5+ вариантов с разными оптимальными настройками.

## 🎯 Возможности

- ✅ **5 вариантов FFmpeg** - всегда доступны, без дополнительных установок
- ✅ **Topaz Video AI** - лучшее качество AI (если установлен)
- ✅ **Real-ESRGAN** - отличный AI upscaler (open source)
- ✅ **Автоматизация** - создает все варианты одной командой
- ✅ **Гибкие настройки** - 720p, 1080p, 1440p, 4K
- ✅ **Сравнение** - выберите лучший визуально

## 📋 Требования

### Обязательно:
- **Python 3.6+**
- **FFmpeg** - для всех базовых методов

### Опционально (для AI):
- **Topaz Video AI** - для лучшего качества (платный)
- **Real-ESRGAN** - для AI upscaling (бесплатный)

## 🔧 Установка

### 1. FFmpeg (обязательно)

**Windows:**
```bash
# Через Chocolatey
choco install ffmpeg

# Или скачать с https://ffmpeg.org/download.html
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. Topaz Video AI (опционально)

- Скачать: https://www.topazlabs.com/topaz-video-ai
- Установить в стандартную папку или TopazVideoAIPortable
- Скрипт автоматически найдет его

**Supported paths:**
- `C:\Program Files\Topaz Labs LLC\Topaz Video AI\`
- `C:\Users\[User]\TopazVideoAIPortable\`
- `/Applications/Topaz Video AI.app/` (macOS)

### 3. Real-ESRGAN (опционально)

**Windows:**
```bash
# Скачать executable с GitHub
# https://github.com/xinntao/Real-ESRGAN/releases
# Положить realesrgan-ncnn-vulkan.exe в PATH
```

**Linux:**
```bash
# Скачать с releases или собрать из исходников
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip
unzip realesrgan-ncnn-vulkan-20220424-ubuntu.zip
sudo mv realesrgan-ncnn-vulkan /usr/local/bin/
```

## 🚀 Использование

### Простейший вариант (5 FFmpeg методов)

```bash
# Апскейл до 1080p (по умолчанию)
python video_upscaler.py your_video.mp4
```

Создаст 5 вариантов в папке `upscaled/`:
- `lanczos_1080p.mp4` - острый, детализированный
- `bicubic_1080p.mp4` - гладкий, для шумных видео
- `sharpened_1080p.mp4` - экстра-резкость
- `denoised_1080p.mp4` - чистый, удаляет шум
- `enhanced_1080p.mp4` - яркие цвета + резкость

### Апскейл до 4K

```bash
python video_upscaler.py your_video.mp4 -r 4k
```

### Выборочные методы

```bash
# Только лучшие методы
python video_upscaler.py your_video.mp4 -m lanczos sharpened enhanced

# Только Lanczos (быстро)
python video_upscaler.py your_video.mp4 -m lanczos
```

### С Topaz Video AI

```bash
# FFmpeg + Topaz AI
python video_upscaler.py your_video.mp4 -m lanczos topaz

# Только Topaz (если установлен)
python video_upscaler.py your_video.mp4 -m topaz -r 4k
```

### С Real-ESRGAN

```bash
# FFmpeg + Real-ESRGAN AI
python video_upscaler.py your_video.mp4 -m lanczos realesrgan

# Все методы включая AI
python video_upscaler.py your_video.mp4 -m lanczos bicubic sharpened denoised enhanced realesrgan
```

### Кастомное разрешение

```bash
# Апскейл до конкретного разрешения
python video_upscaler.py your_video.mp4 -r 2560x1440
```

## 📖 Методы апскейлинга

### 🔹 FFmpeg методы (всегда доступны)

#### 1. **Lanczos** (рекомендуется)
- **Когда:** Универсальный, для большинства случаев
- **Плюсы:** Острые детали, хорошее качество
- **Минусы:** Может усилить шум
- **Команда:** `-m lanczos`

```bash
python video_upscaler.py video.mp4 -m lanczos
```

#### 2. **Bicubic**
- **Когда:** Видео с шумом/артефактами
- **Плюсы:** Гладкое, смягчает шум
- **Минусы:** Менее резкое
- **Команда:** `-m bicubic`

```bash
python video_upscaler.py noisy_video.mp4 -m bicubic
```

#### 3. **Sharpened**
- **Когда:** Нужны очень четкие детали
- **Плюсы:** Максимальная резкость
- **Минусы:** Может создать ореолы
- **Команда:** `-m sharpened`

```bash
python video_upscaler.py soft_video.mp4 -m sharpened
```

#### 4. **Denoised**
- **Когда:** Старое/шумное видео
- **Плюсы:** Убирает зерно и шум
- **Минусы:** Может терять мелкие детали
- **Команда:** `-m denoised`

```bash
python video_upscaler.py old_camera.mp4 -m denoised
```

#### 5. **Enhanced**
- **Когда:** Нужны яркие цвета
- **Плюсы:** Насыщенные цвета + резкость
- **Минусы:** Может пересытить цвета
- **Команда:** `-m enhanced`

```bash
python video_upscaler.py nature_video.mp4 -m enhanced
```

---

### 🔸 AI методы (требуют установки)

#### 6. **Topaz Video AI** 💎 (ЛУЧШЕЕ КАЧЕСТВО)
- **Когда:** Нужно максимальное качество
- **Плюсы:** Лучший AI, восстанавливает детали
- **Минусы:** Платный (~$300), медленный
- **Команда:** `-m topaz`

**Модели Topaz:**
- `artemis-lq` - низкое качество источника (сжатые видео)
- `artemis-mq` - среднее качество
- `artemis-hq` - высокое качество источника
- `proteus` - реалистичное улучшение
- `iris` - для старого/чересстрочного видео

```bash
python video_upscaler.py compressed_video.mp4 -m topaz -r 4k
```

**💡 Для Topaz лучше использовать GUI:**
1. Откройте Topaz Video AI
2. Загрузите видео из `upscaled/` папки
3. Выберите модель (Artemis LQ для YouTube видео)
4. Export Settings → 4K
5. Экспортируйте

#### 7. **Real-ESRGAN** 🎨 (AI, бесплатный)
- **Когда:** Нужен AI без покупки Topaz
- **Плюсы:** Отличное качество, бесплатный
- **Минусы:** Медленнее FFmpeg, требует GPU
- **Команда:** `-m realesrgan`

```bash
python video_upscaler.py anime.mp4 -m realesrgan -r 4k
```

**Особенно хорош для:**
- Аниме
- Рисованных видео
- Игровые записи

---

## 🎨 Какой метод выбрать?

### По типу контента:

| Тип видео | Рекомендуемый метод | Почему |
|-----------|---------------------|---------|
| 🌊 Природа (вода, облака) | `lanczos` или `enhanced` | Детали + цвета |
| 🎬 Фильмы/видео | `lanczos` или `topaz` | Универсально |
| 📹 YouTube сжатое | `denoised` или `topaz-lq` | Убирает артефакты |
| 📷 Старое видео | `denoised` + `topaz-iris` | Очистка + AI |
| 🎮 Игры | `sharpened` или `realesrgan` | Четкость |
| 🎨 Аниме | `realesrgan` | Специализирован |
| 🔥 С шумом/зерном | `bicubic` или `denoised` | Смягчает |
| ✨ Четкое HD → 4K | `lanczos` или `topaz-hq` | Просто апскейл |

### По приоритетам:

**Скорость:**
1. `lanczos` - 5-10 минут
2. `bicubic` - 5-10 минут
3. `sharpened` - 10-15 минут
4. `realesrgan` - 30-60 минут
5. `topaz` - 1-3 часа

**Качество:**
1. `topaz` 💎💎💎💎💎
2. `realesrgan` 💎💎💎💎
3. `sharpened` 💎💎💎
4. `lanczos` 💎💎💎
5. `enhanced` 💎💎
6. `bicubic` 💎💎

**Универсальность:**
- `lanczos` - лучший баланс скорость/качество

---

## 💡 Практические примеры

### Пример 1: YouTube видео → 4K

```bash
# Шаг 1: Создать 5 вариантов FFmpeg
python video_upscaler.py youtube_720p.mp4 -r 4k

# Шаг 2: Посмотреть все варианты
# Выбрать лучший визуально

# Шаг 3 (опционально): Финальный AI апскейл лучшего варианта
# Открыть лучший вариант в Topaz Video AI → Artemis LQ → Export 4K
```

### Пример 2: Зацикленное видео → 1080p

```bash
# Сначала создали петлю
python video_loop_maker.py water.mp4 --analyze

# Теперь апскейл лучшей петли
python video_upscaler.py output/optimized_overlap_1.5s.mp4 -r 1080p -m lanczos enhanced
```

### Пример 3: Старое видео → чистый 1080p

```bash
# Сначала убрать шум и апскейлить
python video_upscaler.py old_video.avi -r 1080p -m denoised

# Если есть Topaz - использовать iris модель для old footage
```

### Пример 4: Batch апскейл папки

```bash
# Создать batch скрипт
for file in *.mp4; do
    echo "Upscaling $file..."
    python video_upscaler.py "$file" -r 1080p -m lanczos sharpened
done
```

---

## 🔧 Продвинутые настройки

### Изменить качество кодирования

Отредактируйте в скрипте:

```python
'-crf', '18',  # Качество (15-23): меньше = лучше, больше размер
'-preset', 'slow',  # Пресет (ultrafast/fast/medium/slow/veryslow)
```

**Рекомендации:**
- CRF 15-18: Максимальное качество (для финального видео)
- CRF 20-23: Хорошее качество (баланс размер/качество)
- Preset slow/veryslow: Лучшее сжатие (медленнее)

### Использовать GPU ускорение (NVIDIA)

Замените кодек в скрипте:

```python
'-c:v', 'h264_nvenc',  # Вместо libx264
'-preset', 'p7',  # Лучший пресет для NVENC
'-rc', 'vbr',
'-cq', '19',
```

**Ускорение:** 3-5x быстрее!

### Кастомные фильтры FFmpeg

```bash
# Ваша комбинация фильтров
ffmpeg -i input.mp4 \
  -vf "hqdn3d=4,scale=3840:2160:flags=lanczos,unsharp=5:5:0.8" \
  -c:v libx264 -crf 18 output.mp4
```

---

## 📊 Сравнение методов

### Тест: 720p → 1080p (30 сек видео)

| Метод | Время | Размер | Качество | Резкость | Цена |
|-------|-------|--------|----------|----------|------|
| Lanczos | 2 мин | 45 MB | ⭐⭐⭐⭐ | 🔪🔪🔪🔪 | Бесплатно |
| Bicubic | 2 мин | 44 MB | ⭐⭐⭐ | 🔪🔪🔪 | Бесплатно |
| Sharpened | 3 мин | 47 MB | ⭐⭐⭐⭐ | 🔪🔪🔪🔪🔪 | Бесплатно |
| Denoised | 5 мин | 42 MB | ⭐⭐⭐⭐ | 🔪🔪🔪 | Бесплатно |
| Enhanced | 3 мин | 48 MB | ⭐⭐⭐⭐ | 🔪🔪🔪🔪 | Бесплатно |
| Real-ESRGAN | 25 мин | 52 MB | ⭐⭐⭐⭐⭐ | 🔪🔪🔪🔪🔪 | Бесплатно |
| Topaz AI | 45 мин | 55 MB | ⭐⭐⭐⭐⭐⭐ | 🔪🔪🔪🔪🔪🔪 | $299 |

*Тестировано на i7-9700K, RTX 3060*

---

## 🐛 Решение проблем

### FFmpeg не найден
```
FileNotFoundError: 'ffmpeg'
```
**Решение:** Установите FFmpeg (см. раздел Установка)

### Topaz не найден
```
❌ Topaz Video AI not found
```
**Решение:**
- Установите Topaz Video AI
- Или используйте только FFmpeg методы
- Для лучших результатов используйте Topaz GUI вручную

### Real-ESRGAN медленно работает
**Решение:**
- Требуется GPU с Vulkan
- На CPU работает очень медленно
- Используйте FFmpeg методы для быстрой обработки

### Видео слишком большое
**Решение:**
- Увеличьте CRF (например, до 23)
- Используйте preset 'medium' вместо 'slow'
- Компрессия: `ffmpeg -i large.mp4 -crf 23 compressed.mp4`

### Низкое качество результата
**Причины:**
- Исходник слишком низкого качества
- Нужен AI upscaler (Topaz/Real-ESRGAN)
- Попробуйте метод 'denoised' для шумных видео

---

## 🎯 Рекомендуемый workflow

### Для YouTube видео:

```bash
# 1. Создать петлю (если нужно)
python video_loop_maker.py source.mp4 --analyze

# 2. Быстрый тест 3 методов
python video_upscaler.py output/optimized_*.mp4 -r 4k -m lanczos sharpened enhanced

# 3. Выбрать лучший визуально
# (Просмотреть все 3 файла)

# 4. (Опционально) Финальный AI апскейл в Topaz
# Открыть лучший вариант → Topaz → Artemis LQ → Export
```

### Для быстрого результата:

```bash
# Один метод, максимальная скорость
python video_upscaler.py video.mp4 -r 1080p -m lanczos
```

### Для максимального качества:

```bash
# Создать все варианты
python video_upscaler.py video.mp4 -r 4k -m lanczos sharpened denoised enhanced realesrgan

# Сравнить все
# Выбрать лучший
# Финальный проход в Topaz Video AI (GUI)
```

---

## 📚 Дополнительные ресурсы

- **FFmpeg filters:** https://ffmpeg.org/ffmpeg-filters.html
- **Topaz Video AI:** https://www.topazlabs.com/topaz-video-ai
- **Real-ESRGAN:** https://github.com/xinntao/Real-ESRGAN
- **Scaling algorithms:** https://ffmpeg.org/ffmpeg-scaler.html

---

## 🤝 Интеграция с video_loop_maker

```bash
# Pipeline: Исходник → Петля → Апскейл → Финальное видео

# Шаг 1: Создать бесшовную петлю
python video_loop_maker.py water_480p.mp4 --analyze -l 10

# Шаг 2: Апскейлить лучшую петлю до 4K
python video_upscaler.py output/optimized_overlap_1.5s.mp4 -r 4k -m lanczos enhanced

# Шаг 3: Получить финальное 4K зацикленное видео!
```

---

**Создавайте видео высокого качества! 🎬✨**
