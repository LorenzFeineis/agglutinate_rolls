"""Define the mixed integer program for the task of agglutinating rolls."""
import mip

class MixedIntegerProgram():
    """Define a mixed integer program for the task of agglutinating rolls."""

    def __init__(self, instance):
        """Initialize an object of the class MixedIntegerProgram."""
        self.instance = instance
        self.milp = mip.Model(sense=mip.MINIMIZE)
        self.variables = {}

    def add_objective(self):
        """Add the objective function to the mixed integer program."""
        num_agglutinations = self.milp.add_var(var_type=mip.INTEGER)
        num_rolls = self.milp.add_var(var_type=mip.INTEGER)
        num_short_rolls = self.milp.add_var(var_type=mip.INTEGER)
        num_unused_rolls = self.milp.add_var(var_type=mip.INTEGER)
        variables = [num_agglutinations,
                     num_rolls,
                     num_short_rolls,
                     num_unused_rolls]
        self.milp += mip.xsum(var * cost for
                              var, cost in zip(variables, self.instance['costs']))

        self.variables['num_agglutinations'] = num_agglutinations
        self.variables['num_rolls'] = num_rolls
        self.variables['num_short_rolls'] = num_short_rolls
        self.variables['num_unused_rolls'] = num_unused_rolls
        return 0


    def add_length_restrictions(self):
        """Add one variable that holds the length of each resulting roll."""
        max_length = self.max_length
        max_number_of_rolls = self.instance.max_number_of_rolls
        rolls_a = self.instance.rolls_a
        rolls_b = self.instance.rolls_b

        # This list contains one variable for each resulting roll
        # The value of the variable corresponds to its length
        length_resulting_rolls = [self.milp.add_var() for i in range(max_number_of_rolls)]

        # The length of each resulting row is limited by a maximum length
        for var in length_resulting_rolls:
            milp += var <= max_length

        # The sum over the length of all rolls
        # must not exceed the available material
        self.milp += mip.xsum(var for var in length_resulting_rolls) <= sum(rolls_a)
        self.milp += mip.xsum(var for var in length_resulting_rolls) <= sum(rolls_b)

        self.variables['length_resulting_rolls'] = length_resulting_rolls
        return 0


    def split_material_on_rolls(milp, problem, length_resulting_rolls):
        """
        Add constraints for each resulting roll.

        Each resulting roll must contain the same amount of material A and B.
        """
        rolls_a = problem.rolls_a
        rolls_b = problem.rolls_b

        # A variable for each resulting row and material roll.
        # The values of the variable correspond to the ratio of the material roll
        # used in the resulting roll
        fraction_per_roll_a = [[milp.add_var for roll in rolls_a] for
                               resulting_roll in length_resulting_rolls]
        fraction_per_roll_b = [[milp.add_var for roll in rolls_b] for
                               resulting_roll in length_resulting_rolls]

        # The ratios must be positive numbers.
        # Constraints (6) - (7)
        for resulting_roll in fraction_per_roll_a:
            for var in resulting_roll:
                milp += var >= 0
        for resulting_roll in fraction_per_roll_b:
            for var in resulting_roll:
                milp += var >= 0

        # Only 100% of each roll is available:
        # Constraints (10) - (11)
        for j, roll in enumerate(rolls_a):
            milp += mip.xsum([fraction_per_roll_a[i][j] for
                             i, resulting_roll in
                             enumerate(length_resulting_rolls)]) <= 1
        for j, roll in enumerate(rolls_b):
            milp += mip.xsum([fraction_per_roll_b[i][j] for
                             i, resulting_roll in
                             enumerate(length_resulting_rolls)]) <= 1

        # The length of each roll must coincide with the length of its parts
        # Constraints: (8) - (9)
        for i, resulting_roll in enumerate(length_resulting_rolls):
            milp += resulting_roll == mip.xsum(var * length for
                                               var, length in
                                               zip(fraction_per_roll_a[i], rolls_a))

        for i, resulting_roll in enumerate(length_resulting_rolls):
            milp += resulting_roll == mip.xsum(var * length for
                                               var, length in
                                               zip(fraction_per_roll_b[i], rolls_b))

        return fraction_per_roll_a, fraction_per_roll_b


    def add_binary_variables(milp, problem, length_resulting_rolls):
        """Add a binary variable for each continuous variable."""
        rolls_a = problem.rolls_a
        rolls_b = problem.rolls_b

        # A binary variable for each resulting row and material roll.
        # The variables indicate wheter a roll was used in a resulting row.
        rolls_used_a = [[milp.add_var(var_type=mip.BINARY) for roll in rolls_a] for
                        resulting_roll in length_resulting_rolls]
        rolls_used_b = [[milp.add_var(var_type=mip.BINARY) for roll in rolls_b] for
                        resulting_roll in length_resulting_rolls]

        return rolls_used_a, rolls_used_b


    def constrain_binary_variables(milp,
                                   rolls_used_a,
                                   rolls_used_b,
                                   fraction_per_roll_a,
                                   fraction_per_roll_b):
        """
        Add constraints for each binary variable.

        Each binary variable should be greater or equal than its continuous
        counterpart.
        Constraints: (12) - (13)
        """
        for i, parts in enumerate(fraction_per_roll_a):
            for j, var in enumerate(parts):
                milp += rolls_used_a[i][j] >= var

        for i, parts in enumerate(fraction_per_roll_b):
            for j, var in enumerate(parts):
                milp += rolls_used_b[i][j] >= var

        return 0
