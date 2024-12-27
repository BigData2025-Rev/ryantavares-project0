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
            'in_depo': self.name,
            'from_delivery': parcel.dkey,
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
    
    def pretty_name(self, underline=False):
        und = ""
        end = ""
        upp_key = self.key.upper()
        if underline == True:
            und = "\033[4m"
            end = "\033[0m"
        return f"{und}{self.name}{end}".replace(f"[{upp_key}]", f"{upp_key}")