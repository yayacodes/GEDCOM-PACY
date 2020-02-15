from validation import allValidators
from parser import GedcomParser

if __name__ == '__main__':
  print('MAIN CODE HERE')
  gedcom = GedcomParser().parse('test_family.ged')
  gedcom.pretty_print()

  problems = []

  # Loop through each validator and apply it to the gedcom file
  # Any problems will be appended to `problems` list
  for validate in allValidators:
    problems_from_validator = validate(gedcom)
    problems.append(problems_from_validator)

  # Print our problems
  print('Problems:', problems)