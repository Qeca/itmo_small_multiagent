from pathlib import Path
import yaml


class PromptLoader:
    def __init__(self, prompts_dir: str = "prompts"):
        self.base_path = Path(prompts_dir)
    
    def load(self, name: str) -> dict:
        file_path = self.base_path / f"{name}.yaml"
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def format(self, name: str, **kwargs) -> dict:
        prompts = self.load(name)
        return {
            key: value.format(**kwargs) if isinstance(value, str) else value
            for key, value in prompts.items()
        }
