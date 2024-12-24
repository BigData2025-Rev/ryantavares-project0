"""This file defines a courier object."""

from parcel import Parcel

class Courier():
    MAX_BACK_ITEMS = 40
    MAX_SIDE_ITEMS = 5
    MAX_TOTAL_ITEMS = MAX_BACK_ITEMS + (MAX_SIDE_ITEMS * 2)
    MAX_BACK_WEIGHT = 140.00
    MAX_SIDE_WEIGHT = 30.00
    MAX_TOTAL_WEIGHT = MAX_BACK_WEIGHT + (MAX_SIDE_WEIGHT * 2)

    def __init__(self, load={}, carrying_weight=0, from_depo=None):
        self.load = load
        self.load['back'] = {'parcels':[], 'weight':0}
        self.load['left'] = {'parcels':[], 'weight':0}
        self.load['right'] = {'parcels':[], 'weight':0}
        self.carrying_weight = carrying_weight
        self.from_depo = from_depo
    
    # TODO: Refactor arrange_parcels() to have less duplicate code and better string formatting
    def arrange_parcels(self, parcels: list[Parcel]):
        # Load each parcel onto back, left, or right.
        for parcel in parcels:
            loaded = False
            while loaded == False:
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
            self.carrying_weight = self.load['back']['weight'] + self.load['left']['weight'] + self.load['right']['weight']

            # Show current load.
            # TODO: Condense Format
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