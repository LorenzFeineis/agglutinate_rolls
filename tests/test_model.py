"""Test the implementation of the model in lib/model.py."""
from lib import model


def main():
    """Start the test."""
    instance = {'costs': (4, 8, 8, 8),
                'max_length': 1000,
                'max_number_of_rolls': 10,
                'rolls_a': [120, 100, 240],
                'rolls_b': [80, 310, 90]}
    problem = model.AgglutinateRolls(instance)
    problem.add_objective()
    problem.add_length_restrictions()
    problem.split_material_on_rolls()
    problem.add_binary_variables()
    problem.constrain_binary_variables()


if __name__ == '__main__':
    main()
