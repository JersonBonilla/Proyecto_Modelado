'''
Module that includes classes that represent the different components in the system: 
Events, messages and processors.
'''

from collections import deque

class Message:
    '''Class that represents a message that circulates through the system.'''

    next_id = 0  # Unique incremental ID for each message.

    def __init__(self, origin, arrival_time):
        '''
        Initializes a new message.

        :param origin: Origin of the message ('C2' or 'C3').
        :param arrival_time: Time of arrival to the system.
        '''

        # Assign an ID to each message.
        self.id = Message.next_id
        Message.next_id += 1

        self.origin = origin  # Origin of the message ('C2' or 'C3').
        self.arrival_time = arrival_time  # Time of arrival to the system.
        self.start_queue_time = None  # Time it begins queueing.
        self.start_proc_time = None  # Time in which processing begins. 
        self.finish_time = None  # Time in which processing ends.
        self.rejected = False  # Indicate if it was rejected or not (by C3 only).


class Event:
    '''Class that represents an event in the simulation.'''

    def __init__(self, time, event_type, source, msg=None):
        """
        Initialize an event in the system.

        :param time: Time in which the event occurs.
        :param event_type: Type of event (see events.py).
        :param source: Source of the event (name of processor).
        :param msg: Message associated to event (if it applies).
        """
                
        self.time = time  # Time in which the event occurs.
        self.event_type = event_type  # Type of event.
        self.source = source  # Source of the event.
        self.msg = msg  # Message associated to event.

    def __lt__(self, other):
        '''This lets events be sorted in a priority queue (heapq).'''
        return self.time < other.time


class Processor:
    '''Class that represents a processor in the simulation.'''

    def __init__(self, name):
        '''
        Initializes a processor.

        :param name: Name of processor ('C1', 'C2' o 'C3').
        '''
        self.name = name  # Identifier of the processor.
        self.queue = deque()  # Queue of pending messages.
        self.current_msg = None  # Current message being processed.
        self.busy = False  # Status of processor (True if it is being used in that moment).
        self.total_work = 0.0  # Accumulated time it has been working. 
        self.last_start = 0.0  # Time when it last started working.
