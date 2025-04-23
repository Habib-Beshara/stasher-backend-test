from flask import Blueprint, jsonify, request, current_app
import jsonschema
from app.models.stashpoint import Stashpoint
from app.modules.stashpoints.repository import StashpointRepository
from app.modules.stashpoints.use_cases.find_stashpoints import FindStashpoints
from app.modules.stashpoints.api.validators.find_stashpoints import find_stashpoints_api_schema
from app.services.api_validation_middleware import validate_request_middleware
from app.services.response import Response, Error
from datetime import datetime


bp = Blueprint("stashpoints", __name__)


@bp.route("/", methods=["GET"])
@validate_request_middleware(find_stashpoints_api_schema)
async def get_stashpoints():
    """Find stashpoints based on query parameters"""
    try:
        # Get query parameters
        query_params = {
            'lat': float(request.args.get('lat')),
            'lng': float(request.args.get('lng')),
            'dropoff': request.args.get('dropoff'),
            'pickup': request.args.get('pickup'),
            'bag_count': int(request.args.get('bag_count')),
        }
        
        # Add optional radius if provided
        if 'radius_km' in request.args:
            query_params['radius_km'] = float(request.args.get('radius_km'))
        
        # Get a session from the database engine
        session = current_app.db.session
        
        # Create repository
        stashpoint_repository = StashpointRepository(session)
        
        # Create use case with validation service
        find_stashpoints_use_case = FindStashpoints(
            stashpoint_repository=stashpoint_repository,
            data=query_params,
            validation_service=jsonschema
        )
        
        # Execute use case
        response = await find_stashpoints_use_case.exec()
        
        # Return response
        return jsonify(response.get_response()), response.status_code
        
    except Exception as e:
        # Handle any unexpected errors
        response = Response()
        response.add_error(Error(str(e)))
        response.set_status_code(500)
        return jsonify(response.get_response()), response.status_code
