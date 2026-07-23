from pathlib import Path

from chatbot_platform.infrastructure.prompts.prompt_renderer import render_system_prompt

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def test_render_system_prompt_includes_context() -> None:
    rendered = render_system_prompt(PROMPTS_DIR, context="Aylık paketimiz 1000 TL'dir.")

    assert "Aylık paketimiz 1000 TL'dir." in rendered
    assert "yetkiliye yönlendiriyorum" in rendered
