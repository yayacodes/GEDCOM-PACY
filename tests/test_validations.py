from gedcom.validation import *
from gedcom.GedcomParser import GedcomParser


def parse_gedcom(file):
    parser = GedcomParser()
    gedcom = parser.parse(file)
    return gedcom

def test_validate_too_old_individual():
    gedcom = parse_gedcom('../res/family_validation.ged')
    errors = validate_too_old_individual(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: The individual Morgan Freeman (I01) is too old, age = 151.'


def test_marriage_before_death():
    gedcom = parse_gedcom('../res/marriage_before_death_test.ged')
    errors = validate_marriage_before_death(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: Family (F01) has the husband Morgan Freeman (I01) death date (01/02/00) before the marriage date (01/01/01)'


def test_divorce_before_death():
    gedcom = parse_gedcom('../res/divorce_before_death_test.ged')
    errors = validate_divorce_before_death(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: Family (F01) has the husband Morgan Freeman (I01) death date (01/02/00) before the divorce date (01/01/01)'




