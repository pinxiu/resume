#!/usr/bin/env python

from __future__ import division
import argparse
import math
import random
import time

"""
===============================================================================
  Please complete the following function.
===============================================================================
"""

def heuristic1(item, max_weight, max_cost):
  return item[2] * item[3] / (1 + (item[4] - item[3]) ** 2)

def heuristic2(item, max_weight, max_cost):
  return item[2] * item[3] / ((item[4] - item[3]) * item[4])

def heuristic3(item, max_weight, max_cost):
  return (item[2] / max_weight + item[3] / max_cost) / (item[4] - item[3])

def solve(P, M, N, C, items, constraints):
  """
  Write your amazing algorithm here.

  Return: a list of strings, corresponding to item names.
  """
  results = list()
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic1, False))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic2, False))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic3, False))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic1, True, 0.95))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic2, True, 0.95))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic3, True, 0.95))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic1, True, 0.5))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic2, True, 0.5))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic3, True, 0.5))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic1, True, 0.4))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic1, True, 0.8))
  results.append(solve_helper(P, M, N, C, items, constraints, heuristic1, True, 0.75))
  result = max(results, key=lambda result: result[0])
  log = open("log/" + str(int(time.time())) + ".txt", "w")
  for index in range(len(results)):
    log.write("result " + str(index) + " : " + str(results[index][0]) + "\n")
  log.close()
  return result[1]

def solve_helper(P, M, N, C, items, constraints, heuristics, random_flag, margin=1):

  max_weight = max(items, key=lambda item: item[2])[2]
  max_cost = max(items, key=lambda item: item[3])[3]
  useful_items = [(heuristics(item, max_weight, max_cost), item) for item in items if item[3] < item[4] and item[3] < M and item[2] < P]
  
  indexed_items = dict()
  unique_indices = set()
  for pair in useful_items:
    item = pair[1]
    index = item[1]
    if index not in indexed_items:
      indexed_items[index] = list()
      unique_indices.add(index)
    indexed_items[index].append(pair)

  if len(unique_indices) > N / 2:
    incompatibles = set()
    for constraint in constraints:
      for cls1 in constraint:
        for cls2 in constraint:
          if cls1 == cls2:
            continue
          incompatibles.add((cls1, cls2))

    unused_copy = list(useful_items)
    best_list = list()
    best_value = 0
    while unused_copy:
      unused = sorted(list(unused_copy), key=lambda pair: pair[0])
      accept_items = list()
      while unused:
        if random_flag and random.random() > margin:
          pair = random.choice(unused)
          unused.remove(pair)
        else:
          pair = unused.pop()
        item = pair[1]
        flag = True
        for old_item in accept_items:
          if (item[1], old_item[1]) in incompatibles:
            flag = False
            break
        if flag:
          accept_items.append(item)
          unused_copy.remove(pair)
      total_weight = 0
      total_cost = 0
      total_resale = 0
      real_list = list()
      accept_items = sorted(accept_items, key=lambda item: heuristics(item, max_weight, max_cost))
      while accept_items:
        if random_flag and random.random() > margin:
          item = random.choice(accept_items)
          accept_items.remove(item)
        else:
          item = accept_items.pop()
        total_weight += item[2]
        total_cost += item[3]
        if total_weight > P or total_cost > M:
          total_weight -= item[2]
          total_cost -= item[3]
          unused.append((heuristics(item, max_weight, max_cost), item))
          continue
        total_resale += item[4]
        real_list.append(item)
      net_income = total_resale + M - total_cost
      if net_income > best_value:
        best_value = net_income
        best_list = list(real_list)
    return (best_value, [item[0] for item in best_list])

  compatibles = dict()
  for cls1 in unique_indices:
    compatibles[cls1] = set(unique_indices)
  for constraint in constraints:
    for cls1 in constraint:
      if cls1 not in unique_indices:
        continue
      for cls2 in constraint:
        if cls1 == cls2:
          continue
        if cls2 not in unique_indices:
          continue
        compatibles[cls1].discard(cls2)
  
  cls_weight = dict()
  for cls in unique_indices:
    cls_weight[cls] = 0
    for pair in indexed_items[cls]:
      cls_weight[cls] += pair[0]
    
  best_list = list()
  best_value = 0
  unused = list(unique_indices)
  unused = sorted(unused, key=lambda index: cls_weight[index])
  
  while unused:
    pivot = unused.pop()
    accept_cls = set()
    good_cls = sorted(list(compatibles[pivot]), key=lambda index: cls_weight[index])
    while good_cls:
      if random_flag and random.random() > margin:
        cls = random.choice(good_cls)
        good_cls.remove(cls)
      else:
        cls = good_cls.pop()
      cls_comp = compatibles[cls]
      flag = True
      for old_cls in accept_cls:
        if old_cls not in cls_comp:
          flag = False
          break
      if flag:
        accept_cls.add(cls)
    used = list()
    for cls in accept_cls:
      used.extend(indexed_items[cls])

    used = sorted(used, key=lambda pair: pair[0])
 
    total_weight = 0
    total_cost = 0
    total_resale = 0
    real_list = list()
    while used:
      if random_flag and random.random() > margin:
        pair = random.choice(used)
        used.remove(pair)
      else:
        pair = used.pop()
      item = pair[1]
      total_weight += item[2]
      total_cost += item[3]
      if total_weight > P or total_cost > M:
        total_weight -= item[2]
        total_cost -= item[3]
        continue
      total_resale += item[4]
      real_list.append(item)
    net_income = total_resale + M - total_cost
    if net_income > best_value:
      best_value = net_income
      best_list = list(real_list)
  return (best_value, [item[0] for item in best_list])


"""
===============================================================================
  No need to change any code below this line.
===============================================================================
"""

def read_input(filename):
  """
  P: float
  M: float
  N: integer
  C: integer
  items: list of tuples
  constraints: list of sets
  """
  with open(filename) as f:
    P = float(f.readline())
    M = float(f.readline())
    N = int(f.readline())
    C = int(f.readline())
    items = []
    constraints = []
    for i in range(N):
      name, cls, weight, cost, val = f.readline().split(";")
      items.append((name, int(cls), float(weight), float(cost), float(val)))
    for i in range(C):
      constraint = set(eval(f.readline()))
      constraints.append(constraint)
  return P, M, N, C, items, constraints

def write_output(filename, items_chosen):
  with open(filename, "w") as f:
    for i in items_chosen:
      f.write("{0}\n".format(i))

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="PickItems solver.")
  parser.add_argument("input_file", type=str, help="____.in")
  parser.add_argument("output_file", type=str, help="____.out")
  args = parser.parse_args()

  P, M, N, C, items, constraints = read_input(args.input_file)
  items_chosen = solve(P, M, N, C, items, constraints)
  write_output(args.output_file, items_chosen)
