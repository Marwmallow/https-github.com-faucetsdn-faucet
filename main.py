#!/usr/bin/env python3
"""
YouTube Content Automation System
Главный файл для запуска системы
"""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

from content_generator.script_generator import ScriptGenerator
from content_generator.quality_randomizer import QualityRandomizer
from video_processor.video_creator import VideoCreator
from youtube_api.uploader import YouTubeUploader, VideoMetadata
from scheduler.content_scheduler import ContentScheduler

console = Console()


@click.group()
def cli():
    """🎬 YouTube Content Automation System"""
    pass


@cli.command()
@click.option('--topic', '-t', required=True, help='Тема видео')
@click.option('--type', '-y', default='tutorial', help='Тип видео (tutorial, review, listicle)')
@click.option('--duration', '-d', default=300, help='Длительность в секундах')
@click.option('--quality', '-q', default='random', help='Качество (low, medium, high, random)')
def generate(topic, type, duration, quality):
    """Генерация скрипта для видео"""
    console.print(f"\n[bold cyan]🎯 Генерация скрипта[/bold cyan]\n")

    generator = ScriptGenerator()
    script = generator.generate_script(
        topic=topic,
        video_type=type,
        duration=duration,
        quality_level=quality
    )

    console.print(f"[green]✓[/green] Заголовок: {script.title}")
    console.print(f"[green]✓[/green] Длительность: ~{script.duration_estimate}с")
    console.print(f"[green]✓[/green] Теги: {', '.join(script.tags[:5])}")
    console.print(f"\n[yellow]Описание:[/yellow]\n{script.description}")
    console.print(f"\n[yellow]Скрипт:[/yellow]\n{script.script[:200]}...")


@cli.command()
@click.option('--base-quality', '-q', default='medium', help='Базовое качество (low, medium, high)')
@click.option('--variance', '-v', default=0.3, help='Вариативность (0.0-1.0)')
@click.option('--count', '-c', default=1, help='Количество профилей')
def quality(base_quality, variance, count):
    """Генерация профилей качества"""
    console.print(f"\n[bold cyan]🎲 Генерация профилей качества[/bold cyan]\n")

    randomizer = QualityRandomizer(base_quality=base_quality, variance=variance)
    profiles = randomizer.get_batch_profiles(count)

    table = Table(title=f"Профили качества (base: {base_quality}, variance: {variance})")
    table.add_column("#", style="cyan")
    table.add_column("Разрешение")
    table.add_column("FPS")
    table.add_column("Битрейт")
    table.add_column("Аудио")
    table.add_column("Теги")

    for i, profile in enumerate(profiles, 1):
        table.add_row(
            str(i),
            profile.resolution,
            str(profile.fps),
            profile.bitrate,
            profile.audio_quality,
            str(profile.tags_count)
        )

    console.print(table)


@cli.command()
@click.option('--topic', '-t', required=True, help='Тема видео')
@click.option('--type', '-y', default='tutorial', help='Тип видео')
@click.option('--count', '-c', default=5, help='Количество задач')
@click.option('--days', '-d', default=7, help='Распределить на N дней')
def schedule(topic, type, count, days):
    """Запланировать создание контента"""
    console.print(f"\n[bold cyan]📅 Планирование задач[/bold cyan]\n")

    scheduler = ContentScheduler()

    if count == 1:
        task = scheduler.add_task(topic=topic, video_type=type)
        console.print(f"[green]✓[/green] Создана задача: {task.task_id}")
        console.print(f"[yellow]  Запланирована на:[/yellow] {task.scheduled_time}")
    else:
        topics = [f"{topic} - Часть {i+1}" for i in range(count)]
        tasks = scheduler.add_batch_tasks(
            topics=topics,
            video_type=type,
            spread_days=days,
            tasks_per_day=max(1, count // days)
        )
        console.print(f"[green]✓[/green] Создано задач: {len(tasks)}")

        table = Table(title="Запланированные задачи")
        table.add_column("Тема", style="cyan")
        table.add_column("Время публикации")

        for task in tasks[:10]:  # Показываем первые 10
            table.add_row(task.topic, task.scheduled_time[:16])

        console.print(table)


@cli.command()
@click.option('--hours', '-h', default=24, help='Показать на N часов вперёд')
def upcoming(hours):
    """Показать предстоящие задачи"""
    console.print(f"\n[bold cyan]📋 Предстоящие задачи ({hours}ч)[/bold cyan]\n")

    scheduler = ContentScheduler()
    tasks = scheduler.get_upcoming_tasks(hours=hours)

    if not tasks:
        console.print("[yellow]Нет запланированных задач[/yellow]")
        return

    table = Table()
    table.add_column("#", style="cyan")
    table.add_column("Тема")
    table.add_column("Тип")
    table.add_column("Время")
    table.add_column("Статус")

    for i, task in enumerate(tasks, 1):
        status_color = {
            "pending": "yellow",
            "in_progress": "blue",
            "completed": "green",
            "failed": "red"
        }.get(task.status, "white")

        table.add_row(
            str(i),
            task.topic,
            task.video_type,
            task.scheduled_time[:16],
            f"[{status_color}]{task.status}[/{status_color}]"
        )

    console.print(table)


@cli.command()
def stats():
    """Показать статистику"""
    scheduler = ContentScheduler()
    stats = scheduler.get_statistics()

    console.print(Panel.fit(
        f"""
[bold cyan]📊 Статистика[/bold cyan]

Всего задач: [cyan]{stats['total']}[/cyan]
Ожидают: [yellow]{stats['pending']}[/yellow]
Завершено: [green]{stats['completed']}[/green]
Ошибки: [red]{stats['failed']}[/red]
Успешность: [cyan]{stats['success_rate']:.1f}%[/cyan]
        """.strip()
    ))


@cli.command()
@click.option('--topic', '-t', required=True, help='Тема видео')
@click.option('--output', '-o', default='./output', help='Директория для сохранения')
def create(topic, output):
    """Создать видео (генерация + рендеринг)"""
    console.print(f"\n[bold cyan]🎬 Создание видео[/bold cyan]\n")

    # 1. Генерация скрипта
    console.print("[yellow]1/3[/yellow] Генерация скрипта...")
    generator = ScriptGenerator()
    script = generator.generate_script(topic=topic, quality_level="random")
    console.print(f"[green]✓[/green] Скрипт создан: {script.title}")

    # 2. Генерация профиля качества
    console.print("\n[yellow]2/3[/yellow] Генерация профиля качества...")
    randomizer = QualityRandomizer(base_quality="medium", variance=0.3)
    quality_profile = randomizer.generate_profile()
    console.print(f"[green]✓[/green] Качество: {quality_profile.resolution} @ {quality_profile.fps}fps")

    # 3. Создание видео
    console.print("\n[yellow]3/3[/yellow] Создание видео...")
    creator = VideoCreator(output_dir=output)
    config = creator.apply_quality_profile(quality_profile)
    video_path = creator.create_video_from_script(
        script=script.script,
        title=script.title,
        config=config
    )
    console.print(f"[green]✓[/green] Видео создано: {video_path}")

    console.print(f"\n[bold green]🎉 Готово![/bold green]")


@cli.command()
def auth():
    """Авторизация в YouTube API"""
    console.print(f"\n[bold cyan]🔑 Авторизация YouTube API[/bold cyan]\n")

    uploader = YouTubeUploader()
    if uploader.authenticate():
        console.print("[green]✓ Авторизация успешна![/green]")
    else:
        console.print("[red]✗ Ошибка авторизации[/red]")


@cli.command()
@click.option('--video', '-v', required=True, help='Путь к видео')
@click.option('--title', '-t', required=True, help='Заголовок')
@click.option('--description', '-d', default='', help='Описание')
def upload(video, title, description):
    """Загрузить видео на YouTube"""
    console.print(f"\n[bold cyan]📤 Загрузка на YouTube[/bold cyan]\n")

    uploader = YouTubeUploader()
    if not uploader.authenticate():
        return

    metadata = VideoMetadata(
        title=title,
        description=description,
        tags=["youtube", "automation"],
        privacy_status="public"
    )

    result = uploader.upload_video(video, metadata)
    if result:
        console.print(f"[green]✓ Видео загружено![/green]")
        console.print(f"[cyan]URL:[/cyan] {result['url']}")


if __name__ == '__main__':
    console.print("""
[bold cyan]
╔══════════════════════════════════════════╗
║  YouTube Content Automation System  ║
║  Система автоматизации контента     ║
╚══════════════════════════════════════════╝
[/bold cyan]
""")
    cli()
