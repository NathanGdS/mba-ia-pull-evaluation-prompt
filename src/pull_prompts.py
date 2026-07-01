"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"

def pull_prompts_from_langsmith() -> bool:
    print_section_header(f"Pulling prompt: {PROMPT_NAME}")

    prompt = hub.pull(PROMPT_NAME)

    system_prompt = ""
    user_prompt = ""

    for message in prompt.messages:
        if isinstance(message, SystemMessagePromptTemplate):
            system_prompt = message.prompt.template
        elif isinstance(message, HumanMessagePromptTemplate):
            user_prompt = message.prompt.template

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    success = save_yaml(data, str(OUTPUT_PATH))
    if success:
        print(f"Saved to {OUTPUT_PATH}")
    return success


def main():
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
