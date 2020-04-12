# Validation methods go here
import datetime
from itertools import combinations
from collections import defaultdict

def validate_too_old_individual(gedcom):
    result = []
    for individual in gedcom.individuals:
        if individual.age > 150:
            result.append(f'Error: US07: The individual {individual.name} ({individual.id}) is too old, age = {individual.age}.')
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
            result.append(f'Error: US03: The individual {individual.name} ({individual.id}) has death before birth, death = {individual.death}, birth = {individual.birthday}')
    
    return result

def birth_before_marriage(gedcom):
    """
        checking if individual was born before or after marriage
    """
    result = []

    for family in gedcom.families:
        mariage_date = family.married

        husband = gedcom.individual_with_id(family.husband_id)
        wife = gedcom.individual_with_id(family.wife_id)

        if not mariage_date:
            continue
        if husband.birthday and husband.birthday > mariage_date:
            result.append(f'Error: US02: The individual {husband.name} ({husband.id}) has marriage before birth, marriage = {mariage_date}, birth = {husband.birthday}')
        if wife.birthday and wife.birthday > mariage_date:
            result.append(f'Error: US02: The individual {wife.name} ({wife.id}) has marriage before birth, marriage = {mariage_date}, birth = {wife.birthday}')

    return result

def validate_marriage_after_divorce(gedcom):
    result = []
    for family in gedcom.families:
        if (family.married is not None and family.divorced is not None) and (family.married > family.divorced):
            result.append(f'Error: US04: Family {family.id} has divorce date {gedcom.date_string(family.divorced)} before marriage date {gedcom.date_string(family.married)}')
    return result

def validate_dates_before_current(gedcom):
    result = []
    today = datetime.datetime.now()
    for family in gedcom.families:
        if family.married is not None and family.married > today:
            result.append(f'Error: US01: The Family {family.id}\'s marriage date {gedcom.date_string(family.married)} is after the current date')
        if family.divorced is not None and family.divorced > today:
            result.append(f'Error: US01: The Family {family.id}\'s divorce date {gedcom.date_string(family.divorced)} is after the current date')
    for individual in gedcom.individuals:
        if individual.birthday is not None and individual.birthday > today:
            result.append(f'Error: US01: The Individual {individual.id}\'s birthday {gedcom.date_string(individual.birthday)} is after the current date')
        if individual.death is not None and individual.death > today:
            result.append(f'Error: US01: The Individual {individual.id}\'s deathdate {gedcom.date_string(individual.death)} is after the current date')  
    
    return result

def validate_corresponding_entries(gedcom):

    # Make sure every individual is in their families
    result = []
    for individual in gedcom.individuals:
        if individual.child is not None:
            family = gedcom.family_with_id(individual.child)
            if family is None:
                result.append(f'Error: US26: The individual {individual.id} says they are a child of family {individual.child}, but that family has no record')
            elif individual.id not in family.children:
                result.append(f'Error: US26: The individual {individual.id} says they are a child of family {family.id}, but that family does not list this individual as a child')
        
        for spouse_family in individual.spouses:
            if spouse_family is not None:
                family = gedcom.family_with_id(spouse_family)
                if family is None:
                    result.append(f'Error: US26: The individual {individual.id} says they are a spouse of family {spouse_family}, but that family has no record')
                elif not family.husband_id == individual.id and not family.wife_id == individual.id:
                    result.append(f'Error: US26: The individual {individual.id} says they are a spouse of family {family.id}, but that family does not list this individual as a spouse')
            
    # Make sure every family member's individual record also mentions the family
    for family in gedcom.families:
        for spouse_id in [family.wife_id, family.husband_id]:
            if spouse_id is not None:
                spouse = gedcom.individual_with_id(spouse_id)
                if spouse is None:
                    result.append(f'Error: US26: The family {family.id} contains spouse {spouse_id}, but that individual has no record')
                elif family.id not in spouse.spouses:
                    result.append(f'Error: US26: The family {family.id} contains spouse {spouse_id}, but that individual does not list this family as a spouse')

        if family.children is not None and len(family.children) > 0:
            for child_id in family.children:
                child = gedcom.individual_with_id(child_id)
                if child is None:
                    result.append(f'Error: US26: The family {family.id} contains child {child_id}, but that individual has no record')
                elif child.child != family.id:
                    result.append(f'Error: US26: The family {family.id} contains child {child_id}, but that individual does not list this family as a child')
    
    return result

def validate_marriage_after_fourteen(gedcom):
    errors = []

    for family in gedcom.families:
        husband = gedcom.individual_with_id(family.husband_id)
        wife = gedcom.individual_with_id(family.wife_id)
        
        if family.married is not None:
            if ((family.married - wife.birthday).days / 365) < 14:
                errors.append(f'Error: US10: Spouse {wife.id} in family {family.id} was married at less than 14 years old, age={wife.age}') 
            if ((family.married - husband.birthday).days / 365) < 14:
                errors.append(f'Error: US10: Spouse {husband.id} in family {family.id} was married at less than 14 years old, age={husband.age}') 
    
    return errors

def validate_fewer_than_15_sibs(gedcom):
    errors = []
    
    for family in gedcom.families:
        if len(family.children) > 15:
            errors.append(f'Error: US15: Family {family.id} has more than 15 siblings')
    return errors

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
            if husband.death is not None:
                if husband.death < marriage_date:
                    result.append(f'Error: US05: Family ({family.id}) has the husband {husband.name} ({family.husband_id})'
                                f' death date ({husband.death.strftime("%x")}) before the marriage date ({marriage_date.strftime("%x")})')
            if wife.death is not None:
                if wife.death < marriage_date:
                    result.append(f'Error: US05: Family ({family.id}) has the wife {wife.name} ({family.wife_id})'
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
                result.append(f'Error: US06: Family ({family.id}) has the husband {husband.name} ({family.husband_id})'
                              f' death date ({husband.death.strftime("%x")}) before the divorce date ({divorce_date.strftime("%x")})')
            if wife.death < divorce_date:
                result.append(f'Error: US06: Family ({family.id}) has the wife {wife.name} ({family.wife_id})'
                              f' death date ({wife.death.strftime("%x")}) before the divorce date ({divorce_date.strftime("%x")})')
    return result

def validate_no_bigamy(gedcom):
    """
        Marriage should not occur during marriage to another spouse
    """

    def format_date(date):
        return date.strftime('%d-%m-%Y')

    errors = []
    # For every family
    for family1 in [x for x in gedcom.families if x is not None]:
    # If there's a marriage date,
    # for each of the spouses
        for spouse in [family1.husband_id, family1.wife_id]:
            spouse = gedcom.individual_with_id(spouse)

            if spouse is not None:
                # for every family that spouse is apart of
                # make sure that marriage date isn't during the marriage of family 1
                for family2 in spouse.spouses:
                    family2 = gedcom.family_with_id(family2)
                    marriage_end_date = family1.divorced if family1.divorced is not None else datetime.datetime.now()

                    if marriage_end_date is not None and family2.married > family1.married and family2.married <= marriage_end_date:
                        print(':', family1, family2)
                        family2_spouse = family2.husband_id if family2.husband_id is not spouse.id else family2.wife_id
                        family2_spouse = gedcom.individual_with_id(family2_spouse)

                        family1_spouse = family1.husband_id if family1.husband_id is not spouse.id else family1.wife_id
                        family1_spouse = gedcom.individual_with_id(family1_spouse)

                        errors.append(f'Error: US11: Individual {spouse.id} married {family2_spouse.id} on {format_date(family2.married)}, which was during their marriage to {family1_spouse.id}')
    return errors

def validate_correct_gender(gedcom):
    """
        Husband in family should be male and wife in family should be female
    """
    result = []
    for family in gedcom.families:
        if family.husband_id != None:
            husband = gedcom.individual_with_id(family.husband_id)
            if husband is not None and husband.sex != "M":
                result.append(f'Error: US21: Husband {husband.id} in Family {family.id} should be male')
        if family.wife_id != None:
            wife = gedcom.individual_with_id(family.wife_id)
            if wife is not None and wife.sex != "F":
                result.append(f'Error: US21: Wife {wife.id} in Family {family.id} should be female')
    return result


def validate_male_last_last_name(gedcom):
    """
    US16: All male members of a family should have the same last name
    """
    errors = []
    for family in gedcom.families:
        if len(family.children) == 0:
            continue  # Nothing to check here
        husband = gedcom.individual_with_id(family.husband_id)
        family_lastname = None
        if husband is not None:
            family_lastname = husband.last_name
        for child_id in family.children:
            child = gedcom.individual_with_id(child_id)
            if child is None or child.last_name is None:
                continue
            
            if family_lastname is None:
                family_lastname = child.last_name

            if child.sex == 'M' and child.last_name != family_lastname:
                errors.append(f"Error: US16: Individual {child.id} last name ({child.last_name}) doesn't follow the family last name ({family_lastname})")

    return errors

def validate_sibling_spacing(gedcom):
    """
    US13: Birth dates of siblings should be more than 8 months apart or less than 2 days apart (twins may be born one day apart, e.g. 11:59 PM and 12:02 AM the following calendar day)
    """
    errors = []
    for family in gedcom.families:
        if len(family.children) <= 1: continue
        for pair in combinations(family.children, 2):
            child1 = gedcom.individual_with_id(pair[0])
            child2 = gedcom.individual_with_id(pair[1])
            if child1 and child2:
                spacing = abs(child1.birthday - child2.birthday).days
                if spacing > 1 and spacing/30.44 < 8:
                    errors.append(f'Error: US13: Child {child1.name} ({child1.id}) in family {family.id} has unrealistic birthday gap ({spacing} days) to his sibling {child2.name} ({child2.id})')
    return errors


def validate_parents_not_too_old(gedcom):
    """
        mother should be atmost 60 years older and father should be atmost 80 years older than the children
    """

    errors = []

    for family in gedcom.families:
        child_list = family.children
        husband = gedcom.individual_with_id(family.husband_id)
        wife = gedcom.individual_with_id(family.wife_id)

        if child_list != None:
            for child in child_list:
                indi = gedcom.individual_with_id(child)
                if indi is None:
                    continue 
                
                childs_age = indi.age
            
                if husband == None and wife == None:
                    continue

                if husband == None and wife != None:
                    moms_age = wife.age
                    if moms_age - childs_age > 60:
                        errors.append(f'Error: US12: parents {wife.name} too old for child {indi.name}')

                if wife == None and husband != None:
                    dads_age = husband.age
                    if dads_age - childs_age > 80:
                        errors.append(f'Error: US12: parents {husband.name} too old for child {indi.name}')

                if husband != None and wife != None:
                    moms_age = wife.age
                    dads_age = husband.age
                    if (moms_age - childs_age > 60) or (dads_age - childs_age > 80):
                        errors.append(f'Error: US12: parents {husband.name}/{wife.name} too old for child {indi.name}')

    return errors
    
def validate_multiple_births(gedcom):
    """
        no more than 5 siblings should be born at the same time
    """

    errors = []
    birth = []
    birthdays = defaultdict(int)

    for family in gedcom.families:
        child_list = family.children

        if len(child_list)<5:
            continue
        else:
            for child in child_list:
                child = gedcom.individual_with_id(child)
                if child is None:
                    continue
                birth.append(child.birthday)

        for item in birth:
            birthdays[item] += 1

        for births in birthdays.values():
            if births > 5:
                errors.append(f'Error: US14: For family with id {family.id} there are more than 5 births at the same time')

    return errors

def validate_list_deceased(gedcom):
    """
        US29: List all deceased individuals in a GEDCOM file
    """

    deceased = []

    for individual in gedcom.individuals:
        if individual.alive is False:
            deceased.append(f'Deceased: US29: ({individual.id}) {individual.name} [DeathDate: {individual.death.date()}]')
    return deceased

def validate_unique_first_name_in_family(gedcom):
    """
        US25: No more than one child with the same name and birth date should appear in a family
    """
    errors = []
    for family in gedcom.families:
        for (id1, id2) in combinations(family.children, 2):
            child1, child2 = gedcom.individual_with_id(id1), gedcom.individual_with_id(id2)
            if not (child1 and child2):
                continue
            if child1.first_name == child2.first_name:
                errors.append(f'Error: US25: Family with id {family.id} has two children with the same first name \'{child1.first_name}\'')
    return errors


def validate_unique_families_by_spouses(gedcom):
    """
        US24: No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file
    """
    errors = []
    for (family1, family2) in combinations(gedcom.families, 2):
        husband1, wife1 = gedcom.individual_with_id(family1.husband_id), gedcom.individual_with_id(family1.wife_id)
        husband2, wife2 = gedcom.individual_with_id(family2.husband_id), gedcom.individual_with_id(family2.wife_id)
        if not (husband1 and wife1 and husband2 and wife2):
            continue

        if family1.married == family2.married and husband1.name == husband2.name and wife1.name == wife2.name:
            errors.append(f'Error: US24: Families with id {family1.id} and {family2.id} have the same spouses '
                          f'names ({husband1.name}, {wife1.name}) and marriage date ({family1.married})')
    return errors

def validate_no_marriage_to_children(gedcom):
    """
        US17: No marriage to children
    """
    errors = []

    def get_families_with_spouse(spouse_id):
        result = []
        for family in gedcom.families: 
            if family.husband_id == spouse_id:
                result.append(family)
            elif family.wife_id == spouse_id:
                result.append(family)
        return result

    for family in gedcom.families:
        # Check whether child is married to their parent
        if family.children:
            family_spouses = [family.husband_id, family.wife_id]
            
            for child_id in family.children:
                childs_families = get_families_with_spouse(child_id)
                for childs_family in childs_families:
                    if childs_family.husband_id in family_spouses:
                        errors.append(f'Error: US17: Individiual {childs_family.husband_id} is married to {child_id}, a child of theirs in Family {family.id}.')
                    if childs_family.wife_id in family_spouses:
                        errors.append(f'Error: US17: Individiual {childs_family.wife_id} is married to {child_id}, a child of theirs in Family {family.id}.')
    return errors

def validate_no_marriage_to_siblings(gedcom):
    """
        US18: No marriage to siblings
    """
    errors = []

    def get_families_with_spouse(spouse_id):
        result = []
        for family in gedcom.families: 
            if family.husband_id == spouse_id:
                result.append(family)
            elif family.wife_id == spouse_id:
                result.append(family)
        return result

    for family in gedcom.families:
        # Check whether child is married to their parent
        if not family.children or len(family.children) == 0:
            pass

        for child_id in family.children:
            siblings = list(filter(lambda x: x is not child_id, family.children))

            # Check this child's fmailies to see if their spouses are siblings
            childs_families = get_families_with_spouse(child_id)
            for childs_family in childs_families:
                if childs_family.husband_id in siblings:
                    errors.append(f'Error: US18: Individiual {childs_family.husband_id} is married to {child_id}, a sibling of theirs in Family {family.id}.')
                if childs_family.wife_id in siblings:
                    errors.append(f'Error: US18: Individiual {childs_family.wife_id} is married to {child_id}, a sibling of theirs in Family {family.id}.')
    return errors

  
def validate_unique_first_name_in_family(gedcom):
    """
        US25: No more than one child with the same name and birth date should appear in a family
    """
    errors = []
    for family in gedcom.families:
        for (id1, id2) in combinations(family.children, 2):
            child1, child2 = gedcom.individual_with_id(id1), gedcom.individual_with_id(id2)
            if not (child1 and child2):
                continue
            if child1.first_name == child2.first_name:
                errors.append(f'Error: US25: Family with id {family.id} has two children with the same first name \'{child1.first_name}\'')
    return errors


def validate_unique_families_by_spouses(gedcom):
    """
        US24: No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file
    """
    errors = []
    for (family1, family2) in combinations(gedcom.families, 2):
        husband1, wife1 = gedcom.individual_with_id(family1.husband_id), gedcom.individual_with_id(family1.wife_id)
        husband2, wife2 = gedcom.individual_with_id(family2.husband_id), gedcom.individual_with_id(family2.wife_id)
        if not (husband1 and wife1 and husband2 and wife2):
            continue

        if family1.married == family2.married and husband1.name == husband2.name and wife1.name == wife2.name:
            errors.append(f'Error: US24: Families with id {family1.id} and {family2.id} have the same spouses '
                          f'names ({husband1.name}, {wife1.name}) and marriage date ({family1.married})')
    return errors

def validate_no_marriage_to_children(gedcom):
    """
        US17: No marriage to children
    """
    errors = []

    def get_families_with_spouse(spouse_id):
        result = []
        for family in gedcom.families: 
            if family.husband_id == spouse_id:
                result.append(family)
            elif family.wife_id == spouse_id:
                result.append(family)
        return result

    for family in gedcom.families:
        # Check whether child is married to their parent
        if family.children:
            family_spouses = [family.husband_id, family.wife_id]
            
            for child_id in family.children:
                childs_families = get_families_with_spouse(child_id)
                for childs_family in childs_families:
                    if childs_family.husband_id in family_spouses:
                        errors.append(f'Error: US17: Individiual {childs_family.husband_id} is married to {child_id}, a child of theirs in Family {family.id}.')
                    if childs_family.wife_id in family_spouses:
                        errors.append(f'Error: US17: Individiual {childs_family.wife_id} is married to {child_id}, a child of theirs in Family {family.id}.')
    return errors

def validate_no_marriage_to_siblings(gedcom):
    """
        US18: No marriage to siblings
    """
    errors = []

    def get_families_with_spouse(spouse_id):
        result = []
        for family in gedcom.families: 
            if family.husband_id == spouse_id:
                result.append(family)
            elif family.wife_id == spouse_id:
                result.append(family)
        return result

    for family in gedcom.families:
        # Check whether child is married to their parent
        if not family.children or len(family.children) == 0:
            pass

        for child_id in family.children:
            siblings = list(filter(lambda x: x is not child_id, family.children))

            # Check this child's fmailies to see if their spouses are siblings
            childs_families = get_families_with_spouse(child_id)
            for childs_family in childs_families:
                if childs_family.husband_id in siblings:
                    errors.append(f'Error: US18: Individiual {childs_family.husband_id} is married to {child_id}, a sibling of theirs in Family {family.id}.')
                if childs_family.wife_id in siblings:
                    errors.append(f'Error: US18: Individiual {childs_family.wife_id} is married to {child_id}, a sibling of theirs in Family {family.id}.')
    return errors


def validate_first_cousins_should_not_marry(gedcom):
    """
        US19: first cousins should not marry one another.
    """

    errors = []

    def find_family_with_child(child_id, gedcom):
        """
            helper function for finding families with children as input.
        """

        for family in gedcom.families:
            if child_id in family.children:
                return gedcom.family_with_id(family.id)

    for fam in gedcom.families:

        if fam.husband_id == None:
            continue

        elif fam.wife_id == None:
            continue

        else:
            fam_with_husb_as_child = find_family_with_child(fam.husband_id, gedcom)
            fam_with_wife_as_child = find_family_with_child(fam.wife_id, gedcom)

            if fam_with_husb_as_child == None:
                continue

            if fam_with_wife_as_child == None:
                continue
        
            husbands_father = fam_with_husb_as_child.husband_id
            husbands_mother = fam_with_husb_as_child.wife_id

            wifes_father = fam_with_wife_as_child.husband_id
            wifes_mother = fam_with_wife_as_child.wife_id

            if husbands_father != None and husbands_mother != None and wifes_father != None and wifes_mother != None:
                husbands_fathers_fam = find_family_with_child(husbands_father, gedcom)
                husbands_mothers_fam = find_family_with_child(husbands_mother, gedcom)

                wifes_fathers_fam = find_family_with_child(wifes_father, gedcom)
                wifes_mothers_fam = find_family_with_child(wifes_mother, gedcom)

                if husbands_fathers_fam:
                    if wifes_fathers_fam:
                        errors.append(f"Error: US19: The family with id {fam.id} has first cousins as a married couple husband: {fam.husband_id}, wife: {fam.wife_id}")
                    if wifes_mothers_fam:
                        errors.append(f"Error: US19: The family with id {fam.id} has first cousins as a married couple husband: {fam.husband_id}, wife: {fam.wife_id}")

                if husbands_mothers_fam:
                    if wifes_fathers_fam:
                        errors.append(f"Error: US19: The family with id {fam.id} has first cousins as a married couple husband: {fam.husband_id}, wife: {fam.wife_id}")
                    if wifes_mothers_fam:
                        errors.append(f"Error: US19: The family with id {fam.id} has first cousins as a married couple husband: {fam.husband_id}, wife: {fam.wife_id}")
    return errors


def validate_aunts_and_uncles(gedcom):
    """
        aunts and uncles should not marry their nieces or nephews.
    """

    errors = []

    def find_family_with_child(child_id, gedcom):
        """
            helper function for finding families with children as input.
        """

        for family in gedcom.families:
            if child_id in family.children:
                return gedcom.family_with_id(family.id)

    for fam in gedcom.families:

        if fam.husband_id == None:
            continue

        elif fam.wife_id == None:
            continue

        else:
            fam_with_husb_as_child = find_family_with_child(fam.husband_id, gedcom)
            fam_with_wife_as_child = find_family_with_child(fam.wife_id, gedcom)

            if fam_with_husb_as_child == None:
                continue

            if fam_with_wife_as_child == None:
                continue
        
            husbands_father = fam_with_husb_as_child.husband_id
            husbands_mother = fam_with_husb_as_child.wife_id

            wifes_father = fam_with_wife_as_child.husband_id
            wifes_mother = fam_with_wife_as_child.wife_id

            if husbands_father != None and husbands_mother != None and wifes_father != None and wifes_mother != None:
                husbands_fathers_fam = find_family_with_child(husbands_father, gedcom)
                husbands_mothers_fam = find_family_with_child(husbands_mother, gedcom)

                wifes_fathers_fam = find_family_with_child(wifes_father, gedcom)
                wifes_mothers_fam = find_family_with_child(wifes_mother, gedcom)


                if husbands_fathers_fam != None and husbands_mothers_fam == None and wifes_fathers_fam != None and wifes_mothers_fam == None:
                    if fam.wife_id in husbands_fathers_fam.children or fam.husband_id in wifes_fathers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}")
                
                elif husbands_fathers_fam != None and husbands_mothers_fam == None and wifes_fathers_fam == None and wifes_mothers_fam != None:
                    if fam.wife_id in husbands_fathers_fam.children or fam.husband_id in wifes_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}")
                
                elif husbands_fathers_fam != None and husbands_mothers_fam == None and wifes_fathers_fam != None and wifes_mothers_fam != None:
                    if fam.wife_id in husbands_fathers_fam.children or fam.husband_id in wifes_fathers_fam.children or fam.husband_id in wifes_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}")
                
                elif husbands_fathers_fam == None and husbands_mothers_fam != None and wifes_fathers_fam == None and wifes_mothers_fam != None:
                    if fam.wife_id in husbands_mothers_fam.children or fam.husband_id in wifes_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}")
                
                elif husbands_fathers_fam == None and husbands_mothers_fam != None and wifes_fathers_fam != None and wifes_mothers_fam == None:
                   if fam.wife_id in husbands_mothers_fam.children or fam.husband_id in wifes_fathers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}")

                elif husbands_fathers_fam == None and husbands_mothers_fam != None and wifes_fathers_fam != None and wifes_mothers_fam != None:
                    if fam.wife_id in husbands_fathers_fam.children or fam.husband_id in wifes_fathers_fam.children or fam.husband_id in wifes_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}") 

                elif husbands_fathers_fam != None and husbands_mothers_fam == None and wifes_fathers_fam == None and wifes_mothers_fam == None:
                    if fam.wife_id in husbands_fathers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}") 
            
                elif husbands_fathers_fam == None and husbands_mothers_fam != None and wifes_fathers_fam == None and wifes_mothers_fam == None:
                    if fam.wife_id in husbands_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}") 

                elif husbands_fathers_fam == None and husbands_mothers_fam == None and wifes_fathers_fam != None and wifes_mothers_fam == None:
                    if fam.husband_id in wifes_fathers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}") 

                elif husbands_fathers_fam == None and husbands_mothers_fam == None and wifes_fathers_fam == None and wifes_mothers_fam != None:
                    if fam.husband_id in wifes_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}") 

                elif husbands_fathers_fam != None and husbands_mothers_fam != None and wifes_fathers_fam != None and wifes_mothers_fam != None:
                    if fam.wife_id in husbands_fathers_fam.children or fam.wife_id in husbands_mothers_fam.children or fam.husband_id in wifes_fathers_fam.children or fam.husband_id in wifes_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}") 

                elif husbands_fathers_fam == None and husbands_mothers_fam == None and wifes_fathers_fam != None and wifes_mothers_fam != None:
                    if fam.husband_id in wifes_fathers_fam.children or fam.husband_id in wifes_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}") 

                elif husbands_fathers_fam != None and husbands_mothers_fam != None and wifes_fathers_fam == None and wifes_mothers_fam == None:
                    if fam.wife_id in husbands_fathers_fam.children or fam.wife_id in husbands_mothers_fam.children:
                        errors.append(f"Error: US20: family with id {fam.id} has uncles and aunts married to niece and nephews husband: {fam.husband_id}, wife: {fam.wife_id}") 

                else:
                    continue
    return errors
                

def validate_list_living_married(gedcom):
    """
        US30: List all living married people in a GEDCOM file
    """
    living_married = []

    for family in gedcom.families:
        if family.divorced == None:
            husband = gedcom.individual_with_id(family.husband_id)
            wife = gedcom.individual_with_id(family.wife_id)
        if husband != None and husband.alive:
            living_married.append(f'Living Married: US30: ({husband.id}) {husband.name}')
        if wife != None and wife.alive:
            living_married.append(f'Living Married: US30: ({wife.id}) {wife.name}')
    return living_married


def list_recent_deaths(gedcom):
    """
           US36: List all people in a GEDCOM file who died in the last 30 days
    """
    recent_death = []
    today = datetime.datetime.now()
    for individual in gedcom.individuals:
        if individual.death and individual.death <= today and (today - individual.death).days <= 30:
            recent_death.append(f'Recent Death: Individual ({individual.id}) {individual.name} was recently died in {gedcom.date_string(individual.death)}')

    return recent_death


def list_upcoming_birthdays(gedcom):
    """
        US38: List all living people in a GEDCOM file whose birthdays occur in the next 30 days
    """
    upcoming_birthdays = []
    today = datetime.datetime.now()
    for individual in gedcom.individuals:
        birthday = individual.birthday
        if birthday and birthday <= today:
            this_year_birthday = datetime.datetime(year=today.year, month=birthday.month, day=birthday.day)
            next_year_birthday = datetime.datetime(year=today.year+1, month=birthday.month, day=birthday.day)
            upcoming_birthday = this_year_birthday if this_year_birthday >= today else next_year_birthday
            if (upcoming_birthday - today).days <= 30:
                upcoming_birthdays.append(f'Upcoming Birthday: Individual ({individual.id}) {individual.name} has upcoming birthday on {gedcom.date_string(upcoming_birthday)}')

    return upcoming_birthdays

def list_large_age_diff(gedcom):
    """
        US34: List all couples who were married when the older spouse was more than twice as old as the younger spouse
    """
    age_diff = []
    for family in gedcom.families:
        husband = gedcom.individual_with_id(family.husband_id)
        wife = gedcom.individual_with_id(family.wife_id)
        marriage_date = family.married

        if(marriage_date is not None and husband.birthday is not None and wife.birthday is not None):
            husband_marriage_age = (marriage_date - husband.birthday).days / 365.25
            wife_marriage_age = (marriage_date - wife.birthday).days / 365.25

            if (husband_marriage_age > (2*wife_marriage_age)): #husband was 2 times older when they wed
                age_diff.append(f'({husband.id}) {husband.name} was more than two times older than his wife ({wife.id}) {wife.name} when they got married on {marriage_date.date()}')
            if (wife_marriage_age > (2*husband_marriage_age)): #wife was 2 times older when they wed
                age_diff.append(f'({wife.id}) {wife.name} was more than two times older than her husband ({husband.id}) {husband.name} when they got married on {marriage_date.date()}')
    
    return age_diff

def list_recent_births(gedcom):
    """
        US35: List all people in a GEDCOM file who were born in the last 30 days
    """
    recent_births = []
    today = datetime.datetime.now()
    for individual in gedcom.individuals:
        birthday = individual.birthday
        if birthday and birthday <= today and ((today - birthday).days <= 30):
            recent_births.append(f'Recent Birth Day: Individual ({individual.id}) {individual.name} was born in the last 30 days on {birthday.date()}')

    return recent_births


all_validators = [
    validate_dates_before_current, #US01
    birth_before_marriage, #US02
    birth_before_death, #US03
    validate_marriage_after_divorce, #US04
    validate_marriage_before_death, #US05
    validate_divorce_before_death, #US06
    validate_too_old_individual, #US07
    validate_marriage_after_fourteen, #US10
    validate_no_bigamy, #US11
    validate_parents_not_too_old, #US12
    validate_sibling_spacing, #US13
    validate_multiple_births, #US14
    validate_fewer_than_15_sibs, #US15
    validate_male_last_last_name, #US16
    validate_no_marriage_to_children, #US17
    validate_no_marriage_to_siblings, #US18
    validate_correct_gender, #US21
    validate_unique_families_by_spouses,  # US24
    validate_unique_first_name_in_family,  # US25
    validate_corresponding_entries, #US26
    validate_first_cousins_should_not_marry, #US19
    validate_aunts_and_uncles, #US20
    validate_list_deceased, #US29
    validate_list_living_married, #US30
    list_recent_deaths,  # US36
    list_upcoming_birthdays,  # US38
    list_large_age_diff, #US34
    list_recent_births #US35
]


def validate_gedcom(gedcom):
    errors = []
    for validator in all_validators:
        errors.extend(validator(gedcom))
    return errors
