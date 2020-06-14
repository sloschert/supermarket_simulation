import pandas as pd
import numpy as np
import cv2
import time

cust_height = 30
cust_width = 30
img = cv2.imread('market.png')
img.shape

transition_probs = pd.read_csv("probabilities.csv", index_col=0)
probabilities_entry = pd.read_csv("probabilities_entry.csv", index_col=0)
probabilities_entry
transition_probs

class Market:
    """
    The market class, which can update it's section's positions, when too many people are in one section.
    """
    def __init__(self):
        self.positions = {"entrance" : np.array([730, 770]), "fruit" : np.array([370, 790]),\
            "spices" : np.array([370, 580]), "dairy" : np.array([370, 350]), "drinks" :\
            np.array([370, 120]), "checkout1" : np.array([560, 110]), "checkout2" :\
             np.array([560, 240]), "checkout3" : np.array([560, 380]), "checkout4" : np.array([560, 520])}

        # self.occupancy = {'dairy': 0, 'drinks': 0, 'entrance': 0, 'checkout1': 0,\
        #  'checkout2': 0, 'checkout3': 0, 'checkout4': 0, "fruit": 0, "spices": 0}

        self.slots = {'dairy': set(), 'drinks': set(), 'entrance': set(), 'checkout1': set(),\
          'checkout2': set(), 'checkout3': set(), 'checkout4': set(), "fruit": set(), "spices": set()}



class Customer:
    """
    The customer class
    """
    def __init__(self, name, current_state, color):
        self.name = name
        self.current_state = "entrance"
        self.color = color

        self.market_pos = np.array([730, 770])#m.positions["entrance"] # the entrance
        self.differ = None
        self.velocity = 2 # how fast the customers are moving
        self.x_reached = None
        self.y_reached = None
        self.next_state = None
        self.reached_state = True
        self.deviation = np.array([0, 0])
        self.slot = ""

        self.waiting = False
        self.original_waiting_duration = 100 # iterations
        self.waiting_duration = self.original_waiting_duration

    def move(self):
        """
        Walk 1 step, based on probability matrix.
        Chage current state and current time accordingly.
        """
        if self.reached_state == True:  # ONLY ONCE
            if self.current_state == "entrance":
                while True:                         # find next (first) section, special trans matrix, directly after entrance
                    rand_nr = np.random.random()
                    rand_index = np.random.choice(probabilities_entry.index)
                    prob = probabilities_entry.loc[rand_index].values
                    if rand_nr > (1-prob):
                        self.next_state = rand_index
                        break
            else:
                while True:                # find next state
                    rand_nr = np.random.random()
                    rand_col = np.random.choice(transition_probs.columns)
                    prob = transition_probs.loc[self.current_state, rand_col]
                    if rand_nr > (1-prob):
                        self.next_state = rand_col
                        break

            if self.next_state == "checkout":
                # find nearest counter on the x-axis (nearest to zero, absolute number) and set this as next_state
                checkout_distance_x = abs((self.market_pos - m.positions["checkout1"])[1])
                nearest_checkout = "checkout1"
                for i in ["checkout1", "checkout2", "checkout3", "checkout4"]:
                    if abs((self.market_pos - m.positions[i])[1]) < checkout_distance_x:
                        checkout_distance_x = abs((self.market_pos - m.positions[i])[1])
                        nearest_checkout = i
                self.next_state = nearest_checkout
            self.differ = self.market_pos - m.positions[self.next_state]
            self.slot = ""

        self.waiting = False
        self.reached_state = False
        self.x_reached = False
        self.y_reached = False


        if self.differ[0] > 0:
            self.market_pos[0] = self.market_pos[0] - self.velocity     # update agent's market position
            self.differ = self.market_pos - m.positions[self.next_state] + self.deviation   # update difference to next state
        elif self.differ[0] < 0:
            self.market_pos[0] = self.market_pos[0] + self.velocity
            self.differ = self.market_pos - m.positions[self.next_state] + self.deviation
        elif self.differ[0] == 0:
            self.x_reached = True


        if self.differ[1] > 0:
            self.market_pos[1] = self.market_pos[1] - self.velocity
            self.differ = self.market_pos - m.positions[self.next_state] + self.deviation
        elif self.differ[1] < 0:
            self.market_pos[1] = self.market_pos[1] + self.velocity
            self.differ = self.market_pos - m.positions[self.next_state] + self.deviation
        elif self.differ[1] == 0:
            self.y_reached = True


        #devition
        if (abs(self.differ.sum()) < (2*self.velocity)) and self.slot == "":

            if len(m.slots[self.next_state]) == 0:
                m.slots[self.next_state].add("a")
                self.slot = "a"
                dev = 0
            else:
                if "a" not in m.slots[self.next_state]:
                    m.slots[self.next_state].add("a")
                    self.slot = "a"
                    dev = 1
                elif "b" not in m.slots[self.next_state]:
                    m.slots[self.next_state].add("b")
                    self.slot = "b"
                    dev = 2
                elif "c" not in m.slots[self.next_state]:
                    m.slots[self.next_state].add("c")
                    self.slot = "c"
                    dev = 3
                elif "d" not in m.slots[self.next_state]:
                    m.slots[self.next_state].add("d")
                    self.slot = "d"
                    dev = 4
                elif "e" not in m.slots[self.next_state]:
                    m.slots[self.next_state].add("e")
                    self.slot = "e"
                    dev = 5
                else:
                    m.slots[self.next_state].add("f")
                    self.slot = "f"
                    dev = 6

            self.deviation = np.array([ dev*30, 0])
            self.x_reached = False
            self.y_reached = False


        # !!! boarders !!! ###########
        if self.current_state == "entrance":
            if self.market_pos[1] < 640 and self.market_pos[0] > 500 :
                self.market_pos[1] = 640

        #
        # elif self.current_state == "fruit" and (self.next_state in ["checkout1", "checkout2", "checkout3", "checkout4"]):
        #     if self.market_pos[0] < 480 and self.market_pos[1] < 780:
        #         self.market_pos[1] = 780
        #
        #     if self.market_pos[0] > 480 and self.market_pos[1] > 560:
        #         self.market_pos[0] = 480




        #
        # elif self.current_state == "fruit": #and (self.next_state == "spices" or \
        # #self.next_state == "dairy" or self.next_state == "drinks"):
        #
        #     #first go down:
        #     if self.market_pos[0] < 480 and self.market_pos[1] > 780:
        #         self.market_pos[0] += 2*self.velocity
        #         self.market_pos[1] += self.velocity # equals out the contrary tendency to go in the other direction
        #     #than go left:
        #     if self.next_state == "spices":
        #         # spices regal x ca. 600
        #         if self.market_pos[0] < 480 and 600 < self.market_pos[1] < 780:
        #             self.market_pos[0] += 2*self.velocity
        #
        #     if self.next_state == "dairy":
        #         # dairy regal x: ca. 380
        #         if self.market_pos[0] < 480 and 380 < self.market_pos[1] < 780:
        #             self.market_pos[0] += 2*self.velocity
        #
        #     if self.next_state == "drinks":
        #         if self.market_pos[0] < 480 and 150 < self.market_pos[1] < 780:
        #             self.market_pos[0] += 2*self.velocity
        #
        #

        ## boarders ##########


        if self.x_reached and self.y_reached:
            self.reached_state = True
            self.waiting = True
            self.current_state = self.next_state
            #m.slots[self.current_state].append(self.slot)

    def wait(self):
        m.slots[self.current_state].add(self.slot)
        self.waiting_duration = self.waiting_duration - 1
        if self.waiting_duration == 0:
            self.waiting = False
            self.waiting_duration = self.original_waiting_duration
            m.slots[self.current_state].remove(self.slot)


# timestamp printed on screen
font                   = cv2.FONT_HERSHEY_SIMPLEX
clock_lowerLeftCornerOfText = (40,40)
counter4_lowerLeftCornerOfText = (575,575)
counter3_lowerLeftCornerOfText = (440,575)
counter2_lowerLeftCornerOfText = (310,575)
counter1_lowerLeftCornerOfText = (170,575)
fontScale              = 1
fontColor              = (255,255,255)
lineType               = 2

current_time = pd.to_datetime("2019-09-02 07:00:00")
active_customers = []
m = Market()
i = 0
while True:
    i += 1
    frame = img.copy()

    cv2.putText(frame, f"Current time: {current_time}",
        clock_lowerLeftCornerOfText,
        font,
        fontScale,
        fontColor,
        lineType)

    color = (i%3)           # 0 = yellow, 1= pink, 2=blau
    if (i%50) == 0:
        c = Customer(f"customer{i}", "entrance", color)
        active_customers.append(c)

    #print(f"----------\nCUSTOMERS PRESENT:\n--{current_time}--")
    for j, cust in enumerate(active_customers):
        if cust.waiting == True:
            cust.wait()
        else:
            cust.move()



        frame[cust.market_pos[0] : cust.market_pos[0] + cust_height, cust.market_pos[1] : cust.market_pos[1] + cust_width, cust.color] = 0.0

        if cust.reached_state == True and cust.current_state in ["checkout1", "checkout2", "checkout3", "checkout4"]:
            if cust.waiting == True:
                cust.wait()
            else:
                del active_customers[j]

    ch4 = len(m.slots["checkout4"])
    ch3 = len(m.slots["checkout3"])
    ch2 = len(m.slots["checkout2"])
    ch1 = len(m.slots["checkout1"])

    cv2.putText(frame, f"{ch4}",
        counter4_lowerLeftCornerOfText,
        font,
        fontScale,
        fontColor,
        lineType)
    cv2.putText(frame, f"{ch3}",
        counter3_lowerLeftCornerOfText,
        font,
        fontScale,
        fontColor,
        lineType)
    cv2.putText(frame, f"{ch2}",
        counter2_lowerLeftCornerOfText,
        font,
        fontScale,
        fontColor,
        lineType)
    cv2.putText(frame, f"{ch1}",
        counter1_lowerLeftCornerOfText,
        font,
        fontScale,
        fontColor,
        lineType)



    cv2.imshow('frame name', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    current_time = current_time + pd.Timedelta("1 seconds")
    #time.sleep(0.001)
