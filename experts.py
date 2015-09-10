from bs4 import BeautifulSoup
import requests
import random
import bisect

# a relatively small penalty per incorrect guess, 
# since we expect there to be many by the end of the season. For example
# if an expert gets 50% correct in week one, then their weight will go 
# down by almost 25% that week
PENALTY = (31.0/32)

# get the expert picks from ESPN and return the table of picks
def getData():
    data = []
    URL = 'http://espn.go.com/nfl/picks'
    soup = BeautifulSoup(requests.get(URL).text) 
    table = soup.find('table')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        data.append([col.contents for col in cols])
    return data

# return an array of weights assigned to each expert based on their
# previous records
def getExpertWeights(data):
    # experts start at index 1 to be consistent with table
    weights = [0]
    records = data[-1]
    for record in records[1:]:
        numIncorrect = int(record[2].split('-')[1]) # gets num incorrect
        weight =  pow(PENALTY, numIncorrect)
        weights.append(weight)
    return weights

# randomly choose an expert using their weights as probabilities, 
# returning the experts index
# use this expert to make the pick
def chooseExpert(weights):
    cumWeights = []
    total = 0
    for weight in weights:
        total += weight
        cumWeights.append(total)
    randomChoice = random.uniform(0, total)
    # choose the expert whose cumWeight is the greatest that is 
    # <= the random number
    expert = bisect.bisect_left(cumWeights, randomChoice)
    return expert

pickData = getData()
weights = getExpertWeights(pickData)
picks = []
# there are 3 rows above and two below the actual game picks
for game in pickData[3:-2]:
    expert = chooseExpert(weights)
    pick = game[expert]
    matchup = game[0][0].text
    # gets the team name from the html and adds it to the list of picks
    picks.append([matchup, pick[1].text if len(pick) > 1 else pick[0]])
print picks


    