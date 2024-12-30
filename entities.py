"""This module contains all of the class definitions for the entities of the game."""

from exceptions import InvalidInputError
import datetime as dt
import csv
import numpy as np


class Parcel:
    def __init__(self, dkey, name, weight, damage=0.00):
        self.dkey = dkey
        self.name = name
        self.weight = weight
        self.damage = damage
    
    def __str__(self):
        return f'Parcel(name={self.name}, weight={self.weight}, damage={self.damage})'
    

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


class Location():
    def __init__(self, coords):
        self.coords = coords

    def distance_to(self, destination_coords):
        a = self.coords['x'] - destination_coords['x']
        b = self.coords['y'] - destination_coords['y']
        return (a**2 + b**2)**0.5
    
    def pretty_coords(self):
        return f"({self.coords['x']}, {self.coords['y']})"


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
    

class Courier():
    MAX_BACK_ITEMS = 40
    MAX_SIDE_ITEMS = 5
    MAX_TOTAL_ITEMS = MAX_BACK_ITEMS + (MAX_SIDE_ITEMS * 2)
    MAX_BACK_WEIGHT = 140.00
    MAX_SIDE_WEIGHT = 30.00
    MAX_TOTAL_WEIGHT = MAX_BACK_WEIGHT + (MAX_SIDE_WEIGHT * 2)

    def __init__(self, load={}, carrying_weight=0, active_deliveries: list[Delivery]=[], from_depo: Depo=None, destination_depo: Depo=None):
        self.load = load
        self.load['back'] = {'parcels':[], 'weight':0}
        self.load['left'] = {'parcels':[], 'weight':0}
        self.load['right'] = {'parcels':[], 'weight':0}
        self.carrying_weight = carrying_weight
        self.active_deliveries = active_deliveries
        self.from_depo = from_depo
        self.destination_depo = destination_depo

    def make_delivery(self, time_completed):
        previously_active_deliveries = self.active_deliveries.copy()
        for delivery in previously_active_deliveries:
            if self.from_depo.name == delivery.destination:
                num_delivered = 0
                total_damage = 0.00
                for side in self.load:
                    for parcel in [parcel_for for parcel_for in self.load[side]['parcels'] if parcel_for.dkey == delivery.key]:
                        self.from_depo.store(parcel)
                        num_delivered += 1
                        total_damage += parcel.damage
                        self.remove_parcel(parcel, side)
                delivery.record(num_delivered, total_damage, time_completed)
                self.active_deliveries.remove(delivery)

    def remove_parcel(self, parcel, side):
        self.load[side]['parcels'].remove(parcel)
        self.load[side]['weight'] -= parcel.weight
        self.carrying_weight -= parcel.weight

    def add_parcel(self, parcel, side):
        self.load[side]['parcels'].append(parcel)
        self.load[side]['weight'] += parcel.weight
        self.carrying_weight += parcel.weight
    
    def arrange_parcels(self, parcels: list[Parcel]):
        # Load each parcel onto back, left, or right.
        for parcel in parcels:
            loaded = False
            self.show_inventory()
            while loaded == False:
                try:
                    option = input(f"Load \'{parcel.name}, weight: {parcel.weight}lb\' onto [B]ack, [L]eft, [R]ight? (or [D]epart without loading remaining items)\n").lower()
                    print()
                    if option == 'b':
                        if self.load['back']['weight'] + parcel.weight <= self.MAX_BACK_WEIGHT and len(self.load['back']['parcels']) < self.MAX_BACK_ITEMS:
                            self.add_parcel(parcel, 'back')
                            loaded = True
                    elif option == 'l':
                        if self.load['left']['weight'] + parcel.weight <= self.MAX_SIDE_WEIGHT and len(self.load['left']['parcels']) < self.MAX_SIDE_ITEMS:
                            self.add_parcel(parcel, 'left')
                            loaded = True
                    elif option == 'r':
                        if self.load['right']['weight'] + parcel.weight <= self.MAX_SIDE_WEIGHT and len(self.load['right']['parcels']) < self.MAX_SIDE_ITEMS:
                            self.add_parcel(parcel, 'right')
                            loaded = True
                    elif option == 'd':
                        return
                    else:
                        raise InvalidInputError(['b', 'l', 'r', 'd'])
                except InvalidInputError as e:
                    print(e)
    
    # TODO: Refactor show_inventory() to have better string formatting
    def show_inventory(self):
        print(f"Total Weight: {self.carrying_weight}lb / {self.MAX_TOTAL_WEIGHT}lb\n" +
                f"Total Number: {len(self.load['back']['parcels']) + len(self.load['left']['parcels']) + len(self.load['right']['parcels'])}/{self.MAX_TOTAL_ITEMS}")
        print(f"\tOn Back ({self.load['back']['weight']}lb / {self.MAX_BACK_WEIGHT}lb; {len(self.load['back']['parcels'])}/{self.MAX_BACK_ITEMS}):")
        for parcel in self.load['back']['parcels']:
            print(f"\t\t{parcel.name} {parcel.weight}lb")
        print(f"\tOn Left ({self.load['left']['weight']}lb / {self.MAX_SIDE_WEIGHT}lb; {len(self.load['left']['parcels'])}/{self.MAX_SIDE_ITEMS}):")
        for parcel in self.load['left']['parcels']:
            print(f"\t\t{parcel.name} {parcel.weight}lb")
        print(f"\tOn Right ({self.load['right']['weight']}lb / {self.MAX_SIDE_WEIGHT}lb; {len(self.load['right']['parcels'])}/{self.MAX_SIDE_ITEMS}):")
        for parcel in self.load['right']['parcels']:
            print(f"\t\t{parcel.name} {parcel.weight}lb")
        print()

    def will_lose_balance(self) -> bool:
        # BTC = Base Trip Chance (%)
        BTC = 0.100
        trip_chance = BTC

        # More weight = more chance to trip (minor)
        trip_chance += BTC * (self.carrying_weight / self.MAX_TOTAL_WEIGHT) 

        # Imbalanced weight = more chance to trip (major)
        imbalance = (self.load['left']['weight'] / self.MAX_SIDE_WEIGHT) - (self.load['right']['weight'] / self.MAX_SIDE_WEIGHT)
        trip_chance += 5*BTC * abs(imbalance)
        return self.happens_by_chance(trip_chance * 100)

    def is_falling(self) -> bool:
        BASE = 0.50
        left_chance = BASE
        right_chance = BASE

        print("You lose your balance!")
        correct_key = ''
        side = ''
        if self.load['left']['weight'] > self.load['right']['weight']:
            left_chance += 0.30
        else:
            right_chance += 0.30

        i = 0
        MAX_ATTEMPTS = 30
        while i < MAX_ATTEMPTS:
            if self.happens_by_chance(left_chance * 100):
                correct_key = 'r'
                side = 'left'
                option = input("Enter [R] to lean right!\n").lower()
                break
            elif self.happens_by_chance(right_chance * 100):
                correct_key = 'l'
                side = 'right'
                option = input("Enter [L] to lean left!\n").lower()
                break
        else:
            correct_key = 'l'
            side = 'right'
            option = input("Enter [L] to lean left!\n").lower()

        if option == correct_key:
            print("You regained your balance!\n")
            return False
        else:
            self.fall(side)
            return True

    def fall(self, side):
        DMG_SIDE = .30
        DMG_BACK = .10
        LOSS_CHANCE_SIDE = 0.05
        LOSS_CHANCE_BACK = 0.025

        print(f"You fall to your {side}!")

        # Apply damage to parcels.
        for parcel in self.load[side]['parcels']:
            parcel.damage += DMG_SIDE
        for parcel in self.load['back']['parcels']:
            parcel.damage += DMG_BACK

        # Apply percent chance to lose parcels.
        for parcel in self.load[side]['parcels']:
            if self.happens_by_chance(LOSS_CHANCE_SIDE * 100):
                self.remove_parcel(parcel, side)
                print(f"Lost {parcel.name}!")
        for parcel in self.load['back']['parcels']:
            if self.happens_by_chance(LOSS_CHANCE_BACK * 100):
                self.remove_parcel(parcel, 'back')
                print(f"Lost {parcel.name}!")

        print("It takes you some time to recover.")
        print("Some of your parcels took damage and you may have lost a few.\n")
        input("Enter any key to continue.\n")

    def apply_time_damage(self, seconds):
        # DPS = parcel damage per second traveled (%)
        DPS = 0.000005
        for side in self.load:
            for parcel in self.load[side]['parcels']:
                if parcel.damage + DPS * seconds > 1.00:
                    parcel.damage = 1.00
                else:
                    parcel.damage += DPS * seconds

    # TODO: Move to happens_by_chance to another class.
    def happens_by_chance(self, percent_chance) -> bool:
        if np.random.uniform(0.00, 100.00) <= percent_chance:
            return True
        else:
            return False