class Route:
    def __init__(self, itinerary_nodes, itinerary_segment_dis_list):
        self.itinerary_nodes = itinerary_nodes
        self.itinerary_segment_dis_list = itinerary_segment_dis_list
        self.prefix_sum = self.calculate_prefix_sum()
        self.current_position = 0
        self.current_index = 0

    def calculate_prefix_sum(self):
        prefix_sum = [0] * (len(self.itinerary_segment_dis_list) + 1)
        for i in range(1, len(prefix_sum)):
            prefix_sum[i] = prefix_sum[i - 1] + self.itinerary_segment_dis_list[i - 1]
        return prefix_sum

    def update_position(self, distance_travelled):
        self.current_position += distance_travelled

        while self.current_index < len(self.prefix_sum) - 1 and self.current_position >= self.prefix_sum[
            self.current_index + 1]:
            self.current_index += 1

        self.itinerary_nodes = self.itinerary_nodes[self.current_index:]
        self.itinerary_segment_dis_list = self.itinerary_segment_dis_list[self.current_index:]
        self.prefix_sum = self.prefix_sum[self.current_index:]

    def get_current_node(self):
        return self.itinerary_nodes[0] if self.itinerary_nodes else None

    def get_next_node(self):
        return self.itinerary_nodes[1] if len(self.itinerary_nodes) > 1 else None
