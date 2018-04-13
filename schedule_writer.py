import os

def lazily_create_folder(folder):
  if not os.path.exists(folder):
    os.makedirs(folder)


def format_time(time):
  hours, minutes = time / 60, time % 60
  suffix = 'AM' if hours < 12 else 'PM'
  if hours == 12 and minutes == 0:
    suffix = 'noon'
  if hours > 12:
    hours -= 12
  return '%02d:%02d %s' % (hours, minutes, suffix)


def format_entry(entry, first_time):
  match, time, court = entry['match'], entry['time'] + first_time, entry['court']
  end_time = time + match.duration
  start, end = format_time(time), format_time(end_time)
  event_and_num = match.event + str(match.number)
  return '%s - %s | %s | %s' % (start, end, event_and_num.ljust(6), court)


def format_entry_by_number(entry, first_time):
  match, time, court = entry['match'], entry['time'] + first_time, entry['court']
  end_time = time + match.duration
  start, end = format_time(time), format_time(end_time)
  event_and_num = match.event + str(match.number)
  return '%s | %s - %s | %s' % (event_and_num.ljust(6), start, end, court)


def write_match_schedule_by_event(day, match_log_by_event, start_hour, start_min):
  for event in match_log_by_event:
    match_log = match_log_by_event[event]
    write_match_schedule(event, match_log, start_hour, start_min)

  for event in match_log_by_event:
    match_log = match_log_by_event[event]
    write_match_schedule_by_match_number(event, match_log, start_hour, start_min)


def write_match_schedule(name, match_log, start_hour, start_min, format_fn=format_entry, folder='time'):
  folder = 'by_%s' % folder
  lazily_create_folder(folder)
  f = open('%s/%s.txt' % (folder, name), 'w')

  buf = ['=== MATCH SCHEDULE FOR %s ===' % name.upper()]
  first_time = start_hour * 60 + start_min
  for entry in match_log:
    buf.append(format_fn(entry, first_time))

  f.write('\n'.join(buf))
  f.close()


def write_match_schedule_by_match_number(name, match_log, start_hour, start_min):
  match_log_copy = list(match_log)
  match_log_copy.sort(key=lambda x: x['match'].number)
  write_match_schedule(name, match_log_copy, start_hour, start_min, format_entry_by_number, 'match_number')


def write_start_times(day, match_log_by_event, start_hour, start_min):
  folder = 'start_times'
  lazily_create_folder(folder)
  f = open('%s/%s.txt' % (folder, day), 'w')

  first_time = start_hour * 60 + start_min
  start_times = []

  for event in match_log_by_event:
    start = match_log_by_event[event][0]['time'] + first_time
    start_times.append((start, '%s - %s' % (format_time(start), event)))

  start_times.sort(key=lambda x: x[0])
  for i in range(len(start_times)):
    start_times[i] = start_times[i][1]

  f.write('\n'.join(start_times))
  f.close()
