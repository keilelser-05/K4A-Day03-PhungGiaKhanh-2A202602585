"""Test only the selected LLM provider. Does not start MCP or touch Calendar."""

from pathlib import Path
import asyncio
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from providers import get_provider


async def main() -> None:
    provider = get_provider()
    print(f"Provider: {provider.provider_name}")
    print(f"Model: {provider.model_name}")
    state = await provider.start(
        "Chỉ trả lời đúng chữ OK",
        tools=[],
        instructions="Trả lời cực ngắn và làm đúng yêu cầu của người dùng.",
    )
    print("Response:", provider.output_text(state))


if __name__ == "__main__":
    asyncio.run(main())
