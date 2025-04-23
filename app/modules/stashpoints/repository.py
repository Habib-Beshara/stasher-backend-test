from app.abstracts.repository import SQLRepository
from app.models.stashpoint import Stashpoint
from app.models.booking import Booking
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_, or_, not_
from sqlalchemy.sql import text
from geoalchemy2.functions import ST_DWithin, ST_Point, ST_Distance
from datetime import datetime


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
    
    async def find_available_stashpoints(
        self,
        latitude: float,
        longitude: float,
        dropoff_time: datetime,
        pickup_time: datetime,
        bag_count: int,
        radius_km: float = 5.0
    ) -> List[Stashpoint]:
        """
        Find stashpoints that:
        1. Are within the specified radius of the search coordinates
        2. Have enough capacity for the requested number of bags during the time period
        3. Are open during the requested drop-off and pick-up times
        
        Results are ordered by distance from the search coordinates
        """
        # Convert km to meters for the spatial query
        radius_meters = radius_km * 1000
        
        # Create point from provided coordinates
        search_point = ST_Point(longitude, latitude, srid=4326)
        
        # Get the time components for open hours check
        dropoff_time_only = func.time(dropoff_time)
        pickup_time_only = func.time(pickup_time)
        
        # First, find all active bookings that overlap with the requested time period
        active_bookings_subquery = (
            select(
                Booking.stashpoint_id,
                func.sum(Booking.bag_count).label("booked_bags")
            )
            .where(
                and_(
                    not_(Booking.is_cancelled),
                    or_(
                        # Booking that overlaps with the requested period
                        and_(
                            Booking.dropoff_time <= pickup_time,
                            Booking.pickup_time >= dropoff_time
                        )
                    )
                )
            )
            .group_by(Booking.stashpoint_id)
            .subquery()
        )
        
        # Main query to find available stashpoints
        stmt = (
            select(
                Stashpoint,
                ST_Distance(Stashpoint.location, search_point).label("distance")
            )
            .outerjoin(
                active_bookings_subquery,
                Stashpoint.id == active_bookings_subquery.c.stashpoint_id
            )
            .where(
                and_(
                    # Within radius
                    ST_DWithin(Stashpoint.location, search_point, radius_meters),
                    
                    # Check capacity: either no bookings or enough capacity left
                    or_(
                        active_bookings_subquery.c.booked_bags.is_(None),
                        Stashpoint.capacity >= active_bookings_subquery.c.booked_bags + bag_count
                    ),
                    
                    # Check opening hours: must be open at drop-off and pick-up times
                    Stashpoint.open_from <= dropoff_time_only,
                    Stashpoint.open_until >= pickup_time_only
                )
            )
            .order_by("distance")
        )
        
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]