from gedcom.validation import *
from gedcom.GedcomParser import GedcomParser
from gedcom import validation, Family, Gedcom, Individual
from datetime import datetime

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, 'C:\\Users\\Prathamesh\\Desktop\\GEDCOM-PACY\\gedcom')

def parse_gedcom(file):
    parser = GedcomParser()
    gedcom = parser.parse(file)
    return gedcom

def test_validate_too_old_individual():
    gedcom = parse_gedcom('../res/family_validation.ged')
    errors = validate_too_old_individual(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: US07: The individual Morgan Freeman (I01) is too old, age = 151.'

def test_marriage_before_death():
    gedcom = parse_gedcom('../res/marriage_before_death_test.ged')
    errors = validate_marriage_before_death(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: US05: Family (F01) has the husband Morgan Freeman (I01) death date (01/02/00) before the marriage date (01/01/01)'

def test_divorce_before_death():
    gedcom = parse_gedcom('../res/divorce_before_death_test.ged')
    errors = validate_divorce_before_death(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: US06: Family (F01) has the husband Morgan Freeman (I01) death date (01/02/00) before the divorce date (01/01/01)'

def test_birth_before_death():
    parser = GedcomParser()
    gedcom = parser.parse('../res/pete_sprint1_tests.ged')
    errors = validation.birth_before_death(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: US03: The individual Pete (@I1@) has death before birth, death = 1995-06-10 00:00:00, birth = 1996-05-18 00:00:00'

def test_birth_before_marriage():
    parser = GedcomParser()
    gedcom = parser.parse('../res/pete_sprint1_tests.ged')
    errors = validation.birth_before_marriage(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: US02: The individual Pete (@I1@) has marriage before birth, marriage = 1995-05-06 00:00:00, birth = 1996-05-18 00:00:00'

def test_corresponding_entries():

    def test(individuals, families, input_errors):
      gedcom = Gedcom(individuals=individuals, families=families)
      errors = validation.validate_corresponding_entries(gedcom)
      for error in errors:
        assert error in input_errors
      assert len(errors) == len(input_errors)

    ### CHILDREN ###

    # Family lists child that doesn't exist
    test(
      [], 
      [Family('F01', children=['I01'])],
      ['Error: US26: The family F01 contains child I01, but that individual has no record']
    )

    # Individual lists family that doesn't exist
    test(
      [Individual('I01', child='F01')],
      [], [
        'Error: US26: The individual I01 says they are a child of family F01, but that family has no record'
      ]
    )

    # Individual lists family that doesn't list them
    test(
      [Individual('I01', child='F01')], [Family('F01')],
      [ 'Error: US26: The individual I01 says they are a child of family F01, but that family does not list this individual as a child']
    )

    # Individual lists family as child, family lists another individual as child, other child doesn't exist
    test(
      [Individual(id='I01', child='F01')], 
      [Family(id='F01', children=['I02'])],
      [
        'Error: US26: The individual I01 says they are a child of family F01, but that family does not list this individual as a child',
        'Error: US26: The family F01 contains child I02, but that individual has no record'
      ]
    )

    # Individua lists family as child, family lists another individual as child, other child does not list family
    test(
      [Individual(id='I01', child='F01'), Individual(id='I02')], 
      [Family(id='F01', children=['I02'])],
      [
        'Error: US26: The individual I01 says they are a child of family F01, but that family does not list this individual as a child',
        'Error: US26: The family F01 contains child I02, but that individual does not list this family as a child',
      ]
    )

    # Records line up for one individual one family child
    test(
      [Individual('I01', child='F01')],
      [Family('F01', children=['I01'])],
      []
    )

    # Records line up for two individuals one family child
    test(
      [Individual('I01', child='F01'), Individual('I02', child='F01')],
      [Family('F01', children=['I01', 'I02'])],
      []
    )

    #### SPOUSES #####

    # Individual lists family as spouse, family does not list individual
    test(
      [Individual('I01', spouse='F01')],
      [Family('F01')],
      ['Error: US26: The individual I01 says they are a spouse of family F01, but that family does not list this individual as a spouse']
    )
    # Individual lists family as spouse, family lists another individual who does not exist
    test(
      [Individual('I01', spouse='F01')],
      [Family('F01', husband_id='I02')],
      [
        'Error: US26: The individual I01 says they are a spouse of family F01, but that family does not list this individual as a spouse',
        'Error: US26: The family F01 contains spouse I02, but that individual has no record'
      ]
    )
    # Individual lists family as spouse, family lists another individual, other individual doesn't list family
    test(
      [Individual('I01', spouse='F01'), Individual('I02', spouse='F02')],
      [Family('F01', wife_id='I02')],
      [
        'Error: US26: The individual I01 says they are a spouse of family F01, but that family does not list this individual as a spouse',
        'Error: US26: The family F01 contains spouse I02, but that individual does not list this family as a spouse',
        'Error: US26: The individual I02 says they are a spouse of family F02, but that family has no record'
      ]
    )

    # Family lists individual as spouse, individual does not list family
    test(
      [Individual('I01')],
      [Family('F01', husband_id='I01')],
      [
        'Error: US26: The family F01 contains spouse I01, but that individual does not list this family as a spouse'
      ]
    )
    # Family lists individual as spouse, spouse lists another family that does not exist
    test(
      [Individual('I01', spouse='F02')],
      [Family('F01', husband_id='I01')],
      [
        'Error: US26: The individual I01 says they are a spouse of family F02, but that family has no record',
        'Error: US26: The family F01 contains spouse I01, but that individual does not list this family as a spouse'
      ]
    )
    # Family lists individual as spouse, spouse lists another family, other family doesnt list individual
    test(
      [Individual('I01', spouse='F02')],
      [Family('F01', husband_id='I01'), Family('F02')],
      [
        'Error: US26: The individual I01 says they are a spouse of family F02, but that family does not list this individual as a spouse',
        'Error: US26: The family F01 contains spouse I01, but that individual does not list this family as a spouse'
      ]
    )

    # Records line up for one individual one family spouse
    test(
      [Individual('I01', spouse='F01')],
      [Family('F01', husband_id='I01')],
      []
    )
    test(
      [Individual('I01', spouse='F01')],
      [Family('F01', wife_id='I01')],
      []
    )

    # Records line up for two individuals one family spouse
    test(
      [Individual('I01', spouse='F01'), Individual('I02', spouse='F01')],
      [Family('F01', husband_id='I01', wife_id='I02')],
      []
    )

def test_marriage_after_fourteen():

  # Husband < 14
  individuals = [Individual('I01', spouse='F01', birthday=datetime(2007, 1, 1)), Individual('I02', spouse='F01', birthday=datetime(1997, 6, 18))]
  families = [Family('F01', husband_id='I01', wife_id='I02', married=datetime(2020, 2, 20))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_marriage_after_fourteen(gedcom)
  assert errors[0] == 'Error: US10: Spouse I01 in family F01 was married at less than 14 years old, age=13'
  assert len(errors) == 1

  # Wife < 14
  individuals = [Individual('I01', spouse='F01', birthday=datetime(2007, 1, 1)), Individual('I02', spouse='F01', birthday=datetime(1997, 6, 18))]
  families = [Family('F01', wife_id='I01', husband_id='I02', married=datetime(2020, 2, 20))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_marriage_after_fourteen(gedcom)
  assert errors[0] == 'Error: US10: Spouse I01 in family F01 was married at less than 14 years old, age=13'
  assert len(errors) == 1

  # Husband + Wife < 14
  individuals = [Individual('I01', spouse='F01', birthday=datetime(2007, 1, 1)), Individual('I02', spouse='F01', birthday=datetime(2007, 1, 1))]
  families = [Family('F01', wife_id='I01', husband_id='I02', married=datetime(2020, 2, 20))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_marriage_after_fourteen(gedcom)
  assert errors[0] == 'Error: US10: Spouse I01 in family F01 was married at less than 14 years old, age=13'
  assert errors[1] == 'Error: US10: Spouse I02 in family F01 was married at less than 14 years old, age=13'
  assert len(errors) == 2

  # Husband + Wife > 14
  individuals = [Individual('I01', spouse='F01', birthday=datetime(1997, 6, 18)), Individual('I02', spouse='F01', birthday=datetime(1997, 6, 18))]
  families = [Family('F01', wife_id='I01', husband_id='I02', married=datetime(2020, 2, 20))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_marriage_after_fourteen(gedcom)
  assert len(errors) == 0

  # No marriage --> no errors
  individuals = [Individual('I01', spouse='F01', birthday=datetime(1997, 6, 18)), Individual('I02', spouse='F01', birthday=datetime(1997, 6, 18))]
  families = [Family('F01', wife_id='I01', husband_id='I02')]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_marriage_after_fourteen(gedcom)
  assert len(errors) == 0

def test_marriage_after_divorce():
  # Marriage is after divorce
  individuals = [Individual('I01', spouse='F01'), Individual('I02', spouse='F01')]
  families = [Family('F01', wife_id='I01', husband_id='I02', married=datetime(2000, 10, 10), divorced=datetime(1999, 10, 10))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_marriage_after_divorce(gedcom)
  assert errors[0] == 'Error: US04: Family F01 has divorce date 1999-10-10 before marriage date 2000-10-10'
  assert len(errors) == 1
  
def test_dates_before_current():
  # Marriage date after Today's date
  individuals = [Individual('I01', spouse='F01'), Individual('I02', spouse='F01')]
  families = [Family('F01', wife_id='I01', husband_id='I02', married=datetime(2025, 10, 10))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_dates_before_current(gedcom)
  assert errors[0] == 'Error: US01: The Family F01\'s marriage date 2025-10-10 is after the current date'
  assert len(errors) == 1

  # Divorce date after Today's date
  individuals = [Individual('I01', spouse='F01'), Individual('I02', spouse='F01')]
  families = [Family('F01', wife_id='I01', husband_id='I02', married=datetime(2000, 10, 10), divorced=datetime(2025, 10, 10))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_dates_before_current(gedcom)
  assert errors[0] == 'Error: US01: The Family F01\'s divorce date 2025-10-10 is after the current date'
  assert len(errors) == 1

  # Birthday after Today's date 
  individual = [Individual('I01', birthday=datetime(2025, 10, 10))]
  gedcom = Gedcom(individuals=individual)
  errors = validation.validate_dates_before_current(gedcom)
  assert errors[0] == 'Error: US01: The Individual I01\'s birthday 2025-10-10 is after the current date'
  assert len(errors) == 1

  # Deathdate after Today's date
  individual = [Individual('I01', birthday=datetime(1999, 10, 10), death=datetime(2025, 10, 10))]
  gedcom = Gedcom(individuals=individual)
  errors = validation.validate_dates_before_current(gedcom)
  assert errors[0] == 'Error: US01: The Individual I01\'s deathdate 2025-10-10 is after the current date'
  assert len(errors) == 1
  
def test_fewer_than_15_sibs():
  # Family has more than 15 siblings
  families = [Family('F01', wife_id='I01', husband_id='I02', children = (['I01']*16))]
  gedcom = Gedcom(individuals=None, families=families)
  errors = validation.validate_fewer_than_15_sibs(gedcom)
  assert errors[0] == 'Error: US15: Family F01 has more than 15 siblings'
  assert len(errors) == 1

def test_validate_no_bigamy():
  # Spouse 1 and Spouse 2 each don't have another marriage
  families = [ Family('f01', married=datetime(2000, 10, 10), husband_id='i01', wife_id='i02') ]
  individuals = [
    Individual('i01', spouses=['f01']),
    Individual('i02', spouses=['f01'])
  ]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_no_bigamy(gedcom)
  assert len(errors) == 0

  # Spouse 1 got married to Spouse 3 during still-existing marriage to Spouse 2
  families = [ 
    Family('f01', married=datetime(2000, 10, 10), husband_id='i01', wife_id='i02'),
    Family('f02', married=datetime(2005, 10, 10), husband_id='i01', wife_id='i03')
  ]

  individuals = [
    Individual('i01', spouses=['f01', 'f02']),
    Individual('i02', spouses=['f01']),
    Individual('i03', spouses=['f02'])
  ]

  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_no_bigamy(gedcom)
  assert errors[0] == 'Error: US11: Individual i01 married i03 on 10-10-2005, which was during their marriage to i02'
  assert len(errors) == 1

  # Spouse 1 got married to spouse 3 during marriage to spouse 2
  # families = [ 
  #   Family('f01', married=datetime(2000, 10, 10), divorced=datetime(2010, 10, 10), husband_id='i01', wife_id='i02'),
  #   Family('f02', married=datetime(2005, 10, 10), husband_id='i01', wife_id='i03')
  # ]

  # individuals = [
  #   Individual('i01', spouses=['f01', 'f02']),
  #   Individual('i02', spouses=['f01']),
  #   Individual('i03', spouses=['f02'])
  # ]

  # gedcom = Gedcom(individuals=individuals, families=families)
  # errors = validation.validate_no_bigamy(gedcom)
  # assert errors[0] == 'Error: US11: Individual i01 married i03 on 10-10-2005, which was during their marriage to i02'
  # assert len(errors) == 1

  # Spouse 1 married Spouse 2, got divorced, and then married Spouse 3
  families = [ 
    Family('f01', married=datetime(2000, 10, 10), divorced=datetime(2010, 10, 10), husband_id='i01', wife_id='i02'),
    Family('f02', married=datetime(2012, 10, 10), husband_id='i01', wife_id='i03')
  ]

  individuals = [
    Individual('i01', spouses=['f01', 'f02']),
    Individual('i02', spouses=['f01']),
    Individual('i03', spouses=['f02'])
  ]

  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_no_bigamy(gedcom)
  assert len(errors) == 0