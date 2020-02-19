from gedcom.validation import validate_too_old_individual
from gedcom.GedcomParser import GedcomParser


def test_validate_too_old_individual():
    parser = GedcomParser()
    gedcom = parser.parse('../res/family_validation.ged')
    errors = validate_too_old_individual(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: The individual Morgan Freeman (I01) is too old, age = 151.'

