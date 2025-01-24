import asyncio

MAX_CONCURRENCY = 3

async def fake_api_call(item: int):
    '''Simultate an API call that takes 1 second'''
    if item == 5 or item == 7:
        raise ValueError('Big error')
    print(f'Item {item}')
    await asyncio.sleep(1)

async def semaphore_limited_fake_api_call(item, semaphore: asyncio.Semaphore):
    '''Wrap the API call in a semaphore to limit concurrency'''
    async with semaphore:
        await fake_api_call(item)

async def process(queue: list[int]):
    '''Process the queue asynchronously with a limited concurrency'''
    max_concurrency = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks: list[asyncio.Task] = [asyncio.create_task(semaphore_limited_fake_api_call(item, max_concurrency)) for item in queue]
    result = await asyncio.gather(*tasks, return_exceptions=True)
    return result

queue: list[int] = list(range(1, 10))
results = asyncio.run(process(queue))
exceptions = [(f'Item {item} failed', result) for item, result in zip(queue, results) if isinstance(result, Exception)]
print(exceptions)
