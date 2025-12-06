from abc import ABC, abstractmethod
from typing import List, Optional

class Repository(ABC):
    @abstractmethod
    async def get(self, id: int):
        pass

    @abstractmethod
    async def list(self):
        pass

    @abstractmethod
    async def create(self,  dict):
        pass

    @abstractmethod
    async def update(self, id: int, data: dict):
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass

