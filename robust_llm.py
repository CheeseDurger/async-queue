from langchain_core.messages import BaseMessage
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_openai import ChatOpenAI


def get_robust_llm(model: str, fallbacks: list[str] = [], max_retries: int = 0, timeout: float = 1.0) -> ChatOpenAI:
    """A robust version of ChatOpenAI that:
    - Has max retries
    - Has a rate limiter
    - Has multiple models as fallbacks
    """
    # Setup primary llm
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=5,      # 5 requests max per second
        check_every_n_seconds=0.1,  # Check every 100 ms whether it is allowed to make a new request
        max_bucket_size=10,         # 10 requests max in parallel
    )
    llm = ChatOpenAI(model=model, max_retries=max_retries, timeout=timeout, rate_limiter=rate_limiter)

    # Setup list of fallback llms
    fallback_models: list[ChatOpenAI] = []
    for fallback in fallbacks:
        fallback_rate_limiter = InMemoryRateLimiter(requests_per_second=5, check_every_n_seconds=0.1, max_bucket_size=10)
        fallback_models.append(ChatOpenAI(model=fallback, max_retries=max_retries, timeout=timeout, rate_limiter=fallback_rate_limiter))
    
    # Add fallbacks to primary llm
    llm: ChatOpenAI = llm.with_fallbacks(fallback_models)
    return llm


llm = get_robust_llm(model="gpt-4o-mini", fallbacks=["gpt-3.5-turbo"], max_retries=0, timeout=1.0)

if __name__ == "__main__":
    for i in range(5):
        result: BaseMessage = llm.invoke("Hello, how are you?")
        print(f'The model used for request {i} is {result.response_metadata["model_name"]} and the answer is: {result.content[:10]}...')