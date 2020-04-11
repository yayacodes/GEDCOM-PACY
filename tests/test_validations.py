from gedcom.validation import *
from gedcom.GedcomParser import GedcomParser
from gedcom import validation, Family, Gedcom, Individual
from datetime import datetime, timedelta

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
      [Individual('I01', spouses=['F01'])],
      [Family('F01')],
      ['Error: US26: The individual I01 says they are a spouse of family F01, but that family does not list this individual as a spouse']
    )
    # Individual lists family as spouse, family lists another individual who does not exist
    test(
      [Individual('I01', spouses=['F01'])],
      [Family('F01', husband_id='I02')],
      [
        'Error: US26: The individual I01 says they are a spouse of family F01, but that family does not list this individual as a spouse',
        'Error: US26: The family F01 contains spouse I02, but that individual has no record'
      ]
    )
    # Individual lists family as spouse, family lists another individual, other individual doesn't list family
    test(
      [Individual('I01', spouses=['F01']), Individual('I02', spouses=['F02'])],
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
      [Individual('I01', spouses=['F02'])],
      [Family('F01', husband_id='I01')],
      [
        'Error: US26: The individual I01 says they are a spouse of family F02, but that family has no record',
        'Error: US26: The family F01 contains spouse I01, but that individual does not list this family as a spouse'
      ]
    )
    # Family lists individual as spouse, spouse lists another family, other family doesnt list individual
    test(
      [Individual('I01', spouses=['F02'])],
      [Family('F01', husband_id='I01'), Family('F02')],
      [
        'Error: US26: The individual I01 says they are a spouse of family F02, but that family does not list this individual as a spouse',
        'Error: US26: The family F01 contains spouse I01, but that individual does not list this family as a spouse'
      ]
    )

    # Records line up for one individual one family spouse
    test(
      [Individual('I01', spouses=['F01'])],
      [Family('F01', husband_id='I01')],
      []
    )
    test(
      [Individual('I01', spouses=['F01'])],
      [Family('F01', wife_id='I01')],
      []
    )

    # Records line up for two individuals one family spouse
    test(
      [Individual('I01', spouses=['F01']), Individual('I02', spouses=['F01'])],
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

def test_correct_gender():
  # Husband is female or anything other than male
  families = [ Family('F01', married=datetime(1999, 9, 9), husband_id='I01', wife_id='I02')]
  individuals = [
    Individual('I01', spouses=['F01'], sex='X'),
    Individual('I02', spouses=['F01'], sex='F')
  ]
  gedcom = Gedcom(individuals = individuals, families = families)
  errors = validation.validate_correct_gender(gedcom)
  assert errors[0] == 'Error: US21: Husband I01 in Family F01 should be male'
  assert len(errors) == 1

  # Wife is male or anything other than female
  families = [ Family('F01', married=datetime(1999, 9, 9), husband_id='I01', wife_id='I02')]
  individuals = [
    Individual('I01', spouses=['F01'], sex='M'),
    Individual('I02', spouses=['F01'], sex='X')
  ]
  gedcom = Gedcom(individuals = individuals, families = families)
  errors = validation.validate_correct_gender(gedcom)
  assert errors[0] == 'Error: US21: Wife I02 in Family F01 should be female'
  assert len(errors) == 1

  # Both Husband and wife are not male and female respectively
  families = [ Family('F01', married=datetime(1999, 9, 9), husband_id='I01', wife_id='I02')]
  individuals = [
    Individual('I01', spouses=['F01'], sex='X'),
    Individual('I02', spouses=['F01'], sex='X')
  ]
  gedcom = Gedcom(individuals = individuals, families = families)
  errors = validation.validate_correct_gender(gedcom)
  assert errors[0] == 'Error: US21: Husband I01 in Family F01 should be male'
  assert errors[1] == 'Error: US21: Wife I02 in Family F01 should be female'
  assert len(errors) == 2

  # Both Husband and Wife are correct gender
  families = [ Family('F01', married=datetime(1999, 9, 9), husband_id='I01', wife_id='I02')]
  individuals = [
    Individual('I01', spouses=['F01'], sex='M'),
    Individual('I02', spouses=['F01'], sex='F')
  ]
  gedcom = Gedcom(individuals = individuals, families = families)
  errors = validation.validate_correct_gender(gedcom)
  assert len(errors) == 0
  
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
  families = [ 
    Family('f01', married=datetime(2000, 10, 10), divorced=datetime(2010, 10, 10), husband_id='i01', wife_id='i02'),
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


def test_validate_male_last_names_all_last_names_valid():
    families = [Family('F01', married=datetime(2000, 10, 10), husband_id='I01', wife_id='I02', children=['I03', 'I04'])]
    individuals = [
        Individual('I01', first_name='Morgan', last_name='Freeman'),
        Individual('I03', first_name='David', last_name='Freeman', sex='M'),
        Individual("I04", first_name='Sarah', last_name='Freeman', sex="F")
    ]

    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_male_last_last_name(gedcom)
    assert len(errors) == 0


def test_validate_male_last_names_invalid_last_name():
    families = [Family('F01', married=datetime(2000, 10, 10), husband_id='I01', wife_id='I02', children=['I03', 'I04'])]
    individuals = [
        Individual('I01', first_name='Morgan', last_name='Freeman'),
        Individual('I03', first_name='David', last_name='Mike', sex="M"),
        Individual('I04', first_name='Sarah', last_name='Mike', sex="F")
    ]

    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_male_last_last_name(gedcom)
    assert len(errors) == 1
    assert errors[0] == "Error: US16: Individual I03 last name (Mike) doesn't follow the family last name (Freeman)"


def test_validate_male_last_names_invalid_last_name_no_father():
    families = [Family('F01', married=datetime(2000, 10, 10), wife_id='I02', children=['I03', 'I04'])]
    individuals = [
        Individual('I03', first_name='David', last_name='Freeman', sex='M'),
        Individual('I04', first_name='Mike', last_name='Mike', sex='M')
    ]

    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_male_last_last_name(gedcom)
    assert len(errors) == 1
    assert errors[0] == "Error: US16: Individual I04 last name (Mike) doesn't follow the family last name (Freeman)"
def test_validate_sibling_spacing_more_than_8_month():
    families = [Family('F01', married=datetime(2000, 10, 10), children=['I01', 'I02'])]
    individuals = [
        Individual('I01', name='Morgan Freeman', birthday=datetime(2010, 1, 1)),
        Individual('I02', name='David Freeman', birthday=datetime(2010, 10, 1)),
    ]
    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_sibling_spacing(gedcom)
    assert len(errors) == 0


def test_validate_sibling_spacing_less_than_2_days():
    families = [Family('F01', married=datetime(2000, 10, 10), children=['I01', 'I02'])]
    individuals = [
        Individual('I01', name='Morgan Freeman', birthday=datetime(2010, 1, 1)),
        Individual('I02', name='David Freeman', birthday=datetime(2010, 1, 2)),
    ]
    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_sibling_spacing(gedcom)
    assert len(errors) == 0


def test_validate_sibling_spacing_unrealistic():
    families = [Family('F01', married=datetime(2000, 10, 10), children=['I01', 'I02', 'I03'])]
    individuals = [
        Individual('I01', name='Morgan Freeman', birthday=datetime(2010, 1, 1)),
        Individual('I02', name='David Freeman', birthday=datetime(2010, 5, 3)),
        Individual('I03', name='Sarah Freeman', birthday=datetime(2010, 10, 3))
    ]
    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_sibling_spacing(gedcom)
    assert len(errors) == 2
    assert errors[0] == "Error: US13: Child Morgan Freeman (I01) in family F01 has unrealistic birthday gap (122 days) to his sibling David Freeman (I02)"
    assert errors[1] == "Error: US13: Child David Freeman (I02) in family F01 has unrealistic birthday gap (153 days) to his sibling Sarah Freeman (I03)"


def test_validate_parents_not_too_old():
  gedcom = parse_gedcom('../res/pete_Sprint2_test.ged')
  errors = validate_parents_not_too_old(gedcom)
  assert len(errors) == 6
  assert errors[0] == 'Error: US12: parents Shawn Cena/Amanda Something too old for child John Cena'
  assert errors[1] == 'Error: US12: parents Shawn Cena/Amanda Something too old for child Dwane Cena'
  assert errors[2] == 'Error: US12: parents Shawn Cena/Amanda Something too old for child Kane Cena'
  assert errors[3] == 'Error: US12: parents Shawn Cena/Amanda Something too old for child Raymisterio Cena'
  assert errors[4] == 'Error: US12: parents Shawn Cena/Amanda Something too old for child Ronda Cena'
  assert errors[5] == 'Error: US12: parents Shawn Cena/Amanda Something too old for child Bigshow Cena'

def test_validate_multiple_births():
  gedcom = parse_gedcom('../res/pete_Sprint2_test.ged')
  errors = validate_multiple_births(gedcom)
  assert len(errors) == 1
  assert errors[0] == 'Error: US14: For family with id @F1@ there are more than 5 births at the same time'


def test_validate_unique_first_name_in_family_error():
    families = [Family('F01', married=datetime(2000, 10, 10), children=['I01', 'I02'])]
    individuals = [
        Individual('I01', first_name='Morgan'),
        Individual('I02', first_name='Morgan'),
    ]
    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_unique_first_name_in_family(gedcom)
    assert len(errors) == 1
    assert errors[0] == "Error: US25: Family with id F01 has two children with the same first name 'Morgan'"


def test_validate_unique_first_name_in_family_valid():
    families = [Family('F01', married=datetime(2000, 10, 10), children=['I01', 'I02'])]
    individuals = [
        Individual('I01', first_name='Morgan'),
        Individual('I02', first_name='Gordon'),
    ]
    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_unique_first_name_in_family(gedcom)


def test_validate_unique_families_by_spouses_error():
    families = [
        Family('F01', married=datetime(2000, 10, 10), wife_id='I01', husband_id='I02'),
        Family('F02', married=datetime(2000, 10, 10), wife_id='I03', husband_id='I04')
    ]
    individuals = [
        Individual('I01', name='Morgan Freeman', sex='M'),
        Individual('I02', name='Sarah Freeman', sex='F'),
        Individual('I03', name='Morgan Freeman', sex='M'),
        Individual('I04', name='Sarah Freeman', sex='F'),
    ]
    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_unique_families_by_spouses(gedcom)
    assert len(errors) == 1
    assert errors[0] == "Error: US24: Families with id F01 and F02 have the same spouses names (Sarah Freeman, Morgan Freeman) and marriage date (2000-10-10 00:00:00)"


def test_validate_unique_families_by_spouses_error_same_marriage_date_diff_names():
    families = [
        Family('F01', married=datetime(2000, 10, 10), wife_id='I01', husband_id='I02'),
        Family('F02', married=datetime(2000, 10, 10), wife_id='I03', husband_id='I04')
    ]
    individuals = [
        Individual('I01', name='Morgan Freeman', sex='M'),
        Individual('I02', name='Sarah Freeman', sex='F'),
        Individual('I03', name='Morgan Freeman', sex='M'),
        Individual('I04', name='Sarah Gordon', sex='F'),
    ]
    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_unique_families_by_spouses(gedcom)
    assert len(errors) == 0


def test_validate_unique_families_by_spouses_error_diff_marriage_date_same_names():
    families = [
        Family('F01', married=datetime(2000, 10, 10), wife_id='I01', husband_id='I02'),
        Family('F02', married=datetime(2000, 10, 11), wife_id='I03', husband_id='I04')
    ]
    individuals = [
        Individual('I01', name='Morgan Freeman', sex='M'),
        Individual('I02', name='Sarah Freeman', sex='F'),
        Individual('I03', name='Morgan Freeman', sex='M'),
        Individual('I04', name='Sarah Freeman', sex='F'),
    ]
    gedcom = Gedcom(individuals=individuals, families=families)
    errors = validation.validate_unique_families_by_spouses(gedcom)
    assert len(errors) == 0

def test_validate_no_marriage_to_siblings():
  """
  Testing US18: No marriage to siblings
  """
  # Husband is married to a sibling
  families = [ 
    Family('F01', children=['I01', 'I02']),
    Family('F02', wife_id='I01', husband_id='I02')
  ]
  gedcom = Gedcom(individuals=[], families=families)
  errors = validation.validate_no_marriage_to_siblings(gedcom)
  assert len(errors) == 2
  assert errors[0] == 'Error: US18: Individiual I02 is married to I01, a sibling of theirs in Family F01.' 
  assert errors[1] == 'Error: US18: Individiual I01 is married to I02, a sibling of theirs in Family F01.' 

  # No one is married to child
  families = [ Family('F01', children=['I01', 'I02'])]
  gedcom = Gedcom(individuals=[], families=families)
  errors = validation.validate_no_marriage_to_siblings(gedcom)
  assert len(errors) == 0
  
def test_validate_no_marriage_to_children():
  """
  Testing US17
  """
  # Husband is married to child
  families = [ 
    Family('F01', wife_id='I02', husband_id='I01', children=['I03']),
    Family('F02', wife_id='I01', husband_id='I03')
  ]
  gedcom = Gedcom(individuals=[], families=families)
  errors = validation.validate_no_marriage_to_children(gedcom)
  assert len(errors) == 1
  assert errors[0] == 'Error: US17: Individiual I01 is married to I03, a child of theirs in Family F01.' 

  # Wife is married to child
  families = [ 
    Family('F01', wife_id='I01', husband_id='I02', children=['I03']),
    Family('F02', wife_id='I01', husband_id='I03')
  ]
  gedcom = Gedcom(individuals=[], families=families)
  errors = validation.validate_no_marriage_to_children(gedcom)
  assert len(errors) == 1
  assert errors[0] == 'Error: US17: Individiual I01 is married to I03, a child of theirs in Family F01.' 

  # No one is married to child
  families = [ Family('F01', wife_id='I01', husband_id='I02', children=['I03'])]
  gedcom = Gedcom(individuals=[], families=families)
  errors = validation.validate_no_marriage_to_children(gedcom)
  assert len(errors) == 0

def test_validate_first_cousins_should_not_marry():
  """
    testing US19
  """
  gedcom = parse_gedcom('../res/Pete_sprint3_US19_test.ged')
  errors = validation.validate_first_cousins_should_not_marry(gedcom)
  print(errors)

  assert len(errors) == 1
  assert errors[0] == 'Error: US19: The family with id @F4@ has first cousins as a married couple husband: @I7@, wife: @I8@'

def test_validate_aunts_and_uncles():
  """
    testing US20
  """
  gedcom = parse_gedcom('../res/Pete_sprint3_US20_test.ged')
  errors = validation.validate_aunts_and_uncles(gedcom)

  assert len(errors) == 1
  assert errors[0] == 'Error: US20: family with id @F1@ has uncles and aunts married to niece and nephews husband: @I6@, wife: @I1@'


def test_list_deceased():
  """
  Testing US29: List All Deceased 
  """
  individuals = [
    Individual('I01', name = 'Morgan Freeman', birthday = datetime(1940, 10, 10), death = datetime(2010, 10, 10))
  ]
  gedcom = Gedcom(individuals = individuals)
  errors = validation.validate_list_deceased(gedcom)
  assert len(errors) == 1
  assert errors[0] == 'Deceased: US29: (I01) Morgan Freeman [DeathDate: 2010-10-10]'

def test_list_living_married():
  """
  Testing US30: List All Living Married
  """
  families = [ Family('F01', married=datetime(2000, 9, 1), husband_id='I01', wife_id='I02')]
  individuals = [
    Individual('I01', name = "John Smith", birthday = datetime(1965, 10, 10), spouses=['F01']),
    Individual('I02', name = "Abby Smith", birthday = datetime(1968, 10, 10), spouses=['F01'])
  ]
  gedcom = Gedcom(individuals = individuals, families = families)
  errors = validation.validate_list_living_married(gedcom)
  assert len(errors) == 2
  assert errors[0] == 'Living Married: US30: (I01) John Smith'
  assert errors[1] == 'Living Married: US30: (I02) Abby Smith'


def test_list_recent_deaths():
    """
        Test US36: List recent death
    """
    individuals = [
        Individual('I01', name='Morgan Freeman', death=datetime.now()),
        Individual('I02', name='Megan Freeman', death=datetime.now() - timedelta(days=15)),
        Individual('I03', name='Sarah Freeman', death=datetime.now() - timedelta(days=31))
    ]

    gedcom = Gedcom(individuals=individuals)
    recent_death = validation.list_recent_deaths(gedcom)

    assert len(recent_death) == 2
    assert recent_death[0] == f"Recent Death: Individual (I01) Morgan Freeman was recently died in {gedcom.date_string(individuals[0].death)}"
    assert recent_death[1] == f"Recent Death: Individual (I02) Megan Freeman was recently died in {gedcom.date_string(individuals[1].death)}"


def test_list_upcoming_birthdays():
    """
        Test US38: List upcoming birthdays
    """
    today = datetime.now()
    individuals = [
        Individual('I01', name='Morgan Freeman', birthday=today - timedelta(days=365*10-10)),
        Individual('I02', name='Megan Freeman', birthday=today - timedelta(days=365*10-60)),
    ]

    gedcom = Gedcom(individuals=individuals)
    upcoming_birthdays = validation.list_upcoming_birthdays(gedcom)

    assert len(upcoming_birthdays) == 1
    birthday = individuals[0].birthday
    assert upcoming_birthdays[0] == f"Upcoming Birthday: Individual (I01) Morgan Freeman has upcoming birthday on " \
                                    f"{gedcom.date_string(datetime(year=today.year, month=birthday.month, day=birthday.day))}"


def test_validate_born_during_parents_marriage():
  """
    Test US08: Birth before marriage of parents (and not more than 9 months after their divorce)
  """

  # Individual born before the marriage of parents
  individuals = [ Individual('I01', child='F01', birthday=datetime.now() - timedelta(days=1)) ]
  families = [ Family('F01', married=datetime.now()) ]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_born_during_parents_marriage(gedcom)
  assert len(errors) == 1
  assert errors[0] == f'Error: US08: Individual I01 was born before the marriage of their parents in F01'

  # Indiviudal born after marriage of parents and before their divorce
  individuals = [ Individual('I01', child='F01', birthday=datetime(year=2010, month=10, day=10)) ]
  families = [ Family('F01', married=datetime(year=2005, month=10, day=10), divorced=datetime(year=2019, month=10, day=10))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_born_during_parents_marriage(gedcom)
  assert len(errors) == 0

  # Individual born 9 months after parent's divorce
  inidividuals = [ Individual('I01', child='F01', birthday=datetime(year=2010, month=10, day=10)) ]
  families = [ Family('F01', divorced=datetime(year=2005, month=10, day=10)) ]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_born_during_parents_marriage(gedcom)
  assert len(errors) == 1
  assert errors[0] == f'Error: US08: Individual I01 was born after the divorce of their parents in F01'


