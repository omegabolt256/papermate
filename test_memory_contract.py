from intelligence.contracts import TaskType
from memory.contracts import (
    MemoryProvider,
    MemoryRecord,
    MemoryScope,
)


class FakeMemory(MemoryProvider):

    def __init__(self):
        self.records = []

    def search(
        self,
        query,
        *,
        scope=None,
        project_id=None,
        limit=5,
    ):
        matches = [
            record
            for record in self.records
            if query.lower() in record.content.lower()
        ]

        return matches[:limit]

    def remember(self, memory):
        self.records.append(memory)

        return memory

    def update(self, memory_id, content):
        for index, record in enumerate(self.records):
            if record.memory_id == memory_id:
                updated = MemoryRecord(
                    content=content,
                    scope=record.scope,
                    project_id=record.project_id,
                    paper_id=record.paper_id,
                    memory_id=memory_id,
                )

                self.records[index] = updated

                return updated

        raise KeyError(memory_id)

    def forget(self, memory_id):
        self.records = [
            record
            for record in self.records
            if record.memory_id != memory_id
        ]


def main():

    memory = FakeMemory()

    memory.remember(
        MemoryRecord(
            memory_id="test-1",
            content=(
                "The project focuses on randomized "
                "controlled trials."
            ),
            scope=MemoryScope.PROJECT,
            project_id="project-001",
        )
    )

    results = memory.search(
        "randomized",
        project_id="project-001",
    )

    assert len(results) == 1
    assert results[0].memory_id == "test-1"

    print("=== PaperMate Memory Contract Test ===")
    print("Stored:", len(memory.records))
    print("Retrieved:", results[0].content)
    print("Scope:", results[0].scope.value)
    print("Project:", results[0].project_id)
    print("STATUS: PASS")


if __name__ == "__main__":
    main()