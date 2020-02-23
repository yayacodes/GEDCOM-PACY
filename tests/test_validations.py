from gedcom.validation import *
from gedcom.GedcomParser import GedcomParser

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, 'C:\\Users\\Prathamesh\\Desktop\\GEDCOM-PACY\\gedcom')

def test_validate_too_old_individual():
    parser = GedcomParser()
    gedcom = parser.parse('res/family_validation.ged')
    errors = validate_too_old_individual(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: The individual Morgan Freeman (I01) is too old, age = 151.'


def test_birth_before_death():
    parser = GedcomParser()
    gedcom = parser.parse('res/pete_sprint1_tests.ged')
    errors = birth_before_death(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: The individual Pete (@I1@) has death before birth, death = 1995-06-10 00:00:00, birth = 1996-05-18 00:00:00'

def test_birth_brfore_marriage():
    parser = GedcomParser()
    gedcom = parser.parse('res/pete_sprint1_tests.ged')
    errors = birth_before_marriage(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: The individual Pete (@I1@) has marriage before birth, marriage = 1995-05-06 00:00:00, birth = 1996-05-18 00:00:00'