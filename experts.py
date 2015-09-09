from bs4 import BeautifulSoup
import requests
import random
from bisect import bisect

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
    weights = [-1]
    records = data[-1]
    for record in records[1:]:
        numIncorrect = int(record[2].split('-')[1])
        weight =  pow((31.0/32), numIncorrect)
        weights.append(weight)
    return weights

# randomly choose an expert using their weights as probablities, 
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



    