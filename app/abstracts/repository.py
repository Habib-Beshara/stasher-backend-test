from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

T = TypeVar('T')

class SQLRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def insert(self, data: Dict[str, Any]) -> T:
        entity = self.model(**data)
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, id: Any) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def find_all(self) -> List[T]:
        stmt = select(self.model)
        result = self.session.execute(stmt)
        return result.scalars().all()
    
    def find(self, filter_criteria: Dict[str, Any]) -> List[T]:
        stmt = select(self.model)
        for key, value in filter_criteria.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = self.session.execute(stmt)
        return result.scalars().all()
    
    def find_one(self, filter_criteria: Dict[str, Any]) -> Optional[T]:
        stmt = select(self.model)
        for key, value in filter_criteria.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = self.session.execute(stmt)
        return result.scalars().first()
    
    def update(self, id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        stmt = update(self.model).where(self.model.id == id).values(**update_data)
        self.session.execute(stmt)
        return self.get_by_id(id)
    
    def delete(self, id: Any) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = self.session.execute(stmt)
        return result.rowcount > 0