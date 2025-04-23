from datetime import datetime
from typing import Dict, Any
from app.modules.stashpoints.repository import StashpointRepository
from app.modules.stashpoints.validators.find_stashpoints import find_stashpoints_input_schema
from app.services.response import Response, Error


class FindStashpoints:
    def __init__(
        self,
        stashpoint_repository: StashpointRepository,
        data: Dict[str, Any],
        validation_service
    ):
        self.data = data
        self.stashpoint_repository = stashpoint_repository
        self.validation_service = validation_service
        self.response = Response()

    async def exec(self) -> Response:
        valid = self.validate_input()
        if valid:
            try:
                # Parse ISO datetime strings to datetime objects
                dropoff_time = datetime.fromisoformat(self.data['dropoff'].replace('Z', '+00:00'))
                pickup_time = datetime.fromisoformat(self.data['pickup'].replace('Z', '+00:00'))
                
                # Check if pickup is after dropoff
                if pickup_time <= dropoff_time:
                    self.response.add_error(Error("Pickup time must be after dropoff time"))
                    self.response.set_status_code(400)
                    return self.response
                
                # Check if dropoff is in the future
                now = datetime.utcnow()
                if dropoff_time < now:
                    self.response.add_error(Error("Dropoff time must be in the future"))
                    self.response.set_status_code(400)
                    return self.response
                
                # Call the repository method with validated parameters
                stashpoints = await self.stashpoint_repository.find_available_stashpoints(
                    latitude=float(self.data['lat']),
                    longitude=float(self.data['lng']),
                    dropoff_time=dropoff_time,
                    pickup_time=pickup_time,
                    bag_count=int(self.data['bag_count']),
                    radius_km=float(self.data.get('radius_km', 5.0))
                )
                
                # Convert stashpoints to dictionary for API response
                stashpoints_data = [stashpoint.to_dict() for stashpoint in stashpoints]
                self.response.set_payload({"stashpoints": stashpoints_data})
                
            except Exception as error:
                self.response.add_error(Error(str(error)))
                self.response.set_status_code(500)
        
        return self.response

    def validate_input(self) -> bool:
        validate = self.validation_service.compile(find_stashpoints_input_schema)
        valid = validate(self.data)
        if not valid:
            # Convert validation errors to Error objects
            errors = [Error(error) for error in getattr(validate, 'errors', [])]
            self.response.add_errors(errors)
            self.response.set_status_code(400)
        return valid