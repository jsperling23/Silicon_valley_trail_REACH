from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    lon: float


LOCATIONS = [
    Location("San Jose",      37.3382, -121.8863),
    Location("Santa Clara",   37.3541, -121.9552),
    Location("Sunnyvale",     37.3688, -122.0363),
    Location("Mountain View", 37.3861, -122.0839),
    Location("Palo Alto",     37.4419, -122.1430),
    Location("Menlo Park",    37.4530, -122.1817),
    Location("Redwood City",  37.4852, -122.3644),
    Location("San Mateo",     37.5630, -122.3255),
    Location("Burlingame",    37.5841, -122.3661),
    Location("South SF",      37.6547, -122.4077),
    Location("San Francisco", 37.7749, -122.4194),
]
