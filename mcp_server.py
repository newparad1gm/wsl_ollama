from mcp.server.fastmcp import FastMCP
import aiohttp
import json


mcp = FastMCP("Ollama Echo")


OLLAMA_BASE_URL = "http://192.168.0.167:11434"


async def generate_with_ollama(prompt: str, model: str = "llama2") -> str:
    """Helper function to generate text using Ollama API"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": prompt},
            headers={"Accept": "application/x-ndjson"}
        ) as response:
            if response.status == 200:
                full_response = ""
                # Read the streaming response line by line
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                full_response += chunk["response"]
                        except json.JSONDecodeError:
                            continue
                return full_response
            else:
                return f"Error: Failed to generate response (Status {response.status})"


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"


@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"


# Add Ollama-specific tools
@mcp.tool()
async def ollama_generate(message: str, model: str = "llama2") -> str:
    """Generate text using Ollama"""
    return await generate_with_ollama(message, model)


@mcp.tool()
async def list_ollama_models() -> str:
    """List available Ollama models"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{OLLAMA_BASE_URL}/api/tags") as response:
            if response.status == 200:
                models = await response.json()
                return json.dumps(models, indent=2)
            return f"Error: Failed to fetch models (Status {response.status})"


@mcp.prompt()
async def ollama_chat(message: str, model: str = "llama2") -> str:
    """Create a chat prompt using Ollama"""
    response = await generate_with_ollama(message, model)
    return f"Model ({model}) response: {response}"


if __name__ == "__main__":
    mcp.run()
    