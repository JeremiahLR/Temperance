import random # To be able to obtain random numbers in the simulation.

# The following variables can be changed:
NUMBER_AGENTS = 3 # Number of agents to create.
SHOW_AGENT_INFO = 3 # Show the information of x number of agents. Usually 1 is already a lot of information.
AGENT_VISION = 2 # The range of vision of the agent; it can see x by x squares around itself.
AGENT_HEALTH = 10 # The starting health of agents.
AGENT_METABOLISM = .5 # Amount of health the agent loses every turn.
AGENT_SOCIALPRESSURE = .2 # Social pressure increases the more the agent interacts with other agents. "Interaction" 
                          # in this case simply means eating food in the presence of other agents (i.e. while being
                          # inside the range of vision of other agents.) 
NUMBER_FOOD = 5 # Number of food patches to create.
SIM_AREA = 5 # Area for the grid world. Creates an x by x grid square.
FOOD_REGROWTH = 3 # X number of turns before food regrows at a food patch.

# For reference, the five cognitive rules that agents in the simulation can learn:
rule1Text = "Consuming 1 food is good for me."
rule2Text = "Consuming 2 food is very good for me."
rule3Text = "Consuming 2 food is bad for the community."
rule4Text = "Consuming 3 food is bad for me."
rule5Text = "Consuming 3 food is bad for the community."
 
# The agent class:
class agent:
    # Initialization of the agent class:
    def __init__(self, id, x, y):
        self.id = id # An identification number for the agent.
        self.xPosition = x # The coordinate position of the agent on the map.
        self.yPosition = y
        self.health = AGENT_HEALTH # The starting health of the agent. Taken from the constant variables above.
        # The cognitive rules known by the agent along with their corresponding weights (refer to the text above).
        # At the start, the agent does not know any of these rules. It has to learn them from experience.
        self.rules = {"rule1": False, "rule1weight": 0,
                      "rule2": False, "rule2weight": 0,
                      "rule3": False, "rule3weight": 0,
                      "rule4": False, "rule4weight": 0,
                      "rule5": False, "rule5weight": 0}
        self.timesSick3 = 0 # Number of times the agent has become sick from eating 3 units of food.
        self.timesPunished3 = 0 # Number of times the agent was punished by others for eating 3 food.
        self.timesPunished2 = 0 # Number of times the agent was punished by others for eating 2 food.
        self.socialPressure = 0 # Number of times the agent has "interacted" with other agents. 
                               # Again, this simply means eating food in the presence of other agents.
        self.seeing = [] # All the food seen by the agent inside its range of vision. 
        self.seeingScores = [] # The decision-making scores for all the food seen.
        self.pursuing = []  # To indicate the food currently being pursued.
        self.consuming = [] # To indicate the food currently being consumed.
        self.punished = False # To indicate if the agent is currently punished by other agents.

# The food class:
class food:
    # Initialization of the food class:
    def __init__(self, id, x, y, amount):
        self.id = id # An identification number for the food.
        self.xPosition = x # The coordinate position of the food on the map.
        self.yPosition = y
        self.amount = amount # The amount of food, from 1 to 3 units.
        self.consumed = False # To indicate if the food has been consumed in the food patch. 
                              # If true, it disappears and will regrow later.
        self.regrowthTimer = FOOD_REGROWTH # A timer to determine when the food will regrow. Taken from the constant
                                           # variables above.


##################################################################################################################
##       Decision-Making Process - The crucial function for the agents which uses a simple PECS framework       ##
##################################################################################################################

def decision(agent, food):
    # The set of scores that will determine whether the agent will pursue or ignore the food under consideration.
    physicalScore = 0
    emotionalScore = 0
    cognitiveScore = 0
    socialScore = 0
    
    # Physical Component - This component's score is based on the agent's hunger.
    # The lesser the agent's health is, the stronger its craving for food.
    if (agent.health >= 10): # 10 health and above means that the agent is satisfied.
        physicalScore = 0
    elif (agent.health < 10 and agent.health > 6):
        physicalScore = 1
    elif (agent.health < 7 and agent.health > 3):
        physicalScore = 2
    elif (agent.health < 4):
        physicalScore = 3

    # Emotional Component - This component's score is based on an appraisal theory of emotions.
    # The greater the amount of food is, the more desirable it seems and the stronger the emotion of desire is.
    # However, previous negative experiences (in particular, with 3 units of food) will lessen this.
    if (food.amount == 1):
        emotionalScore = 1
    elif (food.amount == 2):
        emotionalScore = 2
    elif (food.amount == 3):
        emotionalScore = 3 - agent.timesSick3 # Though 3 units of food is initially the most desirable, the emotional
                                              # desire decreases according to the number of times it has made the 
                                              # agent sick.

    # Cognitive Component - This component's score is based on the rules that the agent has learned through experience.
    # Each rule has a corresponding weight which increases as the agent experiences things. Notice that the first two 
    # rules (! & 2) obtain a positive value and the last three rules (3, 4, & 5) obtain a negative value. You can 
    # refer to the five cognitive rules above.
    if (food.amount == 1 and agent.rules["rule1"]):
        cognitiveScore = agent.rules["rule1weight"]
    if (food.amount == 2 and agent.rules["rule2"]):
        cognitiveScore = agent.rules["rule2weight"]
    if (food.amount == 2 and agent.rules["rule3"]):
        cognitiveScore -= agent.rules["rule3weight"]
    if (food.amount == 3 and agent.rules["rule4"]):
        cognitiveScore -= agent.rules["rule4weight"]
    if (food.amount == 3 and agent.rules["rule5"]):
        cognitiveScore -= agent.rules ["rule5weight"]

    # Social Component - This component's score is based on the prospect of social approbation or punishment
    # multiplied (or amplified) by a "social pressure" value. 1 unit of food means social approbation while 2 and 3 
    # units of food could mean social punishment. This gets multiplied immediately after.
    if (food.amount == 1):
        socialScore = 1
    if (food.amount == 2):
        socialScore -= agent.timesPunished2
    if (food.amount == 3):
        socialScore -= agent.timesPunished3
        
    socialScore = socialScore * agent.socialPressure # The social score is multiplied here by social pressure.
                                                     # Again, social pressure depends on the number of times the agent
                                                     # has "interacted" with other agents in the past.
    socialScore = int(round(socialScore, 1)) # Rounded and turned to an integer.

    # Total Decision Score
    decisionScore = physicalScore + emotionalScore + cognitiveScore + socialScore

    # This function gives all the scores, to be displayed in the information panel.
    return physicalScore, emotionalScore, cognitiveScore, socialScore, decisionScore

#######################################################################################
##       This is the graphics function that draws everything using ASCII text.       ##
##       If you want better graphics you can replace this with something else.       ##  
#######################################################################################

def draw(agentList, foodList):
    # Draw the grid world with agents and food.
    print("\n")
    print("   ", end=" ")
    for x in range(SIM_AREA): # Draw the x coordinate numbers.
        print("(", x,")", sep="", end=" ")
    print(" x")
    for y in range(SIM_AREA):
        print("(", y,")", sep="", end=" ") # Draw the y coordinate numbers.
        for x in range(SIM_AREA): # Draw the square locations of the grid world.
            agentPresent = False # By default, there is no agent or food in the square location.
            foodPresent = False
            # If an agent is present in the coordinate, then display "A" + agent id number.
            # To simplify our lives, no two agents can occupy the same square location. 
            # This is guaranteed in the main program code below.
            for a in agentList:
                if (a.xPosition == x and a.yPosition == y):
                    print("A",a.id, "*", sep="", end=" ")
                    agentPresent = True
            # If no agent is present in the coordinate, but there is food, display the food as food amount + "F".
            # This means that if an agent and food are in the same location, the agent will cover up the food.
            if (agentPresent == False):
                for f in foodList:
                    if (f.xPosition == x and f.yPosition == y and f.consumed == False):
                        print(f.amount,"F*", sep="", end=" ")
                        foodPresent = True
            # If the square location is empty, diplay "***".
            if (agentPresent == False and foodPresent == False):            
                print("***", end=" ")
        print("\n")
    print("y\n")    

    # You can display the information for x number of agents, set through the constant variable SHOW_AGENT_INFO above.
    # This piece of code gets the list of agents whose information will be displayed in the information panel.
    newList = []
    if len(agentList) < SHOW_AGENT_INFO: # This is in case some agents have died. Then you might have a list that is
        showAgents = len(agentList)      # even shorter than SHOW_AGENT_INFO 
    else:
        showAgents = SHOW_AGENT_INFO
    for i in range(showAgents):
        newList.append(agentList[i])
        
    # The information panel for agents.
    print("INFORMATION PANEL:\n")
    for a in newList:
        # First line has the agent id number, its current health, indicates whether the agent is currently pursuing
        # or consuming food, whether the agent is made sick, and whether it is punished by others.
        print("Agent ",a.id," at (",a.xPosition,",",a.yPosition,").", sep="", end=" ")
        print("Health: ",a.health,".", sep="", end=" ")
        if a.pursuing:
            print("Pursuing food at (",a.pursuing.xPosition,",",a.pursuing.yPosition,") with amount ",a.pursuing.amount,".", sep="")
        elif a.consuming: 
            print("Consuming food at (",a.consuming.xPosition,",",a.consuming.yPosition,") with amount ",a.consuming.amount,".", sep="", end=" ")
            if (a.consuming.amount == 3): print("Got sick!", end=" ")
            if (a.punished == True): print("Punished by others!")
            else: print("")
        else: print("")
        # Second line has the cognitive rules that the agent knows along with their corresponding weights.
        print("Cognitive Knowledge: Rule1:", a.rules["rule1weight"], "|| Rule2:", a.rules["rule2weight"], "|| Rule3:", a.rules["rule3weight"], "|| Rule4:", a.rules["rule4weight"], "|| Rule5:", a.rules["rule5weight"])
        # Third line has the agent's social pressure value, the number of times the agent has been punished for 
        # eating 2 or 3 units of food, and the number of times the agent has become sick from 3 units of food.
        print("Social Pressure:",a.socialPressure,"|| Punished 2 Food:", a.timesPunished2, "|| Punished 3 Food:", a.timesPunished3, "|| Sick 3 Food:", a.timesSick3)
        # Finally, the list of food that the agent is currently seeing along with their scores from the agent's
        # decision-making process. Take note that the agent does not automatically go for the highest scoring food. 
        # Rather, it chooses a positive scoring food at random.
        if a.seeing:
            for i in range(len(a.seeing)):
                print("Seeing food at (",a.seeing[i].xPosition,",",a.seeing[i].yPosition,") with amount ",a.seeing[i].amount,". Decision P:",a.seeingScores[i][0], " E:",a.seeingScores[i][1], " C:",a.seeingScores[i][2], " S:",a.seeingScores[i][3], " Total Score:", a.seeingScores[i][4], ".",  sep="")   
        print("\n")

###########################################
##       The main program function       ##
###########################################

def main():
    # The agents and food are contained in their own lists.
    agentList = []
    foodList = []

    # Create agents and place them randomly in the grid world.
    for a in range(NUMBER_AGENTS):
        # Create a new agent with a random position.
        newAgent = agent(a, random.randint(0, SIM_AREA-1), random.randint(0,SIM_AREA-1))
        # Check if this agent is on the same position as another agent. If yes, then re-create agent with a new 
        # random position. If it is alone, then append the agent to the agent list.
        anotherAgentHere = True
        while anotherAgentHere:
            if any (a2.xPosition == newAgent.xPosition and a2.yPosition == newAgent.yPosition for a2 in agentList):
                anotherAgentHere = True
                newAgent = agent(a, random.randint(0, SIM_AREA-1), random.randint(0,SIM_AREA-1))
            else:
                anotherAgentHere = False
                agentList.append(newAgent)

    # Create food and place them randomly in the grid world.
    for f in range(NUMBER_FOOD):
        # Create new food with a random position.
        newFood = food(f, random.randint(0, SIM_AREA-1), random.randint(0,SIM_AREA-1), random.randint(1,3))
        # Check if food is on the same position with other food. If yes, then re-create food with a new random 
        # position. If it is alone, then append the food to the food list.
        anotherFoodHere = True
        while anotherFoodHere:
            if any (f2.xPosition == newFood.xPosition and f2.yPosition == newFood.yPosition for f2 in foodList):
                anotherFoodHere = True
                newFood = food(f, random.randint(0, SIM_AREA-1), random.randint(0,SIM_AREA-1), random.randint(1,3))
            else:
                anotherFoodHere = False
                foodList.append(newFood)

    # Draw the the grid world and the information panel (see the draw function above).
    draw(agentList,foodList)

    # Ask the user to press Enter to continue.
    key = input("Press Enter to continue one step, or \"q\" to quit.")
    # If user types "q", then quit the program.
    if (key == "q"): quit()
    
###################################################################################
##       The main program loop. This is where a lot of the action happens.       ##
###################################################################################

    while True:

        # Regrow food in empty food patches according to constant variable FOOD_REGROWTH (see above).
        for f in foodList:
            if f.consumed:
                f.regrowthTimer -= 1
                if (f.regrowthTimer <= 0):
                    f.regrowthTimer = FOOD_REGROWTH
                    f.consumed = False

        # Agents are going to do several things every step:
        # 1. MOVE - The agent will either move around randomly or move towards food.
        # 2. LOOK - The agent will look around within its range of vision (AGENT_VISION) and note all the food
        #           that is sees.   
        # 3. DECIDE - The agent will perform a decision-making process for every food that it sees.
        # 4. CONSUME - If the agent is on top of the food that it wants, then it consumes it.
        # 5. METABOLIZE - The agent loses health according to the constant variable AGENT_METABOLISM.
        for a in agentList:      

            # MOVE - If the agent is pursuing food, then it moves closer to that food. 
            # If not, then the agent moves around randomly.
            while True:
                if a.pursuing: # If pursuing food, make the agent's prospective coordinate position (tempx, tempy)
                               # closer to the pursued food. 
                    if (a.xPosition > a.pursuing.xPosition): tempx = a.xPosition - 1
                    elif (a.xPosition < a.pursuing.xPosition): tempx = a.xPosition + 1
                    else: tempx = a.xPosition
                    if (a.yPosition > a.pursuing.yPosition): tempy = a.yPosition - 1
                    elif (a.yPosition < a.pursuing.yPosition): tempy = a.yPosition + 1
                    else: tempy = a.yPosition             
                elif a.consuming: # If on top of pursued food, prospectively stay in current position 
                                  # to consume this food.
                    tempx = a.xPosition
                    tempy = a.yPosition  
                else: # If neither pursuing nor consuming, prospectively move to a random nearby position 
                      # or stay in place.
                    tempx = a.xPosition + random.randint(-1, 1)
                    tempy = a.yPosition + random.randint(-1, 1)   
                # This grid world has closed edges. Bring back the agent if, according to its 
                # prospective coordinates (tempx, tempy), it falls over the edge.
                if tempx == -1: tempx = 0
                if tempx == SIM_AREA: tempx = SIM_AREA - 1
                if tempy == -1: tempy = 0
                if tempy == SIM_AREA: tempy = SIM_AREA - 1
                # To keep things simple, a rule is that no two agents can occupy the same place.
                # In case another agent is blocking the agent's prospective path, the agent will stay in place.
                if any (a2.xPosition == tempx and a2.yPosition == tempy for a2 in agentList): 
                    break # If the loop breaks then the agent's position will not change.
                else:
                    # If everything is good, then the agent will move to the prospective coordinate position.
                    a.xPosition = tempx
                    a.yPosition = tempy
                    break
            
            # LOOK - The agent looks at all the food within its range of vision and places them in a list.
            seeingList = []
            for x in range(a.xPosition-AGENT_VISION, a.xPosition+AGENT_VISION+1):
                for y in range(a.yPosition-AGENT_VISION, a.yPosition+AGENT_VISION+1):
                    for f in foodList:
                        if (f.xPosition == x and f.yPosition == y and f.consumed == False):
                            seeingList.append(f) 

            # DECIDE - The agent uses a decision-making process on all the food it sees.                     
            # First, we shuffle the list of food seen so that the agent doesn't always start with
            # the food at the top left corner of the screen.
            random.shuffle(seeingList)
            a.seeing = seeingList
            # Then the decision-making scores for all the food in the list is put in another list.
            a.seeingScores = []
            for i in range(len(a.seeing)):
                a.seeingScores.append(decision(a, a.seeing[i]))               
            # If the agent is not currently pursuing food, then it pursues the first food in its list 
            # with a positive decision score.
            if not a.pursuing:
                a.consuming = [] # This removes the agent's last indiciated consumed food
                                 # because it will try to consume a new one.
                a.punished = False # This removes the agent's last punishment marker, if any.
                for i in range(len(a.seeing)):
                    if (a.seeingScores[i][4] > 0): # If the decision score is positive...
                        a.pursuing = a.seeing[i]   # Then the agent pursues the food.
                        break

            # CONSUME - If the agent is pursuing food and is on top of it, then the agent consumes the food.
            # The agent might be punished by others or get sick from the consumption. All information is updated.
            if (a.pursuing and a.xPosition == a.pursuing.xPosition and a.yPosition == a.pursuing.yPosition):
                for f in foodList:
                    if (f.xPosition == a.xPosition and f.yPosition == a.yPosition):
                        
                        # The agent consumes the food (the food disappears).
                        f.consumed = True
                        a.consuming = a.pursuing
                        
                        # The agent's health is updated. 
                        if (f.amount == 1 or f.amount == 2): a.health += f.amount # Agent gains health.
                        elif (f.amount == 3): a.health -= 1 # Agent gets sick and loses health.
                            
                        # If applicable, increases the number of times the agent has gotten sick from eating 3 food.
                        if (f.amount == 3): a.timesSick3 += 1
                            
                        # Depending on what food was consumed, upates the weight of a corresponding rule 
                        # (rules 1, 2 or 4). The weights of the two other rules will be updated in the next code.
                        if (f.amount == 1): 
                            a.rules["rule1"] = True
                            a.rules["rule1weight"] += 1
                        elif (f.amount == 2):
                            a.rules["rule2"] = True
                            a.rules["rule2weight"] += 1
                        elif (f.amount == 3):
                            a.rules["rule4"] = True
                            a.rules["rule4weight"] += 1
                            
                        # Checks if the agent was seen by other agents consuming the food.
                        # If so, then there was an "interaction" and the agent's social pressure increases.
                        # Also, if applicable, the weights of rules 3 and 5 get updated.
                        tempAgentList = agentList.copy()
                        tempAgentList.remove(a)
                        # Is there any agent within the agent's range of vision? 
                        if any (abs(ta.xPosition - a.xPosition) <= AGENT_VISION and abs(ta.yPosition - a.yPosition) <= AGENT_VISION for ta in tempAgentList):
                            a.socialPressure += AGENT_SOCIALPRESSURE
                            a.socialPressure = round(a.socialPressure, 1) # Round to 1 decimal point.
                                                                          # Just to avoid trailing zeroes.
                            # Rules 3 and 5 get updated here because they depend on punishment by others.
                            if (f.amount == 2): 
                                a.timesPunished2 += 1
                                a.punished = True
                                a.rules["rule3"] = True
                                a.rules["rule3weight"] += 1
                            if (f.amount == 3): 
                                a.timesPunished3 += 1
                                a.punished = True
                                a.rules["rule5"] = True
                                a.rules["rule5weight"] += 1
                                
                        # All other agents who were pursuing the same food should stop 
                        # because the food has been consumed.
                        for a2 in agentList:
                            if a2.pursuing:
                                if (a2.pursuing.xPosition == f.xPosition and a2.pursuing.yPosition == f.yPosition):
                                    a2.pursuing = []

            # METABOLIZE - The agent loses health according to AGENT_METABOLISM. 
            # If its health is 0 or less, it dies.
            a.health -= AGENT_METABOLISM
            a.health = round(a.health, 1) # Just to avoid trailing zeroes.
            if (a.health <= 0):
                agentList.remove(a)

        # Draw the new state of the gird world and information panel.
        draw(agentList,foodList)
          
        # Ask the user to press Enter to continue.
        key = input("Press Enter to continue one step, or \"q\" to quit.")
        # If user types "q", then quit the program.
        if (key == "q"):             
            break
        else:
            continue

    
main()
