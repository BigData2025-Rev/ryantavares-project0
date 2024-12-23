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
            print(selected_deliveries)
        else:
            for delivery in deliveries:
                if option == delivery.key:
                    selected_deliveries.append(delivery)
                    deliveries.remove(delivery)

def new_game():
    print("Welcome Sam, we have some new deliveries for you:")

    with open("depos.json", 'r') as file:
        depos_json = json.load(file)
        starting_depo = Depo(**depos_json[0])

    # start
    select_deliveries(starting_depo.deliveries)


if __name__ == "__main__":
    main()
