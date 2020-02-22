# Validation methods go here


def validate_too_old_individual(gedcom):
    result = []
    for individual in gedcom.individuals:
        if individual.age > 150:
            result.append(f'Error: The individual {individual.name} ({individual.id}) is too old, age = {individual.age}.')
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

all_validators = [validate_too_old_individual]


def validate_gedcom(gedcom):
    errors = []
    for validator in all_validators:
        errors.extend(validator(gedcom))