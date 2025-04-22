from app.abstracts.repository import SQLRepository
from app.models.stashpoint import Stashpoint
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from geoalchemy2.functions import ST_DWithin, ST_Point


class StashpointRepository(SQLRepository[Stashpoint]):
    def __init__(self, session: Session):
        super().__init__(Stashpoint, session)
    
    async def find_by_name(self, name: str) -> List[Stashpoint]:
        stmt = select(self.model).where(self.model.name.ilike(f"%{name}%"))
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_location(self, latitude: float, longitude: float, distance_meters: int = 5000) -> List[Stashpoint]:
        """Find stashpoints within a specified distance from coordinates"""
        point = ST_Point(longitude, latitude, srid=4326)
        stmt = select(self.model).where(
            ST_DWithin(self.model.location, point, distance_meters)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_with_available_capacity(self, min_capacity: int = 1) -> List[Stashpoint]:
        """Find stashpoints with at least the specified available capacity"""
        stmt = select(self.model).where(self.model.capacity >= min_capacity)
        result = await self.session.execute(stmt)
        return result.scalars().all()