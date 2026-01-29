import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.jarvis import JARVIS


def main():
    jarvis = JARVIS(verbose=True)
    
    task = "Обучи RandomForest на iris и выведи accuracy"
    
    jarvis.run(task)


if __name__ == "__main__":
    main()
