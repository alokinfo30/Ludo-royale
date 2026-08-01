import random

class Dice:
    @staticmethod
    def roll() -> int:
        return random.randint(1, 6)

    @staticmethod
    def roll_multiple(n: int) -> list[int]:
        return [Dice.roll() for _ in range(n)]