"""The main entry point for the text-based game."""

from depo import Depo
from delivery import Delivery
import json

def main():
    option = input("[N]ew game\n" +
                   "[Q]uit\n")
    match option.lower():
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
    select_deliveries(starting_depo.deliveries)

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
        option = input(prompt)
        if option == 'c':
            confirmed = True
            print("Deliveries confirmed. Time to load up for departure.")
            arrange_parcels(selected_deliveries)
        else:
            for delivery in deliveries:
                if option == delivery.key:
                    selected_deliveries.append(delivery)
                    deliveries.remove(delivery)

# TODO: Implement arrange_parcels()
def arrange_parcels(selected_deliveries: list[Delivery]):
    print("Arranging parcels")
    print(selected_deliveries)
    select_destination()

# TODO: Implement select_destination()
def select_destination():
    print("Selecting Destination...")
    print("Departing to [Destination]...")
    traverse(101)

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
