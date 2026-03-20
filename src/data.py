from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """
    Represents a geographic location in the game.

    Attributes:
        name (str): The name of the location.
        lat (float): Latitude of the location.
        long (float): Longitude of the location.
        index (int): Index of the location in the game's location list.
    """
    name: str
    lat: float
    long: float
    index: int


LOCATIONS = [
    Location("San Jose",      37.3382, -121.8863, 0),
    Location("Santa Clara",   37.3541, -121.9552, 1),
    Location("Sunnyvale",     37.3688, -122.0363, 2),
    Location("Mountain View", 37.3861, -122.0839, 3),
    Location("Palo Alto",     37.4419, -122.1430, 4),
    Location("Menlo Park",    37.4530, -122.1817, 5),
    Location("Redwood City",  37.4852, -122.3644, 6),
    Location("San Mateo",     37.5630, -122.3255, 7),
    Location("Burlingame",    37.5841, -122.3661, 8),
    Location("South SF",      37.6547, -122.4077, 9),
    Location("San Francisco", 37.7749, -122.4194, 10),
]


@dataclass(frozen=True)
class Event:
    """
    Represents an event that can affect the player's game stats.

    Attributes:
        type (str): The name or type of the event.
        cash (int): Change in cash caused by the event.
        coffee (int): Change in coffee caused by the event.
        bugs (int): Change in bug count caused by the event.
        morale (int): Change in team morale caused by the event.
        hype (int): Change in product hype caused by the event.
        delay (bool): Whether the event prevents the player from moving
                      forward.
        index (int): Index of the event in the game's event table.
    """
    type: str
    cash: int
    coffee: int
    bugs: int
    morale: int
    hype: int
    delay: bool
    index: int


SIDE_EFFECTS = {
    "Hot": Event("Hot", 0, 0, 5, -5, 0, False, 0),
    "Mild": Event("Mild", 0, 0, 0, 0, 0, False, 1),
    "Cold": Event("Cold", 0, -5, 0, -5, 0, False, 2),
    "Dry": Event("Dry", 0, 0, 0, 0, 0, False, 3),
    "Wet": Event("Wet", -5, 0, 0, -5, 0, False, 4)
}


CHOICES = [
    Event("Pitch to an Investor", 10, -10, 0, 10, 0, False, 0),
    Event("Speak at a Conferece", 0, -10, 0, -10, 10, False, 1),
    Event("Get Supplies", -10, 20, 0, 0, 0, False, 2),
    Event("Work on Product", 0, -10, -10, 0, 0, False, 3),
    Event("Rest", 0, 0, 5, 10, 10, False, 4),
    Event("Post Update on LinkedIn", -10, -10, 0, 0, 10, False, 5)
]


RANDOM_EVENT = [
    Event("Freak Thunderstorm", -20, 0, 0, -20, 0, True, 0),
    Event("Positive Investor Email", 20, 0, 0, 20, 20, False, 1),
    Event("Git Force Push to Main", 0, -10, 20, -10, 0, False, 2),
    Event("AWS Servers Down", 0, -10, 0, -10, -10, False, 3),
    Event("Influencer Callout", 0, 0, 0, 20, 20, False, 4),
    Event("Lightbulb Idea", -10, -10, 5, 10, 0, False, 5),
    Event("Taco Truck!!", -10, 0, 0, 10, 0, False, 6),
    Event("Waymo Stuck Wrong Way on 280, Traffic Jam!", -10, 0, 0, -20, 0,
          True, 7)
]
