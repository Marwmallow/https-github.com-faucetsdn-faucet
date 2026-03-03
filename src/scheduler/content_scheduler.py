"""
Планировщик создания и публикации контента
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import random


@dataclass
class ScheduledTask:
    """Запланированная задача"""
    task_id: str
    task_type: str  # generate, upload, both
    topic: str
    video_type: str
    scheduled_time: str  # ISO format
    quality_profile: Optional[Dict] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: str = None
    video_path: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class ContentScheduler:
    """Планировщик контента"""

    def __init__(self, schedule_file: str = "config/schedule.json"):
        """
        Args:
            schedule_file: Файл для хранения расписания
        """
        self.schedule_file = Path(schedule_file)
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: List[ScheduledTask] = []
        self._load_schedule()

    def _load_schedule(self):
        """Загрузка расписания из файла"""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [ScheduledTask(**task) for task in data]
        else:
            self.tasks = []

    def _save_schedule(self):
        """Сохранение расписания в файл"""
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(task) for task in self.tasks], f, indent=2, ensure_ascii=False)

    def add_task(
        self,
        topic: str,
        video_type: str = "tutorial",
        scheduled_time: Optional[datetime] = None,
        task_type: str = "both"
    ) -> ScheduledTask:
        """
        Добавить задачу в расписание

        Args:
            topic: Тема видео
            video_type: Тип видео
            scheduled_time: Время публикации (если None - случайное)
            task_type: Тип задачи (generate, upload, both)

        Returns:
            ScheduledTask
        """
        if scheduled_time is None:
            # Генерируем случайное время в ближайшие 7 дней
            days_ahead = random.randint(1, 7)
            hour = random.randint(9, 21)
            minute = random.randint(0, 59)
            scheduled_time = datetime.now() + timedelta(days=days_ahead)
            scheduled_time = scheduled_time.replace(hour=hour, minute=minute, second=0)

        task = ScheduledTask(
            task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}",
            task_type=task_type,
            topic=topic,
            video_type=video_type,
            scheduled_time=scheduled_time.isoformat(),
        )

        self.tasks.append(task)
        self._save_schedule()
        return task

    def add_batch_tasks(
        self,
        topics: List[str],
        video_type: str = "tutorial",
        spread_days: int = 7,
        tasks_per_day: int = 1
    ) -> List[ScheduledTask]:
        """
        Добавить батч задач с автоматическим распределением по времени

        Args:
            topics: Список тем
            video_type: Тип видео
            spread_days: Распределить на N дней
            tasks_per_day: Задач в день

        Returns:
            Список созданных задач
        """
        created_tasks = []
        current_time = datetime.now()

        for i, topic in enumerate(topics):
            day_offset = (i // tasks_per_day) % spread_days
            task_in_day = i % tasks_per_day

            # Распределяем задачи в течение дня
            hour = 9 + (task_in_day * (12 // max(tasks_per_day, 1)))  # С 9 до 21
            scheduled_time = current_time + timedelta(days=day_offset)
            scheduled_time = scheduled_time.replace(
                hour=hour + random.randint(0, 2),
                minute=random.randint(0, 59),
                second=0
            )

            task = self.add_task(topic, video_type, scheduled_time)
            created_tasks.append(task)

        return created_tasks

    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Получить задачи готовые к выполнению"""
        now = datetime.now()
        pending = []

        for task in self.tasks:
            if task.status == "pending":
                task_time = datetime.fromisoformat(task.scheduled_time)
                if task_time <= now:
                    pending.append(task)

        return pending

    def get_upcoming_tasks(self, hours: int = 24) -> List[ScheduledTask]:
        """
        Получить задачи на ближайшее время

        Args:
            hours: Временной интервал в часах

        Returns:
            Список задач
        """
        now = datetime.now()
        future = now + timedelta(hours=hours)
        upcoming = []

        for task in self.tasks:
            if task.status == "pending":
                task_time = datetime.fromisoformat(task.scheduled_time)
                if now <= task_time <= future:
                    upcoming.append(task)

        return sorted(upcoming, key=lambda t: t.scheduled_time)

    def update_task_status(self, task_id: str, status: str, video_path: Optional[str] = None):
        """
        Обновить статус задачи

        Args:
            task_id: ID задачи
            status: Новый статус
            video_path: Путь к созданному видео (опционально)
        """
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = status
                if video_path:
                    task.video_path = video_path
                self._save_schedule()
                return

    def get_statistics(self) -> Dict:
        """Получить статистику по задачам"""
        total = len(self.tasks)
        pending = len([t for t in self.tasks if t.status == "pending"])
        completed = len([t for t in self.tasks if t.status == "completed"])
        failed = len([t for t in self.tasks if t.status == "failed"])

        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0,
        }

    def cleanup_old_tasks(self, days: int = 30):
        """
        Удалить старые завершённые задачи

        Args:
            days: Удалить задачи старше N дней
        """
        cutoff = datetime.now() - timedelta(days=days)
        self.tasks = [
            task for task in self.tasks
            if task.status != "completed" or
            datetime.fromisoformat(task.created_at) > cutoff
        ]
        self._save_schedule()


if __name__ == "__main__":
    # Пример использования
    scheduler = ContentScheduler()

    print("=== Добавление одной задачи ===")
    task = scheduler.add_task(
        topic="Python для начинающих",
        video_type="tutorial"
    )
    print(f"Создана задача: {task.task_id}")
    print(f"Запланирована на: {task.scheduled_time}")

    print("\n=== Добавление батча задач ===")
    topics = [
        "Установка Python",
        "Первая программа на Python",
        "Переменные и типы данных",
        "Условные операторы",
        "Циклы в Python",
    ]
    batch = scheduler.add_batch_tasks(
        topics=topics,
        spread_days=7,
        tasks_per_day=1
    )
    print(f"Создано задач: {len(batch)}")

    print("\n=== Предстоящие задачи (24 часа) ===")
    upcoming = scheduler.get_upcoming_tasks(hours=24)
    for task in upcoming:
        print(f"- {task.topic} ({task.scheduled_time})")

    print("\n=== Статистика ===")
    stats = scheduler.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
