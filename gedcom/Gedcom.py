import attr
from prettytable import PrettyTable

from gedcom.Individual import Individual


@attr.s
class Gedcom:
    individuals = attr.ib(factory=list)
    families = attr.ib(factory=list)

    def pretty_print(self):
        individuals_table = PrettyTable()
        individuals_table.field_names = ['ID', 'Name', 'Sex', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse']
        for i in self.individuals:
            individuals_table.add_row([
                i.id,
                i.name,
                i.sex,
                self.date_string(i.birthday),
                i.age, i.alive,
                self.date_string(i.death),
                i.child,
                i.spouse
            ])

        families_table = PrettyTable()
        families_table.field_names = [
            'ID', 'Married',
            'Divorced',
            'Husband ID',
            'Husband Name',
            'Wife ID',
            'Wife Name',
            'Children'
        ]

        for f in self.families:
            husband = self.individual_with_id(f.husband_id)
            wife = self.individual_with_id(f.wife_id)
            families_table.add_row([
                f.id,
                self.date_string(f.married),
                self.date_string(f.divorced),
                f.husband_id,
                husband.name if husband is not None else 'Not found',
                f.wife_id,
                wife.name if wife is not None else 'Not found',
                f.children
            ])

        print('Individuals')
        print(individuals_table)
        print('Families')
        print(families_table)
        return ("Individuals\n" + str(individuals_table) + "\nFamilies\n" + str(families_table))

    def date_string(self, date):
        if date is None:
            return 'NA'
        else:
            return date.strftime('%Y-%m-%d')

    def individual_with_id(self, id):
        individual = [i for i in self.individuals if i.id == id]
        if len(individual) > 0:
            return individual[0]
        else:
            return None

    # Get a family with the corresponding id
    def family_with_id(self, id):
        family = [f for f in self.families if f.id == id]
        return family[0] if len(family) > 0 else None

    def get_parents(self, child_id):
        
        if child_id is None:
            return None

        child = self.individual_with_id(child_id)
        if child is None or child.child is None:
            return None

        family = self.family_with_id(child.child)
        if family is None:
            return None
        
        husband = self.individual_with_id(family.husband_id)
        wife = self.individual_with_id(family.wife_id)
        if wife is None and husband is None:
            return None
        
        return { 'mother': wife, 'father': husband}