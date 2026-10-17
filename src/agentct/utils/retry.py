# import time

# def invoke_with_retry(model, prompt: str, max_attempts: int = 3, delay: float = 2.0):
#     """
#     Call a structured-output model with retries on transient failures
#     (e.g. malformed JSON from tool-calling generation glitches).
    
#     Args:
#         model: a LangChain model (typically bound via with_structured_output).
#         prompt (str): the prompt to send.
#         max_attempts (int): how many total attempts before giving up.
#         delay (float): seconds to wait between attempts.

#     Returns:
#         The validated structured response.

#     Raises:
#         The last exception encountered, if all attempts fail.
#     """
#     last_exception = None
#     for attempt in range(1, max_attempts + 1):
#         try:
#             return model.invoke(input=prompt)
#         except Exception as e:
#             last_exception = e
#             print(f"Attempt {attempt}/{max_attempts} failed: {e}")
#             if attempt < max_attempts:
#                 time.sleep(delay)
#     raise last_exception



import time
import random


def invoke_with_retry(
    model,
    prompt: str,
    max_attempts: int = 3,
    delay: float = 2.0,
    max_delay: float = 30.0,
):
    """
    Invoke a structured-output model with exponential backoff.

    Retries transient failures, including rate limits and temporary
    provider errors. Persistent schema/prompt errors may still fail
    after retries and should be fixed at their source.
    """
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            return model.invoke(input=prompt)

        except Exception as e:
            last_exception = e
            error_text = str(e).lower()

            print(
                f"Attempt {attempt}/{max_attempts} failed: "
                f"{type(e).__name__}: {e}"
            )

            if attempt == max_attempts:
                break

            # Retry likely transient errors, but don't waste attempts
            # on errors that are unlikely to change with time.
            permanent_error_markers = (
                "invalid api key",
                "authentication",
                "permission",
                "model_not_found",
                "does not exist",
            )

            if any(marker in error_text for marker in permanent_error_markers):
                raise

            # Exponential backoff with small random jitter.
            wait = min(delay * (2 ** (attempt - 1)), max_delay)
            wait += random.uniform(0, min(1.0, wait * 0.1))

            # Rate limits may require longer waits.
            if "rate limit" in error_text or "429" in error_text:
                wait = max(wait, 10.0 * (2 ** (attempt - 1)))
                wait = min(wait, max_delay)

            print(f"Retrying in {wait:.1f} seconds...")
            time.sleep(wait)

    raise last_exception
