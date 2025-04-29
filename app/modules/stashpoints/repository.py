from app.abstracts.repository import SQLRepository
from app.models.stashpoint import Stashpoint
from app.models.booking import Booking
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_, or_, not_, cast
from sqlalchemy.sql import text
from geoalchemy2.functions import ST_DWithin, ST_Point, ST_Distance
from app import db
from datetime import datetime


class StashpointRepository(SQLRepository[Stashpoint]):
    def __init__(self, session: Session):
        super().__init__(Stashpoint, session)
    
    def find_by_name(self, name: str) -> List[Stashpoint]:
        stmt = select(self.model).where(self.model.name.ilike(f"%{name}%"))
        result = self.session.execute(stmt)
        return result.scalars().all()
    
    def find_by_location(self, latitude: float, longitude: float, distance_meters: int = 5000) -> List[Stashpoint]:
        """Find stashpoints within a specified distance from coordinates"""
        point = ST_Point(longitude, latitude, srid=4326)
        stmt = select(self.model).where(
            ST_DWithin(self.model.location, point, distance_meters)
        )
        result = self.session.execute(stmt)
        return result.scalars().all()
    
    def find_with_available_capacity(self, min_capacity: int = 1) -> List[Stashpoint]:
        """Find stashpoints with at least the specified available capacity"""
        stmt = select(self.model).where(self.model.capacity >= min_capacity)
        result = self.session.execute(stmt)
        return result.scalars().all()
    
    def find_available_stashpoints(
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
        
        # Convert to naive datetime objects for database comparison
        dropoff_time = dropoff_time.replace(tzinfo=None)
        pickup_time = pickup_time.replace(tzinfo=None)
        
        # Extract time portion for opening hours comparison
        # We need to use a different approach to extract just the time part
        dropoff_time_only = dropoff_time.time()  
        pickup_time_only = pickup_time.time()
        
        # First, find all active bookings that overlap with the requested time period
        # Logic: a booking overlaps if:
        # - It's not cancelled
        # - Existing booking drop-off occurs before our pickup time
        # - Existing booking pickup occurs after our drop-off time
        active_bookings_subquery = (
            select(
                Booking.stashpoint_id,
                func.sum(Booking.bag_count).label("booked_bags")
            )
            .where(
                and_(
                    not_(Booking.is_cancelled),
                    Booking.dropoff_time <= pickup_time,
                    Booking.pickup_time >= dropoff_time
                )
            )
            .group_by(Booking.stashpoint_id)
            .subquery()
        )
        
        # Main query to find available stashpoints with distance calculation and available capacity
        stmt = (
            select(
                Stashpoint,
                # Calculate distance in meters and convert to kilometers
                # Note: ST_Distance returns meters for geography type
                (ST_Distance(Stashpoint.location, search_point) / 1000.0).label("distance_km"),
                # Calculate available capacity by subtracting booked bags
                (Stashpoint.capacity - func.coalesce(active_bookings_subquery.c.booked_bags, 0)).label("available_capacity")
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
                    # Using direct string comparison for times
                    func.cast(Stashpoint.open_from, db.String) <= func.cast(dropoff_time_only, db.String),
                    func.cast(Stashpoint.open_until, db.String) >= func.cast(pickup_time_only, db.String)
                )
            )
            .order_by("distance_km")
        )
        
        result = self.session.execute(stmt)
        
        # Process results to build formatted response
        formatted_results = []
        for row in result.all():
            stashpoint = row[0]
            distance_km = row[1]
            available_capacity = row[2]
            
            # Create dictionary with the required fields
            formatted_stashpoint = {
                "id": stashpoint.id,
                "name": stashpoint.name,
                "address": stashpoint.address,
                "latitude": stashpoint.latitude,
                "longitude": stashpoint.longitude,
                "distance_km": round(distance_km, 2),
                "capacity": stashpoint.capacity,
                "available_capacity": available_capacity,
                "open_from": stashpoint.open_from.strftime("%H:%M") if stashpoint.open_from else None,
                "open_until": stashpoint.open_until.strftime("%H:%M") if stashpoint.open_until else None
            }
            
            formatted_results.append(formatted_stashpoint)
            
        return formatted_results