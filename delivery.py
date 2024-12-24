"""This file defines a delivery object."""

from parcel import Parcel

class Delivery:
    def __init__(self, key, title, name_of_parcels, num_of_parcels, total_weight, destination):
        self.key = key
        self.title = title
        self.name_of_parcels = name_of_parcels
        self.num_of_parcels = num_of_parcels
        self.total_weight = total_weight
        self.destination = destination
    
    def generate_parcels(self) -> list[Parcel]:
        parcels = []
        weight_per = self.total_weight / self.num_of_parcels
        for i in range(self.num_of_parcels):
            parcels.append(Parcel(self.name_of_parcels, weight_per))
        return parcels