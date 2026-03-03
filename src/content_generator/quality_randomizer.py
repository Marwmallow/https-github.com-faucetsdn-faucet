"""
Рандомизатор качества контента
Создаёт вариативность для избежания паттернов
"""

import random
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class QualityProfile:
    """Профиль качества контента"""
    resolution: str  # 720p, 1080p, 4k
    fps: int  # 24, 30, 60
    bitrate: str  # low, medium, high
    audio_quality: str  # low, medium, high
    thumbnail_quality: str  # basic, good, excellent
    description_length: str  # short, medium, long
    tags_count: int
    title_style: str  # simple, engaging, clickbait


class QualityRandomizer:
    """Генератор случайных профилей качества"""

    # Предустановленные профили
    PROFILES = {
        "low": {
            "resolution": ["720p"],
            "fps": [24, 30],
            "bitrate": ["low", "medium"],
            "audio_quality": ["low", "medium"],
            "thumbnail_quality": ["basic", "good"],
            "description_length": ["short", "medium"],
            "tags_count": range(5, 10),
            "title_style": ["simple", "engaging"],
        },
        "medium": {
            "resolution": ["720p", "1080p"],
            "fps": [30, 60],
            "bitrate": ["medium", "high"],
            "audio_quality": ["medium", "high"],
            "thumbnail_quality": ["good", "excellent"],
            "description_length": ["medium", "long"],
            "tags_count": range(10, 20),
            "title_style": ["engaging", "clickbait"],
        },
        "high": {
            "resolution": ["1080p", "4k"],
            "fps": [60],
            "bitrate": ["high"],
            "audio_quality": ["high"],
            "thumbnail_quality": ["excellent"],
            "description_length": ["long"],
            "tags_count": range(15, 25),
            "title_style": ["engaging"],
        },
    }

    def __init__(self, base_quality: str = "medium", variance: float = 0.3):
        """
        Args:
            base_quality: Базовый уровень качества (low, medium, high)
            variance: Степень вариативности (0.0 - 1.0)
        """
        self.base_quality = base_quality
        self.variance = variance

    def generate_profile(self, force_random: bool = False) -> QualityProfile:
        """
        Генерация профиля качества

        Args:
            force_random: Полностью случайный профиль

        Returns:
            QualityProfile
        """
        if force_random:
            # Полностью случайный выбор из всех возможных опций
            all_options = self._get_all_options()
        else:
            # Выбор с учётом базового качества и вариативности
            all_options = self._get_varied_options()

        return QualityProfile(
            resolution=random.choice(all_options["resolution"]),
            fps=random.choice(all_options["fps"]),
            bitrate=random.choice(all_options["bitrate"]),
            audio_quality=random.choice(all_options["audio_quality"]),
            thumbnail_quality=random.choice(all_options["thumbnail_quality"]),
            description_length=random.choice(all_options["description_length"]),
            tags_count=random.choice(list(all_options["tags_count"])),
            title_style=random.choice(all_options["title_style"]),
        )

    def _get_all_options(self) -> Dict[str, Any]:
        """Получить все возможные опции"""
        return {
            "resolution": ["720p", "1080p", "4k"],
            "fps": [24, 30, 60],
            "bitrate": ["low", "medium", "high"],
            "audio_quality": ["low", "medium", "high"],
            "thumbnail_quality": ["basic", "good", "excellent"],
            "description_length": ["short", "medium", "long"],
            "tags_count": range(5, 30),
            "title_style": ["simple", "engaging", "clickbait"],
        }

    def _get_varied_options(self) -> Dict[str, Any]:
        """Получить опции с учётом вариативности"""
        base_profile = self.PROFILES[self.base_quality]

        # Если высокая вариативность, добавляем опции из соседних профилей
        if self.variance > 0.5:
            profiles_to_mix = list(self.PROFILES.keys())
        elif self.variance > 0.2:
            # Смешиваем с соседними уровнями
            quality_levels = ["low", "medium", "high"]
            current_idx = quality_levels.index(self.base_quality)
            profiles_to_mix = [
                quality_levels[max(0, current_idx - 1)],
                self.base_quality,
                quality_levels[min(2, current_idx + 1)],
            ]
        else:
            profiles_to_mix = [self.base_quality]

        # Объединяем опции
        mixed_options = {}
        for key in base_profile.keys():
            mixed_options[key] = []
            for profile_name in profiles_to_mix:
                options = self.PROFILES[profile_name][key]
                if isinstance(options, range):
                    mixed_options[key] = options
                else:
                    mixed_options[key].extend(options)

            # Убираем дубликаты
            if not isinstance(mixed_options[key], range):
                mixed_options[key] = list(set(mixed_options[key]))

        return mixed_options

    def get_batch_profiles(self, count: int) -> list[QualityProfile]:
        """
        Генерация батча профилей для серии видео

        Args:
            count: Количество профилей

        Returns:
            Список QualityProfile
        """
        profiles = []
        for _ in range(count):
            # Для каждого видео немного меняем вариативность
            varied_randomizer = QualityRandomizer(
                self.base_quality,
                variance=self.variance + random.uniform(-0.1, 0.1)
            )
            profiles.append(varied_randomizer.generate_profile())

        return profiles


def randomize_upload_schedule() -> Dict[str, Any]:
    """Рандомизация расписания публикаций"""
    return {
        "hour": random.randint(9, 21),  # 9 утра - 9 вечера
        "minute": random.randint(0, 59),
        "day_of_week": random.randint(0, 6),  # 0 = понедельник
        "interval_days": random.choice([1, 2, 3, 7]),  # Интервал между публикациями
    }


if __name__ == "__main__":
    # Примеры использования
    print("=== Пример 1: Средний уровень качества ===")
    randomizer = QualityRandomizer(base_quality="medium", variance=0.3)
    profile = randomizer.generate_profile()
    print(f"Разрешение: {profile.resolution}")
    print(f"FPS: {profile.fps}")
    print(f"Битрейт: {profile.bitrate}")
    print(f"Теги: {profile.tags_count}")

    print("\n=== Пример 2: Батч профилей ===")
    batch = randomizer.get_batch_profiles(3)
    for i, p in enumerate(batch, 1):
        print(f"Профиль {i}: {p.resolution} @ {p.fps}fps, {p.bitrate} bitrate")

    print("\n=== Пример 3: Расписание ===")
    schedule = randomize_upload_schedule()
    print(f"Публикация: {schedule['hour']}:{schedule['minute']:02d}, каждые {schedule['interval_days']} дня")
