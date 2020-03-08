import attr
from datetime import datetime

from gedcom.Family import Family
from gedcom.Gedcom import Gedcom
from gedcom.Individual import Individual


@attr.s
class GedcomRow:
    level_string: str = attr.ib()
    tag: str = attr.ib()
    arg: str = attr.ib()

    valid_tags_per_level = {
        0: ['INDI', 'FAM', 'HEAD', 'TRLR', 'NOTE'],
        1: ['NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS','MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV'],
        2: ['DATE']
    }

    @property
    def level(self) -> int:
        return int(self.level_string)

    @property
    def valid(self) -> bool:
        if self.level in self.valid_tags_per_level.keys():
            if self.tag in self.valid_tags_per_level[int(self.level)]:
                return True
            else: return False
        else: return False


class GedcomParser:
    def parse(self, filename):
        def modify_lines(line):
            line = line.rstrip('\n')
            row = self.line_to_GedcomRow(line)
            return row
    
        with open(filename, 'r') as f:
            all_lines = f.readlines()
            lines_as_rows = map(modify_lines, all_lines)
            data = list(filter(lambda x: x.valid, lines_as_rows))
            all_records = self.seperate_rows_into_records(data)
            all_records = list(filter(lambda x: x is not None, map(self.convert_record_array_to_object, all_records)))
            
            # Sorted lists by id
            individuals = sorted(list(filter(lambda x: x.kind is 'INDI', all_records)), key=lambda x: x.id)
            families = sorted(list(filter(lambda x: x.kind is 'FAM', all_records)), key=lambda x: x.id)
            return Gedcom(individuals, families)
            
    def line_to_GedcomRow(self, line):
        # Extract the level, tag, and argument from a line in a GED file
        (level, tag, arg) = (line.split(' ', 2) + [''])[:3]

        # Swap arg and tag if they are INDI or FAM, recheck validity
        if arg in ['INDI', 'FAM'] or tag in ['INDI', 'FAM']:
            arg, tag = tag, arg

        return GedcomRow(level, tag, arg)
    
    # Seperate data into a per-level structure
    # Rows are in format (level, tag, arg)
    def seperate_rows_into_records(self, list_of_rows):
        """ Returns array of record-arrays, where each 
            record-array is an array of all the rows in a record
        """
        all_records = [] # list of all records

        this_record = [] # a list of rows for a given record
        for row in list_of_rows:
            if row.level == 0:
                all_records.append(this_record) # Add the last record to our master list
                this_record = [row] # start a new record
            else:
                this_record.append(row)

        return all_records[1:]
    
    # Convert a record-array into objects
    def convert_record_array_to_object(self, record_array):
        """ Returns list of records structured as objects """
        first_row = record_array[0]

        # What kind of record is it (individual/family)
        record = None
        if first_row.tag == 'INDI':
            record = Individual(first_row.arg)


        elif first_row.tag == 'FAM':
            record = Family(first_row.arg)

        # Handle the attributes of the record
        for (index, row) in enumerate(record_array[1:]):
            if index+2 <= len(record_array[1:]):
                next_row = record_array[index+1+1]

            # If not level 1, it's not an attribute to handle
            if row.level > 1:
                next

            def name_part_of(name, part="first"):
                if "/" in name:
                    return name[:name.find("/")].strip() if part == "first" else name[name.find("/") + 1:name.rfind("/")]
                elif " " in name:
                    return name[:name.find(" ")] if part == "first" else name[name.find(" "):].strip()
                else:
                    return name if part == "first" else ""

            # Get attributes for individual from row
            if first_row.tag == 'INDI':
                if row.tag == 'NAME':
                    record.first_name = name_part_of(row.arg, "first")
                    record.last_name = name_part_of(row.arg, "last")
                    record.name = row.arg.replace('/', '')
                if row.tag == 'SEX':
                    record.sex = row.arg
                if row.tag == 'BIRT' and next_row.tag == 'DATE':
                    record.birthday = datetime.strptime(next_row.arg.lower().title(), '%d %b %Y')
                if row.tag == 'DEAT' and next_row.tag == 'DATE':
                    record.death = datetime.strptime(next_row.arg.lower().title(), '%d %b %Y')
                if row.tag == 'FAMC':
                    record.child = row.arg
                if row.tag == 'FAMS':
                    record.spouse = row.arg
                    record.spouses.append(row.arg)

            # Get attributes for family from row
            if first_row.tag == 'FAM':
                if row.tag == 'MARR' and next_row.tag == 'DATE':
                    record.married = datetime.strptime(next_row.arg.lower().title(), '%d %b %Y')
                if row.tag == 'DIV' and next_row.tag == 'DATE':
                    record.divorced = datetime.strptime(next_row.arg.lower().title(), '%d %b %Y')
                if row.tag == 'HUSB':
                    record.husband_id = row.arg
                if row.tag == 'WIFE':
                    record.wife_id = row.arg
                if row.tag == 'CHIL':
                    record.children.append(row.arg)

        return record


if __name__ == '__main__':
    gedcom_file = GedcomParser().parse('../res/test_family.ged')
    with open('../res/output.txt', 'w') as f:
        f.write(gedcom_file.pretty_print())