"""This file defines a depo object."""

from location import Location
from delivery import Delivery
from parcel import Parcel
import csv

class Depo(Location):
    def __init__(self, key, name, coords, deliveries):
        self.key = key
        self.name = name
        super(Depo, self).__init__(coords)
        self.deliveries = [Delivery(**delivery) for delivery in deliveries]

    def store(self, parcel: Parcel):
        data = {
            'in_depo': self.name,
            'from_delivery': parcel.dkey,
            'name': parcel.name,
            'weight': parcel.weight,
            'damage': round(parcel.damage, 2)
        }
        file_name = 'records/delivered_parcels.csv'
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