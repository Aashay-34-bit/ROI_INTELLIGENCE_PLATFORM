import asyncio
import httpx
from app.core.enums import TaskCategory


async def main() -> None:
    samples = [(TaskCategory.CLASSIFICATION, "Classify customer says great work"), (TaskCategory.REASONING, "Compare these approaches step by step"), (TaskCategory.EXTRACTION, "Extract email ava@example.com"), (TaskCategory.GENERATION, "Write a short greeting")]
    async with httpx.AsyncClient() as client:
        for index in range(20):
            category, text = samples[index % len(samples)]
            response = await client.post("http://localhost:8000/v1/request", headers={"X-API-Key": "demo-key"}, json={"input": text, "task_category": category.value})
            response.raise_for_status()
    print("Submitted 20 demo requests")


if __name__ == "__main__":
    asyncio.run(main())
