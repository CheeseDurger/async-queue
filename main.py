import asyncio

MAX_CONCURRENCY = 3

async def fake_api_call(item: int) -> None:
    '''Simultate an API call that takes 1 second'''
    if item == 5 or item == 7:
        raise ValueError('Big error')
    print(f'Item {item}')
    await asyncio.sleep(1)

async def semaphore_limited_fake_api_call(item: int, semaphore: asyncio.Semaphore) -> None:
    '''Wrap the API call in a semaphore to limit concurrency'''
    async with semaphore:
        await fake_api_call(item)

async def process(queue: list[int]) -> list[None | BaseException]:
    '''Process the queue asynchronously with a limited concurrency'''
    max_concurrency = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks: list[asyncio.Task] = [asyncio.create_task(semaphore_limited_fake_api_call(item, max_concurrency)) for item in queue]
    results: list[None | BaseException] = await asyncio.gather(*tasks, return_exceptions=True)
    return results

queue: list[int] = list(range(1, 10))
results: list[BaseException | None] = asyncio.run(process(queue))
exceptions: list[tuple[str, Exception]] = [(f'Item {item} failed', result) for item, result in zip(queue, results) if isinstance(result, Exception)]
print(exceptions)
