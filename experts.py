from bs4 import BeautifulSoup
import requests
import random
import bisect
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import os

# a relatively small penalty per incorrect guess, 
# since we expect there to be many by the end of the season. For example
# if an expert gets 50% correct in week one, then their weight will go 
# down by almost 60% that week
PENALTY = (8.0/9)

# this gets the picks and then sends an email containing the week's games
def main():
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
    sendEmail(picks)   

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

# sends the email with the weekly picks
def sendEmail(picks):
    # me == my email address
    # you == recipient's email address
    me = "nflexpertalgorithm@gmail.com"
    recipients = ["tommy.lomont@gmail.com"]

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Weekly NFL Expert Picks! - " + str(date.today())
    msg['From'] = "NFL Expert Picks"
    msg['To'] = ", ".join(recipients)

    # Create the body of the message (a plain-text and an HTML version).
    text = ''
    html = """\
    <html>
      <head></head>
      <body><h2> This week's NFL picks</h2>
    """
    for game in picks:
        text+= game[0] + ": " + game[1] + "\n"
        html += "<p><b>" + game[0] + ": </b>" + game[1] + "</p>"

    html+="""
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    server = smtplib.SMTP('smtp.gmail.com:587')
    username = 'nflexpertalgorithm@gmail.com'  
    password = os.environ.get('NFLPASS') # must set enviro variable
    server.ehlo()
    server.starttls()  
    server.login(username,password)  
    server.sendmail(me, recipients, msg.as_string())         
    server.quit()

if __name__ == "__main__":
    main()