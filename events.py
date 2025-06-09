'''
Definition of the type of events used in the discrete event simulation (DES). 
Each constant represents an specific type of event that can happen in the system at any moment: 
arrivals and processing completions in the different computers. 
'''

# Arrival event to Computer 2 (C2).
EVENT_ARRIVAL_C2 = 'Arrival_C2'

# Arrival event to Computer 3 (C3).
EVENT_ARRIVAL_C3 = 'Arrival_C3'

# Processing completion in Computer 2 (C2).
EVENT_FINISH_C2 = 'Finish_C2'

# Processing completion in Computer 3 (C3).
EVENT_FINISH_C3 = 'Finish_C3'

# Processing completion in Computer 1 (C1). 
# C1 does not need an arrival event because it does not receive messages directly from 
# outside like C2 and C3 do. It instead receives them internally from C2 and C3 completions. 
# This means its arrivals depend on the other parts of the system.
EVENT_FINISH_C1 = 'Finish_C1'
