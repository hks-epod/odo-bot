odo-bot
=======

November 2015. A bot, written in Python, for our Slack channels, to amuse, inform and encourage us. Based on [Odo](https://en.wikipedia.org/wiki/Odo_%28Star_Trek%29), from Star Trek: Deep Space Nine. 

## Resources
* [Heroku: Getting started with deploying a Python app](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)
* [Slack: API methods](https://api.slack.com/methods)
* [NYT Top Stories API](http://developer.nytimes.com/docs/read/top_stories_api)
* [Harvard Art Museums API](http://www.harvardartmuseums.org/collections/api)
* [Reddit API](https://www.reddit.com/dev/api)
* [OpenWeatherMap API](http://openweathermap.org/api)


## TODO
1. Add more crimes to `crimes`. We can never have enough `crimes`.
2. `def`: Odo tells you to stop working at 6pm EST. DM, based on time zone?
3. ~~`odo news`: Odo tells you a daily (?) update, pulling from NYT/Harvard/etc?~~
  * `odo nyt` is a thing. What about !nyt?
4. `def`: `if` weather is sunny and temp > 30, then Odo reminds you to go see something at the Harvard art museums.
5. Odo counts votes for food?
6. Odo responds to convos more than once.
7. `odo welcome`: Odo welcomes new users to the Slack channel. 
8. `odo random`: Odo randomly goes to join the great Link with the other Founders. Kind of like the bits in Sims/Sim City/etc. when aliens arrived. Very rare, very random.
9. At least one reference to the bucket.
10. Docstrings on all the funcs. Make them more serious/real.
11. `odo dj`: Some integration with Spotify?
~~12. Where to get Odo quotes?~~
13. Fix Odo's boring/dark picture to something more lively.
14. ~~How to do .config file stuff in Heroku? [This stuff](https://devcenter.heroku.com/articles/getting-started-with-python#define-config-vars)...~~
  * ~~To run locally: `odo_secret.json`~~
  * ~~To run on Heroku: `os.env.get()`~~
15. ~~`odo report`: Only active users to get randomly chosen.~~
16. Odo responds to DMs/mentions. 
