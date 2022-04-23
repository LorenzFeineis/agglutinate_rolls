"""Define the mixed integer program for the task of agglutinating rolls."""
import mip


class AgglutinateRolls(mip.Model):
    """Define a mixed integer program for the task of agglutinating rolls."""

    def __init__(self, instance):
        """Initialize an object of the class MixedIntegerProgram."""
        self.instance = instance
        self.variables = {}

        super().__init__(sense=mip.MINIMIZE)

    def add_objective(self):
        """Add the objective function to the mixed integer program."""
        num_agglutinations = self.add_var(var_type=mip.INTEGER)
        num_rolls = self.add_var(var_type=mip.INTEGER)
        num_short_rolls = self.add_var(var_type=mip.INTEGER)
        num_unused_rolls = self.add_var(var_type=mip.INTEGER)
        variables = [num_agglutinations,
                     num_rolls,
                     num_short_rolls,
                     num_unused_rolls]
        self += mip.xsum(var * cost for var, cost in zip(variables, self.instance['costs']))

        self.variables['num_agglutinations'] = num_agglutinations
        self.variables['num_rolls'] = num_rolls
        self.variables['num_short_rolls'] = num_short_rolls
        self.variables['num_unused_rolls'] = num_unused_rolls
        return 0

    def add_length_restrictions(self):
        """Add one variable that holds the length of each resulting roll."""
        max_length = self.instance['max_length']
        max_number_of_rolls = self.instance['max_number_of_rolls']
        rolls_a = self.instance['rolls_a']
        rolls_b = self.instance['rolls_b']

        # This list contains one variable for each resulting roll
        # The value of the variable corresponds to its length
        length_resulting_rolls = [self.add_var() for i in range(max_number_of_rolls)]

        # The length of each resulting row is limited by a maximum length
        for var in length_resulting_rolls:
            self += var <= max_length

        # The sum over the length of all rolls
        # must not exceed the available material
        self += mip.xsum(var for var in length_resulting_rolls) <= sum(rolls_a)
        self += mip.xsum(var for var in length_resulting_rolls) <= sum(rolls_b)

        self.variables['length_resulting_rolls'] = length_resulting_rolls
        return 0

    def split_material_on_rolls(self):
        """
        Add constraints for each resulting roll.

        Each resulting roll must contain the same amount of material A and B.
        """
        rolls_a = self.instance['rolls_a']
        rolls_b = self.instance['rolls_b']
        length_resulting_rolls = self.variables['length_resulting_rolls']

        # A variable for each resulting row and material roll.
        # The values of the variable correspond to the ratio of the material
        # roll used in the resulting roll
        fraction_per_roll_a = [[self.add_var() for roll in rolls_a] for
                               resulting_roll in length_resulting_rolls]
        fraction_per_roll_b = [[self.add_var() for roll in rolls_b] for
                               resulting_roll in length_resulting_rolls]

        # The ratios must be positive numbers.
        # Constraints (6) - (7)
        for resulting_roll in fraction_per_roll_a:
            for var in resulting_roll:
                self += var >= 0
        for resulting_roll in fraction_per_roll_b:
            for var in resulting_roll:
                self += var >= 0

        # Only 100% of each roll is available:
        # Constraints (10) - (11)
        for j, roll in enumerate(rolls_a):
            self += mip.xsum([fraction_per_roll_a[i][j] for i, resulting_roll in
                              enumerate(length_resulting_rolls)]) <= 1
        for j, roll in enumerate(rolls_b):
            self += mip.xsum([fraction_per_roll_b[i][j] for i, resulting_roll in
                             enumerate(length_resulting_rolls)]) <= 1

        # The length of each roll must coincide with the length of its parts
        # Constraints: (8) - (9)
        for i, resulting_roll in enumerate(length_resulting_rolls):
            self += resulting_roll == mip.xsum(var * length for var, length in
                                               zip(fraction_per_roll_a[i], rolls_a))

        for i, resulting_roll in enumerate(length_resulting_rolls):
            self += resulting_roll == mip.xsum(var * length for var, length in
                                               zip(fraction_per_roll_b[i], rolls_b))

        self.variables['fraction_per_roll_a'] = fraction_per_roll_a
        self.variables['fraction_per_roll_b'] = fraction_per_roll_b
        return 0

    def add_binary_variables(self):
        """Add a binary variable for each continuous variable."""
        rolls_a = self.instance['rolls_a']
        rolls_b = self.instance['rolls_b']
        length_resulting_rolls = self.variables['length_resulting_rolls']

        # A binary variable for each resulting row and material roll.
        # The variables indicate wheter a roll was used in a resulting row.
        rolls_used_a = [[self.add_var(var_type=mip.BINARY) for roll in rolls_a] for
                        resulting_roll in length_resulting_rolls]
        rolls_used_b = [[self.add_var(var_type=mip.BINARY) for roll in rolls_b] for
                        resulting_roll in length_resulting_rolls]

        self.variables['rolls_used_a'] = rolls_used_a
        self.variables['rolls_used_b'] = rolls_used_b
        return 0

    def constrain_binary_variables(self):
        """
        Add constraints for each binary variable.

        Each binary variable should be greater or equal than its continuous
        counterpart.
        Constraints: (12) - (13)
        """
        rolls_used_a = self.variables['rolls_used_a']
        rolls_used_b = self.variables['rolls_used_b']
        fraction_per_roll_a = self.variables['fraction_per_roll_a']
        fraction_per_roll_b = self.variables['fraction_per_roll_b']

        for i, parts in enumerate(fraction_per_roll_a):
            for j, var in enumerate(parts):
                self += rolls_used_a[i][j] >= var

        for i, parts in enumerate(fraction_per_roll_b):
            for j, var in enumerate(parts):
                self += rolls_used_b[i][j] >= var

        return 0

    def constrain_roll_order(self):
        """
        Add constraints that only allow the rolls to be used in a subsequent order.

        Define new binary variables (14).
        Constrain the subsequent order of rolls.
        """
        for i in range(self.instance['max_number_of_rolls']):
            for j, roll in enumerate(self.instance['rolls_a']):
                self.add_var(var_type=mip.BINARY)
