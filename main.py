import asyncio

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from robust_llm import get_robust_llm


MAX_CONCURRENCY = 3

async def action(item: int, llm: ChatOpenAI) -> None:
    """Do a dummy action with llm"""
    result: BaseMessage = await llm.ainvoke("Hello, how are you?")
    print(f'Item: {item}; Model: {result.response_metadata["model_name"]}; Answer: {result.content[:10]}...')

async def semaphore_limited_action(item: int, llm: ChatOpenAI, semaphore: asyncio.Semaphore) -> None:
    """Wrap the dummy action in a semaphore to limit concurrency"""
    async with semaphore:
        await action(item, llm)

async def process(queue: list[int], llm: ChatOpenAI) -> list[None | BaseException]:
    """Process the queue asynchronously with a limited concurrency"""
    max_concurrency = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks: list[asyncio.Task] = [asyncio.create_task(semaphore_limited_action(item, llm, max_concurrency)) for item in queue]
    results: list[None | BaseException] = await asyncio.gather(*tasks, return_exceptions=True)
    return results

if __name__ == "__main__":
    queue: list[int] = list(range(1, 10))
    llm: ChatOpenAI = get_robust_llm(model="gpt-4o-mini", fallbacks=["gpt-4-turbo", "gpt-3.5-turbo"])
    results: list[BaseException | None] = asyncio.run(process(queue, llm))
    exceptions: list[tuple[str, Exception]] = [(f'Item {item} failed', result) for item, result in zip(queue, results) if isinstance(result, Exception)]
    print(exceptions)
