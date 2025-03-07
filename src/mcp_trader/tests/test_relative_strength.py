import asyncio
import json
import aiohttp


async def test_relative_strength():
    """Test the relative-strength tool with NVDA and SPY."""
    async with aiohttp.ClientSession() as session:
        # Call the tool
        payload = {
            "name": "relative-strength",
            "arguments": {"symbol": "NVDA", "benchmark": "SPY"},
        }

        async with session.post(
            "http://localhost:8000/call-tool", json=payload
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(json.dumps(result, indent=2))
            else:
                print(f"Error: {response.status}")
                print(await response.text())


if __name__ == "__main__":
    asyncio.run(test_relative_strength())
