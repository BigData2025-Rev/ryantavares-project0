"""The main entry point for the text-based game."""

from entities import (Courier, Depo, Delivery)
from exceptions import InvalidInputError
import datetime as dt
import numpy as np
import pandas as pd
import json

sam = Courier()             # The player.
depos: list[Depo] = []      # Available depos in the world.
now = dt.datetime(year=2024, month=12, day=30, hour=6, minute=0, second=0, microsecond=0)   # The time in the game-world.

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
    print(now.strftime('%H:%M:%S'))
    try:
        option = input("[M]ake delivery\n" +
                    "[T]ake on new deliveries\n" + 
                    "Select [D]estination\n" +
                    "Show [R]esults\n" +
                    "[Q]uit game\n").lower()
        print()
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
    selected_deliveries: list[Delivery] = []
    previously_active_deliveries = sam.active_deliveries.copy()
    confirmed = False

    while confirmed == False:
        selectable_deliveries = [delivery for delivery in deliveries if delivery not in sam.active_deliveries]
        # Build prompt.
        prompt = ""
        if len(selectable_deliveries) == 0:
            print("We don't have any more deliveries available, check back later!")
        for delivery in selectable_deliveries:
            prompt = prompt + delivery.pretty_title() + "\n"
        if len(selected_deliveries) > 0:
            prompt += "[C]onfirm selected deliveries?\n"
        prompt += "[x] to cancel\n"

        # Handle input.
        selectable_delivery_keys = [delivery.key for delivery in selectable_deliveries]
        try:
            option = input(prompt).lower()
            print()
            if option == 'c' and len(selected_deliveries) > 0:
                confirmed = True
                print("Deliveries confirmed. Time to load up for departure.\n")
                for delivery in sam.active_deliveries:
                    delivery.time_activated = now
                parcels = [parcel for delivery in selected_deliveries for parcel in delivery.generate_parcels()]
                sam.arrange_parcels(parcels)
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

def select_destination():
    valid = False

    while valid == False:
        prompt = f"Select Destination:\t You are at {sam.from_depo.pretty_coords()}\n"
        for depo in depos:
            if depo != sam.from_depo:
                # TODO: Implement a better way to indicate direction and/or location of potential destinations.
                prompt += depo.name + f"\t{sam.from_depo.distance_to(depo.coords):.2f} miles away at {depo.pretty_coords()}" 
                if depo.name in [delivery.destination for delivery in sam.active_deliveries]:
                    prompt += "\t*ACTIVE DELIVERY*"
                prompt += '\n'
        prompt += '[x] to cancel\n'

        try:
            option = input(prompt).lower()
            print()
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
    # 1 mile = BTT + MULTIPLIER(BTT) * (TOTAL-WEIGHT / MAX-WEIGHT)
    BTT = 540
    MULTIPLIER = 1.25
    travel_time_sec = round((BTT + (MULTIPLIER*BTT) * (sam.carrying_weight / sam.MAX_TOTAL_WEIGHT) * miles))
    miles_per = BTT / (BTT + (MULTIPLIER*BTT) * (sam.carrying_weight / sam.MAX_TOTAL_WEIGHT))

    advance_time(travel_time_sec)
    while miles > 0:
        if sam.will_lose_balance():
            advance_time(20)
            if sam.is_falling():
                advance_time(120)
        if miles < miles_per:
            print(f"{miles:.2f} miles traveled")
            miles -= miles
        else:
            miles -= miles_per
            print(f"{miles_per:.2f} miles traveled")
            print(f"{miles:.2f} miles to go")
        input("Enter any key to continue.\n")
    arrival()

def advance_time(seconds_to_add, outside=True):
    if outside:
        sam.apply_time_damage(seconds_to_add)
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
    try:
        dr = pd.read_csv('records/delivery-results.csv')
        dp = pd.read_csv('records/delivered_parcels.csv')
    except Exception as e:
        print("No results to show. Make some deliveries first!\n")
        return

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

    # Had some trouble with the below data presentation, so it's in a try block to avoid any errors I may have missed.
    try:
        # Get data about number of completed deliveries and their expected total parcel counts.        
        valid_keys = dr['delivery_key'].unique().astype(str)
        num_expected = np.array([delivery.num_of_parcels for depo in depos for delivery in depo.deliveries if delivery.key in valid_keys.tolist()])
        num_deliveries = dr.groupby(['delivery_key'], sort=True)[dr.columns[0]].count().values
        expected = num_deliveries * num_expected     # numpy array multiplication
        data = {
            'dkey': valid_keys,
            'expected': expected,
            'delivery_count': num_deliveries
        }

        # Construct the dataframe for display, merging the total number of delivered parcels.
        df = pd.DataFrame(data)
        df['dkey'] = df['dkey'].astype(int)
        count = dp.merge(df, left_on='from_delivery', right_on='dkey').groupby(['from_delivery'], sort=True)[dp.columns[0]].count().to_frame()
        df = df.merge(count, left_on='dkey', right_on='from_delivery', how='outer')
        df = df.astype('Int64').fillna(0)
        df = df.iloc[:, [0, 3, 1, 2]]  # Reorder the columns
        df = df.rename(columns={'dkey': 'from_delivery', 'in_depo': 'delivered'})
        print(UND + "Total Number of Parcels Delivered vs. Expected Number of Parcels by Delivery:" + END)
        print(df.to_string(index=False))
        input()
    except Exception as e:
        pass

    print(UND + "S-Rank Deliveries (Completion Rate == 100%, Damage Rate < 5%, Minutes To Complete < 90):" + END)
    df = dr.query("completion_rate == 100.0 & damage_rate < 5.00 & minutes_to_complete < 90")
    print(df) if df.empty == False else print("You didn't make any S-Rank deliveries. Sorry!")

    print()
    print("END OF RESULTS".center(30, '='))
    input("Enter any key to continue.\n")

if __name__ == "__main__":
    main()
