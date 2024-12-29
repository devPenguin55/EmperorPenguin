nullMovePruning = False # overall, incorrect. some error implementing it
moveOrdering = True # is beneficial, but takes too long to sort rather than the nodes it prunes
quiesce = True # True is fine here, might have some lower depths though, which cause it make bad decisions

openingThreshold = 0.2
middleGameThreshold = 0.66

minDepth = 2 # if minDepth is 1, that really minDepth + 1 so depth 2, minDepth 2 -> 3