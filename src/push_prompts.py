"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    for field in ["description", "system_prompt", "version"]:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    if "TODO" in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (chave raiz do YAML)
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()

    system_prompt = prompt_data["system_prompt"]
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")
    description = prompt_data.get("description", "")
    tags = prompt_data.get("tags", [])

    template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    hub_name = f"{username}/{prompt_name}" if username else prompt_name

    print(f"Fazendo push para: {hub_name}")

    try:
        url = hub.push(
            hub_name,
            template,
            new_repo_is_public=True,
            new_repo_description=description,
        )
        print(f"Push realizado com sucesso!")
        print(f"URL: {url}")
        return True
    except Exception as e:
        print(f"Erro no push: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    # Tenta v2 primeiro, cai em v1
    v2_path = PROMPTS_DIR / "bug_to_user_story_v2.yml"
    v1_path = PROMPTS_DIR / "bug_to_user_story_v1.yml"

    if v2_path.exists():
        yaml_path = v2_path
        prompt_key = "bug_to_user_story_v2"
    else:
        print(f"AVISO: v2 não encontrada, usando v1 como fallback")
        yaml_path = v1_path
        prompt_key = "bug_to_user_story_v1"

    print(f"Carregando: {yaml_path.name}")
    data = load_yaml(str(yaml_path))
    if not data:
        return 1

    prompt_data = data.get(prompt_key)
    if not prompt_data:
        print(f"Chave '{prompt_key}' não encontrada no YAML")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt inválido:")
        for e in errors:
            print(f"  - {e}")
        return 1

    success = push_prompt_to_langsmith(prompt_key, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
