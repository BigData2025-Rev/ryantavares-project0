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
        file_name = f'records/delivery-results.csv'
        completion_rate = num_delivered / self.num_of_parcels
        damage_rate = total_damage / self.num_of_parcels
        minutes_to_complete = round((time_completed - self.time_activated).seconds / 60, 2)
        data = {
            'delivery-key': self.key,
            'completion-rate': completion_rate,
            'damage-rate': damage_rate,
            'minutes-to-complete': minutes_to_complete
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
        print(f"Completion Rate: {completion_rate:.2f}")
        print(f"Damage Rate: {damage_rate:.2f}")
        print(f"Time to Complete: {minutes_to_complete:.2f} minutes")
        print("".center(width, '='))