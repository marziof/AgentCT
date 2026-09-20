import time

def invoke_with_retry(model, prompt: str, max_attempts: int = 3, delay: float = 2.0):
    """
    Call a structured-output model with retries on transient failures
    (e.g. malformed JSON from tool-calling generation glitches).

    Args:
        model: a LangChain model (typically bound via with_structured_output).
        prompt (str): the prompt to send.
        max_attempts (int): how many total attempts before giving up.
        delay (float): seconds to wait between attempts.

    Returns:
        The validated structured response.

    Raises:
        The last exception encountered, if all attempts fail.
    """
    last_exception = None
    for attempt in range(1, max_attempts + 1):
        try:
            return model.invoke(input=prompt)
        except Exception as e:
            last_exception = e
            print(f"Attempt {attempt}/{max_attempts} failed: {e}")
            if attempt < max_attempts:
                time.sleep(delay)
    raise last_exception