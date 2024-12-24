"""The main entry point for the text-based game."""

from depo import Depo
from delivery import Delivery
from courier import Courier
import json

sam = Courier() # The player

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
        starting_depo = Depo(**depos_json[0])

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

# TODO: Implement select_destination()
def select_destination():
    print("Selecting Destination...")
    print("Departing to [Destination]...")
    #traverse(101)

# TODO: Implement traverse()
def traverse(miles):
    print("Traversing...")
    print("...")
    print("...")
    print("...")
    arrival()

# TODO: Implement arrival()
def arrival():
    print("Welcome, Sam")
    print("Looks like you brought something for us. We'll gladly take it off your hands.")
    at_depo()

# TODO: Implement at_depo()
def at_depo():
    print("[M]ake delivery")
    print("[T]ake on new deliveries")
    print("Select [D]estination")



if __name__ == "__main__":
    main()
