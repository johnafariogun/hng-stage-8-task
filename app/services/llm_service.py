import json
import httpx
from config import settings
from utils.logger import logger

async def analyze_with_llm(text: str):
    prompt = f"""
    Analyze the document. Return ONLY valid JSON with:
    - summary
    - document_type
    - metadata (object)
    Text: {text[:3500]}
    """

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            res = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "nvidia/nemotron-nano-12b-v2-vl:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }
            )
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"]

            if "```" in content:
                content = content.split("```")[1].replace("json", "").strip()

            return json.loads(content)

        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return {"summary": "LLM failed", "document_type": "unknown", "metadata": {}}

