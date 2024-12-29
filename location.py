"""This file defines a location object."""

class Location():
    def __init__(self, coords):
        self.coords = coords

    def distance_to(self, destination_coords):
        a = self.coords['x'] - destination_coords['x']
        b = self.coords['y'] - destination_coords['y']
        return (a**2 + b**2)**0.5
    
    def pretty_coords(self):
        return f"({self.coords['x']}, {self.coords['y']})"