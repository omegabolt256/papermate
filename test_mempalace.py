import asyncio

from mcp import (
    ClientSession,
    StdioServerParameters,
    stdio_client,
)


PALACE = r"D:\Projects\PaperMate\data\memory"


async def main():

    server = StdioServerParameters(
        command="mempalace-mcp",
        args=["--palace", PALACE],
    )

    async with stdio_client(server) as streams:
        read_stream, write_stream = streams

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            print("=== STATUS BEFORE ===")

            status = await session.call_tool(
                "mempalace_status",
                {},
            )

            print(status)

            print("\n=== ADD ===")

            added = await session.call_tool(
                "mempalace_add_drawer",
                {
                    "wing": "papermate-test",
                    "room": "general",
                    "content": (
                        "PaperMate diagnostic test: "
                        "randomized controlled trials "
                        "are the preferred study design."
                    ),
                    "source_file": "integration-test",
                    "added_by": "papermate",
                },
            )

            print(added)

            print("\n=== STATUS AFTER ADD ===")

            status = await session.call_tool(
                "mempalace_status",
                {},
            )

            print(status)

            print("\n=== RECONNECT ===")

            reconnect = await session.call_tool(
                "mempalace_reconnect",
                {},
            )

            print(reconnect)

            print("\n=== SEARCH ===")

            search = await session.call_tool(
                "mempalace_search",
                {
                    "query": "randomized controlled trials",
                    "limit": 10,
                    "wing": "papermate-test",
                    "room": "general",
                    "max_distance": 1.5,
                },
            )

            print(search)


if __name__ == "__main__":
    asyncio.run(main())