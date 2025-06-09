'''
Module that includes all the functions needed by the simulation.
'''

# Import our functions for random variable generation.
from myrandom import uniform, expovariate, triangular, gauss, lcg, c3_processing_time, c3_arrival_time

import time
import heapq
from collections import deque, defaultdict
from statistics import mean, stdev
from math import sqrt
from models import Message, Event, Processor
from events import *

from collections import deque

class Simulation:
    '''
    Class that manages the execution of the discrete events simulation (DES)
    of the system formed by the three computers (C1, C2, C3).
    '''
    
    def __init__(self, max_time, run_number=1, slow=False):
        '''
        Initialize an instance of simulation.

        :param max_time: Max time in seconds to run the simulation.
        :param run_number: Run number (to print onscreen).
        :param slow: if True, adds pauses for step-by-step display. 
        '''

        self.clock = 0  # Global clock of the simulation.
        self.max_time = max_time  # Time limit.
        self.events = []  # Future events queue.

        self.proc_c1 = Processor("C1")  # C1 processor.
        self.proc_c2 = Processor("C2")  # C2 processor.
        self.proc_c3 = Processor("C3")  # C3 processor.
        self.arrivals_c2 = 0  # Counter for arrivals to C2.
        self.arrivals_c3 = 0  # Counter for arrivals to C3.
        self.rejected_by_c3 = 0  # Counter for messages rejected by C3.
        self.sent_by_c1 = 0  # Counter of shipments by C1.

        self.trio_time = 0.0  # Total time where C1, C2 and C3 were busy at the same time.
        self.last_update_time = 0.0  # Last time registered.
        self.last_trio_check = 0.0  # Last time trio status was checked.

        self.slow = slow  # Flag for slow mode.
        self.run_number = run_number  # Current run number.
        self.messages = []  # Global list for messages processed.
        self.c1_input = deque()  # Special queue for C1.


    def schedule(self, event):
        '''
        Add a new event to future events queue. Uses heapq to heap sorted by time.

        :param event: Event to be added.
        '''

        heapq.heappush(self.events, event)


    def is_trio_busy(self):
        '''
        Check if C1, C2 and C3 are busy at the same time.
        '''

        return self.proc_c1.busy and self.proc_c2.busy and self.proc_c3.busy


    def update_trio_time(self, new_time):
        '''
        If all three processors are busy, updates total time they were working together.

        :param new_time: Current time of event that will be processed when this happens.
        '''

        if self.is_trio_busy():
            self.trio_time += new_time - self.last_trio_check
        self.last_trio_check = new_time


    def run(self):
        '''
        Run the discrete event simulation until the events
        are emptied or the maximum time is reached.

        - Arrival events for C2 and C3 are initially scheduled at t=0.
        - At each iteration:
            - The next event in time is taken.
            - The system clock is updated.
            - The joint working time is updated if C1, C2 and C3 are busy.
            - The corresponding event is executed.
            - The current system status is printed.
            - If the mode is slow, a pause of 0.5 seconds is entered.
        - At the end, it prints a summary of processed messages and the final time.
        '''

        # Schedule initial arrivals to C2 and C3 in t=0.
        self.schedule(Event(0, EVENT_ARRIVAL_C2, 'C2'))
        self.schedule(Event(0, EVENT_ARRIVAL_C3, 'C3'))

        # Main loop: keep going until reaching max time.
        while self.events and self.clock <= self.max_time:
            event = heapq.heappop(self.events)  # Get next event.
            self.update_trio_time(event.time)  # Check if trio is active.
            self.clock = event.time  # Advance clock.
            self.handle(event)  # Run event.
            self.print_status(event)  # Print current status.

            # Wait some time if slow mode.
            if self.slow:
                time.sleep(0.5) 

        # End of simulation
        print("\n" + "="*50)
        print(f"✔️ Simulation complete at t = {self.clock:.2f} s")
        print(f"📦 Total messages processed: {len(self.messages)}")
        print("="*50)
    

    def print_status(self, event):
        '''
        Print the current status of the system during an specific time in the simulation.

        :param event: Current event.
        '''

        # Print run and clock.
        print("\n" + "-" * 50)
        print(f"Run #{self.run_number} | Clock: {self.clock:.2f} s")
        
        # Print event happening now.
        print(f"📍 Event: {event.event_type} from {event.source}")

        # Print queues sizes of the three processors.
        print(f"📦 Queue sizes -> C2: {len(self.proc_c2.queue)}, C3: {len(self.proc_c3.queue)}, C1: {len(self.c1_input)}")

        # Function that shows IDs of messages in each queue.
        def queue_ids(q): return [m.id for m in q]

        # Print contents of each queue as lists of IDs.
        print(f"🔎 Queue contents ->")
        print(f"   - C2: {queue_ids(self.proc_c2.queue)}")
        print(f"   - C3: {queue_ids(self.proc_c3.queue)}")
        print(f"   - C1: {queue_ids(self.c1_input)}")

        # Status of each processor.
        print(f"⚙️  Processor states -> C2: {'Busy' if self.proc_c2.busy else 'Idle'}, "
            f"C3: {'Busy' if self.proc_c3.busy else 'Idle'}, "
            f"C1: {'Busy' if self.proc_c1.busy else 'Idle'}")

        # Totals accumulated at the moment.
        print(f"📊 Totals so far:")
        print(f"   - Messages arrived to C2: {self.arrivals_c2}")
        print(f"   - Messages arrived to C3: {self.arrivals_c3}")
        print(f"   - Messages rejected by C3: {self.rejected_by_c3}")
        print(f"   - Messages sent by C1: {self.sent_by_c1}")
        print(f"   - Trio Active Time: {self.trio_time:.2f} s")
        print("\n" + "-" * 50)

        # Show the ID of the last message if there is one.
        if self.messages:
            print(f"🆔 Last message ID: {self.messages[-1].id}")


    def handle(self, e):
        '''
        Handle an specific event. 

        :param e: Event
        '''

        if e.event_type == EVENT_ARRIVAL_C2:
            self.arrival_c2()
        elif e.event_type == EVENT_ARRIVAL_C3:
            self.arrival_c3()
        elif e.event_type == EVENT_FINISH_C2:
            self.finish_c2()
        elif e.event_type == EVENT_FINISH_C3:
            self.finish_c3()
        elif e.event_type == EVENT_FINISH_C1:
            self.finish_c1(e.msg)


    def arrival_c2(self):
        '''
        Process an arrival of an external message to C2. 
        '''

        msg = Message("C2", self.clock)  # Create a new message with current time.
        msg.start_queue_time = self.clock  # Mark arrival time to queue.

        self.proc_c2.queue.append(msg)  # Enqueue message in C2. 
        self.arrivals_c2 += 1  # Increase counter of arrivals.
        self.messages.append(msg)  # Add to global list of messages.

        # If C2 is idle, start processing right away.
        if not self.proc_c2.busy:
            self.start_proc(self.proc_c2, EVENT_FINISH_C2, uniform(5, 10))
            
        # Program next arrival to C2 with exponential time.
        next_arrival = self.clock + expovariate(1 / 15)
        if next_arrival <= self.max_time:
            self.schedule(Event(next_arrival, EVENT_ARRIVAL_C2, 'C2'))


    def arrival_c3(self):
        '''
        Process an arrival of an external message to C3. 
        '''

        msg = Message("C3", self.clock)  # Create a new message with current time.
        msg.start_queue_time = self.clock  # Mark arrival time to queue.

        self.proc_c3.queue.append(msg)  # Enqueue message in C3. 
        self.arrivals_c3 += 1  # Increase counter of arrivals.
        self.messages.append(msg)  # Add to global list of messages.

        # If C3 is idle, start processing right away.
        if not self.proc_c3.busy:
            self.start_proc(self.proc_c3, EVENT_FINISH_C3, c3_processing_time())

        # Program next arrival to C3 with triangular time.
        next_arrival = self.clock + c3_arrival_time()
        if next_arrival <= self.max_time:
            self.schedule(Event(next_arrival, EVENT_ARRIVAL_C3, 'C3'))


    def start_proc(self, proc, evt_type, duration):
        '''
        Start the processing of a message on a given processor.

        :param proc: Object that represents a processor (C1, C2, C3).
        :param evt_type: Type of termination event to program (e.g., EVENT_FINISH_C2).
        :param duration: Time the processing will take.
        '''

        # If it is C1, get messages from the special queue c1_input.
        if proc.name == "C1":
            if not self.c1_input:
                return  # Return if there are no messages to process.
            msg = self.c1_input.popleft()
        else:
            # C2 and C3 use their own queues.
            if not proc.queue:
                return # Return if there are no messages to process.
            msg = proc.queue.popleft()

        # Mark the beginning of processing.
        msg.start_proc_time = self.clock

        # Set processor's current message to this one. 
        proc.current_msg = msg

        # Record the start time.
        proc.last_start = self.clock

        # Mark as busy.
        proc.busy = True

        # Schedule termination event.
        self.schedule(Event(self.clock + duration, evt_type, proc.name, msg))


    def finish_c2(self):
        '''
        Finish processing in C2 and send message to C1.
        '''

        # Update C2.
        self.proc_c2.total_work += self.clock - self.proc_c2.last_start
        self.proc_c2.busy = False
        msg = self.proc_c2.current_msg

        # Send message to C1's queue.
        self.c1_input.append(msg)

        # If C1 is idle, start processing right away.
        if not self.proc_c1.busy and self.c1_input:
            self.start_proc(self.proc_c1, EVENT_FINISH_C1, max(0, gauss(3, 1)))

        # If there are more in C2's queue, process next one.
        if self.proc_c2.queue:
            self.start_proc(self.proc_c2, EVENT_FINISH_C2, uniform(5, 10))


    def finish_c3(self):
        '''
        Finish processing in C3: rejects or sends message to C1.
        '''

        # Update C3.
        self.proc_c3.total_work += self.clock - self.proc_c3.last_start
        self.proc_c3.busy = False
        msg = self.proc_c3.current_msg


        if lcg.rand() < 0.75:
            # Reject message.
            msg.rejected = True
            msg.finish_time = self.clock 
            self.rejected_by_c3 += 1
        else:
            # Accepted, send to C1.
            self.c1_input.append(msg)
            if not self.proc_c1.busy and self.c1_input:
                self.start_proc(self.proc_c1, EVENT_FINISH_C1, max(0, gauss(3, 1)))

        # If there are more in C3's queue, process next one.
        if self.proc_c3.queue:
            self.start_proc(self.proc_c3, EVENT_FINISH_C3, c3_processing_time())


    def finish_c1(self, msg):
        '''
        Finish processing in C1: decides whether to send or return.
        '''

        # Update C1.
        self.proc_c1.total_work += self.clock - self.proc_c1.last_start
        self.proc_c1.busy = False
        msg.finish_time = self.clock
        self.sent_by_c1 += 1

        # Determine if message is leaving the system or being reprocessed. 
        left_system = True

        # Resend message to C2? (20%). 
        if msg.origin == 'C2' and lcg.rand() < 0.2:
            msg.start_queue_time = self.clock
            self.proc_c2.queue.append(msg)
            if not self.proc_c2.busy:
                self.start_proc(self.proc_c2, EVENT_FINISH_C2, uniform(5, 10))
            left_system = False
        # Resend message to C3? (50%).
        elif msg.origin == 'C3' and lcg.rand() < 0.5:
            msg.start_queue_time = self.clock
            self.proc_c3.queue.append(msg)
            if not self.proc_c3.busy:
                self.start_proc(self.proc_c3, EVENT_FINISH_C3, self.tri_density())
            left_system = False

        # Only count as sent if the message leaves the system.
        if left_system:
            self.sent_by_c1 += 1

        # If there are more in C1's queue, process next one.
        if self.c1_input:
            self.start_proc(self.proc_c1, EVENT_FINISH_C1, max(0, gauss(3, 1)))


    def collect_stats(self):
        '''
        Calculate performance statistics after finishing one run.
        '''
        
        # Group messages by type: successful by C2, successful by C3 and rejected.
        groups = defaultdict(list)
        for msg in self.messages:
            # Determine category of the message. 
            if msg.rejected:
                key = 'C3_rejected'
            elif msg.origin == 'C2':
                key = 'C2_success'
            elif msg.origin == 'C3':
                key = 'C3_success'
            else:
                key = 'Other'

            # Only consider messages that completed their "journey".
            if msg.finish_time:
                total = msg.finish_time - msg.arrival_time  # Total time in system.
                wait = msg.start_proc_time - msg.start_queue_time  # Time in queue.
                groups[key].append((total, wait))  # Save tuple (total, queue).

        # Function for averaging total times.
        def avg(lst): 
            return mean(lst) if lst else 0.0
        
        # Function for efficiency = queue time / total time.
        def eff(lst): 
            return mean(w / t for t, w in lst) if lst else 0.0
        
        # 95% confidence interval function for means.
        def ci(lst):
            if len(lst) < 2: return (0, 0)
            m, s = mean(lst), stdev(lst)
            h = 1.96 * s / sqrt(len(lst))  # 1.96 -> z for 95%.
            return (m - h, m + h)

        return {
            # Average times in system.
            'T_C2': avg([t for t, _ in groups['C2_success']]),
            'T_C3': avg([t for t, _ in groups['C3_success']]),
            'T_RJ': avg([t for t, _ in groups['C3_rejected']]),
            'T_ALL': avg([
                m.finish_time - m.arrival_time 
                for m in self.messages if m.finish_time
                ]),
            
            # Efficiency per category. 
            'E_C2': eff(groups['C2_success']),
            'E_C3': eff(groups['C3_success']),
            'E_RJ': eff(groups['C3_rejected']),
            'E_ALL': eff([
                (m.finish_time - m.arrival_time, 
                 m.start_proc_time - m.start_queue_time) 
                 for m in self.messages if m.finish_time
                ]),

            # Use of each processor.
            'U_C1': self.proc_c1.total_work / self.max_time,
            'U_C2': self.proc_c2.total_work / self.max_time,
            'U_C3': self.proc_c3.total_work / self.max_time,

            # Joint time where C1, C2 and C3 were active.
            'TRIO_TIME': self.trio_time,
            'TRIO_PERCENT': self.trio_time / self.max_time,

            # Confidence intervals for average times.
            #'CI_C2': ci([t for t, _ in groups['C2_success']]),
            #'CI_C3': ci([t for t, _ in groups['C3_success']]),
            #'CI_RJ': ci([t for t, _ in groups['C3_rejected']]),
            #'CI_ALL': ci([
            #    m.finish_time - m.arrival_time 
            #    for m in self.messages if m.finish_time
            #    ])
        }
