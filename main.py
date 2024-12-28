"""The main entry point for the text-based game."""

from exceptions.invalid_input_error import InvalidInputError
from depo import Depo
from delivery import Delivery
from courier import Courier
import datetime as dt
import json

sam = Courier()             # The player.
depos = []                  # Available depos in the world.
# TODO: Implement global in-game world time.

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
            traverse(distance)

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

def at_depo():
    print(f"{sam.from_depo.pretty_name(underline=True)}")

    try:
        option = input("[M]ake delivery\n" +
                    "[T]ake on new deliveries\n" + 
                    "Select [D]estination\n" +
                    "[Q]uit game\n").lower()
        if option == 'm':
            sam.make_delivery(dt.datetime.today())
            return True
        elif option == 't':
            select_deliveries(sam.from_depo.deliveries)
            return True
        elif option == 'd':
            if select_destination() == True:
                return False    # Courier is departing
            else:
                return True
        elif option == 'q':
            quit()
        else:
            raise InvalidInputError(['m', 't', 'd', 'q'])
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
                    delivery.time_activated = dt.datetime.today()
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


# TODO: Implement traverse()
def traverse(miles):
    print("Traversing...")
    print("...")
    print("...")
    print("...")
    arrival()

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


if __name__ == "__main__":
    main()
