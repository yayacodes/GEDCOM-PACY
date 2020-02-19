# Validation methods go here


def validate_too_old_individual(gedcom):
    result = []
    for individual in gedcom.individuals:
        if individual.age > 150:
            result.append(f'Error: The individual {individual.name} ({individual.id}) is too old, age = {individual.age}.')
    return result


all_validators = [validate_too_old_individual]


def validate_gedcom(gedcom):
    errors = []
    for validator in all_validators:
        errors.extend(validator(gedcom))