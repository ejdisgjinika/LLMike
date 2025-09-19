import random

class Wheel():

    def __init__(self, args):
        self.args = args
        self.wheel = [
            "1000$",
            "400$",
            "250$",
            "300$",
            "100$",
            "350$",
            "200$",
            "450$",
            "150$",
            "300$",
            "200$",
            "500$",
            "250$",
            "400$",
            "150$",
            "300$",
            "450$",
            "100$",
            "400$",
            "200$",
        ]
    
    def spin_wheel(self):
        return random.choice(self.wheel)
    

    def get_sectors(self):
        return self.wheel
