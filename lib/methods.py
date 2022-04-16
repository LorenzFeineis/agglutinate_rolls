"""Class to create and solve the optimization problem."""
import mip
from collections import namedtuple

CluedRole = namedtuple('CluedRole', 'roles_a, roles_b ')

def main():
    """Define main function."""
    role_a = [2350, 9200, 6650, 9150]
    role_b = [2300, 9150, 2850, 3650, 8250]
    roles = (role_a, role_b)
    costs = (2, 8)
    problem = ClueRoles(roles, costs, max_roles=10, max_length=10000)
    problem.solve()


class ClueRoles():
    """Define class for the optimization problem."""

    def __init__(self, roles, costs=(2, 8), max_roles=20, max_length=15000):
        """Initialize object."""
        self.role_a = roles[0]
        self.role_b = roles[1]

        self.num_a = len(self.role_a)
        self.num_b = len(self.role_b)
        self.costs = costs
        # costs = (cost_rollen_verkleben, costs_rollen_tauschen)
        self.max_roles = max_roles
        self.max_length = max_length

    def mixed_integer_linear_program(self):
        """Generate mixed integer program."""
        milp = mip.Model(sense=mip.MINIMIZE)

        ########################
        # DEFINE VARIABLES
        ########################

        # number of times the roles have to be changed
        x_tauschen = milp.add_var(var_type=mip.INTEGER)
        # number of times two roles are clued together
        x_verkleben = milp.add_var(var_type=mip.INTEGER)

        # continuous variables that determine, which roles are clued together
        role_a_clue = [[milp.add_var() for i in range(self.max_roles)]
                       for j in range(self.num_a)]
        role_b_clue = [[milp.add_var() for i in range(self.max_roles)]
                       for j in range(self.num_b)]

        # binary variables, that indicate the resulting roles
        roles_in_use = [milp.add_var(var_type=mip.BINARY)
                        for j in range(self.max_roles)]

        # binary variables that determine, which roles are clued together
        binary_role_a_clued = [[milp.add_var(var_type=mip.BINARY)
                               for i in range(self.max_roles)]
                               for j in range(self.num_a)]
        binary_role_b_clued = [[milp.add_var(var_type=mip.BINARY)
                               for i in range(self.max_roles)]
                               for j in range(self.num_b)]

        # gives for each resulting role the number of roles clued together
        num_clued_roles_a = [milp.add_var(var_type=mip.INTEGER)
                             for j in range(self.max_roles)]
        num_clued_roles_b = [milp.add_var(var_type=mip.INTEGER)
                             for j in range(self.max_roles)]

        #################
        # OBJECTIVE
        #################
        milp += x_verkleben * self.costs[0] + x_tauschen * self.costs[1]

        #####################
        # CONSTRAINTS
        ###################
        part1 = mip.xsum(num_clued_roles_a[j] for j in range(self.max_roles))
        part2 = mip.xsum(num_clued_roles_b[j] for j in range(self.max_roles))
        milp += x_verkleben == part1 + part2
        milp += x_tauschen == mip.xsum(roles_in_use[j]
                                       for j in range(self.max_roles))

        # definition domains
        for j in range(self.max_roles):

            for i in range(self.num_a):
                milp += role_a_clue[i][j] >= 0
                # milp += role_a_clue[i][j] <= 1

                # Wurde Rolle j benutzt
                milp += roles_in_use[j] >= role_a_clue[i][j]

                # binary variables
                milp += binary_role_a_clued[i][j] >= role_a_clue[i][j]

            for i in range(self.num_b):
                milp += role_b_clue[i][j] >= 0
                # milp += role_b_clue[i][j] <= 1

                # binary variables
                milp += binary_role_b_clued[i][j] >= role_b_clue[i][j]

            # Anzahl Klebestellen
            milp += num_clued_roles_a[j] >= 0
            milp += num_clued_roles_b[j] >= 0

            milp += num_clued_roles_a[j] >= mip.xsum(binary_role_a_clued[i][j]
                                                     for i in range(self.num_a)) - 1
            milp += num_clued_roles_b[j] >= mip.xsum(binary_role_b_clued[i][j]
                                                     for i in range(self.num_b)) - 1

            # Length restriction
            milp += mip.xsum(role_a_clue[i][j] * self.role_a[i]
                             for i in range(self.num_a)) == mip.xsum(role_b_clue[i][j] * self.role_b[i] for i in range(self.num_b))

            milp += mip.xsum(role_a_clue[i][j] * self.role_a[i]
                             for i in range(self.num_a)) <= self.max_length

        # Every role can only be used to 100%
        for i in range(self.num_a):
            milp += 1 >= mip.xsum(role_a_clue[i][j]
                                  for j in range(self.max_roles))

        for i in range(self.num_b):
            milp += 1 >= mip.xsum(role_b_clue[i][j]
                                  for j in range(self.max_roles))

        # use as much of the roles as possible
        if sum(self.role_a) <= sum(self.role_b):
            milp += sum(self.role_a) == mip.xsum(
                                        mip.xsum(role_a_clue[i][j]*self.role_a[i]
                                                 for i in range(self.num_a))
                                                 for j in range(self.max_roles))
        else:
            milp += sum(self.role_b) == mip.xsum(
                                        mip.xsum(role_b_clue[i][j]*self.role_b[i]
                                                 for i in range(self.num_b))
                                                 for j in range(self.max_roles))

        return milp, role_a_clue, role_b_clue


    def solve(self):
        """Solve the integer linear program."""
        output = self.mixed_integer_linear_program()
        milp, role_a_clue, role_b_clue = output
        milp.optimize()

        final_roles = []
        print()
        k = 0
        for j in range(self.max_roles):
            print([role_a_clue[i][j].x for i in range(self.num_a)])

        for j in range(self.max_roles):
            if sum([role_a_clue[i][j].x for i in range(self.num_a)]) >= 1e-8:
                k += 1
                print(f'{k}. Rolle:')
                clued_roles_a = []
                for role in range(self.num_a):
                    part_a = role_a_clue[role][j].x * self.role_a[role]
                    clued_roles_a.append(part_a)

                clued_roles_b = []
                for role in range(self.num_b):
                    part_b = role_b_clue[role][j].x * self.role_b[role]
                    clued_roles_b.append(part_b)

                final_roles.append(CluedRole(roles_a=clued_roles_a,
                                             roles_b=clued_roles_b))
                print('Rollen A:')
                print(clued_roles_a)
                print('Rollen B:')
                print(clued_roles_b)

        return final_roles


if __name__ == '__main__':
    main()
