from gedcom.validation import validate_gedcom
from gedcom.GedcomParser import GedcomParser

if __name__ == '__main__':
    print('MAIN CODE HERE')
    gedcom = GedcomParser().parse('test_family.ged')
    gedcom.pretty_print()

    problems = validate_gedcom(gedcom)

    # Print our problems
    print('Problems:', problems)
