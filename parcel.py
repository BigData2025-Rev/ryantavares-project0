"""This file defines a parcel object."""

class Parcel:
    def __init__(self, dkey, name, weight, damage=0.00):
        self.dkey = dkey
        self.name = name
        self.weight = weight
        self.damage = damage
    
    def __str__(self):
        return f'Parcel(name={self.name}, weight={self.weight}, damage={self.damage})'