import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.jarvis import JARVIS


def main():
    jarvis = JARVIS(verbose=True)
    
    print("\n🧪 Тест 1: Первая задача - обучение RandomForest\n")
    jarvis.run("Обучи RandomForest на iris и выведи accuracy")
    
    print("\n" + "="*80)
    print("\n🧪 Тест 2: Похожая задача - агент должен найти в памяти\n")
    jarvis.run("Обучи RandomForest на iris и выведи accuracy если не делал этого")
    


if __name__ == "__main__":
    main()
