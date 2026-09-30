import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")


class LLMClient:
    """Zhipu AI (BigModel) LLM client, OpenAI-compatible API."""

    def __init__(self):
        self.api_key = os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ZHIPU_API_KEY not set. Please set it in .env file."
            )
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/"
        self.model = os.getenv("ZHIPU_MODEL", "glm-4-flash-250414")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def analyze(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """Send a chat completion request and return the response text."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
