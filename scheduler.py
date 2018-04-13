# https://en.wikipedia.org/wiki/Heterogeneous_Earliest_Finish_Time

from tournament_structures import *
from draws_parser import get_match_nums_tuples as get_tuples_from_draws
from graph_maker import get_matches_by_event, start_event_round_a_after_event_round_b
from matches_maker import main as get_tuples_from_entries
from schedule_writer import *

import sys

INFINITY = float('inf')

class Scheduler:
  def __init__(self, courts=[], matches=[]):
    self.time = 0
    self.start_time = 0
    self.courts = courts
    self.matches = matches
    self.match_log = []
    self.match_log_by_event = {}
    self.match_num = 0


  def add_court(self, court):
    self.courts.append(court)


  def add_match(self, match):
    self.matches.append(match)


  def sort_matches_by_rank(self):
    self.matches.sort(key=lambda x: x.get_rank(), reverse=True)


  def schedule_matches(self):
    if not self.matches:
      return

    free_courts = self.get_free_courts()
    if not free_courts:
      self.finish_next_free_court()
      self.schedule_matches()
      return

    self.match_num = 0

    def schedule_match_on_worst_acceptable_free_court(match):
      court = self.get_worst_acceptable_free_court(match, free_courts)
      if court:
        court.schedule_match(match)
        schedule_info = match.schedule(court, self.time)
        self.match_log.append(schedule_info)

        if match.event not in self.match_log_by_event:
          self.match_log_by_event[match.event] = []

        self.match_log_by_event[match.event].append(schedule_info)
        self.matches.pop(self.match_num)
        free_courts.remove(court)
        self.match_num = 0
      else:
        self.match_num += 1

    while free_courts and self.matches and (self.match_num < len(self.matches)):
      match = self.matches[self.match_num]
      if not match.are_predecessors_finished(self.time):
        self.match_num += 1
      else:
        schedule_match_on_worst_acceptable_free_court(match)

    # no more free courts or free courts are not good enough
    if (not free_courts) or (self.match_num >= len(self.matches) and self.match_num != 0):
      self.finish_next_free_court()
      self.schedule_matches()


  def finish_next_free_court(self):
    next_free_court = self.get_next_free_court()
    if next_free_court is None:
      self.advance_time(1)
    else:
      self.advance_time(next_free_court.time_til_free)


  def advance_time(self, increment):
    self.time += increment
    for court in self.courts:
      court.decrement_time(increment)


  def get_free_courts(self):
    return [court for court in self.courts if court.is_free()]


  def get_occupied_courts(self):
    return [court for court in self.courts if not court.is_free()]


  def get_next_free_court(self):
    next_time_til_free, next_free_court = INFINITY, None
    for court in self.get_occupied_courts():
      if court.time_til_free < next_time_til_free:
        next_time_til_free, next_free_court = court.time_til_free, court
    return next_free_court


  def get_worst_acceptable_free_court(self, match, free_courts):
    min_court_quality = match.min_court_quality
    worst_acceptable_quality, worst_acceptable_court = INFINITY, None
    for court in free_courts:
      quality = court.quality
      if quality >= min_court_quality and quality < worst_acceptable_quality:
        worst_acceptable_quality, worst_acceptable_court = quality, court
    return worst_acceptable_court


def separate_doubles_matches(matches_by_event):
  other_matches, doubles_matches = [], []
  for event in matches_by_event:
    matches = matches_by_event[event]
    all_matches = matches['main'] + matches['cons']
    matches = doubles_matches if 'MD' in event or 'WD' in event else other_matches
    for match in all_matches:
      event = match.event
      match.event = event[:-1] if event[-1] == 'C' else event
      matches.append(match)

  return other_matches, doubles_matches


def main():
  if len(sys.argv) == 2:
    match_nums_tuples = get_tuples_from_draws(sys.argv[1])
  else:
    print('*** Using num_entries_by_event defined in matches_maker.py to generate and schedule matches. ***\nTo use draws from tournamentsoftware\'s Badminton Tournament Planner instead:\n 1. Export the draws to an Excel file.\n 2. Provide the file as an argument to this script.\n')
    match_nums_tuples = get_tuples_from_entries()

  match_nums_tuples.sort()
  matches_by_event = get_matches_by_event(match_nums_tuples)
  # sun_matches, sat_matches = separate_doubles_matches(matches_by_event)
  sat_matches, sun_matches = separate_doubles_matches(matches_by_event)


  # start first round BWD after AWD semis
  # start_event_round_a_after_event_round_b(matches_by_event, 'BWD', 0, 'AWD', -2)

  sat_courts = [Court(1, Court.HIGH_QUALITY),
                Court(2, Court.HIGH_QUALITY),
                Court(3, Court.MED_QUALITY),
                Court(4, Court.HIGH_QUALITY),
                Court(5, Court.HIGH_QUALITY),
                Court(6, Court.MED_QUALITY),
                Court(7, Court.MED_QUALITY, 180),
                Court(8, Court.MED_QUALITY, 180),
                Court(9, Court.MED_QUALITY, 180),
                Court(10, Court.LOW_QUALITY, 180),
                Court(11, Court.LOW_QUALITY, 180),
                Court(12, Court.LOW_QUALITY, 180)]

  sat_scheduler = Scheduler(sat_courts, sat_matches)
  sat_scheduler.sort_matches_by_rank()
  sat_scheduler.schedule_matches()

  sun_courts = [Court(1, Court.HIGH_QUALITY),
                Court(2, Court.HIGH_QUALITY),
                Court(3, Court.MED_QUALITY),
                Court(4, Court.HIGH_QUALITY),
                Court(5, Court.HIGH_QUALITY),
                Court(6, Court.MED_QUALITY),
                Court(7, Court.MED_QUALITY),
                Court(8, Court.MED_QUALITY),
                Court(9, Court.MED_QUALITY),
                Court(10, Court.LOW_QUALITY),
                Court(11, Court.LOW_QUALITY),
                Court(12, Court.LOW_QUALITY)]

  sun_scheduler = Scheduler(sun_courts, sun_matches)
  sun_scheduler.sort_matches_by_rank()
  sun_scheduler.schedule_matches()

  START_HR, START_MIN = 8, 0

  write_start_times('saturday', sat_scheduler.match_log_by_event, START_HR, START_MIN)
  write_start_times('sunday', sun_scheduler.match_log_by_event, START_HR, START_MIN)

  write_match_schedule('saturday', sat_scheduler.match_log, START_HR, START_MIN)
  write_match_schedule('sunday', sun_scheduler.match_log, START_HR, START_MIN)

  write_match_schedule_by_event('saturday', sat_scheduler.match_log_by_event, START_HR, START_MIN)
  write_match_schedule_by_event('sunday', sun_scheduler.match_log_by_event, START_HR, START_MIN)


if __name__ == '__main__':
  main()
