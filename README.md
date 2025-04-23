# Stasher Backend Interview Challenge

Welcome to the Stasher backend interview challenge! This project is a simplified version of our bag storage platform, where travelers can find locations to store their luggage.

## Task Overview

Your task is to implement a search feature that allows users to find available stashpoints (bag storage locations) based on:

- Location (latitude/longitude)
- Desired drop-off and pick-up times
- Number of bags to store

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine
- Git

### Setup

1. Clone this repository
2. Navigate to the project directory
3. Start the application using Docker Compose:

```bash
docker-compose up -d
```

4. The API will be available at `http://localhost:5000`
5. You can verify it's running with:

```bash
curl http://localhost:5000/healthcheck
```

## The Challenge

### Current Functionality

The application already has basic functionality:

- A Stashpoint model that represents bag storage locations
- A Booking model to track bag storage reservations
- An endpoint to list all stashpoints at `/api/v1/stashpoints/`
- Database with test data pre-populated

### Your Task

You need to enhance the stashpoints endpoint to allow filtering by availability. The endpoint should:

1. Accept the following query parameters:

   - `lat` (float): Latitude for the search location
   - `lng` (float): Longitude for the search location
   - `dropoff` (ISO datetime): When the user wants to drop off their bags
   - `pickup` (ISO datetime): When the user wants to pick up their bags
   - `bag_count` (integer): Number of bags to store
   - `radius_km` (float, optional): Search radius in kilometers

2. Return only stashpoints that:

   - Are within the specified radius of the coordinates
   - Have enough capacity for the requested number of bags during the specified time period
   - Are open during the requested drop-off and pick-up times

3. Results should be ordered by distance from the search coordinates

### Example Request

```
GET /api/v1/stashpoints/?lat=51.5074&lng=-0.1278&dropoff=2023-04-20T10:00:00Z&pickup=2023-04-20T18:00:00Z&bag_count=2&radius_km=5
```

### Response Format

The response should be a JSON array of available stashpoints, with each stashpoint containing at least:

```json
[
  {
    "id": "abc123",
    "name": "Central Cafe Storage",
    "address": "123 Main Street",
    "latitude": 51.5107,
    "longitude": -0.1246,
    "distance_km": 0.5,
    "capacity": 20,
    "available_capacity": 15,
    "open_from": "08:00",
    "open_until": "22:00"
  },
  ...
]
```

## Evaluation Criteria

We'll evaluate your solution based on:

- Correctness: Does it return the correct stashpoints?
- Code quality: Is your code clean and well-organized?
- Edge cases: How does your solution handle edge cases?
- Performance: How efficient is your solution?

## Submission

When you're ready, send us your solution as a Git repository. Make sure to include instructions for running your solution if they differ from the above.

You may also submit a README.md to accompany your solution, to explain any decisions made or enhancements you would make with more time.

Good luck!

---

## Solution notes:

- The code for this challenge is in a branch called `test` and there is a pull request made for it. The reason is just because i figured it could be easier to look at the PR.
- Nothing changes on how you run the code. the only change is the branch. so just checkout the branch and then use docker compose to run everything.
- The code is AI generated. Or more accurately, it's translated from a typescript code that i wrote. The structure is mine.
- A couple of things here were made to show structure rather than necessity. for example:
  - The 2 validation layers. In this case both of them are the same which shouldn't be the case, but in this requirement both aren't necessary. I only included the one in the domain layer (use case) to show how i think a more complicated validation should be handled.
  - Response class. I believe there should a form of consistent way to send data to the frontend. but the task had how the response should show up in the first place so eventually i did do the response class but it wasn't necessary
- What I would do to make this better:
  - Add testing
  - Add interfaces
  - Separate the data type transformers into a more proper place (remove the one in the model, make a folder inside the module and add these different types for different api responses).
  - There is probably some way to make the route more compact but I need more knowledge about the language.
  - Modules should encapsulate all of their resources including the model and the routes. So, I would move the model and the router for stashpoints to be inside the stashpoint module.

