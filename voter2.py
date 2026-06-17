import os
os.environ["VOTER_ID"]    = "Voter2"
os.environ["VOTE_CHOICE"] = "B"
os.environ["NODE_NAME"]   = "Voter2"
from voter import main
main()
