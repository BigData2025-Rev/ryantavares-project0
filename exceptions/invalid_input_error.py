"""Custom Exception for handling invalid input options."""

class InvalidInputError(Exception):
    def __init__(self, valid_keys: list[str], message=""):
        self.valid_keys = valid_keys            
        
    def __str__(self):
        bold = "\033[1m"
        red = '\033[91m'
        end = "\033[0m"
        return red + bold + "Invalid input. Try: " + ", ".join(self.valid_keys) + end + "\n"