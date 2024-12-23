"""This file defines a depo object."""

from delivery import Delivery

class Depo:
    def __init__(self, name, deliveries):
        self.name = name
        self.deliveries = [Delivery(**delivery) for delivery in deliveries]
