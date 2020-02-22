# Validation methods go here

all_validators = []


def validate_gedcom(gedcom):
    errors = []
    for validator in all_validators:
        errors.extend(validator(gedcom))