from bs4 import BeautifulSoup
import requests
import random
import bisect
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import os

# this gets the picks and then sends an email containing the week's games
def main():
    (away_probs, away_teams, home_teams) = getData()
    picks = []
    for i in range(0,len(away_probs)):
        prob = float(away_probs[i].text[:-1])/100
        if (random.random() < prob):
            pick = away_teams[i].text
        else:
            pick = home_teams[i].text
        matchup = "%s vs. %s" % (away_teams[i].text, home_teams[i].text)
        picks.append([matchup, pick]) 
    sendEmail(picks)   

# get the probabilities and matchups from 538
def getData():
    data = []
    URL = 'http://projects.fivethirtyeight.com/2016-nfl-predictions/'
    soup = BeautifulSoup(requests.get(URL).text) 
    away_probs = soup.findAll(attrs={'class':'prob away'})
    away_teams = soup.find('tr',attrs={'class':'away'}).findAll(attrs={'class':'team'})
    home_teams = soup.find('tr',attrs={'class':'home'}).findAll(attrs={'class':'team'})
    return (away_probs, away_teams, home_teams)

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
