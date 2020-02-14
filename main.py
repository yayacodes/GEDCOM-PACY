from validation import allValidators

if __name__ == '__main__':
  print('MAIN CODE HERE')

  problems = []
  for validator in allValidators:
    problems.append(validator(gedcom))