from tournament_structures import Match

NUM_MATCHES_TO_FIRST_ROUND_CONS_MATCHES = {0: 0, 5: 2, 11: 4, 23: 8, 47: 16, 95: 32, 191: 64, 383: 128}

def get_playoff_matches(match_nums_tuple):
  event, total_matches, first_cons_match_num, finished_match_nums, match_nums_to_remove, if_loser_match_nums = match_nums_tuple
  matches = []

  cons_event = event + 'C'
  for i in range(1, first_cons_match_num):
    matches.append(Match(i, event))

  for i in range(first_cons_match_num, total_matches):
    matches.append(Match(i, cons_event))

  matches.append(Match(total_matches, cons_event, True))

  main_matches = matches[:first_cons_match_num - 1]
  cons_matches = matches[first_cons_match_num - 1:]

  num_first_round_matches = (len(main_matches) + 1) / 2
  link_matches(main_matches, num_first_round_matches)

  # Connect first round matches to their corresponding cons matches
  for i in range(num_first_round_matches):
    if (i + 1) not in finished_match_nums:
      main_matches[i].add_successor(cons_matches[int(i / 2)])

  num_first_round_cons_matches = NUM_MATCHES_TO_FIRST_ROUND_CONS_MATCHES[len(cons_matches)]
  link_matches(cons_matches[num_first_round_cons_matches:], num_first_round_cons_matches)

  # Connect first round cons matches to their corresponding next matches
  for i in range(num_first_round_cons_matches):
    cons_matches[i].add_successor(cons_matches[i + num_first_round_cons_matches])

  # If Loser dependencies
  for if_loser_match_num in if_loser_match_nums:
    cons, main = if_loser_match_num
    matches[main - 1].add_successor(matches[cons - 1])

  # Remove useless and finished matches from the graph
  for match_num in match_nums_to_remove:
    match = matches[match_num - 1]
    if match_num in finished_match_nums and match.predecessors:
      print('WARNING: Removing finished match with predecessors.')
    match.remove()

  # Remove matches without links from the given list of matches
  def remove_matches_without_links(matches):
    copy = list(matches)
    for match in copy:
      if match.predecessors or match.successors:
        continue
      match_num = match.number
      if match_num in match_nums_to_remove:
        matches.remove(match)
      else:
        print('WARNING: Match %d has no links, but is not useless or finished' % (match_num))
    return matches

  remove_matches_without_links(main_matches)
  remove_matches_without_links(cons_matches)

  return {'main': main_matches, 'cons': cons_matches}


def get_round_robin_matches(rr_match_nums_tuple):
  event, rr_match_num_sets = rr_match_nums_tuple
  matches = []
  last_round_matches = set()

  for rr_match_num_set in rr_match_num_sets.values():
    rr_matches = set()
    for rr_match_num in rr_match_num_set:
      rr_match = Match(rr_match_num, event)
      rr_matches.add(rr_match)
      matches.append(rr_match)
      for last_round_match in last_round_matches:
        last_round_match.add_successor(rr_match)
    last_round_matches = rr_matches

  return {'main': matches, 'cons': []}


def link_matches(matches, num_first_round_matches):
  num_matches = len(matches)
  for i in range(num_matches):
    successor_ind = num_first_round_matches + int(i / 2)
    if successor_ind >= num_matches:
      break
    matches[i].add_successor(matches[successor_ind])


def get_matches_by_event(match_nums_tuples):
  matches_by_event = {}
  for match_nums_tuple in match_nums_tuples:
    event = match_nums_tuple[0]
    rr_match_num_sets = match_nums_tuple[-1]
    if rr_match_num_sets:
      matches = get_round_robin_matches((event, rr_match_num_sets))
    else:
      matches = get_playoff_matches(match_nums_tuple[:-1])
    matches_by_event[event] = matches
  return matches_by_event


def group_main_matches_by_round(main_matches):
  main_matches_by_round = [main_matches[-1:]]
  num_matches_in_round, num_grouped_matches = 2, 1

  while num_grouped_matches < len(main_matches):
    matches_in_round = main_matches[-(num_matches_in_round + num_grouped_matches):-num_grouped_matches]
    main_matches_by_round.insert(0, matches_in_round)
    num_grouped_matches += num_matches_in_round
    num_matches_in_round *= 2

  return main_matches_by_round


def get_event_round_matches(matches_by_event, event, rnd):
  return group_main_matches_by_round(matches_by_event[event]['main'])[rnd]


def start_event_round_a_after_event_round_b(matches_by_event, event_a, round_a, event_b, round_b):
  a_matches = get_event_round_matches(matches_by_event, event_a, round_a)
  b_matches = get_event_round_matches(matches_by_event, event_b, round_b)
  for a_match in a_matches:
    for b_match in b_matches:
      b_match.add_successor(a_match)
