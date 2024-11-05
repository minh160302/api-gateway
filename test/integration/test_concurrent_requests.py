import asyncio

import httpx
import pytest

# from errors import RateLimitExceededError
# import ratelimit as ratelimit


@pytest.mark.asyncio
async def test_concurrent_requests():
    url = "http://127.0.0.1:8000/s1"  # Replace with your endpoint
    async with httpx.AsyncClient() as client:
        tasks = [client.get(
            url, headers={'Authorization': 'your-secret-token'}) for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        # Check each response for expected values
        for i, response in enumerate(responses):
            assert response.status_code == 200  # Check the status code
            print(f"Response {i + 1}: {response.json()}")


# Sequential run
@pytest.mark.asyncio
async def test_should_raise_rate_limit_error():
    await asyncio.sleep(5)
    # Reset cache
    url = "http://127.0.0.1:8000/s1"  # Replace with your endpoint
    number_of_requests = 105

    async def send_request():
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={'Authorization': 'your-secret-token'})
            return response

    # Create a list of tasks to send requests concurrently
    tasks = [send_request() for _ in range(number_of_requests)]

    freq = {
        200: 0,
        429: 0
    }
    for _ in range(number_of_requests):
        response = await send_request()
        assert response.status_code == 200 or response.status_code == 429
        freq[response.status_code] += 1
        print(response.json())  # Prints the JSON response

    print(freq)
    assert freq[429] == number_of_requests - 100
