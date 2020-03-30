from gedcom.validation import validate_gedcom
from gedcom.GedcomParser import GedcomParser

if __name__ == '__main__':
    gedcom = GedcomParser().parse('res/Pete_sprint3_US20_test.ged')
    gedcom.pretty_print()

    problems = validate_gedcom(gedcom)
    for problem in problems:
        print(problem)
