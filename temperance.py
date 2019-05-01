import random

# The following variables can be changed:
NUMBER_AGENTS = 3 # Number of agents to create.
SHOW_AGENT_INFO = 1 # Show the information of how many agents.
AGENT_VISION = 2 # The range of vision of the agent; it can see x by x squares around itself.
AGENT_HEALTH = 10 # The starting health of agents
AGENT_METABOLISM = .5 # Amount of health the agent loses every turn.
AGENT_SOCIALIZATION = .2 # The increase of socialization after every "interaction."
NUMBER_FOOD = 5 # Number of food to create.
SIM_AREA = 5 # Area for randomly generating agents and food. Creates an x by x square.
FOOD_REGROWTH = 3 # X number of turns before food regrows at a particular spot.

# The rules or proposition that agents in the simulation can learn:
rule1Text = "Consuming 1 food is good for me."
rule2Text = "Consuming 2 food is very good for me."
rule3Text = "Consuming 2 food is bad for the community."
rule4Text = "Consuming 3 food is bad for me."
rule5Text = "Consuming 3 food is bad for the community."
 
class agent:
    def __init__(self, id, x, y):
        self.id = id # An identification number for the agent.
        self.xPosition = x # The position of the agent on the map.
        self.yPosition = y
        self.health = AGENT_HEALTH # The health of the agent. When it reaches 0 then the agent dies.
        self.rules = {"rule1": False, "rule1weight": 0, # The rules known by the agent with their corresponding weights.
                      "rule2": False, "rule2weight": 0,
                      "rule3": False, "rule3weight": 0,
                      "rule4": False, "rule4weight": 0,
                      "rule5": False, "rule5weight": 0}
        self.timesSick3 = 0 # Times the agent became sick for eating excessively, i.e. 3 sugar.
        self.timesPunished2 = 0 # Times the agent was punished by others for eating 2 sugar.
        self.timesPunished3 = 0 # Times the agent was punished by others for eating 3 sugar.
        self.socialization = 0 # Times the agent has "interacted" with other agents. 

        self.seeing = [] # The list of food seen by the agent. 
        self.seeingScores = [] # The scores to see the decision prcesses.
        self.pursuing = []  # The food currently pursued.
        self.consuming = [] # The food currently consuming.
        self.punished = False # If punished for consuming the food.

class food:
    def __init__(self, id, x, y, amount):
        self.id = id # An identification number for the food.
        self.xPosition = x # The position of the food on the map.
        self.yPosition = y
        self.amount = amount # The amount of food, from 1 to 3 units.
        self.consumed = False # Whether the food has been consumed. It will regrow later.
        self.regrowthTimer = FOOD_REGROWTH # A timer to determine when the food regrows after it is consumed.


#############################################################################################
## Decision Procedure - The crucial function for the agents that uses a simple PECS model  ##
#############################################################################################
def decision(agent, food):
    # The set of scores for deciding whether to pursue or avoid food.
    physicalScore = 0
    emotionalScore = 0
    cognitiveScore = 0
    socialScore = 0
    
    # Physical Component - This component's score is based on survival instinct.
    # The less the agent's health is, the stronger its craving for food.
    if (agent.health >= 10): # 10 health and above means that the agent is satisfied.
        physicalScore = 0
    elif (agent.health < 10 and agent.health > 6):
        physicalScore = 1
    elif (agent.health < 7 and agent.health > 3):
        physicalScore = 2
    elif (agent.health < 4):
        physicalScore = 3

    # Emotional Component - This component's score is based on an appraisal theory
    # of emotions. The more the food is, the better it seems and the stronger the
    # emotion of desire is. However, previous negative experiences may counteract this.
    if (food.amount == 1):
        emotionalScore = 1
    elif (food.amount == 2):
        emotionalScore = 2
    elif (food.amount == 3):
        emotionalScore = 3 - agent.timesSick3  
        # Though 3 units of food initially seems to be most attractive, the emotional 
        # desire decreases the more times it makes the agent sick.

    # Cognitive Component - This component's score is based on the rules that the agent
    # knows and how "experienced" it is.
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

    # Social Component
    if (food.amount == 1):
        socialScore = 1
    if (food.amount == 2):
        socialScore -= agent.timesPunished2
    if (food.amount == 3):
        socialScore -= agent.timesPunished3
    socialScore = socialScore * agent.socialization
    socialScore = round(socialScore, 1) # To avoid trailing zeroes.

    # Decision Score
    decisionScore = physicalScore + emotionalScore + cognitiveScore + socialScore
    decisionScore = round(decisionScore, 1)

    # Return the scores
    return physicalScore, emotionalScore, cognitiveScore, socialScore, decisionScore

################################################################
## This function draws everything using ASCII text.           ##
## It can be replaced with a different graphics function      ##  
################################################################
def draw(agentList, foodList):
    # Draw the world with agents and food
    print("  ", end=" ")
    for x in range(SIM_AREA):
        print(x,"]", sep="", end=" ")
    print(" ")
    for y in range(SIM_AREA):
        print(y,"]", sep="", end=" ")
        for x in range(SIM_AREA):
            agentPresent = False
            foodPresent = False
            # If an agent is present in the coordinate, then display A
            for a in agentList:
                if (a.xPosition == x and a.yPosition == y):
                    print("A",a.id, sep="", end=" ")
                    agentPresent = True
            # If no agent is present, but there is food, display the food amount.
            if (agentPresent == False):
                for f in foodList:
                    if (f.xPosition == x and f.yPosition == y and f.consumed == False):
                        print(f.amount,"F", sep="", end=" ")
                        foodPresent = True
            # Otherwise, it is an empty coordinate, represented by *
            if (agentPresent == False and foodPresent == False):            
                print("**", end=" ")
        print("\n")

    # Just a way to limit the number of agent information shown.
    newList = []
    for i in range(SHOW_AGENT_INFO):
        newList.append(agentList[i])
    # Print information of agents.
    for a in newList:
        # First line
        print("Agent ",a.id," at ",a.xPosition,",",a.yPosition,".", sep="", end=" ")
        print("Health: ",a.health,".", sep="", end=" ")
        if a.pursuing:
            print("Pursuing food at (",a.pursuing.xPosition,",",a.pursuing.yPosition,") with amount ",a.pursuing.amount,".", sep="")
        elif a.consuming: 
            print("Consuming food at (",a.consuming.xPosition,",",a.consuming.yPosition,") with amount ",a.consuming.amount,".", sep="", end=" ")
            if (a.consuming.amount == 3): print("Got sick!", end=" ")
            if (a.punished == True): print("Punished by others!")
            else: print("")
        else: print("")
        # Second line
        print("Knowledge: Rule1:", a.rules["rule1weight"], "|| Rule2:", a.rules["rule2weight"], "|| Rule3:", a.rules["rule3weight"], "|| Rule4:", a.rules["rule4weight"], "|| Rule5:", a.rules["rule5weight"])
        # Third line
        print("Socialization:",a.socialization,"|| Times punished for 2:", a.timesPunished2, "|| Times punished for 3:", a.timesPunished3, "|| Times sick 3:",a.timesSick3)
        # Fourth and following lines
        if a.seeing:
            for i in range(len(a.seeing)):
                print("Seeing food at (",a.seeing[i].xPosition,",",a.seeing[i].yPosition,") with amount ",a.seeing[i].amount,". Decision: P:",a.seeingScores[i][0], " E:",a.seeingScores[i][1], " C:",a.seeingScores[i][2], " S:",a.seeingScores[i][3], " Total Score:", a.seeingScores[i][4], ".",  sep="")   



#########################
## This main function  ##
#########################
def main():
    agentList = []
    foodList = []

    for a in range(NUMBER_AGENTS):
        #Create a new agent
        newAgent = agent(a, random.randint(0, SIM_AREA-1), random.randint(0,SIM_AREA-1))
        # Check if this agent is on the same space as another agent. If yes, then create again.
        # Otherwise, append the agent to the agent list.
        duplicate = True
        while duplicate:
            if any (a2.xPosition == newAgent.xPosition and a2.yPosition == newAgent.yPosition for a2 in agentList):
                duplicate = True
                newAgent = agent(a, random.randint(0, SIM_AREA-1), random.randint(0,SIM_AREA-1))
            else:
                duplicate = False
                agentList.append(newAgent)

    for f in range(NUMBER_FOOD):
        #Create a new food patch with food
        newFood = food(f, random.randint(0, SIM_AREA-1), random.randint(0,SIM_AREA-1), random.randint(1,3))
        # Check if this food is on the same space as another food. If yes, then create again.
        # Otherwise, append the food to the food list.
        duplicate = True
        while duplicate:
            if any (f2.xPosition == newFood.xPosition and f2.yPosition == newFood.yPosition for f2 in foodList):
                duplicate = True
                newFood = food(f, random.randint(0, SIM_AREA-1), random.randint(0,SIM_AREA-1), random.randint(1,3))
            else:
                duplicate = False
                foodList.append(newFood)

    # Draw the original state of the world.
    draw(agentList,foodList)

    key = input("Press Enter to move, or \"q\" to quit.")
    # If user types "q" or "Q" then quit.
    if (key == "q"): quit()
    
    # The main program loop
    while True:

        # Regrow any missing food according to regrowth rate
        for f in foodList:
            if f.consumed:
                f.regrowthTimer -= 1
                if (f.regrowthTimer == 0):
                    f.regrowthTimer = FOOD_REGROWTH
                    f.consumed = False

        # Do move, search, decision, consume, and metabolize procedures
        for a in agentList:      

            # Move function - if agent is pursuing a food patch, then move closer, otherwise move randomly
            while True:
                if a.pursuing: 
                    if (a.xPosition > a.pursuing.xPosition): tempx = a.xPosition - 1
                    elif (a.xPosition < a.pursuing.xPosition): tempx = a.xPosition + 1
                    else: tempx = a.xPosition
                    if (a.yPosition > a.pursuing.yPosition): tempy = a.yPosition - 1
                    elif (a.yPosition < a.pursuing.yPosition): tempy = a.yPosition + 1
                    else: tempy = a.yPosition             
                elif a.consuming:
                    tempx = a.xPosition
                    tempy = a.yPosition  
                else: 
                    tempx = a.xPosition + random.randint(-1, 1)
                    tempy = a.yPosition + random.randint(-1, 1)   
                # The world is a closed world. Bring back the agent if it falls over the edge.
                if tempx == -1: tempx = 0
                if tempx == SIM_AREA: tempx = SIM_AREA - 1
                if tempy == -1: tempy = 0
                if tempy == SIM_AREA: tempy = SIM_AREA - 1
                # To keep things simpler, no two agents can occupy the same space.
                if any (a2.xPosition == tempx and a2.yPosition == tempy for a2 in agentList):
                    # If pursuing and it is already on the pursued food patch, or if it is consuming food,
                    # or if it is blocked, then don't move.
                    if a.pursuing or a.consuming: 
                        break
                    else: continue
                else:
                    # If everything is ok, give agent new position.
                    a.xPosition = tempx
                    a.yPosition = tempy
                    break
            
            # Search - The agent looks around at its surroundings for food
            seeingList = []
            for x in range(a.xPosition-AGENT_VISION, a.xPosition+AGENT_VISION+1):
                for y in range(a.yPosition-AGENT_VISION, a.yPosition+AGENT_VISION+1):
                    for f in foodList:
                        if (f.xPosition == x and f.yPosition == y and f.consumed == False):
                            seeingList.append(f)
            random.shuffle(seeingList)
            a.seeing = seeingList

            # Decide on everything seen
            a.seeingScores = []
            for i in range(len(a.seeing)):
                a.seeingScores.append(decision(a, a.seeing[i]))

            # If not already pursuing, pursue the first positive
            if not a.pursuing:
                a.consuming = [] # Just removes the indicator for the last consumed food. See below.
                a.punished = False # Just removes the indicator for the last punishment, if any.
                for i in range(len(a.seeing)):
                    if (a.seeingScores[i][4] > 0):
                        a.pursuing = a.seeing[i]
                        break

            # If pursuing and on top of it already, then consume, update PECS
            if (a.pursuing and a.xPosition == a.pursuing.xPosition and a.yPosition == a.pursuing.yPosition):
                for f in foodList:
                    if (f.xPosition == a.xPosition and f.yPosition == a.yPosition):
                        # Consume proper
                        f.consumed = True
                        a.consuming = a.pursuing
                        # Physical component update
                        if (f.amount == 1 or f.amount == 2): a.health += f.amount
                        elif (f.amount == 3): a.health -= 1
                        # Emotional component update
                        if (f.amount == 3): a.timesSick3 += 1
                        # Cognitive component update
                        if (f.amount == 1): 
                            a.rules["rule1"] = True
                            a.rules["rule1weight"] += 1
                        elif (f.amount == 2):
                            a.rules["rule2"] = True
                            a.rules["rule2weight"] += 1
                        elif (f.amount == 3):
                            a.rules["rule4"] = True
                            a.rules["rule4weight"] += 1
                        # Social component update
                        tempAgentList = agentList.copy()
                        tempAgentList.remove(a)
                        if any (abs(ta.xPosition - a.xPosition) <= AGENT_VISION and abs(ta.yPosition - a.yPosition) <= AGENT_VISION for ta in tempAgentList):
                            a.socialization += AGENT_SOCIALIZATION
                            a.socialization = round(a.socialization, 1)
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
                        # All agents stop pursuing this consumed food.
                        for a2 in agentList:
                            if a2.pursuing:
                                if (a2.pursuing.xPosition == f.xPosition and a2.pursuing.yPosition == f.yPosition):
                                    a2.pursuing = []

            # Metabolize (and possibly die)
            a.health -= AGENT_METABOLISM
            a.health = round(a.health, 1)
            if (a.health <= 0):
                agentList.remove(a)

        # Draw the new state of the world.
        draw(agentList,foodList)

        key = input("Press Enter to move, or \"q\" to quit.")
        # If user types "q" or "Q" then quit.
        if (key == "q"):
            break
        else:
            continue
    

main()
