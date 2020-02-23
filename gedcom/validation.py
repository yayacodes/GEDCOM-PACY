# Validation methods go here
import datetime

def validate_too_old_individual(gedcom):
    result = []
    for individual in gedcom.individuals:
        if individual.age > 150:
            result.append(f'Error: The individual {individual.name} ({individual.id}) is too old, age = {individual.age}.')
    return result

def validate_marriage_after_divorce(gedcom):
    result = []
    for family in gedcom.families:
        if (family.married is not None and family.divorced is not None) and (family.married > family.divorced):
            result.append(f'Error: Family {family.id} has divorce date before marriage date')
    return result

def validate_dates_before_current(gedcom):
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

def validate_corresponding_entries(gedcom):

    # Make sure every individual is in their families
    result = []
    for individual in gedcom.individuals:
        if individual.child is not None:
            family = gedcom.family_with_id(individual.child)
            if family is None:
                result.append(f'Error: The individual {individual.id} says they are a child of family {individual.child}, but that family has no record')
            elif individual.id not in family.children:
                result.append(f'Error: The individual {individual.id} says they are a child of family {family.id}, but that family does not list this individual as a child')
        
        if individual.spouse is not None:
            family = family = gedcom.family_with_id(individual.spouse)
            if family is None:
                result.append(f'Error: The individual {individual.id} says they are a spouse of family {individual.spouse}, but that family has no record')
            elif not family.husband_id == individual.id and not family.wife_id == individual.id:
                result.append(f'Error: The individual {individual.id} says they are a spouse of family {family.id}, but that family does not list this individual as a spouse')
            
    # Make sure every family member's individual record also mentions the family
    for family in gedcom.families:
        for spouse_id in [family.wife_id, family.husband_id]:
            if spouse_id is not None:
                spouse = gedcom.individual_with_id(spouse_id)
                if spouse is None:
                    result.append(f'Error: The family {family.id} contains spouse {spouse_id}, but that individual has no record')
                elif spouse.spouse != family.id:
                    result.append(f'Error: The family {family.id} contains spouse {spouse_id}, but that individual does not list this family as a spouse')

        if family.children is not None and len(family.children) > 0:
            for child_id in family.children:
                child = gedcom.individual_with_id(child_id)
                if child is None:
                    result.append(f'Error: The family {family.id} contains child {child_id}, but that individual has no record')
                elif child.child != family.id:
                    result.append(f'Error: The family {family.id} contains child {child_id}, but that individual does not list this family as a child')
    
    return result

def validate_marriage_after_fourteen(gedcom):
    errors = []

    for family in gedcom.families:
        husband = gedcom.individual_with_id(family.husband_id)
        wife = gedcom.individual_with_id(family.wife_id)
        
        if family.married is not None:
            if ((family.married - wife.birthday).days / 365) < 14:
                errors.append(f'Error: Spouse {wife.id} in family {family.id} was married at less than 14 years old') 
            if ((family.married - husband.birthday).days / 365) < 14:
                errors.append(f'Error: Spouse {husband.id} in family {family.id} was married at less than 14 years old') 
    
    return errors


def validate_fewer_than_15_sibs(gedcom):
    errors = []
    
    for family in gedcom.families:
        if len(family.children) > 15:
            errors.append(f'Error: Family {family.id} has more than 15 siblings')
    return errors

all_validators = [validate_marriage_after_fourteen, validate_corresponding_entries, validate_too_old_individual, validate_marriage_after_divorce]


def validate_gedcom(gedcom):
    errors = []
    for validator in all_validators:
        errors.extend(validator(gedcom))