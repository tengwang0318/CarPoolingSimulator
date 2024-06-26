from data_preprocessing.map_preprocessing.preprocess import find_hexagon
from easydict import EasyDict
from route import Route


class Vehicle:
    def __init__(self,
                 config: EasyDict,
                 vehicle_id: int,
                 current_location: tuple,  # (longitude, latitude)
                 start_time: int,
                 end_time: int,
                 current_speed: float = 11,  # m/s
                 online: bool = True,
                 status: str = "IDLE",  # "IDLE", "FULL", "PARTIALLY_OCCUPIED",
                 ):
        self.config = config
        self.vehicle_id = vehicle_id

        self.current_speed = current_speed
        self.max_capacity = config.Vehicle.max_capacity
        self.current_capacity = 0

        self.current_location = current_location
        lon, lat = current_location
        self.current_position_idx = find_hexagon(lat, lon, config.Environment.resolution)

        self.current_requests = []
        self.next_requests = []

        self.road_idx = None  # build a list to retrieve the index
        self.start_time = start_time
        self.end_time = end_time

        self.online = online
        self.status = status

        self.route = None

    def offline(self):
        self.online = False

    def update_status(self):
        if self.current_capacity == 0:
            self.status = "IDLE"
        elif self.current_capacity < self.max_capacity:
            self.status = "PARTIALLY_OCCUPIED"
        else:
            self.status = "FULL"

    def update_path(self, route: Route):
        self.route = route
