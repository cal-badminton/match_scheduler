# Excel file parsing
from xlrd import open_workbook as xlopen
import re

# File management
import sys, os

INFINITY = sys.maxint

MATCH_NUM_REGEX = re.compile('#([0-9]+):')
LOSER_REGEX = re.compile('Loser #([0-9]+)')
IF_LOSER_REGEX = re.compile('If Loser #([0-9]+)')
ROUND_ROBIN_MATCH_REGEX = re.compile('#([0-9]+): R([0-9]+)')

def get_match_num(cell_value):
  if MATCH_NUM_REGEX.match(cell_value):
    try:
      return int(cell_value[1:-1])
    except ValueError:
      return None
  return None


def get_successor_match_num(sheet, no_match_row, no_match_col):
  no_match_col += 1
  above_match_num, above_match_dist = None, sheet.nrows - no_match_row
  for row_num in range(no_match_row, -1, -1):
    cell_value = sheet.cell(row_num, no_match_col).value.strip()
    match_num = get_match_num(cell_value)
    if match_num is not None:
      above_match_num, above_match_dist = match_num, no_match_row - row_num
      break

  max_below_row = no_match_row + above_match_dist
  for row_num in range(no_match_row, max_below_row):
    cell_value = sheet.cell(row_num, no_match_col).value.strip()
    match_num = get_match_num(cell_value)
    if match_num is not None:
      return match_num
  return above_match_num


def get_match_nums_tuple(sheet):
  match_nums = []
  finished_match_nums = []
  useless_match_nums = [] # a useless match has only 1 team/player that automically wins and advances to the next round
  if_loser_match_nums = []
  rr_match_num_sets = {}

  for col_num in xrange(0, sheet.ncols):
    for row_num in xrange(0, sheet.nrows):
      cell_value = sheet.cell(row_num, col_num).value.strip()

      match_num = get_match_num(cell_value)
      if match_num is not None:
        match_nums.append(match_num)
        above_cell_value = sheet.cell(row_num - 1, col_num).value.strip()
        # If above cell is filled, the match is finished
        if above_cell_value != '':
          finished_match_nums.append(match_num)
          # If the above cell is Bye, the next match is useless (CONS ONLY)
          if above_cell_value == 'Bye':
            useless_match_num = get_successor_match_num(sheet, row_num, col_num)
            useless_match_nums.append(useless_match_num)

      # If the cell value is No Match, the next match is useless (CONS ONLY)
      if cell_value == 'No Match':
        useless_match_num = get_successor_match_num(sheet, row_num, col_num)
        if useless_match_num is not None:
          useless_match_nums.append(useless_match_num)

      # If the cell value is If Loser #<number> (bye in main draw), link the main match with the cons match.
      if_loser_match = IF_LOSER_REGEX.match(cell_value)
      if if_loser_match:
        main_match_num = int(if_loser_match.group(1))
        cons_match_num = get_successor_match_num(sheet, row_num, col_num)
        if cons_match_num is not None:
          if_loser_match_nums.append((cons_match_num, main_match_num))

      # First round cons matches. If the above cell is filled, the next match is useless
      if LOSER_REGEX.match(cell_value):
        if sheet.cell(row_num - 1, col_num).value.strip() != '':
          useless_match_num = get_successor_match_num(sheet, row_num, col_num)
          if useless_match_num is not None:
            useless_match_nums.append(useless_match_num)

      # Find round robin matches
      round_robin_match_match = ROUND_ROBIN_MATCH_REGEX.match(cell_value)
      if round_robin_match_match:
        rr_match_num = int(round_robin_match_match.group(1))
        round_num = int(round_robin_match_match.group(2))
        if round_num not in rr_match_num_sets:
          rr_match_num_sets[round_num] = set()
        rr_match_num_sets[round_num].add(rr_match_num)

  event = str(sheet.name.strip())
  first_cons_match_num = match_nums[0] if match_nums else 0
  total_matches = len(match_nums)
  finished_match_nums = list(set(finished_match_nums))
  match_nums_to_remove = list(set(finished_match_nums + useless_match_nums))
  if_loser_match_nums = list(set(if_loser_match_nums))
  finished_match_nums.sort()
  match_nums_to_remove.sort()
  if_loser_match_nums.sort()
  return (event, total_matches, first_cons_match_num, finished_match_nums,
          match_nums_to_remove, if_loser_match_nums, rr_match_num_sets)


def get_match_nums_tuples(input_file):
  if not os.path.isfile(input_file):
    print('* {0} does not exist.'.format(input_file))
    return None

  book = xlopen(input_file, formatting_info=True)
  sheets = book.sheets()
  return [get_match_nums_tuple(sheet) for sheet in sheets]


def main():
  if len(sys.argv) != 2:
    print('Please specify an Excel file of draws exported from tournamentsoftware\'s Badminton Tournament Planner.')
    exit(0)

  match_nums_tuples = get_match_nums_tuples(sys.argv[1])


if __name__ == '__main__':
  main()
