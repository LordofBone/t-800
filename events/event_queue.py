# !/user/bin/env python3

# This module is for inserting priority-based events into a queue that is called and can perform actions from these
# events; the HK project has been designed with threading in mind. Prior projects have been 1 action at a time,
# this project will be able to do multiple things at once, such as detect a face and perform actions as well as
# process movements - this is where the event queue comes in, instead of just doing direct calls to modules to
# perform actions anything that needs doing will be passed into this queue and processed one at a time (the highest
# priority first, lower the number the higher the priority). Multiple threaded modules running all at once will have
# access to this queue and so will be able to pass their results and requests into it

import threading
from queue import PriorityQueue
from time import sleep
import logging

logger = logging.getLogger("event-queue")


def queue_adder(event_type, event_content, priority):
    """
    This function is to add events to the event queue, but also the separate draw queue for drawing events
    :param event_type: the type of event to add to the queue
    :param event_content: the content of the event to add to the queue
    :param priority: the priority of the event to add to the queue
    :return:
    """
    EventQueueAccess.queue_addition(event_type, event_content, priority)
    DrawListQueueAccess.queue_addition(event_type, event_content, priority)


# todo: find out how task complete works within priority queue, if it is needed
# todo: determine whether this needs to be a dataclass
class EventQueue:
    def __init__(self):
        """
        Initialise the event queue
        """
        self.priority_queue = PriorityQueue(
            maxsize=0)  # we initialise the PQ class instead of using a function to operate upon a list.

    def queue_addition(self, event_type, event_content, priority=3):
        """
        Add an event to the queue
        :param event_type:
        :param event_content:
        :param priority:
        :return:
        """
        self.priority_queue.put((priority, event_type, event_content))

    def get_latest_event(self, event_match):
        """
        Get the latest event from the queue, will grab the highest priority first (lower the number,
        the higher the priority)
        :return:
        """
        try:
            if self.priority_queue.queue[0][1] in event_match:
                return self.priority_queue.get()
            else:
                return None
        except IndexError:
            return None

    def all_event_tester(self):
        """
        This is a test.txt function to test the event queue
        :return:
        """
        while True:
            event = self.priority_queue.get(timeout=5)
            if event:
                print(f"Detected {event[2]}")
                self.priority_queue.task_done()
            elif event is None:
                break

            sleep(1)

    def event_tester_1(self):
        """
        This is a test.txt function to test the event queue
        :return:
        """
        test_event_1 = "EVENT_TYPE_1"
        while True:
            event = self.get_latest_event([test_event_1])
            if event:
                if event[2] == "BASIC TEST 2":
                    print(f"Detected {event[2]} with event type {test_event_1}")
                    self.priority_queue.task_done()

            sleep(1)

    def event_tester_2(self):
        """
        This is a test.txt function to test the event queue
        :return:
        """
        test_event_2 = "EVENT_TYPE_2"
        while True:
            event = self.get_latest_event([test_event_2])
            if event:
                if event[2] == "BASIC TEST 5":
                    print(f"Detected {event[2]} with event type {test_event_2}")
                    self.priority_queue.task_done()

            sleep(1)


# get an instance of the EventQueue class that can be accessed from other modules, this ensures that every module
# accessing will use the same instance
EventQueueAccess = EventQueue()

DrawListQueueAccess = EventQueue()

CurrentProcessQueueAccess = EventQueue()

# when this module is called on its own run a quick test.txt, check 'Testing' folder for more tests around this
if __name__ == "__main__":
    # start the thread for this instance

    # testing the main event queue that will be used by other modules in the overall system
    EventQueueAccess.queue_addition("EVENT_TYPE_1", "BASIC TEST 2", 2)
    EventQueueAccess.queue_addition("EVENT_TYPE_1", "BASIC TEST 3", 3)
    EventQueueAccess.queue_addition("EVENT_TYPE_1", "BASIC TEST 4", 4)
    EventQueueAccess.queue_addition("EVENT_TYPE_1", "BASIC TEST 1", 1)
    EventQueueAccess.queue_addition("EVENT_TYPE_2", "BASIC TEST 5", 1)
    EventQueueAccess.queue_addition("EVENT_TYPE_2", "BASIC TEST 6", 4)
    EventQueueAccess.queue_addition("EVENT_TYPE_2", "BASIC TEST 7", 3)
    EventQueueAccess.queue_addition("EVENT_TYPE_2", "BASIC TEST 8", 1)

    threading.Thread(target=EventQueueAccess.event_tester_1, daemon=False).start()
    threading.Thread(target=EventQueueAccess.event_tester_2, daemon=False).start()

    # threading.Thread(target=EventQueueAccess.all_event_tester, daemon=False).start()

    # Freeze the queue to prevent the program from exiting out before all events are processed - this isn't required
    # when the main program is running
    EventQueueAccess.priority_queue.join()
