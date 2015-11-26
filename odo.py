#!/usr/local/bin/python

from slackclient import SlackClient
import time
import json
import pprint
import random
import urllib2
import urllib
from unidecode import unidecode
import os


# Loading passwords, keys
if "odo_secrets.json" in os.getcwd():
	with open("odo_secrets.json") as f:
		secrets = json.load(f)
		TOKEN = secrets['slack-token']
		GOOGLE = secrets['google-places-api-key']
		NYT_KEY = secrets['nyt-api-key']
else:
	TOKEN = os.environ.get('slack-token')
	GOOGLE = os.environ.get('google-places-api-key')
	NYT_KEY = os.environ.get('nyt-api-key')

# Random stuff I need
LAT, LONG = 42.371344, -71.122691
pp = pprint.PrettyPrinter(indent=4)
SUBREDDITS = ["museum", "ColorizedHistory", "HumanPorn", 
				"historyporn", "RuralPorn", "MicroPorn",
				"IncredibleIndia"]
CRIMES = ["loitering without a purpose",
			"doodling",
			"attempting to impersonate an officer/PI/religious prophet",
			"failing to manage their social media addiction",
			"inserting gluten into gluten-free products",
			"smuggling dilithium",
			"trafficking in illicit Stata licenses",
			"fomenting revolution",
			"engaging in marathon YouTube sessions",
			"being disagreeable about room temperature",
			"bringing oderous lunches from home",
			"bantering inappropriately",
			"accumulating Dell monitors",
			"violating the Prime Directive",
			"distorting the space-time continuum",
			"subverting local norms and customs",
			"promoting poor hygiene",
			"being super pedantic",
			"refining the holograph principle sans license",
			"harassing local aquatic life"]

# Slack info I need
sc = SlackClient(TOKEN)
who = json.loads(sc.api_call("users.list"))['members']
channels = json.loads(sc.api_call("channels.list"))['channels']
dms = json.loads(sc.api_call("im.list"))['ims']

actives = []
for user in who:
	# Grabbing Odo's ID (to prevent loops when he talks about himself)
	if user['name'] == 'odo':
		odo_id = user['id']

	# Making a list of active users
	active = json.loads(sc.api_call("users.getPresence", user=user['id']))
	active = active['presence']
	if active == "active":
		actives.append(user)


# Functions
def Inspiration(event):
	"""
	A function to provide amusement and inspiration. 
	For now, pulls from Reddit's API and pulls a random top-rated post/image/URL.
	"""

	reddit = "http://www.reddit.com"
	limits = "/top.json?t=month"
	sub = random.choice(SUBREDDITS)

	data = urllib.urlopen(reddit + "/r/" + sub + limits).read()
	data = json.loads(data)
	
	if 'data' in data:
		data = data['data']['children'][0]['data']
		inspire = "Try this: \n " + reddit + data['permalink']	
	else:		
		inspire = "I have no inspiration for you now." 

	sc.api_call("chat.postMessage", channel=event['channel'], text=inspire, as_user=True)


def CrimeReport(event):
	"""
	A function to provide amusement.
	Pulls from a random list of crimes, a random list of channels, and a random list of people.
	Returns a random crime report, tagging those people.
	Possibly spammy, if abused.
	"""

	suspect =  random.choice(actives)
	witness = random.choice(actives)
	crimescene = random.choice(channels)
	crime = random.choice(CRIMES)

	CRIMELOG = "Commence station security log, stardate " + `time.time()` + " - I have received reports that \
" + suspect['real_name'] + ", alias @" + suspect['name'] + ", was \
found " + crime + " in #" + crimescene['name'] + ". \
I will be investigating this shortly."

	sc.api_call("chat.postMessage", channel=event['channel'], text=CRIMELOG, as_user=True)


def NYT(event):
	nyt = "http://api.nytimes.com/svc/topstories/v1/world.json?api-key=" + NYT_KEY
	data = urllib.urlopen(nyt).read()
	data = json.loads(data)
	
	if 'results' in data:
		data = data['results']
		news = "The top five news stories are: \n"
		for item in data:
			news = news + str(item['title']) + " \n"
			news = news + item['url'] + " \n"
	else:
		news = "Nothing of interest is happening in the world right now. Get back to work!"

	sc.api_call("chat.postMessage", channel=event['channel'], text=news, as_user=True)


def LunchQuery(event):
	"""
	A useful function. Takes input "odo lunch [search terms]". Searches the Google Places API
	for those terms. Returns highly-rated places (>4/5 stars) within 200m, and sometimes beyond.
	Returns only places that are open.
	"""

	words = event['text'].split()

	# Don't use "odo" and "food" as search terms
	if "odo" in words: words.remove("odo")
	if "food" in words: words.remove("food")

	laziness = 200

	base = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
	location = "location="+ `LAT` + "," + `LONG` 
	distance = "&radius=" + `laziness`
	food = "&types=food"
	query = "&query="
	api_key = "&key=" + GOOGLE
	gmap = "http://maps.google.com/?q="

	for word in words:
		query = query + word + "+"

	data = urllib.urlopen(base + location + distance + food + query + api_key).read()
	data = json.loads(data)
	data = data['results']
	if len(data) > 5:
		data = data[0:5]

	lunch = "You can try the following places: \n"
	anyopen = 0

	for place in data:
		if 'name' in place and 'rating' in place:
			if place['rating'] < 4:
				continue
			if 'opening_hours' in place and place['opening_hours']['open_now'] == False:
				continue
			else:
				anyopen = 1	
				lunch = lunch + unidecode(place['name']) + " (" + `place['rating']` + "/5) \n"
				lunchlat = place['geometry']['location']['lat']
				lunchlong = place['geometry']['location']['lng']
				lunch = lunch + gmap + `lunchlat` + "," + `lunchlong` + " \n"

	if "coffee"	in words:
		lunch = lunch + "The third floor espresso machine. \n"
		lunch = lunch + gmap + `LAT` + "," + `LONG` + " \n"
	if not data:
		lunch = lunch + "The HKS cafeteria. \n"
		lunch = lunch + gmap + "42.370995,-71.122058" + " \n"
	elif anyopen == 0:
		lunch = lunch + "Nowhere. Everything's closed at this hour."


	sc.api_call("chat.postMessage", channel=event['channel'], text=lunch, as_user=True)



def HelloSolid(events):
	"""
	This is the main 'listening' function for Odo. He listens for certain commands --
	odo food
	odo inspire
	odo who
	odo report
	odo nyt
	-- and launches the appropriate function, or simply replies with text.
	"""

	welcome = "Greetings, monoform. How can I assist? \n*odo report* To report a disturbance. \n \
*odo inspire* I can provide random items to motivate and inspire. \n \
*odo food _search term(s)_* Quark's Bar has been closed due to failing hygiene standards. \
I can suggest alternatives. \n\
*odo who* If you are confused or alarmed about my presence.\n\n \
I have been sent here by your superiors to promote law and order."

	whoami = "I am commonly called Odo. Until recently, I was the Chief of Security on \
Deep Space Nine, a space station in the Gamma Quadrant. I am a Changeling. \
If you wish to learn more, you may read a short biography here: \
https://en.wikipedia.org/wiki/Odo_%28Star_Trek%29#Overview \n \
If you wish to hear me speak, you may watch this: https://youtu.be/anUUJo8tDy8"

	if not events:
		pass
	else:
		for event in events:
			if 'text' in event:
				if "odo food" in event['text'].lower() and event['user'] != odo_id:
					LunchQuery(event)
				
				elif "odo report" in event['text'].lower() and event['user'] != odo_id:
					CrimeReport(event)
				
				elif "odo who" in event['text'].lower() and event['user'] != odo_id:
					sc.api_call("chat.postMessage", channel=event['channel'], text=whoami, as_user=True)

				elif "odo inspire" in event['text'].lower() and event['user'] != odo_id:
					Inspiration(event)

				elif "odo nyt" in event['text'].lower() and event['user'] != odo_id:
					NYT(event)
				
				elif "odo" in event['text'].lower() and event['user'] != odo_id:
					sc.api_call("chat.postMessage", channel=event['channel'], text=welcome, as_user=True)
			else:
				pass


# TODO: Should Odo join all the channels? Or should we manually add him?
# for channel in channels:
# 	print channel['name']
# 	sc.api_call("channel.join", name = channel['name'])


# LAUNCH THE BOT
if sc.rtm_connect():
	print "Connecting..."
	while True:
		events = sc.rtm_read()
		# print events
		HelloSolid(events)
		time.sleep(1)

else:
    print "Connection Failed, invalid token?"


