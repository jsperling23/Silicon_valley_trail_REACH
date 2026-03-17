from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    long: float


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


@dataclass(frozen=True)
class Event:
    type: str
    cash: int
    coffee: int
    bugs: int
    morale: int
    hype: int


SIDE_EFFECTS = {
    "Hot": Event("Hot", 0, 0, 5, -5, 0),
    "Mild": Event("Mild", 0, 0, 0, 0, 0),
    "Cold": Event("Cold", 0, -5, 0, -5, 0),
    "Dry": Event("Dry", 0, 0, 0, 0, 0),
    "Wet": Event("Wet", -5, 0, 0, -5, 0)
}


CHOICES = [
    Event("Pitch to an Investor", 10, -5, 0, 10, 0),
    Event("Speak at a Conferece", 0, -5, 0, 0, 10),
    Event("Get Supplies", -10, 20, 0, 0, 0),
    Event("Work on Product", 0, -10, -10, 0, 0),
    Event("Rest", 0, 0, 5, 10, 10)
]


RANDOM_EVENT = [
    Event("Freak Thunderstorm", -20, 0, 0, -20, 0),
    Event("Positive Investor Email", +20, 0, 0, 20, 20),
    Event("Git Force Push to Main", 0, -10, 20, -10, 0),
    Event("AWS Servers Down", 0, -10, 0, -10, -10),
    Event("Influencer Callout", 0, 0, 0, 20, 20),
    Event("Lightbulb Idea", -10, -10, 5, +10, 0),
    Event("Taco Truck!!", -10, 0, 0, 10, 0),
    Event("Waymo Stuck Wrong Way on 280, Traffic Jam!", -10, 0, 0, -20, 0)
]
