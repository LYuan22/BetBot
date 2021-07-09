# BetBot

This is a Discord Bot that allows users to place bets on NBA Games, and uses a database to keep track of games, bets, and users. Users are able to bet fake money using the $bet command or gamble their money using $coinflip. 

**SETUP**
Create a txt file and name it .env and place it in the same file as the rest of the files.
DISCORD_TOKEN - Create a Bot through discord developer portal and add it to your channel. After this copy the token from the Bot website and set it to Discord_Token = 'token' 
api_key - go on The Odds API and get your free key and set api_key = the key u get
channel - copy channel id from discord after turn developer settings on and set channel = the number u get

![env file example](https://user-images.githubusercontent.com/10456113/125017369-ff425c80-e040-11eb-8512-1637cacbbab8.png)



**Commands**

$stats

![image](https://user-images.githubusercontent.com/10456113/124977064-08f6a080-dffe-11eb-9670-032132a080cb.png)

$odds

![image](https://user-images.githubusercontent.com/10456113/124977076-0dbb5480-dffe-11eb-8769-17745f4685f6.png)

$bet amount gameid team

![image](https://user-images.githubusercontent.com/10456113/124977083-11e77200-dffe-11eb-91f9-13de30521dc3.png)

$coinflip amount heads/tails

![image](https://user-images.githubusercontent.com/10456113/124977129-20ce2480-dffe-11eb-959e-89084cfcf70c.png)

$revive

![image](https://user-images.githubusercontent.com/10456113/124977104-16ac2600-dffe-11eb-81f7-3f711bec1ecf.png)

**ADMIN ONLY**
$editmoney amount userid

![image](https://user-images.githubusercontent.com/10456113/124977755-dac59080-dffe-11eb-820a-f2a017ea1369.png)

