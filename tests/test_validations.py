from gedcom.validation import validate_too_old_individual
from gedcom.GedcomParser import GedcomParser
from gedcom import validation, Family, Gedcom, Individual
from datetime import datetime


def test_validate_too_old_individual():
    parser = GedcomParser()
    gedcom = parser.parse('../res/family_validation.ged')
    errors = validate_too_old_individual(gedcom)
    assert len(errors) == 1
    assert errors[0] == 'Error: The individual Morgan Freeman (I01) is too old, age = 151.'

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
      ['Error: The family F01 contains child I01, but that individual has no record']
    )

    # Individual lists family that doesn't exist
    test(
      [Individual('I01', child='F01')],
      [], [
        'Error: The individual I01 says they are a child of family F01, but that family has no record'
      ]
    )

    # Individual lists family that doesn't list them
    test(
      [Individual('I01', child='F01')], [Family('F01')],
      [ 'Error: The individual I01 says they are a child of family F01, but that family does not list this individual as a child']
    )

    # Individual lists family as child, family lists another individual as child, other child doesn't exist
    test(
      [Individual(id='I01', child='F01')], 
      [Family(id='F01', children=['I02'])],
      [
        'Error: The individual I01 says they are a child of family F01, but that family does not list this individual as a child',
        'Error: The family F01 contains child I02, but that individual has no record'
      ]
    )

    # Individua lists family as child, family lists another individual as child, other child does not list family
    test(
      [Individual(id='I01', child='F01'), Individual(id='I02')], 
      [Family(id='F01', children=['I02'])],
      [
        'Error: The individual I01 says they are a child of family F01, but that family does not list this individual as a child',
        'Error: The family F01 contains child I02, but that individual does not list this family as a child',
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
      ['Error: The individual I01 says they are a spouse of family F01, but that family does not list this individual as a spouse']
    )
    # Individual lists family as spouse, family lists another individual who does not exist
    test(
      [Individual('I01', spouse='F01')],
      [Family('F01', husband_id='I02')],
      [
        'Error: The individual I01 says they are a spouse of family F01, but that family does not list this individual as a spouse',
        'Error: The family F01 contains spouse I02, but that individual has no record'
      ]
    )
    # Individual lists family as spouse, family lists another individual, other individual doesn't list family
    test(
      [Individual('I01', spouse='F01'), Individual('I02', spouse='F02')],
      [Family('F01', wife_id='I02')],
      [
        'Error: The individual I01 says they are a spouse of family F01, but that family does not list this individual as a spouse',
        'Error: The family F01 contains spouse I02, but that individual does not list this family as a spouse',
        'Error: The individual I02 says they are a spouse of family F02, but that family has no record'
      ]
    )

    # Family lists individual as spouse, individual does not list family
    test(
      [Individual('I01')],
      [Family('F01', husband_id='I01')],
      [
        'Error: The family F01 contains spouse I01, but that individual does not list this family as a spouse'
      ]
    )
    # Family lists individual as spouse, spouse lists another family that does not exist
    test(
      [Individual('I01', spouse='F02')],
      [Family('F01', husband_id='I01')],
      [
        'Error: The individual I01 says they are a spouse of family F02, but that family has no record',
        'Error: The family F01 contains spouse I01, but that individual does not list this family as a spouse'
      ]
    )
    # Family lists individual as spouse, spouse lists another family, other family doesnt list individual
    test(
      [Individual('I01', spouse='F02')],
      [Family('F01', husband_id='I01'), Family('F02')],
      [
        'Error: The individual I01 says they are a spouse of family F02, but that family does not list this individual as a spouse',
        'Error: The family F01 contains spouse I01, but that individual does not list this family as a spouse'
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
  assert errors[0] == 'Error: Spouse I01 in family F01 was married at less than 14 years old'
  assert len(errors) == 1

  # Wife < 14
  individuals = [Individual('I01', spouse='F01', birthday=datetime(2007, 1, 1)), Individual('I02', spouse='F01', birthday=datetime(1997, 6, 18))]
  families = [Family('F01', wife_id='I01', husband_id='I02', married=datetime(2020, 2, 20))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_marriage_after_fourteen(gedcom)
  assert errors[0] == 'Error: Spouse I01 in family F01 was married at less than 14 years old'
  assert len(errors) == 1

  # Husband + Wife < 14
  individuals = [Individual('I01', spouse='F01', birthday=datetime(2007, 1, 1)), Individual('I02', spouse='F01', birthday=datetime(2007, 1, 1))]
  families = [Family('F01', wife_id='I01', husband_id='I02', married=datetime(2020, 2, 20))]
  gedcom = Gedcom(individuals=individuals, families=families)
  errors = validation.validate_marriage_after_fourteen(gedcom)
  assert errors[0] == 'Error: Spouse I01 in family F01 was married at less than 14 years old'
  assert errors[1] == 'Error: Spouse I02 in family F01 was married at less than 14 years old'
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
  assert errors[0] == 'Error: Family F01 has divorce date before marriage date'
  assert len(errors) == 1

def test_validate_fewer_than_15_sibs():
  # Family has more than 15 siblings
  families = [Family('F01', wife_id='I01', husband_id='I02', children = (['I01']*16))]
  gedcom = Gedcom(individuals=None, families=families)
  errors = validation.validate_fewer_than_15_sibs(gedcom)
  assert errors[0] == 'Error: Family F01 has more than 15 siblings'
  assert len(errors) == 1