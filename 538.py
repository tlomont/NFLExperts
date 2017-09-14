from bs4 import BeautifulSoup
import requests
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import os

# this gets the picks and then sends an email containing the week's games
def main():
    games = getData()
    picks = []
    for i in range(0,len(games)):
        first_prob = float(games[i].find(attrs={'class':"td number chance"}).text[:-1])
        teams = map(lambda x: x.text.strip(), games[i].findAll(attrs={'class':"team"})[1:])
        if (random.random()*100 < first_prob):
            pick = teams[0]
        else:
            pick = teams[1]
        matchup = "%s vs. %s" % (teams[0], teams[1])
        picks.append([matchup, pick]) 
    sendEmail(picks)   

# get the probabilities and matchups from 538
def getData():
    data = []
    URL = 'http://projects.fivethirtyeight.com/2017-nfl-predictions/games'
    soup = BeautifulSoup(requests.get(URL).text) 
    games = soup.find(attrs={'class':'week'}).findAll(attrs={'class':'game'})
    return (games)

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
