"""This file defines a delivery object."""

class Delivery:
    def __init__(self, key, title, name_of_parcels, num_of_parcels, total_weight, destination):
        self.key = key
        self.title = title
        self.name_of_parcels = name_of_parcels
        self.num_of_parcels = num_of_parcels
        self.total_weight = total_weight
        self.destination = destination
        