# ⚡ Video Upscaler - Quick Start

## 1️⃣ Установка FFmpeg

### Windows:
```bash
# Скачать с https://ffmpeg.org/download.html
# Или через Chocolatey:
choco install ffmpeg
```

### Mac/Linux:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg -y
```

Проверка:
```bash
ffmpeg -version
```

---

## 2️⃣ Базовое использование

### Создать 5 вариантов апскейла (1080p):

```bash
python video_upscaler.py your_video.mp4
```

**Результат в папке `upscaled/`:**
- `lanczos_1080p.mp4` ← Рекомендуется для большинства
- `bicubic_1080p.mp4` ← Для шумных видео
- `sharpened_1080p.mp4` ← Максимальная резкость
- `denoised_1080p.mp4` ← Для старых видео
- `enhanced_1080p.mp4` ← Яркие цвета

### Апскейл до 4K:

```bash
python video_upscaler.py your_video.mp4 -r 4k
```

---

## 3️⃣ Быстрый выбор метода

**По типу видео:**

```bash
# Обычное видео → Lanczos (универсальный)
python video_upscaler.py video.mp4 -m lanczos

# Старое/шумное → Denoised
python video_upscaler.py old.mp4 -m denoised

# Природа/пейзажи → Enhanced (яркие цвета)
python video_upscaler.py nature.mp4 -m enhanced

# Нужна резкость → Sharpened
python video_upscaler.py soft.mp4 -m sharpened
```

---

## 4️⃣ С Topaz Video AI (если установлен)

```bash
# Лучшее AI качество
python video_upscaler.py video.mp4 -m topaz -r 4k
```

**Или используйте Topaz GUI вручную:**
1. Откройте Topaz Video AI
2. Перетащите ваше видео
3. Model: **Artemis LQ** (для YouTube/сжатых видео)
4. Output: 4K
5. Export

---

## 5️⃣ Полный Pipeline (Петля + Апскейл)

```bash
# Шаг 1: Создать бесшовную петлю
python video_loop_maker.py water.mp4 --analyze

# Шаг 2: Апскейлить лучшую петлю
python video_upscaler.py output/optimized_overlap_1.5s.mp4 -r 4k -m lanczos enhanced

# Шаг 3: Выбрать лучший вариант визуально!
```

---

## 📊 Сравнение методов

| Метод | Скорость | Качество | Когда использовать |
|-------|----------|----------|-------------------|
| **lanczos** | ⚡⚡⚡ | ⭐⭐⭐⭐ | Универсально (начните с этого) |
| **bicubic** | ⚡⚡⚡ | ⭐⭐⭐ | Шумные/сжатые видео |
| **sharpened** | ⚡⚡ | ⭐⭐⭐⭐ | Нужна резкость |
| **denoised** | ⚡⚡ | ⭐⭐⭐⭐ | Старое видео с зерном |
| **enhanced** | ⚡⚡ | ⭐⭐⭐⭐ | Природа, яркие цвета |
| **topaz** | ⚡ | ⭐⭐⭐⭐⭐⭐ | Максимальное качество |

---

## 💡 Частые случаи

### YouTube видео 720p → 4K:
```bash
python video_upscaler.py youtube.mp4 -r 4k -m lanczos denoised enhanced
# Выбрать лучший из 3 вариантов
```

### Вертикальное для Instagram/TikTok:
```bash
# Сначала апскейл
python video_upscaler.py video.mp4 -r 1080p -m lanczos

# Потом crop в вертикальный формат
ffmpeg -i upscaled/lanczos_1080p.mp4 \
  -vf "crop=1080:1920" \
  vertical_1080x1920.mp4
```

### Batch обработка папки:
```bash
# Windows
for %f in (*.mp4) do python video_upscaler.py "%f" -r 1080p -m lanczos

# Mac/Linux
for file in *.mp4; do python video_upscaler.py "$file" -r 1080p -m lanczos; done
```

---

## 🎯 Рекомендуемый Workflow

1. **Быстрый тест** - создайте один вариант:
   ```bash
   python video_upscaler.py video.mp4 -m lanczos
   ```

2. **Если не устраивает** - создайте все варианты:
   ```bash
   python video_upscaler.py video.mp4
   ```

3. **Сравните все** и выберите лучший визуально

4. **Для финального качества** - используйте Topaz Video AI (GUI)

---

## ⚠️ Важно

✅ **FFmpeg работает всегда** (бесплатно, быстро)
✅ **Topaz дает лучшее качество** (платно, медленно)
✅ **Создавайте несколько вариантов** и выбирайте лучший
✅ **Lanczos - хороший старт** для 90% случаев

---

## 🆘 Проблемы?

**FFmpeg не найден:**
```bash
# Установите FFmpeg (см. шаг 1)
ffmpeg -version
```

**Медленно работает:**
```bash
# Используйте только один метод
python video_upscaler.py video.mp4 -m lanczos
```

**Низкое качество:**
- Попробуйте другие методы
- Используйте Topaz Video AI для AI апскейла

---

## 📖 Полная документация

См. **README_UPSCALER.md** для детальной информации о всех методах!

---

**Создавайте видео высокого качества! 🎬✨**
