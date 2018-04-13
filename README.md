## Match Scheduling

[tournamentsoftware's Badminton Tournament Planner](http://www.tournamentsoftware.com/product/download.aspx?id=16&s=2) is great for making draws, but their match scheduling functionality is lacking. For example, it is impossible to schedule consolation matches to take less time than main matches.

### What It Does
This script generates the match schedule for a tournament either by specifying the number of entires for each event or by passing in an Excel spreadsheet of draws exported from [tournamentsoftware's Badminton Tournament Planner](http://www.tournamentsoftware.com/product/download.aspx?id=16&s=2).

### Dependencies
This works with `python2`, but not `python3` because of its dependency on [`xlrd`](https://pypi.python.org/pypi/xlrd).

### Setup
1. Specify the number of entries for each eventmatches/number of entries 

### Usage - Specify Number of Entires for Each Event
The fastest and easiest way to run this script is to define `num_entries_by_event` in `matches_maker.py`'s `main()` function in this form:

	num_entries_by_event = {event1_name: event1_num_entries,
							event2_name: event2_num_entries,
							...
							eventN_name: eventN_num_entries}

Then run `scheduler.py`:

	$ python scheduler.py

### Usage - Pass in Excel Spreadsheet of Draws
Another way to run this script is to parse a spreadsheet of draws. Make sure you forward all matches for all draws, then export the draws.

Then run `scheduler.py`:

	$ python scheduler.py <full_path_to_spread_sheet>

### Products
Running the script writes schedules to the following folders:

- `by_match_number`: Schedules sorted by match number. One file for each event.
- `by_time`: Schedules sorted by start time. One file for each event and one file for each day of matches.
- `start_times`: One file for each day that contains the start times of events on that day.
