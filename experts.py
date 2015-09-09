from bs4 import BeautifulSoup
import requests
from random import random

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

def getExpertWeights(data):
    weights = [-1]
    records = data[-1]
    for record in records[1:]:
        numIncorrect = int(record[2].split('-')[1])
        weight =  pow((31.0/32), numIncorrect)
        weights.append(weight)
    return weights

def decidePick(team1, sumOfWeights1, team2, sumOfWeights2):
    probablityTeam1 = sumOfWeights1/(sumOfWeights1+sumOfWeights2)
    if (random() < probablityTeam1):
        return team1
    return team2