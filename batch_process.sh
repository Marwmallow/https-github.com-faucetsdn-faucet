#!/bin/bash

# Batch Video Loop Processor
# Обрабатывает все видео в папке и создает бесшовные петли

# Настройки
INPUT_DIR="${1:-.}"  # Папка с видео (по умолчанию текущая)
OUTPUT_BASE="loops_output"
USE_ANALYZE="${2:-yes}"  # Использовать анализ (yes/no)

echo "🎬 Batch Video Loop Processor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Input directory: $INPUT_DIR"
echo "Use analysis: $USE_ANALYZE"
echo ""

# Создать основную папку для вывода
mkdir -p "$OUTPUT_BASE"

# Счетчик
count=0
success=0

# Обработать все видео файлы
for video in "$INPUT_DIR"/*.{mp4,MP4,mov,MOV,avi,AVI,mkv,MKV} 2>/dev/null; do
    # Проверить что файл существует (glob может не совпасть)
    [ -e "$video" ] || continue

    count=$((count + 1))
    filename=$(basename "$video")
    name="${filename%.*}"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[$count] Processing: $filename"
    echo ""

    # Создать папку для этого видео
    output_dir="$OUTPUT_BASE/${name}_loops"
    mkdir -p "$output_dir"

    # Запустить скрипт
    if [ "$USE_ANALYZE" = "yes" ]; then
        python3 video_loop_maker.py "$video" --analyze -d "$output_dir" -l 3
    else
        python3 video_loop_maker.py "$video" -d "$output_dir" -l 3
    fi

    # Проверить успех
    if [ $? -eq 0 ]; then
        echo "✅ Success: $filename"
        success=$((success + 1))
    else
        echo "❌ Failed: $filename"
    fi

    echo ""
done

# Итоги
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "  Total processed: $count"
echo "  Successful: $success"
echo "  Failed: $((count - success))"
echo ""
echo "📁 Output directory: $OUTPUT_BASE/"
echo ""
echo "✨ Done!"
