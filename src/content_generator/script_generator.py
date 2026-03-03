"""
Генератор скриптов для видео
Поддерживает разные типы контента и AI-модели
"""

import os
import random
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class VideoScript:
    """Структура видео-скрипта"""
    title: str
    description: str
    script: str
    tags: List[str]
    category: str
    duration_estimate: int  # в секундах


class ScriptGenerator:
    """Генератор скриптов для видео"""

    def __init__(self, ai_provider: str = "openai"):
        """
        Args:
            ai_provider: Провайдер AI (openai, anthropic, local)
        """
        self.ai_provider = ai_provider
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Загрузка шаблонов контента"""
        return {
            "tutorial": "Обучающее видео о {topic}",
            "review": "Обзор {product}",
            "listicle": "ТОП {number} {topic}",
            "story": "История о {topic}",
            "news": "Новости: {topic}",
        }

    def generate_script(
        self,
        topic: str,
        video_type: str = "tutorial",
        duration: int = 300,
        quality_level: str = "high"
    ) -> VideoScript:
        """
        Генерация скрипта для видео

        Args:
            topic: Тема видео
            video_type: Тип видео (tutorial, review, listicle, etc.)
            duration: Желаемая длительность в секундах
            quality_level: Уровень качества (low, medium, high, random)

        Returns:
            VideoScript object
        """
        if quality_level == "random":
            quality_level = random.choice(["low", "medium", "high"])

        # Здесь можно интегрировать OpenAI/Claude API
        # Пока используем базовую генерацию
        template = self.templates.get(video_type, self.templates["tutorial"])

        title = self._generate_title(topic, video_type)
        description = self._generate_description(topic, video_type)
        script = self._generate_full_script(topic, video_type, duration, quality_level)
        tags = self._generate_tags(topic)

        return VideoScript(
            title=title,
            description=description,
            script=script,
            tags=tags,
            category=video_type,
            duration_estimate=duration
        )

    def _generate_title(self, topic: str, video_type: str) -> str:
        """Генерация заголовка"""
        prefixes = {
            "tutorial": ["Как", "Учимся", "Полное руководство:", "Пошаговое руководство:"],
            "review": ["Обзор:", "Детальный обзор:", "Честный обзор:"],
            "listicle": ["ТОП", "Лучшие", "5 способов"],
            "story": ["История:", "Рассказ о:", "Опыт:"],
            "news": ["Новости:", "Важно:", "Срочно:"],
        }

        prefix = random.choice(prefixes.get(video_type, ["Всё о"]))
        return f"{prefix} {topic}"

    def _generate_description(self, topic: str, video_type: str) -> str:
        """Генерация описания"""
        return f"""В этом видео мы рассмотрим тему: {topic}

🎯 Что вы узнаете:
- Основные концепции
- Практические примеры
- Советы и рекомендации

👍 Не забудьте поставить лайк и подписаться!

#youtube #контент #{topic.replace(' ', '')}
"""

    def _generate_full_script(
        self,
        topic: str,
        video_type: str,
        duration: int,
        quality_level: str
    ) -> str:
        """Генерация полного скрипта"""
        words_per_second = 2.5 if quality_level == "high" else 3.5
        target_words = int(duration * words_per_second)

        script_parts = [
            f"Привет! Сегодня мы поговорим о {topic}.",
            f"\n[ОСНОВНАЯ ЧАСТЬ - {target_words} слов]\n",
            "Это была основная информация по теме.",
            "Спасибо за просмотр! Не забудьте подписаться!",
        ]

        return "\n\n".join(script_parts)

    def _generate_tags(self, topic: str) -> List[str]:
        """Генерация тегов"""
        base_tags = ["youtube", "video", "контент"]
        topic_tags = topic.lower().split()
        return base_tags + topic_tags[:5]


# Функция для быстрого использования
def quick_generate(topic: str, **kwargs) -> VideoScript:
    """Быстрая генерация скрипта"""
    generator = ScriptGenerator()
    return generator.generate_script(topic, **kwargs)


if __name__ == "__main__":
    # Пример использования
    script = quick_generate(
        topic="Python для начинающих",
        video_type="tutorial",
        duration=300,
        quality_level="random"
    )
    print(f"Заголовок: {script.title}")
    print(f"Теги: {', '.join(script.tags)}")
