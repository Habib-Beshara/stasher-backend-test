find_stashpoints_api_schema = {
    "type": "object",
    "required": ["lat", "lng", "dropoff", "pickup", "bag_count"],
    "properties": {
        "lat": {
            "type": "number",
            "minimum": -90,
            "maximum": 90
        },
        "lng": {
            "type": "number",
            "minimum": -180,
            "maximum": 180
        },
        "dropoff": {
            "type": "string",
            "format": "date-time",
            "description": "ISO datetime string format (e.g. 2023-04-20T10:00:00Z)"
        },
        "pickup": {
            "type": "string",
            "format": "date-time",
            "description": "ISO datetime string format (e.g. 2023-04-20T18:00:00Z)"
        },
        "bag_count": {
            "type": "integer",
            "minimum": 1
        },
        "radius_km": {
            "type": "number",
            "minimum": 0.1,
            "default": 5.0
        }
    }
}