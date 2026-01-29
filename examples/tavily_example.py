import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.jarvis import JARVIS


def main():
    jarvis = JARVIS(verbose=True)
    
    print("\n🧪 Тест Tavily: Поиск актуальной информации\n")
    jarvis.run("Найди последние новости о LangGraph и покажи примеры использования")


if __name__ == "__main__":
    main()
