import pytest

from unittest.mock import Mock
from app.utils.retry import retry_with_backoff, retry_with_backoff_async, RetryableAPIClient

class CustomException(Exception):
    pass

class OtherException(Exception):
    pass

def create_mock_func(side_effect=None, return_value=None):
    mock = Mock(side_effect=side_effect, return_value=return_value)
    mock.__name__ = "mock_func"
    return mock

# Tests for retry_with_backoff
def test_retry_with_backoff_success():
    mock_func = create_mock_func(return_value="success")
    decorated_func = retry_with_backoff(max_retries=3, initial_delay=0.01)(mock_func)

    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 1

def test_retry_with_backoff_success_after_retries():
    mock_func = create_mock_func(side_effect=[Exception("fail1"), Exception("fail2"), "success"])
    decorated_func = retry_with_backoff(max_retries=3, initial_delay=0.01)(mock_func)

    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3

def test_retry_with_backoff_max_retries_exceeded():
    mock_func = create_mock_func(side_effect=Exception("fail"))
    decorated_func = retry_with_backoff(max_retries=3, initial_delay=0.01)(mock_func)

    with pytest.raises(Exception, match="fail"):
        decorated_func()

    assert mock_func.call_count == 4 # Initial + 3 retries

def test_retry_with_backoff_specific_exceptions():
    mock_func = create_mock_func(side_effect=OtherException("other fail"))
    decorated_func = retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(CustomException,)
    )(mock_func)

    with pytest.raises(OtherException):
        decorated_func()

    assert mock_func.call_count == 1 # Shouldn't retry on OtherException

def test_retry_with_backoff_on_retry_callback():
    mock_func = create_mock_func(side_effect=[Exception("fail1"), "success"])
    callback_mock = Mock()
    decorated_func = retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        on_retry=callback_mock
    )(mock_func)

    decorated_func()

    assert callback_mock.call_count == 1
    call_args = callback_mock.call_args[0]
    assert isinstance(call_args[0], Exception)
    assert call_args[1] == 1 # First retry


# Tests for retry_with_backoff_async
def create_async_mock_func(side_effect=None, return_value=None):
    from unittest.mock import AsyncMock
    mock = AsyncMock(side_effect=side_effect, return_value=return_value)
    mock.__name__ = "async_mock_func"
    return mock

@pytest.mark.asyncio
async def test_retry_with_backoff_async_success():
    mock_func = create_async_mock_func(return_value="success")
    decorated_func = retry_with_backoff_async(max_retries=3, initial_delay=0.01)(mock_func)

    result = await decorated_func()

    assert result == "success"
    assert mock_func.call_count == 1

@pytest.mark.asyncio
async def test_retry_with_backoff_async_success_after_retries():
    mock_func = create_async_mock_func(side_effect=[Exception("fail1"), Exception("fail2"), "success"])
    decorated_func = retry_with_backoff_async(max_retries=3, initial_delay=0.01)(mock_func)

    result = await decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_retry_with_backoff_async_max_retries_exceeded():
    mock_func = create_async_mock_func(side_effect=Exception("fail"))
    decorated_func = retry_with_backoff_async(max_retries=3, initial_delay=0.01)(mock_func)

    with pytest.raises(Exception, match="fail"):
        await decorated_func()

    assert mock_func.call_count == 4 # Initial + 3 retries

@pytest.mark.asyncio
async def test_retry_with_backoff_async_specific_exceptions():
    mock_func = create_async_mock_func(side_effect=OtherException("other fail"))
    decorated_func = retry_with_backoff_async(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(CustomException,)
    )(mock_func)

    with pytest.raises(OtherException):
        await decorated_func()

    assert mock_func.call_count == 1 # Shouldn't retry on OtherException

@pytest.mark.asyncio
async def test_retry_with_backoff_async_on_retry_callback():
    mock_func = create_async_mock_func(side_effect=[Exception("fail1"), "success"])
    callback_mock = Mock()
    decorated_func = retry_with_backoff_async(
        max_retries=3,
        initial_delay=0.01,
        on_retry=callback_mock
    )(mock_func)

    await decorated_func()

    assert callback_mock.call_count == 1
    call_args = callback_mock.call_args[0]
    assert isinstance(call_args[0], Exception)
    assert call_args[1] == 1 # First retry

# Tests for RetryableAPIClient
def test_retryable_api_client_call_with_retry_success():
    client = RetryableAPIClient(max_retries=3, initial_delay=0.01)
    mock_func = Mock(return_value="success")

    result = client.call_with_retry(mock_func)

    assert result == "success"
    assert mock_func.call_count == 1

def test_retryable_api_client_call_with_retry_after_failures():
    client = RetryableAPIClient(max_retries=3, initial_delay=0.01)
    mock_func = Mock(side_effect=[Exception("fail1"), Exception("fail2"), "success"])

    result = client.call_with_retry(mock_func)

    assert result == "success"
    assert mock_func.call_count == 3

def test_retryable_api_client_call_with_retry_max_retries():
    client = RetryableAPIClient(max_retries=3, initial_delay=0.01)
    mock_func = Mock(side_effect=Exception("fail"))

    with pytest.raises(Exception, match="fail"):
        client.call_with_retry(mock_func)

    assert mock_func.call_count == 4

def test_retryable_api_client_call_batch_continue_on_failure():
    client = RetryableAPIClient(max_retries=2, initial_delay=0.01)
    items = [1, 2, 3]

    # Succeeds on 1, fails on 2, succeeds on 3
    def process_func(item):
        if item == 2:
            raise Exception("item 2 fail")
        return f"success {item}"

    mock_func = Mock(side_effect=process_func)

    results, failures = client.call_batch_with_retry(
        items, mock_func, continue_on_failure=True
    )

    assert results == ["success 1", "success 3"]
    assert len(failures) == 1
    assert failures[0]["index"] == 1
    assert failures[0]["item"] == 2
    assert failures[0]["error"] == "item 2 fail"

    # 1 call for item 1
    # 3 calls for item 2 (initial + 2 retries)
    # 1 call for item 3
    assert mock_func.call_count == 5

def test_retryable_api_client_call_batch_stop_on_failure():
    client = RetryableAPIClient(max_retries=2, initial_delay=0.01)
    items = [1, 2, 3]

    def process_func(item):
        if item == 2:
            raise Exception("item 2 fail")
        return f"success {item}"

    mock_func = Mock(side_effect=process_func)

    with pytest.raises(Exception, match="item 2 fail"):
        client.call_batch_with_retry(
            items, mock_func, continue_on_failure=False
        )

    # 1 call for item 1
    # 3 calls for item 2
    # 0 calls for item 3 (stopped early)
    assert mock_func.call_count == 4

# Tests for with_retry
from app.utils.retry import with_retry

def test_with_retry_success():
    mock_func = create_mock_func(return_value="success")
    decorated_func = with_retry(max_retries=3, delay=0.01)(mock_func)

    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 1

def test_with_retry_success_after_retries():
    mock_func = create_mock_func(side_effect=[Exception("fail1"), Exception("fail2"), "success"])
    decorated_func = with_retry(max_retries=3, delay=0.01)(mock_func)

    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3

def test_with_retry_max_retries_exceeded():
    mock_func = create_mock_func(side_effect=Exception("fail"))
    decorated_func = with_retry(max_retries=3, delay=0.01)(mock_func)

    with pytest.raises(Exception, match="fail"):
        decorated_func()

    assert mock_func.call_count == 4 # Initial + 3 retries

def test_with_retry_specific_exceptions():
    mock_func = create_mock_func(side_effect=OtherException("other fail"))
    decorated_func = with_retry(
        max_retries=3,
        delay=0.01,
        exceptions=(CustomException,)
    )(mock_func)

    with pytest.raises(OtherException):
        decorated_func()

    assert mock_func.call_count == 1 # Shouldn't retry on OtherException
