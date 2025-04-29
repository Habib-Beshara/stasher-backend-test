from functools import wraps
from flask import request, jsonify
from jsonschema import validate, ValidationError
from app.services.response import Response, Error
from typing import Dict, Any, Callable


def validate_request_middleware(schema: Dict[str, Any], parameter_source='args'):
    """
    Generic API validation middleware that validates request parameters against a schema.
    
    Args:
        schema: The JSON schema to validate against
        parameter_source: Where to find parameters ('args' for query params, 'json' for body)
    
    Returns:
        A decorator function that can be applied to route handlers
    """
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get parameters from the request
            if parameter_source == 'args':
                # For query parameters, convert to the right types
                params = {}
                for key, value in request.args.items():
                    # Try to convert numeric parameters
                    if key in schema.get('properties', {}):
                        prop_type = schema['properties'][key].get('type')
                        try:
                            if prop_type == 'number' or prop_type == 'integer':
                                value = float(value) if prop_type == 'number' else int(value)
                        except (ValueError, TypeError):
                            pass
                    params[key] = value
            elif parameter_source == 'json':
                # For JSON body
                params = request.get_json(silent=True) or {}
            else:
                params = {}
            
            # Create a response object
            response = Response()
            
            # Validate parameters against schema
            try:
                validate(instance=params, schema=schema)
                # Pass validated parameters to the route handler
                return f(*args, **kwargs)
            except ValidationError as e:
                # Handle validation errors
                response.add_error(Error(str(e)))
                response.set_status_code(400)
                return jsonify(response.get_response()), response.status_code
        
        return decorated_function
    
    return decorator