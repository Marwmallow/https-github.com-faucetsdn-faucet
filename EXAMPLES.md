# 📚 Примеры использования Video Loop Maker

## 🌊 Пример 1: Водопад для YouTube

**Задача:** Создать 1-часовое видео водопада для релаксации

**Исходник:** `waterfall.mp4` (8 секунд)

```bash
# Шаг 1: Найти оптимальное перекрытие
python3 video_loop_maker.py waterfall.mp4 --analyze -l 20

# Результат: ~2.5 минуты зацикленного видео

# Шаг 2: Посмотреть какое перекрытие получилось лучшим
# Допустим, скрипт создал optimized_overlap_1.5s.mp4

# Шаг 3: Растянуть до 1 часа через FFmpeg
ffmpeg -stream_loop 25 -i output/optimized_overlap_1.5s.mp4 \
       -c copy waterfall_1hour.mp4
```

**Совет:** Добавьте фоновые звуки воды через аудиоредактор!

---

## 🔥 Пример 2: Камин для Zoom фона

**Задача:** Создать короткую (2-3 минуты) бесшовную петлю огня

**Исходник:** `fireplace.mp4` (6 секунд)

```bash
# Огонь имеет хаотичное движение - используем короткие перекрытия
python3 video_loop_maker.py fireplace.mp4 -o 0.5 0.7 1.0 1.2 -l 30

# Получим 4 варианта, каждый ~3 минуты
# Выбираем лучший визуально!
```

**Совет:** Короткие crossfade (0.5-1.0s) лучше для быстрого движения!

---

## ☁️ Пример 3: Плывущие облака

**Задача:** Timelapse облаков с идеальной петлей

**Исходник:** `clouds_timelapse.mp4` (15 секунд)

```bash
# Облака движутся медленно - нужны длинные перекрытия
python3 video_loop_maker.py clouds_timelapse.mp4 \
    -o 2.0 3.0 4.0 5.0 -l 10
```

**Совет:** Для медленного движения используйте длинные crossfade (2-5s)!

---

## 🎨 Пример 4: VJ Loop для концерта

**Задача:** Создать короткую (30 сек) идеальную петлю для VJ

**Исходник:** `abstract_motion.mp4` (10 секунд)

```bash
# VJ loops должны быть ИДЕАЛЬНО бесшовными
python3 video_loop_maker.py abstract_motion.mp4 --analyze -l 3

# Если анализ не дал идеального результата, пробуем вручную:
python3 video_loop_maker.py abstract_motion.mp4 \
    -o 0.3 0.5 0.8 1.0 1.3 1.5 2.0 -l 3
```

**Совет:** Для VJ критична бесшовность - тестируйте ВСЕ варианты!

---

## 🏞️ Пример 5: Batch обработка коллекции природы

**Задача:** Обработать 50 клипов природы за один раз

**Структура:**
```
nature_clips/
├── waterfall_01.mp4
├── river_02.mp4
├── ocean_03.mp4
└── ... (еще 47 файлов)
```

```bash
# Автоматическая обработка всех файлов
./batch_process.sh nature_clips/

# Результат:
loops_output/
├── waterfall_01_loops/
│   ├── optimized_overlap_1.5s.mp4
│   ├── variant_1_overlap_1.0s.mp4
│   └── variant_2_overlap_2.0s.mp4
├── river_02_loops/
│   └── ...
└── ocean_03_loops/
    └── ...
```

**Совет:** Запустите на ночь - batch обработка может занять время!

---

## 📱 Пример 6: Instagram Story Background

**Задача:** Короткая (15 сек) петля для Instagram Stories

**Исходник:** `aesthetic_gradient.mp4` (5 секунд)

```bash
# Короткая петля, 3 повторения
python3 video_loop_maker.py aesthetic_gradient.mp4 --analyze -l 3

# Instagram Stories = 1080x1920 (вертикально)
# Обрежем и изменим размер после:
ffmpeg -i output/optimized_overlap_*.mp4 \
       -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
       -t 15 instagram_story_bg.mp4
```

---

## 🎮 Пример 7: Twitch Stream Overlay

**Задача:** Бесконечная анимация для наложения на стрим

**Исходник:** `particle_effect.mp4` (7 секунд)

```bash
# Создаем длинную петлю
python3 video_loop_maker.py particle_effect.mp4 --analyze -l 50

# Конвертируем в WebM с прозрачностью (если есть альфа-канал)
ffmpeg -i output/optimized_overlap_*.mp4 \
       -c:v libvpx-vp9 -pix_fmt yuva420p \
       stream_overlay.webm
```

---

## 🖼️ Пример 8: Digital Signage (8 часов)

**Задача:** Создать 8-часовое видео для рекламного экрана

**Исходник:** `brand_animation.mp4` (12 секунд)

```bash
# Шаг 1: Создать оптимальную петлю
python3 video_loop_maker.py brand_animation.mp4 --analyze -l 5

# Шаг 2: Рассчитать количество повторений
# 8 часов = 28800 секунд
# Если петля получилась 60 секунд:
# 28800 / 60 = 480 повторений

# Шаг 3: Создать 8-часовое видео
ffmpeg -stream_loop 480 -i output/optimized_overlap_*.mp4 \
       -c copy brand_animation_8hours.mp4
```

**Совет:** Для digital signage используйте высокое качество (CRF 18-20)!

---

## 🧘 Пример 9: Медитация с водой (10 часов)

**Задача:** Длинное видео для медитации/фокуса/сна

**Исходники:**
- `calm_water.mp4` (10 секунд)
- `nature_sounds.mp3` (5 минут аудио петли)

```bash
# Шаг 1: Создать длинную видео петлю
python3 video_loop_maker.py calm_water.mp4 --analyze -l 100

# Шаг 2: Зациклить аудио с crossfade
ffmpeg -stream_loop 120 -i nature_sounds.mp3 \
       -af "afade=t=in:d=3,afade=t=out:st=297:d=3" \
       nature_sounds_10h.mp3

# Шаг 3: Объединить видео и аудио
ffmpeg -i output/optimized_overlap_*.mp4 \
       -stream_loop 100 \
       -i nature_sounds_10h.mp3 \
       -c:v copy -c:a aac -shortest \
       meditation_10hours.mp4
```

---

## 🎬 Пример 10: Тестирование всех вариантов

**Задача:** Создать сравнительное видео всех вариантов

**Исходник:** `test_clip.mp4` (8 секунд)

```bash
# Создать много вариантов
python3 video_loop_maker.py test_clip.mp4 \
    -o 0.3 0.5 0.7 1.0 1.3 1.5 2.0 2.5 3.0 -l 5

# Создать grid видео для сравнения (требует 4 файла)
ffmpeg -i output/variant_1_overlap_0.5s.mp4 \
       -i output/variant_2_overlap_1.0s.mp4 \
       -i output/variant_3_overlap_1.5s.mp4 \
       -i output/variant_4_overlap_2.0s.mp4 \
       -filter_complex \
       "[0:v][1:v][2:v][3:v]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v]" \
       -map "[v]" comparison_grid.mp4
```

---

## 🚀 Продвинутые техники

### А. Автоматический выбор лучшего варианта

```python
# Добавьте в конец video_loop_maker.py:

def auto_select_best(output_dir: str) -> str:
    """Автоматически выбрать файл с наивысшим SSIM"""
    import re
    import glob

    files = glob.glob(f"{output_dir}/variant_*.mp4")

    best_file = None
    best_similarity = 0

    for file in files:
        # Извлечь overlap из имени файла
        match = re.search(r'overlap_([\d.]+)s', file)
        if match:
            overlap = float(match.group(1))
            # Анализировать этот файл
            # ... (код анализа)

    return best_file
```

### Б. Создание GIF петли

```bash
# После создания петли конвертировать в GIF
python3 video_loop_maker.py animation.mp4 --analyze -l 3

ffmpeg -i output/optimized_overlap_*.mp4 \
       -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
       -loop 0 seamless_loop.gif
```

### В. Стабилизация перед петлей

```bash
# Если видео трясется - сначала стабилизировать

# Шаг 1: Анализ
ffmpeg -i shaky_video.mp4 -vf vidstabdetect -f null -

# Шаг 2: Стабилизация
ffmpeg -i shaky_video.mp4 \
       -vf vidstabtransform=smoothing=30 \
       stabilized_video.mp4

# Шаг 3: Создать петлю
python3 video_loop_maker.py stabilized_video.mp4 --analyze
```

---

## 💾 Оптимизация размера файла

### Для веба (маленький размер):

```bash
python3 video_loop_maker.py video.mp4 --analyze

# Сжать результат
ffmpeg -i output/optimized_overlap_*.mp4 \
       -c:v libx264 -crf 28 -preset slow \
       -vf "scale=1280:-2" \
       optimized_web.mp4
```

### Для качества (большой размер):

```bash
# Редактировать в скрипте:
# '-crf', '18',  # Высокое качество
# '-preset', 'veryslow',  # Лучшее сжатие
```

---

## 🎯 Чек-лист для идеальной петли

✅ Видео снято на штативе/gimbal
✅ Движение циклическое (вода, огонь, облака)
✅ Нет объектов входящих/выходящих из кадра
✅ Освещение постоянное
✅ Длина клипа минимум 5-6 секунд
✅ Использован режим `--analyze`
✅ Проверены все варианты визуально
✅ Выбрана оптимальная длина crossfade

---

**Больше примеров? Экспериментируйте! 🎨**

Поделитесь своими результатами и best practices!
