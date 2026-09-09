from functools import lru_cache

from openai import AzureOpenAI

from app.config import settings


@lru_cache
def get_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )


def get_chat_completion(message: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=settings.azure_openai_deployment,
        messages=[{"role": "user", "content": message}],
    )
    return response.choices[0].message.content or ""
