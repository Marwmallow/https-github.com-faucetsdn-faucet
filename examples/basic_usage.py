"""
Базовые примеры использования системы
"""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from content_generator.script_generator import ScriptGenerator, quick_generate
from content_generator.quality_randomizer import QualityRandomizer, randomize_upload_schedule
from video_processor.video_creator import VideoCreator
from youtube_api.uploader import YouTubeUploader, VideoMetadata
from scheduler.content_scheduler import ContentScheduler


def example_1_generate_script():
    """Пример 1: Генерация скрипта"""
    print("=" * 50)
    print("ПРИМЕР 1: Генерация скрипта")
    print("=" * 50)

    # Способ 1: Использование класса
    generator = ScriptGenerator()
    script = generator.generate_script(
        topic="Python для начинающих",
        video_type="tutorial",
        duration=300,
        quality_level="high"
    )

    print(f"Заголовок: {script.title}")
    print(f"Теги: {', '.join(script.tags)}")
    print(f"Длительность: {script.duration_estimate}с")

    # Способ 2: Быстрая генерация
    quick_script = quick_generate("Django Tutorial", video_type="tutorial")
    print(f"\nБыстрая генерация: {quick_script.title}")


def example_2_quality_profiles():
    """Пример 2: Работа с профилями качества"""
    print("\n" + "=" * 50)
    print("ПРИМЕР 2: Профили качества")
    print("=" * 50)

    # Создание рандомизатора
    randomizer = QualityRandomizer(base_quality="medium", variance=0.3)

    # Генерация одного профиля
    profile = randomizer.generate_profile()
    print(f"Разрешение: {profile.resolution}")
    print(f"FPS: {profile.fps}")
    print(f"Битрейт: {profile.bitrate}")
    print(f"Теги: {profile.tags_count}")

    # Генерация батча профилей
    print("\nБатч профилей:")
    batch = randomizer.get_batch_profiles(5)
    for i, p in enumerate(batch, 1):
        print(f"{i}. {p.resolution} @ {p.fps}fps, bitrate: {p.bitrate}")

    # Полностью случайный профиль
    random_profile = randomizer.generate_profile(force_random=True)
    print(f"\nСлучайный: {random_profile.resolution} @ {random_profile.fps}fps")


def example_3_schedule_content():
    """Пример 3: Планирование контента"""
    print("\n" + "=" * 50)
    print("ПРИМЕР 3: Планирование контента")
    print("=" * 50)

    scheduler = ContentScheduler()

    # Добавление одной задачи
    task = scheduler.add_task(
        topic="Python основы",
        video_type="tutorial"
    )
    print(f"Создана задача: {task.task_id}")
    print(f"Запланирована на: {task.scheduled_time}")

    # Добавление серии задач
    topics = [
        "Python - Введение",
        "Python - Переменные",
        "Python - Условия",
        "Python - Циклы",
        "Python - Функции",
    ]

    batch_tasks = scheduler.add_batch_tasks(
        topics=topics,
        video_type="tutorial",
        spread_days=7,
        tasks_per_day=1
    )
    print(f"\nСоздано задач: {len(batch_tasks)}")

    # Просмотр предстоящих задач
    upcoming = scheduler.get_upcoming_tasks(hours=168)  # 7 дней
    print(f"\nПредстоящие задачи ({len(upcoming)}):")
    for task in upcoming[:5]:
        print(f"- {task.topic} ({task.scheduled_time[:10]})")

    # Статистика
    stats = scheduler.get_statistics()
    print(f"\nСтатистика:")
    print(f"Всего: {stats['total']}, Ожидают: {stats['pending']}")


def example_4_create_video():
    """Пример 4: Создание видео"""
    print("\n" + "=" * 50)
    print("ПРИМЕР 4: Создание видео")
    print("=" * 50)

    # 1. Генерация скрипта
    generator = ScriptGenerator()
    script = generator.generate_script(
        topic="FastAPI Tutorial",
        video_type="tutorial",
        quality_level="random"
    )
    print(f"1. Скрипт создан: {script.title}")

    # 2. Генерация профиля качества
    randomizer = QualityRandomizer(base_quality="medium", variance=0.3)
    profile = randomizer.generate_profile()
    print(f"2. Профиль: {profile.resolution} @ {profile.fps}fps")

    # 3. Создание видео
    creator = VideoCreator(output_dir="./output")
    config = creator.apply_quality_profile(profile)

    video_path = creator.create_video_from_script(
        script=script.script,
        title=script.title,
        config=config
    )
    print(f"3. Видео: {video_path}")

    # 4. Создание миниатюры
    thumbnail_path = creator.create_thumbnail(
        video_path=video_path,
        title=script.title,
        quality=profile.thumbnail_quality
    )
    print(f"4. Миниатюра: {thumbnail_path}")


def example_5_upload_workflow():
    """Пример 5: Процесс загрузки"""
    print("\n" + "=" * 50)
    print("ПРИМЕР 5: Загрузка на YouTube")
    print("=" * 50)

    uploader = YouTubeUploader()

    # Аутентификация
    if uploader.authenticate():
        print("✓ Аутентификация успешна")

        # Подготовка метаданных
        metadata = VideoMetadata(
            title="Python Tutorial - Основы",
            description="""
Полное руководство по Python для начинающих.

🎯 Что вы узнаете:
- Основы синтаксиса
- Переменные и типы
- Условия и циклы

👍 Подписывайтесь!

#python #programming #tutorial
            """.strip(),
            tags=["python", "tutorial", "programming", "coding", "beginners"],
            category_id=YouTubeUploader.CATEGORIES["education"],
            privacy_status="public"
        )

        # Загрузка (в demo режиме)
        result = uploader.upload_video(
            video_path="./output/test_video.mp4",
            metadata=metadata
        )

        if result:
            print(f"✓ Видео загружено: {result['id']}")
            print(f"  URL: {result['url']}")

        # Проверка квоты
        quota = uploader.get_upload_quota_usage()
        print(f"\nКвота: {quota['remaining']}/{quota['daily_limit']}")
        print(f"Можно загрузить сегодня: {quota['videos_uploadable_today']} видео")


def example_6_full_automation():
    """Пример 6: Полная автоматизация"""
    print("\n" + "=" * 50)
    print("ПРИМЕР 6: Полная автоматизация")
    print("=" * 50)

    # 1. Планирование серии видео
    scheduler = ContentScheduler()
    topics = [
        "Python - Установка",
        "Python - Первая программа",
        "Python - Переменные",
    ]

    tasks = scheduler.add_batch_tasks(
        topics=topics,
        spread_days=3,
        tasks_per_day=1
    )
    print(f"Запланировано: {len(tasks)} задач")

    # 2. Обработка задач
    pending = scheduler.get_pending_tasks()
    print(f"К выполнению: {len(pending)} задач")

    for task in pending[:1]:  # Обрабатываем первую задачу
        print(f"\nОбработка: {task.topic}")

        # Генерация
        generator = ScriptGenerator()
        script = generator.generate_script(
            topic=task.topic,
            video_type=task.video_type,
            quality_level="random"
        )

        # Создание видео
        randomizer = QualityRandomizer()
        profile = randomizer.generate_profile()

        creator = VideoCreator()
        config = creator.apply_quality_profile(profile)
        video_path = creator.create_video_from_script(
            script=script.script,
            title=script.title,
            config=config
        )

        # Обновление статуса
        scheduler.update_task_status(
            task_id=task.task_id,
            status="completed",
            video_path=video_path
        )
        print(f"✓ Задача выполнена: {task.task_id}")

    # 3. Статистика
    stats = scheduler.get_statistics()
    print(f"\nИтоговая статистика:")
    print(f"Завершено: {stats['completed']}/{stats['total']}")
    print(f"Успешность: {stats['success_rate']:.1f}%")


def example_7_randomization():
    """Пример 7: Рандомизация для избежания паттернов"""
    print("\n" + "=" * 50)
    print("ПРИМЕР 7: Рандомизация")
    print("=" * 50)

    # Разная вариативность
    variances = [0.1, 0.3, 0.5, 0.8]

    for variance in variances:
        print(f"\nВариативность: {variance}")
        randomizer = QualityRandomizer(base_quality="medium", variance=variance)
        profiles = randomizer.get_batch_profiles(3)

        for p in profiles:
            print(f"  {p.resolution} @ {p.fps}fps, {p.bitrate}")

    # Расписание публикаций
    print("\nСлучайные расписания:")
    for i in range(5):
        schedule = randomize_upload_schedule()
        print(f"{i+1}. {schedule['hour']}:{schedule['minute']:02d}, "
              f"каждые {schedule['interval_days']} дня")


if __name__ == "__main__":
    print("\n🎬 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ YOUTUBE AUTOMATION\n")

    # Запуск всех примеров
    example_1_generate_script()
    example_2_quality_profiles()
    example_3_schedule_content()
    example_4_create_video()
    example_5_upload_workflow()
    example_6_full_automation()
    example_7_randomization()

    print("\n" + "=" * 50)
    print("✅ Все примеры выполнены!")
    print("=" * 50)
