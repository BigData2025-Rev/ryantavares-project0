"""The main entry point for the text-based game."""

from depo import Depo
from delivery import Delivery
from courier import Courier
import json

sam = Courier() # The player
depos = []

def main():
    option = input("[N]ew game\n" +
                   "[Q]uit\n").lower()
    match option:
        case 'n':
            print("Starting a new game...")
            new_game()
        case 'q':
            exit()

def new_game():
    print("Welcome Sam, we have some new deliveries for you:")

    with open("depos.json", 'r') as file:
        depos_json = json.load(file)
        depos.extend([Depo(**object) for object in depos_json])
        starting_depo = depos[0]

    # start
    sam.from_depo = starting_depo
    select_deliveries(sam.from_depo.deliveries)

def select_deliveries(deliveries: list[Delivery]):
    selected_deliveries = []
    confirmed = False

    while confirmed == False:
        # Build prompt.
        prompt = ""
        for delivery in deliveries:
            prompt = prompt + delivery.title + "\n"
        if len(selected_deliveries) > 0:
            prompt += "[C]onfirm selected deliveries?\n"

        # Handle input.
        #   TODO:   Handle removal of selected deliveries before confirmation.
        option = input(prompt).lower()
        if option == 'c' and len(selected_deliveries) > 0:
            confirmed = True
            sam.active_deliveries = selected_deliveries
            print("Deliveries confirmed. Time to load up for departure.")
            load_up(selected_deliveries)
        else:
            for delivery in deliveries:
                if option == delivery.key:
                    selected_deliveries.append(delivery)
                    deliveries.remove(delivery)

def load_up(selected_deliveries: list[Delivery]):
    parcels = []
    for delivery in selected_deliveries:
         parcels.extend(delivery.generate_parcels())
    sam.arrange_parcels(parcels)
    select_destination()

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
        option = input(prompt).lower()
        for depo in depos:
            if option == depo.key and option != sam.from_depo.key:
                sam.destination_depo = depo
                valid = True
    
    distance = sam.from_depo.distance_to(sam.destination_depo.coords)
    print(f"Departing for {sam.destination_depo.name}...\n")
    traverse(distance)

# TODO: Implement traverse()
def traverse(miles):
    print("Traversing...")
    print("...")
    print("...")
    print("...")
    arrival()

def arrival():
    print(f"\n*You've arrived at {sam.destination_depo.name.upper()}*\n")
    print("Welcome, Sam.")
    if sam.destination_depo.name in [delivery.destination for delivery in sam.active_deliveries]:
        print("Looks like you brought something for us. We'll gladly take it off your hands.")
    else:
        print("Before you go, we might have some deliveries you'd be interested in.")
    
    # Update Courier's location.
    sam.from_depo = sam.destination_depo
    sam.destination_depo = None

    at_depo()

# TODO: Implement at_depo()
def at_depo():
    print("[M]ake delivery")
    print("[T]ake on new deliveries")
    print("Select [D]estination")



if __name__ == "__main__":
    main()
