class EventAttributes:
  def __init__(self, default_attributes):
    self.attributes = {}
    self.default = default_attributes


  def get_attributes(self, event):
    if event in self.attributes:
      return self.attributes[event]

    attributes = dict(self.default)
    if event[0] == 'A':
      attributes['min court quality'] = Court.HIGH_QUALITY
    elif event[0] == 'B':
      attributes['min court quality'] = Court.MED_QUALITY
    else:
      attributes['min court quality'] = Court.LOW_QUALITY

    if event[-1] == 'C':
      attributes['duration'] = less_duration(attributes['duration'])
      attributes['min court quality'] = Court.inferior_quality(attributes['min court quality'])

    return attributes


  def set_attributes(self, event, attributes):
    self.attributes[event] = attributes


class Match:
  def __init__(self, number, event='', is_final=False):
    self.event = event
    self.number = number
    self.successors = [] # rank = duration + rest_time + (rank of succ w/ greatest rank)
    self.predecessors = [] # all predecessors must finish before scheduling

    event_attributes = EVENT_ATTRIBUTES.get_attributes(event)
    self.duration = event_attributes['duration']
    self.min_court_quality = event_attributes['min court quality']
    self.rest_time = event_attributes['rest time']

    if is_final:
      self.duration = more_duration(self.duration)
      self.min_court_quality = Court.superior_quality(self.min_court_quality)

    self.rank = self.duration
    self.is_rank_stale = False
    self.scheduled_court = None
    self.scheduled_time = None
    self.completed_time = None


  def __repr__(self):
    successors = (' > ' + (str(self.successors) if len(self.successors) > 1 else str(self.successors[0]))) if self.successors else ''
    return self.event + str(self.number) + successors


  def get_rank(self):
    if not self.is_rank_stale:
      return self.rank

    self.rank = self.duration + self.rest_time + self.max_successor_rank()
    return self.rank


  def max_successor_rank(self):
    max_rank = 0
    for successor in self.successors:
      rank = successor.get_rank()
      if rank > max_rank:
        max_rank = rank

    return max_rank


  def total_successor_rank(self):
    total_rank = 0
    for successor in self.successors:
      total_rank += successor.get_rank()

    return total_rank


  def add_successor(self, successor):
    if successor not in self.successors:
      self.is_rank_stale = True
      self.successors.append(successor)

    if self not in successor.predecessors:
      successor.predecessors.append(self)


  def add_predecessor(self, predecessor):
    predecessor.add_successor(self)


  def remove_successor(self, successor):
    if successor in self.successors:
      self.successors.remove(successor)

    if self in successor.predecessors:
      successor.predecessors.remove(self)


  def remove_predecessor(self, predecessor):
    predecessor.remove_successor(self)


  def remove(self):
    if len(self.predecessors) > 1:
      print('WARNING: Removing Match with more than one predecessor.')

    for successor in self.successors:
      for predecessor in self.predecessors:
        predecessor.add_successor(successor)

    successors, predecessors = list(self.successors), list(self.predecessors)
    for successor in successors:
      self.remove_successor(successor)

    for predecessor in predecessors:
      self.remove_predecessor(predecessor)


  def schedule(self, court, time):
    self.scheduled_court = court
    self.scheduled_time = time
    self.completed_time = time + self.duration
    return {'time': time, 'court': court, 'match': self}


  def is_finished(self, time):
    return ((self.completed_time is not None) and
            (self.completed_time + self.rest_time <= time))


  def are_predecessors_finished(self, time):
    for predecessor in self.predecessors:
      if not predecessor.is_finished(time):
        return False
    return True


class Court:
  LOW_QUALITY = 0
  MED_QUALITY = 1
  HIGH_QUALITY = 2

  @staticmethod
  def superior_quality(quality):
    return quality + 1 if quality < Court.HIGH_QUALITY else quality


  @staticmethod
  def inferior_quality(quality):
    return quality - 1 if quality > Court.LOW_QUALITY else quality


  def __init__(self, number, quality, time_til_free=0):
    self.number = number
    self.quality = quality
    self.match = None
    self.time_til_free = time_til_free


  def __repr__(self):
    return 'Court ' + str(self.number)


  def is_free(self):
    if self.time_til_free <= 0:
      self.match = None
    else:
      return False

    return self.match is None


  def schedule_match(self, match):
    self.match = match
    self.time_til_free = match.duration


  def decrement_time(self, decrement):
    if not self.is_free():
      self.time_til_free -= min(self.time_til_free, decrement)


def more_duration(duration):
  return duration + 20


def less_duration(duration):
  return duration - 20


MAIN_DURATION = 30
EVENT_ATTRIBUTES = EventAttributes({'duration': MAIN_DURATION, 'rest time': 15, 'min court quality': Court.MED_QUALITY})
