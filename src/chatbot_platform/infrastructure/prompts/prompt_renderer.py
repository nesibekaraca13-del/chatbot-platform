from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_SYSTEM_PROMPT_FILENAME = "system_prompt.j2"


def render_system_prompt(prompts_dir: Path, context: str) -> str:
    environment = Environment(loader=FileSystemLoader(str(prompts_dir)))
    template = environment.get_template(_SYSTEM_PROMPT_FILENAME)
    return template.render(context=context)
