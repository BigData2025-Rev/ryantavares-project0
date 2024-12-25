"""This file defines a depo object."""

from delivery import Delivery

class Depo:
    def __init__(self, key, name, coords, deliveries):
        self.key = key
        self.name = name
        self.coords = coords
        self.deliveries = [Delivery(**delivery) for delivery in deliveries]

    def distance_to(self, destination_coords):
        return (destination_coords['x']**2 + destination_coords['y']**2)**0.5
