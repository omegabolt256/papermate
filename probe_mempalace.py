import asyncio

from mcp import (
    ClientSession,
    StdioServerParameters,
    stdio_client,
)


KEYWORDS = (
    "kg",
    "diary",
    "memory",
    "fact",
)


async def main():
    server = StdioServerParameters(
        command="mempalace-mcp",
        args=[
            "--palace",
            r"D:\Projects\PaperMate\data\memory",
        ],
    )

    async with stdio_client(server) as streams:
        read_stream, write_stream = streams

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()
            result = await session.list_tools()

            print("=== MemPalace Advanced Memory Tools ===")

            for tool in result.tools:
                name = tool.name.lower()

                if not any(
                    keyword in name
                    for keyword in KEYWORDS
                ):
                    continue

                print()
                print("=" * 70)
                print("NAME:", tool.name)
                print("DESCRIPTION:", tool.description)
                print("INPUT SCHEMA:")
                print(tool.input_schema)


if __name__ == "__main__":
    asyncio.run(main())