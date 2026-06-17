import os
os.environ["VOTER_ID"]    = "Voter3"
os.environ["VOTE_CHOICE"] = "A"
os.environ["NODE_NAME"]   = "Voter3"
from voter import main
main()
