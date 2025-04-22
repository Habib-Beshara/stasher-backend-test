from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

T = TypeVar('T')

class SQLRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    async def insert(self, data: Dict[str, Any]) -> T:
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, id: Any) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_all(self) -> List[T]:
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find(self, filter_criteria: Dict[str, Any]) -> List[T]:
        stmt = select(self.model)
        for key, value in filter_criteria.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_one(self, filter_criteria: Dict[str, Any]) -> Optional[T]:
        stmt = select(self.model)
        for key, value in filter_criteria.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def update(self, id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        stmt = update(self.model).where(self.model.id == id).values(**update_data)
        await self.session.execute(stmt)
        return await self.get_by_id(id)
    
    async def delete(self, id: Any) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0