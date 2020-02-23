# Validation methods go here


def validate_too_old_individual(gedcom):
    result = []
    for individual in gedcom.individuals:
        if individual.age > 150:
            result.append(f'Error: The individual {individual.name} ({individual.id}) is too old, age = {individual.age}.')
    return result


def validate_marriage_before_death(gedcom):
    """
    Marriage should occur before death of either spouse
    """
    result = []
    for family in gedcom.families:
        marriage_date = family.married
        if marriage_date:
            husband = gedcom.individual_with_id(family.husband_id)
            wife = gedcom.individual_with_id(family.wife_id)
            if husband.death < marriage_date:
                result.append(f'Error: Family ({family.id}) has the husband {husband.name} ({family.husband_id})'
                              f' death date ({husband.death.strftime("%x")}) before the marriage date ({marriage_date.strftime("%x")})')
            if wife.death < marriage_date:
                result.append(f'Error: Family ({family.id}) has the wife {wife.name} ({family.wife_id})'
                              f' death date ({wife.death.strftime("%x")}) before the marriage date ({marriage_date.strftime("%x")})')
    return result


def validate_divorce_before_death(gedcom):
    """
    Divorce can only occur before death of both spouses
    """
    result = []
    for family in gedcom.families:
        divorce_date = family.divorced
        if divorce_date:
            husband = gedcom.individual_with_id(family.husband_id)
            wife = gedcom.individual_with_id(family.wife_id)
            if husband.death < divorce_date:
                result.append(f'Error: Family ({family.id}) has the husband {husband.name} ({family.husband_id})'
                              f' death date ({husband.death.strftime("%x")}) before the divorce date ({divorce_date.strftime("%x")})')
            if wife.death < divorce_date:
                result.append(f'Error: Family ({family.id}) has the wife {wife.name} ({family.wife_id})'
                              f' death date ({wife.death.strftime("%x")}) before the divorce date ({divorce_date.strftime("%x")})')
    return result


all_validators = [validate_too_old_individual, validate_marriage_before_death, validate_divorce_before_death]


def validate_gedcom(gedcom):
    errors = []
    for validator in all_validators:
        errors.extend(validator(gedcom))
