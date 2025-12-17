from typing import Protocol


class ApplicationFacadeProtocol(Protocol):
    async def start_processing(self) -> None: ...
