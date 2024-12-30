"""This file defines a delivery object."""

from parcel import Parcel
import datetime as dt
import csv

class Delivery:
    def __init__(self, key, title, name_of_parcels, num_of_parcels, total_weight, destination, time_activated: dt.datetime = None):
        self.key = key
        self.title = title
        self.name_of_parcels = name_of_parcels
        self.num_of_parcels = num_of_parcels
        self.total_weight = total_weight
        self.destination = destination
        self.time_activated = time_activated
    
    def generate_parcels(self) -> list[Parcel]:
        parcels = []
        weight_per = self.total_weight / self.num_of_parcels
        for i in range(self.num_of_parcels):
            parcels.append(Parcel(self.key, self.name_of_parcels, weight_per))
        return parcels
    
    def record(self, num_delivered: int, total_damage: float, time_completed: dt.datetime = None):
        # Write results of the delivery to a csv file.
        file_name = 'records/delivery-results.csv'
        completion_rate = round(num_delivered / self.num_of_parcels * 100, 2)
        damage_rate = round(total_damage / self.num_of_parcels * 100, 2)
        minutes_to_complete = round((time_completed - self.time_activated).seconds / 60, 2)
        data = {
            'delivery_key': self.key,
            'completion_rate': completion_rate,
            'damage_rate': damage_rate,
            'minutes_to_complete': minutes_to_complete
            }
        with open(file_name, 'a') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=data)
            if outfile.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
        
        # Give some immediate information to the user.
        width = 30
        print(f"D{self.key} RESULT".center(width, '='))
        print(f"{num_delivered} / {self.num_of_parcels} {self.name_of_parcels}")
        print(f"Completion Rate: {completion_rate:.2f}%")
        print(f"Damage Rate: {damage_rate:.2f}%")
        print(f"Time to Complete: {minutes_to_complete:.2f} minutes")
        print("".center(width, '='))
        print()

    def pretty_title(self):
        return f"{self.title} ({self.num_of_parcels} {self.name_of_parcels}, {self.total_weight}lb)"