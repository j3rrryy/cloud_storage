from typing import Protocol


class ApplicationFacadeProtocol(Protocol):
    async def process_messages(self) -> None: ...
