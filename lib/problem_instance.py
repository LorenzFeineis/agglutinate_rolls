"""Contains the class for a problem instance."""


class AgglutinatingRolls():
    """Define a class for a problem instance."""

    def __init__(self, instance: dict):
        """Initialize an object."""
        self.rolls_a = instance.get('rolls_a', [])
        self.rolls_b = instance.get('rolls_a', [])

        # costs = [agglutinate, new_roll, short_roll, unused_roll]
        self.costs = instance.get('costs', [5, 8, 7, 7])

        self.max_length = instance.get('max_length', 10000)
        self.max_number_of_rolls = instance.get('max_number_of_rolls', 10)
