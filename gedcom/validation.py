# Validation methods go here

def validate_too_old_individual(gedcom):
    result = []
    for individual in gedcom.individuals:
        if individual.age > 150:
            result.append(f'Error: The individual {individual.name} ({individual.id}) is too old, age = {individual.age}.')
    return result

def birth_before_death(gedcom):
    """
        validationg that individuals birthday is before individuals death.
    """
    result = []
    for individual in gedcom.individuals:
        birth = individual.birthday
        death = individual.death
        
        if death == None:
            continue
        elif death < birth:
            result.append(f'Error: The individual {individual.name} ({individual.id}) has death before birth, death = {individual.death}, birth = {individual.birthday}')
    
    return result

def birth_before_marriage(gedcom):
    """
        checking if individual was born before or after marriage
    """
    result = []

    for family in gedcom.families:
        childernlist = family.children

        for child in childernlist:
            if family.married == None:
                result.append(f'Error: Parents are not married for {child}')
            else:
                for i in gedcom.individuals:
                    if i.id == child and i.birthday < family.married:
                         result.append(f'Error: The individual {i.name} ({i.id}) has birth before marriage, birth = {child.birthday}, marriage = {family.marriage}')

    return result


all_validators = [validate_too_old_individual, birth_before_marriage, birth_before_death]

def validate_gedcom(gedcom):
    errors = []
    for validator in all_validators:
        errors.extend(validator(gedcom))