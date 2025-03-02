# hackery to make import work.
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import FRTB

import sys
import pickle

aggregator = FRTB.init(FRTB.D352_1)

for filename in sys.argv[1:]:
    with open(filename, "rb") as fb:
        next_part = pickle.load(fb)
        aggregator.merge(next_part)

valuation = aggregator.calculate()
print(f"Result is: {valuation["total"]})")
