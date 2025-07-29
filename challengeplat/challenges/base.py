from typing import Dict, List, Optional

class Challenge:
    def __init__(self):
        self.id: str = ""
        self.title: str = ""
        self.description: str = ""
        self.difficulty: str = ""
        self.files: Dict[str, str] = {}
        self.test_command: str = ""
        self.solution: Dict[str, str] = {}
        self.hints: List[str] = []
