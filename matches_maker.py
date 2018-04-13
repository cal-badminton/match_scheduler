import math

def get_size(num_entries):
  if num_entries < 5:
    return 4
  elif num_entries < 9:
    return 8
  elif num_entries < 17:
    return 16
  elif num_entries < 33:
    return 32
  elif num_entries < 65:
    return 64
  elif num_entries < 129:
    return 128


def get_num_matches(size):
  mains = size - 1
  num_first_cons = size / 4
  cons = num_first_cons + 2 * num_first_cons - 1
  return (mains, cons, num_first_cons)


def get_num_byes(size, num_entries):
  return size - num_entries


def get_playoff_match_nums_tuple(event, num_entries):
  size = get_size(num_entries)
  num_main_matches, num_cons_matches, num_first_cons = get_num_matches(size)
  total_matches = num_main_matches + num_cons_matches

  num_byes = get_num_byes(size, num_entries)
  num_first_mains = size / 2
  bye_entries = get_bye_entries(size)[:num_byes]
  bye_match_nums = [int(math.ceil(e / 2.0)) for e in bye_entries]
  bye_match_nums.sort()

  finished_cons_matches = []
  useless_match_nums = []
  if_loser_match_nums = []

  for first in range(1, num_first_mains + 1, 2):
    second = first + 1
    main_match_num = second / 2
    if first in bye_match_nums and second in bye_match_nums:
      # pairs of bye match nums in first round cons (bye in 2nd round cons)
      finished_cons_matches.append(num_main_matches + second / 2)
      useless_match_nums.append(num_main_matches + main_match_num + num_first_cons)
    elif first not in bye_match_nums and second not in bye_match_nums:
      no_match_succ = num_main_matches + main_match_num + num_first_cons
      # no match
      useless_match_nums.append(no_match_succ)
    else:
      cons_match_num = num_main_matches + main_match_num + num_first_cons
      if_loser_match_num = num_first_mains + main_match_num
      if_loser_match_nums.append((cons_match_num, if_loser_match_num))
      # bye fills first round cons entry, match is useless
      useless_match_nums.append(num_main_matches + main_match_num)

  finished_match_nums = bye_match_nums + finished_cons_matches
  finished_match_nums = list(set(finished_match_nums))
  match_nums_to_remove = list(set(finished_match_nums + useless_match_nums))
  if_loser_match_nums = list(set(if_loser_match_nums))
  finished_match_nums.sort()
  match_nums_to_remove.sort()
  if_loser_match_nums.sort()

  return (event, total_matches, num_main_matches + 1, finished_match_nums,
          match_nums_to_remove, if_loser_match_nums, {})


def get_round_robin_match_nums_tuple(event, num_entries):
  if num_entries == 3:
    return (event, 0, 0, [], [], [], {1: set([1]), 2: set([2]), 3: set([3])})
  elif num_entries == 4:
    return (event, 0, 0, [], [], [], {1: set([1, 2]), 2: set([3, 4]), 3: set([5, 6])})
  elif num_entries == 5:
    return (event, 0, 0, [], [], [], {1: set([1, 2]), 2: set([3, 4]), 3: set([5, 6]), 4: set([8, 7]), 5: set([9, 10])})
  elif num_entries == 6:
    return (event, 0, 0, [], [], [], {1: set([1, 2, 3]), 2: set([4, 5, 6]), 3: set([7, 8, 9]), 4: set([10, 11, 12]), 5: set([13, 14, 15])})
  print('WARNING: Unsupported number of entries for round robin')


def get_bye_entries(size):
  if size == 4:
    return [2]
  elif size == 8:
    return [2, 7, 4]
  elif size == 16:
    return [2, 15, 6, 11, 4, 13, 8]
  elif size == 32:
    return [2, 31, 10, 23, 6, 27, 14, 19, 4, 29, 12, 21, 8, 25, 16]
  elif size == 64:
    return [2, 63, 18, 47, 10, 55, 26, 39, 6, 59, 22, 43, 14, 51, 30, 35, 4, 61, 20, 45, 12, 53, 28, 37, 8, 57, 24, 41, 16, 49, 32]


def get_match_nums_tuples(num_entries_by_event):
  match_nums_tuples = []
  for event, entries in num_entries_by_event.iteritems():
    if entries < 6:
      match_nums_tuples.append(get_round_robin_match_nums_tuple(event, entries))
    else:
      match_nums_tuples.append(get_playoff_match_nums_tuple(event, entries))
  return match_nums_tuples


def main():
  # Golden Bear LVI
  num_entries_by_event = {'AMS': 17,
  						  'ABWS':5,
                          'AMD': 10,
                          'ABWD': 8,
                          'AXD': 9,
                          'BMS': 20,
                          'BMD': 22,
                          'BXD': 13,
                          'CMS': 22,
                          'CWS': 9,
                          'CMD': 53,
                          'CWD': 20,
                          'CXD': 30,
                          'DMS': 38,
                          'DWS': 13,
                          'DMD': 50, 
                          'DWD': 18,
                          'DXD': 25}

  return get_match_nums_tuples(num_entries_by_event)

if __name__ == '__main__':
  main()
