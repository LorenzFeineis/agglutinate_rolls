"""Module to run tests on the application."""
from tests import test_model


def main():
    """Run script."""
    test_model.main()
    print('All tests finished successfully!')
    return 0


if __name__ == '__main__':
    main()
