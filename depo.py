"""This file defines a depo object."""

from delivery import Delivery
from parcel import Parcel
import csv

class Depo:
    def __init__(self, key, name, coords, deliveries):
        self.key = key
        self.name = name
        self.coords = coords
        self.deliveries = [Delivery(**delivery) for delivery in deliveries]

    def distance_to(self, destination_coords):
        a = self.coords['x'] - destination_coords['x']
        b = self.coords['y'] - destination_coords['y']
        return (a**2 + b**2)**0.5

    def store(self, parcel: Parcel):
        data = {
            'in-depo': self.name,
            'from-delivery': parcel.dkey,
            'name': parcel.name,
            'weight': parcel.weight,
            'damage': 0
        }
        file_name = f'records/delivered_parcels.csv'
        with open(file_name, 'a') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=data)
            if outfile.tell() == 0:
                writer.writeheader()
            writer.writerow(data)