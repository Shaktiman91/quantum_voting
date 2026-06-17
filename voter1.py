import os
os.environ["VOTER_ID"]    = "Voter1"
os.environ["VOTE_CHOICE"] = "A"
os.environ["NODE_NAME"]   = "Voter1"
from voter import main
main()
