"""This file defines a courier object."""

from parcel import Parcel
from depo import Depo
from delivery import Delivery
from exceptions.invalid_input_error import InvalidInputError
import numpy as np

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
    
    # TODO: Refactor arrange_parcels() to have less duplicate code and better string formatting
    def arrange_parcels(self, parcels: list[Parcel]):
        # Load each parcel onto back, left, or right.
        for parcel in parcels:
            loaded = False
            self.show_inventory()
            while loaded == False:
                try:
                    option = input(f"Load \'{parcel.name}, weight: {parcel.weight}\' onto [B]ack, [L]eft, [R]ight? (or [D]epart without loading remaining items)\n").lower()
                    if option == 'b':
                        if self.load['back']['weight'] + parcel.weight <= self.MAX_BACK_WEIGHT and len(self.load['back']['parcels']) < self.MAX_BACK_ITEMS:
                            self.load['back']['parcels'].append(parcel)
                            self.load['back']['weight'] += parcel.weight
                        loaded = True
                    elif option == 'l':
                        if self.load['left']['weight'] + parcel.weight <= self.MAX_SIDE_WEIGHT and len(self.load['left']['parcels']) < self.MAX_SIDE_ITEMS:
                            self.load['left']['parcels'].append(parcel)
                            self.load['left']['weight'] += parcel.weight
                            loaded = True
                    elif option == 'r':
                        if self.load['right']['weight'] + parcel.weight <= self.MAX_SIDE_WEIGHT and len(self.load['right']['parcels']) < self.MAX_SIDE_ITEMS:
                            self.load['right']['parcels'].append(parcel)
                            self.load['right']['weight'] += parcel.weight
                            loaded = True
                    elif option == 'd':
                        return
                    else:
                        raise InvalidInputError(['b', 'l', 'r', 'd'])
                except InvalidInputError as e:
                    print(e)
            self.carrying_weight = self.load['back']['weight'] + self.load['left']['weight'] + self.load['right']['weight']   
    
    def show_inventory(self):
        print()
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
        BTC = 0.025
        trip_chance = BTC

        # More weight = more chance to trip (minor)
        trip_chance += BTC * (self.carrying_weight / self.MAX_TOTAL_WEIGHT) 

        # Imbalanced weight = more chance to trip (major)
        imbalance = (self.load['left']['weight'] / self.MAX_SIDE_WEIGHT) - (self.load['right']['weight'] / self.MAX_SIDE_WEIGHT)
        trip_chance += 5*BTC * abs(imbalance)
        return self.happens_by_chance(trip_chance * 100)

    def is_falling(self) -> bool:
        print("You lose your balance!")
        correct_key = ''
        side = ''
        if self.load['left']['weight'] > self.load['right']['weight']:
            correct_key = 'r'
            side = 'left'
            option = input("Enter [R] to lean right!\n").lower()
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