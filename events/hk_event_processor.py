# !/user/bin/env python3
from hk_console_logger import ConsoleAccess


# todo: determine whether this needs to be a dataclass
class EventFactory:
    def __init__(self):
        #  These are event queue lists, once the event processor
        #  has taken in a new event it puts into a specific queue for the module it is calling; this allows for the
        #  queue to take in events, process them in order of priority then setup a further sub-queue for module
        #  actions - to prevent multiple calls on the same module ( for instance multiple calls to the movement
        #  sub-systems, which would overlap and cause problems)
        self.event_list_to_draw = []
        self.serial_list_to_draw = []
        self.serial_list_to_write = []
        # self.object_detect_events = []
        self.mission_objective_events = []
        self.action_events = []

    # These are designed as lists to feed the low-fps vision display of events without slowing up the processing of
    # the queues - this is handles as LIFO (Last In First Out, so the latest event is always being drawn)
    def get_event_list_to_draw(self):
        try:
            event_popped = self.event_list_to_draw.pop(0)
        except IndexError:
            event_popped = ""
        return event_popped

    # The serial output list is FIFO, so that on the Vision the serial outputs are viewed in order
    def get_serial_list_to_draw(self):
        try:
            serial_popped = self.serial_list_to_draw.pop(0)
        except IndexError:
            serial_popped = ""
        return serial_popped

    # The serial write list is FIFO, so that on the Vision the serial outputs are viewed in order
    def get_serial_list_to_write(self):
        try:
            serial_popped = self.serial_list_to_write.pop()
        except IndexError:
            serial_popped = ""
        return serial_popped

    # List for processing object detections.
    # todo: need to look into removing this as all object detection processing
    #  should be handled in hk_camera_obj_detect
    # def get_object_detect_list(self):
    #     try:
    #         object_detect_popped = self.object_detect_events.pop()
    #     except IndexError:
    #         object_detect_popped = ""
    #     return object_detect_popped

    # Mission objectives are currently processed as Last In First Out - so that the latest mission objective is
    # processed first.
    # todo: may change this to be FIFO so that mission objectives are handled by the module in order
    #  of importance
    def get_mission_objective_list(self):
        try:
            mission_objective_popped = self.mission_objective_events.pop()
        except IndexError:
            mission_objective_popped = ""
        return mission_objective_popped

    def get_action_list(self):
        try:
            action_popped = self.action_events.pop()
        except IndexError:
            action_popped = ""
        return action_popped

    # The event receiver processes all events from the queue and based on their event-type puts them into the correct
    # sub-queues for processing by individual modules
    def event_receiver(self, event_in):
        # Show a count of the amount of events to draw in the list if console print is enabled
        ConsoleAccess.console_printer('events to draw: {}'.format(len(self.event_list_to_draw)))

        # Set a default description in case no event gets caught
        event_desc = "NO_EVENT"

        # Event type and content are put into a single variable, this splits them out
        event_type, event_content = event_in[1], event_in[2]

        # todo: add in ability to detect and process text
        if event_type == "TEXT":
            ConsoleAccess.console_printer("text found: " + event_content)

        # Handling for serial writes, puts serial write instructions into a list so the serial interface module can
        # pick them up, also writes to the screen
        elif event_type == "SERIAL_WRITE":
            self.serial_list_to_write.insert(0, event_content)
            event_desc = "{} SENT TO SERIAL".format(event_content)

        # Handling for test event (shouldn't happen in actual use)
        elif event_type == "TEST_EVENT":
            event_desc = "{} WAS SUCCESSFULLY SENT TO EVENT QUEUE AND PROCESSED!".format(event_content)

        # Handling for mission events, puts mission instructions into a list so the objective processor in the
        # mission parameteriser module can pick them up, also writes to the screen the objective details
        elif "MSN" in event_type:
            detail = event_type.split(":")
            event_desc = '{}:{}|ACT={}'.format(detail[0].upper(), detail[1], event_in[2])
            self.event_list_to_draw.insert(0, event_desc)
            self.mission_objective_events.insert(0, event_in[2])

        # Handling for detection of a human - writes to the screen to draw the detection + confidence
        # todo: add in further actions on detection of humans
        elif "HUMAN" in event_type:
            detail = event_type.split(":")
            event_desc = 'DETECT:{}|CONF={}'.format(detail[1].upper().strip(), detail[2].strip())
            self.event_list_to_draw.insert(0, event_desc)

        # Handling for detection of an object - writes to the screen to draw the detection + confidence
        # todo: add in further actions on detection of objects
        elif "OBJECT" in event_type:
            detail = event_type.split(":")
            event_desc = 'DETECT:{}|CONF={}'.format(detail[1].upper().strip(), detail[2].strip())
            self.event_list_to_draw.insert(0, event_desc)

        elif "ACTION" in event_type:
            detail = event_type.split(":")
            event_desc = '{}:{}={}'.format(detail[0].upper().strip(), detail[1].upper().strip(), event_content)
            self.event_list_to_draw.insert(0, event_desc)
            self.action_events.insert(0, event_content)

        else:
            print("Unknown Event Type: " + event_type)

        ConsoleAccess.console_printer(event_desc)

    # Function that takes in serial outputs from the Arduino and logs them into the list for drawing on-screen
    def serial_receiver(self, serial_in):
        if not serial_in == "NO_SERIAL":
            ConsoleAccess.console_printer("{} Sent to Serial Receiver".format(serial_in))
            self.serial_list_to_draw.insert(0, serial_in)


# Instantiate the EventFactory as a class that can be accessed from other modules
EventFactoryAccess = EventFactory()

if __name__ == "__main__":
    pass
