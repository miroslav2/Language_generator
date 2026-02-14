from typing import List

class WordSeparator:
    """
    Управление пробелами и разделением слов.
    """
    def join_words(self, words: List[str]) -> str:
        # Может быть ' ', '', '-', или спецсимволы
        return " ".join(words)