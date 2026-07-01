"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data():
    data = load_prompts(str(PROMPT_PATH))
    return data["bug_to_user_story_v2"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' ausente"
        assert prompt_data["system_prompt"].strip(), "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data["system_prompt"]
        role_indicators = ["você é", "you are", "sua especialidade", "product manager", "agile coach"]
        lower = system_prompt.lower()
        assert any(indicator in lower for indicator in role_indicators), (
            "system_prompt não define persona/role"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"]
        format_indicators = [
            "como um", "eu quero", "para que",
            "critérios de aceitação", "dado que", "quando", "então",
            "user story", "given", "when", "then"
        ]
        lower = system_prompt.lower()
        assert any(indicator in lower for indicator in format_indicators), (
            "system_prompt não menciona formato de User Story ou Markdown"
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"]
        lower = system_prompt.lower()
        example_indicators = ["exemplo", "example", "bug report:", "user story:"]
        has_examples = any(indicator in lower for indicator in example_indicators)
        assert has_examples, "system_prompt não contém exemplos Few-shot"
        example_count = lower.count("exemplo") + lower.count("example")
        assert example_count >= 2, (
            f"Few-shot requer pelo menos 2 exemplos, encontrado(s): {example_count}"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que nenhum TODO foi esquecido no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        description = prompt_data.get("description", "")
        full_text = f"{system_prompt} {user_prompt} {description}"
        assert "TODO" not in full_text, "Prompt contém TODO não resolvido"
        assert "[TODO]" not in full_text, "Prompt contém [TODO] não resolvido"

    def test_minimum_techniques(self, prompt_data):
        """Verifica se pelo menos 2 técnicas foram listadas nos metadados do YAML."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requerido, encontradas: {len(techniques)} — {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
