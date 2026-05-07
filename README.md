# JARVIS Multi-Agent System

Небольшой фреймворк для экспериментов с multi-agent пайплайнами: агент-оркестратор принимает задачу, подключает специализированных агентов, вызывает инструменты и сохраняет рабочий контекст.

## Что реализовано

- оркестратор для распределения задач между агентами;
- аналитический агент для разборa запроса и планирования;
- command/CLI agent для выполнения команд и работы с окружением;
- инструменты для запуска Python-кода, CLI-команд, веб-поиска и памяти;
- FAISS-память для сохранения и поиска контекста;
- YAML-промпты для быстрой настройки поведения агентов;
- примеры базового запуска, работы с CLI, памятью и Tavily.

## Структура

```text
src/
  jarvis.py        # главный класс системы
  agents/          # реализации агентов
  core/            # базовые компоненты LLM и tool calling
  memory/          # векторная память
  tools/           # Python, CLI, search и memory tools
  prompts/         # промпты внутри пакета
examples/          # минимальные сценарии запуска
prompts/           # YAML-конфигурации агентов
multiagent.ipynb   # исходный notebook-эксперимент
```

## Настройка окружения

```bash
git clone https://github.com/Qeca/itmo_small_multiagent.git
cd itmo_small_multiagent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env` локальными ключами. Файл `.env` не должен попадать в git.

```env
OPENAI_API_KEY=
OPENAI_MODEL=qwen/qwen3-next-80b-a3b-instruct
EMBEDDING_MODEL=qwen/qwen3-embedding-4b
EMBEDDING_DIM=2560
TAVILY_API_KEY=
```

## Примеры

```bash
python examples/basic.py
python examples/cli_example.py
python examples/memory_example.py
python examples/tavily_example.py
```

## Статус проекта

Учебный прототип для проверки архитектуры multi-agent ассистента. Код подходит для экспериментов с агентами, инструментами и памятью; перед production-использованием нужны изоляция выполнения команд, тесты и явная политика безопасности для tool calling.