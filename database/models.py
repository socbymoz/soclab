from dataclasses import dataclass, field
from typing import List


@dataclass
class Question:
    q: str
    options: List[str]
    answer: int


@dataclass
class Module:
    id: int
    title: str
    icon: str
    color: str
    desc: str
    lessons: List[str]
    questions: List[Question] = field(default_factory=list)
