from easydict import EasyDict


class Request:
    def __init__(self,
                 cfg,
                 request_id: int,
                 send_request_timestamp: int,
                 pick_up_position: tuple[float, float],
                 drop_off_position: tuple[float, float],
                 pick_up_idx: int,
                 drop_up_idx: int,
                 itinerary_nodes: list,
                 itinerary_distance: list,
                 itinerary_t: list,
                 original_travel_distance: float,
                 original_travel_time: float,
                 num_persons=1
                 ):
        self.cfg = cfg
        self.request_id = request_id
        self.send_request_timestamp = send_request_timestamp
        self.pick_up_position = pick_up_position
        self.drop_off_position = drop_off_position
        self.pick_up_idx = pick_up_idx
        self.drop_up_idx = drop_up_idx
        self.itinerary_nodes = itinerary_nodes
        self.itinerary_distance = itinerary_distance
        self.itinerary_t = itinerary_t

        self.original_travel_distance = original_travel_distance
        self.original_travel_time = original_travel_time

        self.num_persons = num_persons
        self.max_tolerated_number_persons = self.cfg.CONSTRAINTS.max_tolerated_number_persons

        self.max_tolerated_assign_time = self.cfg.CONSTRAINTS.max_assign_time
        self.cancel_prob_assign = self.cfg.CONSTRAINTS.cancel_prob_assign
        self.max_tolerated_pickup_time = self.cfg.CONSTRAINTS.max_pickup_time
        self.cancel_prob_pickup = self.cfg.CONSTRAINTS.cancel_prob_pickup
        self.max_tolerated_vehicle_capacity = self.cfg.CONSTRAINTS.max_tol_vehicle_capacity

        self.max_tolerated_travel_distance = self.cfg.CONSTRAINTS.max_travel_dis_mul * self.original_travel_distance
        self.max_tolerated_travel_time = self.cfg.CONSTRAINTS.max_travel_time_mul * self.original_travel_time

        self.MAX_DROPOFF_DELAY = self.max_tolerated_travel_time - self.original_travel_time

        self.finish_assign = False
        self.finish_pickup = False
        self.finish_dropoff = False
        self.assign_timepoint = 0
        self.pickup_timepoint = 0
        self.dropoff_timepoint = 0
        self.vehicle_id = None

    def update_route(self, iti_nodes, iti_dis,iti_t):
        self.itinerary_nodes = iti_nodes
        self.itinerary_distance = iti_dis
        self.itinerary_t = iti_t
        self.original_travel_distance = sum(iti_dis)
        self.original_travel_time = sum(iti_t)
        self.max_tolerated_travel_distance = self.cfg.CONSTRAINTS.max_travel_dis_mul * self.original_travel_distance

    # Calculate the price of request
    # We refer to: https://www.introducingnewyork.com/taxis#:~:text=These%20are%20the%20general%20rates%3A%201%20Base%20fare%3A,%28from%204%20pm%20to%208%20pm%29%3A%20US%24%201

    def calculate_price(self, DISCOUNT=0.7):
        initial_charge = 3.0
        mileage_charge = 0.7  # per 322 meters
        waiting_charge = 0.5  # per 60 seconds
        night_surcharge = 1.0 if self.send_request_timestamp > 20 * 3600 or self.send_request_timestamp < 6 * 3600 else 0.0
        peak_hour_price = 1.0 if 16 * 3600 < self.send_request_timestamp < 20 * 3600 else 0.0

        # Calculate total price
        total_price = initial_charge + (self.original_travel_distance / 322) * mileage_charge + (
                self.original_travel_time / 60) * waiting_charge + night_surcharge + peak_hour_price

        # No discount without ride-pooling
        if self.max_tolerated_number_persons == 1:
            discount = 1.0
        else:
            discount = DISCOUNT

        return discount * total_price
