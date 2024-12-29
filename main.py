"""The main entry point for the text-based game."""

from exceptions.invalid_input_error import InvalidInputError
from depo import Depo
from delivery import Delivery
from courier import Courier
import datetime as dt
import numpy as np
import pandas as pd
import json

sam = Courier()             # The player.
depos: list[Depo] = []      # Available depos in the world.
now = dt.datetime(year=2024, month=12, day=30, hour=9, minute=0, second=0, microsecond=0)   # The time in the game-world.

def main():
    while game_loaded() == False:
        pass

    # Run until user quits at a depo.
    while True:
        while at_depo() == True:
            pass
        else:
            print(f"*Departing for {sam.destination_depo.pretty_name().upper()}...*\n")
            distance = sam.from_depo.distance_to(sam.destination_depo.coords)
            travel(distance)

def game_loaded():
    try:
        option = input("[N]ew game\n" +
                    "[Q]uit game\n").lower()
        match option:
            case 'n':
                print("Starting a new game...\n")
                new_game()
                return True
            case 'q':
                exit()
            case _:
                raise InvalidInputError(['n', 'q'])
    except InvalidInputError as e:
        print(e)
        return False

def new_game():
    with open("depos.json", 'r') as file:
        depos_json = json.load(file)
        depos.extend([Depo(**object) for object in depos_json])
        starting_depo = depos[0]
    sam.from_depo = starting_depo
    # Clear results data.
    open('records/delivery-results.csv', 'w').close()
    open('records/delivered_parcels.csv', 'w').close()

def at_depo():
    print(f"{sam.from_depo.pretty_name(underline=True)}")
    print(now)
    try:
        option = input("[M]ake delivery\n" +
                    "[T]ake on new deliveries\n" + 
                    "Select [D]estination\n" +
                    "Show [R]esults\n" +
                    "[Q]uit game\n").lower()
        if option == 'm':
            sam.make_delivery(now)
            return True
        elif option == 't':
            select_deliveries(sam.from_depo.deliveries)
            return True
        elif option == 'd':
            if select_destination() == True:
                return False    # Courier is departing
            else:
                return True
        elif option == 'r':
            show_results()
            return True
        elif option == 'q':
            quit()
        else:
            raise InvalidInputError(['m', 't', 'd', 'r', 'q'])
    except InvalidInputError as e:
        print(e)
        return True

def select_deliveries(deliveries: list[Delivery]):
    selected_deliveries = []
    previously_active_deliveries = sam.active_deliveries.copy()
    confirmed = False

    while confirmed == False:
        selectable_deliveries = [delivery for delivery in deliveries if delivery not in sam.active_deliveries]
        # Build prompt.
        prompt = ""
        for delivery in selectable_deliveries:
            prompt = prompt + delivery.title + "\n"
        if len(selected_deliveries) > 0:
            prompt += "[C]onfirm selected deliveries?\n"
        prompt += "[x] to cancel\n"

        # Handle input.
        selectable_delivery_keys = [delivery.key for delivery in selectable_deliveries]
        try:
            option = input(prompt).lower()
            if option == 'c' and len(selected_deliveries) > 0:
                confirmed = True
                print("Deliveries confirmed. Time to load up for departure.")
                for delivery in sam.active_deliveries:
                    delivery.time_activated = now
                load_up(selected_deliveries)
            elif option == 'x':
                sam.active_deliveries = previously_active_deliveries
                return
            elif option in selectable_delivery_keys:
                for delivery in selectable_deliveries:
                    if option == delivery.key:
                        selected_deliveries.append(delivery)
                        sam.active_deliveries.append(delivery)
            else:
                valid_keys = selectable_delivery_keys
                raise InvalidInputError(valid_keys + ['c', 'x']) if len(selected_deliveries) > 0 else InvalidInputError(valid_keys + ['x'])
        except InvalidInputError as e:
            print(e)


def load_up(selected_deliveries: list[Delivery]):
    parcels = []
    for delivery in selected_deliveries:
         parcels.extend(delivery.generate_parcels())
    sam.arrange_parcels(parcels)

def select_destination():
    valid = False

    while valid == False:
        prompt = "Select Destination:\n"
        for depo in depos:
            if depo != sam.from_depo:
                # TODO: Implement a better way to indicate direction and/or location of potential destinations.
                prompt += depo.name + f"\t{sam.from_depo.distance_to(depo.coords):.2f} miles away at ({depo.coords['x']}, {depo.coords['y']})" 
                if depo.name in [delivery.destination for delivery in sam.active_deliveries]:
                    prompt += "\t*ACTIVE DELIVERY*"
                prompt += '\n'
        prompt += '[x] to cancel\n'

        try:
            option = input(prompt).lower()
            for depo in depos:
                if option == depo.key and option != sam.from_depo.key:
                    sam.destination_depo = depo
                    return True
            if option == 'x':
                return False
            else:
                raise InvalidInputError([depo.key for depo in depos if depo is not sam.from_depo] + ['x'])
        except InvalidInputError as e:
            print(e)

def travel(miles):
    # BTT = Base Travel Time (seconds)
    # 1 mile = BTT + 2(BTT) * (TOTAL-WEIGHT / MAX-WEIGHT)
    BTT = 540
    travel_time_sec = round((BTT + (2*BTT) * (sam.carrying_weight / sam.MAX_TOTAL_WEIGHT) * miles))
    miles_per = BTT / (BTT + (2*BTT) * (sam.carrying_weight / sam.MAX_TOTAL_WEIGHT))

    advance_time(travel_time_sec)
    while miles > 0:
        if will_trip():
            trip()
        if miles < miles_per:
            print(f"{miles:.2f} miles traveled")
            miles -= miles
        else:
            miles -= miles_per
            print(f"{miles_per:.2f} miles traveled")
            print(f"{miles:.2f} miles to go")
        input("Enter any key to continue.\n")
    arrival()

def will_trip() -> bool:
    # BTC = Base Trip Chance (%)
    BTC = 0.025
    trip_chance = BTC

    # More weight = more chance to trip (minor)
    trip_chance += BTC * (sam.carrying_weight / sam.MAX_TOTAL_WEIGHT) 

    # Imbalanced weight = more chance to trip (major)
    imbalance = (sam.load['left']['weight'] / sam.MAX_SIDE_WEIGHT) - (sam.load['right']['weight'] / sam.MAX_SIDE_WEIGHT)
    trip_chance += 5*BTC * abs(imbalance)
    return happens_by_chance(trip_chance * 100)

def trip():
    print("You lose your balance!")
    correct_key = ''
    side = ''
    if sam.load['left']['weight'] > sam.load['right']['weight']:
        correct_key = 'r'
        side = 'left'
        option = input("Enter [R] to lean right!\n").lower()
    else:
        correct_key = 'l'
        side = 'right'
        option = input("Enter [L] to lean left!\n").lower()

    if option == correct_key:
        print("You regained your balance!\n")
        advance_time(20)
    else:
        fall(side)

def fall(side):
    DMG_SIDE = .30
    DMG_BACK = .10
    LOSS_CHANCE_SIDE = 0.05
    LOSS_CHANCE_BACK = 0.025

    print(f"You fall to your {side}!")

    # Apply damage to parcels.
    for parcel in sam.load[side]['parcels']:
        parcel.damage += DMG_SIDE
    for parcel in sam.load['back']['parcels']:
        parcel.damage += DMG_BACK

    # Apply percent chance to lose parcels.
    for parcel in sam.load[side]['parcels']:
        if happens_by_chance(LOSS_CHANCE_SIDE * 100):
            sam.remove_parcel(parcel, side)
            print(f"Lost {parcel.name}!")
    for parcel in sam.load['back']['parcels']:
        if happens_by_chance(LOSS_CHANCE_BACK * 100):
            sam.remove_parcel(parcel, 'back')
            print(f"Lost {parcel.name}!")

    advance_time(120)
    print("It takes you some time to recover.")
    print("Some of your parcels took damage and you may have lost a few.\n")
    input("Enter any key to continue.\n")

def happens_by_chance(percent_chance) -> bool:
    if np.random.uniform(0.00, 100.00) <= percent_chance:
        return True
    else:
        return False

def advance_time(seconds_to_add, outside=True):
    if outside:
        apply_time_damage(seconds_to_add)
    global now
    hour = now.hour
    minute = now.minute + (seconds_to_add // 60)
    second = now.second + (seconds_to_add % 60)
    if second > 59:
        minute += 1
        second = second % 60
    if minute > 59:
        hour += 1
        minute = minute % 60
    if hour > 23:
        hour = 0    # For the purposes of this application, the day will simply reset.
    now = now.replace(hour=hour, minute=minute, second=second)

def apply_time_damage(seconds):
    # DPS = parcel damage per second traveled (%)
    DPS = 0.000005
    for side in sam.load:
        for parcel in sam.load[side]['parcels']:
            if parcel.damage + DPS * seconds > 1.00:
                parcel.damage = 1.00
            else:
                parcel.damage += DPS * seconds

def arrival():
    print(f"\n*You've arrived at {sam.destination_depo.pretty_name().upper()}*\n")
    print("Welcome, Sam.")
    if sam.destination_depo.name in [delivery.destination for delivery in sam.active_deliveries]:
        print("Looks like you brought something for us. We'll gladly take it off your hands.\n")
    else:
        print("Before you go, we might have some deliveries you'd be interested in.\n")
    # Update Courier's location.
    sam.from_depo = sam.destination_depo
    sam.destination_depo = None

def show_results():
    UND = "\033[4m"
    END = "\033[0m"
    dr = pd.read_csv('records/delivery-results.csv')
    dp = pd.read_csv('records/delivered_parcels.csv')

    print()
    print("OVERALL GAME RESULTS".center(30, '='))
    input("Enter any key to continue.\n")

    print(UND + "Total Number of Parcels Delivered:" + END)
    print(dp[dp.columns[0]].count())
    input()

    print(UND + "Total Weight of Parcels Delivered:" + END)
    print(dp['weight'].sum())
    input()

    print(UND + "Total Number of Parcels Delivered by Depo:" + END)
    print(dp.groupby(['in_depo'], sort=True)[dp.columns[0]].count().to_string())
    input()

    print(UND + "Total Weight of Parcels Delivered by Depo:" + END)
    print(dp.groupby(['in_depo'], sort=True)['weight'].sum().to_string())
    input()

    print(UND + "Total Number of Each Parcel Delivered:" + END)
    print(dp.groupby(['name'], sort=True)[dp.columns[0]].count().to_string())
    input()

    print(UND + "Total Number of Deliveries Made:" + END)
    print(dr[dr.columns[0]].count())
    input()

    print(UND + "The Number of Deliveries With 100% Completion Rate:" + END)
    print(dr.query('completion_rate == 100.0')[dr.columns[0]].count())
    input()

    print(UND + "Top 5 Fastest Deliveries:" + END)
    print(dr.sort_values(['minutes_to_complete']).head(5).to_string(index=False))
    input()

    print(UND + "Total Number of Parcels Delivered vs. Expected Number of Parcels by Delivery:" + END)
    df = dp.groupby(['from_delivery'], sort=True)[dp.columns[0]].count().to_frame()
    num_expected = np.array([delivery.num_of_parcels for depo in depos for delivery in depo.deliveries])
    num_deliveries = dr.groupby(['delivery_key'], sort=True)[dr.columns[0]].count().values
    expected = num_deliveries * num_expected     # numpy array multiplication
    print(df.assign(expected = expected).rename(columns={'in_depo': 'delivered'}).to_string())
    input()

    print(UND + "S-Rank Deliveries (Completion Rate == 100%, Damage Rate < 5%, Minutes To Complete < 90):" + END)
    print(dr.query("completion_rate == 100.0 & damage_rate < 5.00 & minutes_to_complete < 90").to_string())

    print()
    print("END OF RESULTS".center(30, '='))
    input("Enter any key to continue.\n")

if __name__ == "__main__":
    main()
