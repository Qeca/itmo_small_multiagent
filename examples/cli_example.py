import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.jarvis import JARVIS


def main():
    jarvis = JARVIS(verbose=True)
    
    
    print("\n🧪 Тест 1: CLI Agent (команды в терминале)\n")
    jarvis.run("Покажи текущую директорию и список файлов")


if __name__ == "__main__":
    main()
