from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio


server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"],  # Path to your server file
)


model = 'deepseek-r1:32b'


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\nTesting echo tool:")
            echo_result = await session.call_tool("echo_tool", {"message": "Hello, World!"})
            print(f"Echo result: {echo_result}")

            print("\nTesting Ollama generation:")
            ollama_result = await session.call_tool(
                "ollama_generate", 
                {"message": "What is the capital of France?", "model": model}
            )
            print(f"Ollama response: {ollama_result}")

            print("\nListing Ollama models:")
            models = await session.call_tool("list_ollama_models")
            print(f"Available models: {models}")


if __name__ == "__main__":
    asyncio.run(main())
