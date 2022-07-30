from compliance_suite.constants.constants import COLORS


def print_blue(text):
    print(f'{COLORS["BLUE"]}{text}{COLORS["END"]}')


def print_red(text):
    print(f'{COLORS["RED"]}{text}{COLORS["END"]}')


def print_green(text):
    print(f'{COLORS["GREEN"]}{text}{COLORS["END"]}')


def print_yellow(text):
    print(f'{COLORS["YELLOW"]}{text}{COLORS["END"]}')


def print_underline(text):
    print(f'{COLORS["UNDERLINE"]}{text}{COLORS["END"]}')
