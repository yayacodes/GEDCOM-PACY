import attr
from prettytable import PrettyTable


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
            families_table.add_row([
                f.id,
                self.date_string(f.married),
                self.date_string(f.divorced),
                f.husband_id,
                self.individual_with_id(f.husband_id).name,
                f.wife_id,
                self.individual_with_id(f.wife_id).name,
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
        individual = list(filter(lambda x: x.id == id, self.individuals))
        if len(individual) > 0:
            return individual[0]
        else:
            return individual(None, name='Not Found')