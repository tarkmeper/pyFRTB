#hackery to make import work.
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import FRTB

import sys
import json
import pickle

aggregator = FRTB.init(FRTB.D352_1)

filename = sys.argv[1]
with open(filename, "r") as fin:
    # read in each line in the file
    for line in fin:
        # parse the line and create a trade object
        trade = json.loads(line)

        # pass the trade to the aggregator
        aggregator.add(trade)


with open(filename + ".pickle", "wb") as fb:
    pickle.dump(aggregator, fb)
