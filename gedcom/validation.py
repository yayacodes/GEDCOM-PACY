# Validation methods go here
import datetime

def validate_too_old_individual(gedcom):
    result = []
    for individual in gedcom.individuals:
        if individual.age > 150:
            result.append(f'Error: The individual {individual.name} ({individual.id}) is too old, age = {individual.age}.')
    return result

def marriage_after_divorce(gedcom):
    result = []
    for family in gedcom.families:
        if (family.married is not None and family.divorced is not None) and (family.married > family.divorced):
            result.append(f'Error: The Husband {family.husbandName} ({family.husband_id}) and Wife {family.wife_name} ({family.wife_id}) cannot have divorce date before marriage date')
    return result

def dates_before_current(gedcom):
    result = []
    today = datetime.datetime.now()
    for family in gedcom.families:
        if family.married is not None and family.married > today:
            result.append(f'Error: The Family {family.id}\'s marriage date ({family.married}) is after the current date ({today})')
        if family.divorced is not None and family.divorced > today:
            result.append(f'Error: The Family {family.id}\'s divorce date ({family.divorced}) is after the current date ({today})')
    for individual in gedcom.individuals:
        if individual.birthday is not None and individual.birthday > today:
            result.append(f'Error: The individual {individual.name} ({individual.id}) has a birthday that is after the current date ({today})')
        if individual.death is not None and individual.death > today:
            result.append(f'Error: The individual {individual.name} ({individual.id}) has a deathdate that is after the current date ({today})')
        
    return result

all_validators = [validate_too_old_individual, marriage_after_divorce, dates_before_current]


def validate_gedcom(gedcom):
    errors = []
    for validator in all_validators:
        errors.extend(validator(gedcom))