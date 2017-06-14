from collections import OrderedDict
import re

#adjectives
adjectives = ['interesting', 'cool', 'awesome', 'thought provoking', 'magnificent', 'swag', 'dapper', 'dank', 'beautiful', 'whimsical', 'funny', 'resilient',
'encouraging', 'thoughtful', 'juicy', 'fresh', 'courageous', 'witty', 'delicious', 'strange', 'spicy', 'smart', 'silly', 'worthy', 'majestic', 'tender',
'crispy', 'swagalicious', 'deep', 'savage', 'honest', 'true', 'exquisite', 'sick', 'wumbo', 'muy caliente', 'bootylicious', 'ticklish',
'sassy', 'bangin', 'lovely', 'cat like', 'passionate', 'wonderful', 'talented', 'inspirational', 'sophisticated', 'motivational', 'hysterical', 'crafty',
'intelligent', 'intellectual', 'inspiring', 'independent', 'unique', 'delicate', 'above average', 'naughty', 'realistic', 'sincere', 'fabulous',
'impressive', 'well-rounded', 'saucy', 'touching', 'resourceful', 'ferocious', 'much wow', 'effective', 'fierce']

#verbs/actions
verbs = ['cry', 'sweat', 'scream at puppies', 'explode', 'shit myself', 'become a girraffe', 'get cancer', 'pee blood', 'fake an orgasm', 'breathe fire', 'kill myself',
'sing', 'read a book', 'bang your mom', 'homeless', 'cook bagels', 'evaporate', 'burn calories', 'resolve my marriage', 'whack it in san diego', 'order pizza',
'acquire currency', 'disrepect women', 'coach soccer', 'liberate Asia', 'calculate the mean', 'assess my problems', 'see a doctor', 'block nickelodeon',
'detain a cripple', 'analyze data', 'come to a hypothesis', 'discover America', 'examine fruit', 'rate words with friends 5 stars', 'lose my virginity',
'demonstrate sex to children', 'gluten free', 'magical', 'consult a doctor', 'advocate poverty', 'forecast the weather', 'assemble a tractor',
'educate hispanics', 'scrutinize Michelle Obama', 'inspect my taint', 'call a lawyer', 'exceed expectations', 'succeed in life', 'revamp society', 'enhance my figure',
'perform surgery', 'organize a local bake sale', 'deductible', 'sustain years of torture', 'lift weights', 'experiment with liquid nitrogen', 'do drugs',
'crave a snack', 'shave my taint', 'dank']

#connection words (adverbs)
connect = ['very', 'so', 'really', 'extremely', 'fucking', 'super', 'amazingly', 'strangely', 'definitely']

#exclaimation wows
exclaim = ['Wow', 'Neat', 'Too cool', 'Hot damn', 'Sweet deal', "For realz", 'Cool beans', 'Jesus Christ', 'Unbelievable', 'Mother of god', 'True dat', 'No way', 'Gee wiz',
 'Great googly moogly', 'Holy shit', 'Well, fuck me in the ass', 'By God', 'Well, call me a tiger']

#general stop responses
stop = ['stop it', 'your goatee is fake', 'wow', "I can't even", 'stop', 'stop smoking that dank kush', 'more memes please', 'L2 fauxhawk', "let's cuddle", 'damn simmons, whered you find this?']

#music vids mostly
links = ['https://www.youtube.com/watch?v=otCpCn0l4Wo', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'https://www.youtube.com/watch?v=FTQbiNvZqaY', 'https://www.youtube.com/watch?v=djV11Xbc914',
 'https://www.youtube.com/watch?v=OPf0YbXqDm0', 'https://www.youtube.com/watch?v=s_x_4UElTDI', 'https://www.youtube.com/watch?v=Oq9iPLyftOk', 'https://www.youtube.com/watch?v=CGndZp98x-8',
 'https://www.youtube.com/watch?v=NkRyWpgmV3Y', 'https://www.youtube.com/watch?v=i8u6EodZseg', 'https://www.youtube.com/watch?v=1Qy9zWeopKk']

#keywords for general replys
rmatches = OrderedDict([
	(r"\b(base|tybg|lil b)",["Stay based. #TYBG", "Lil B loves you"]),
	(r"\b(bot|robot)",["I am a real person with feelings", "This is a false accusation", "Stop spreading lies please, I am living and breathing"]),
	(r"\b(sorry|apolog)",["It's ok, I forgive you", "apology accepted"]),
	(r"\b(love|hate) you",["Love you too!", "Let's get married"]),
	(r"\bstop",["I'll stop when I'm dead, which is never", "no"]),
	(r"\b(you (are|have|can|look)|you're)",["Thank you!", "Thanks!", "TYBG", u"This means so much \ud83d\ude0d", "I just cried a little"]),
	(r"\bwho",["Your Mom", "Your Dad", "Your Grandma", "Jesus Christ", "God", "Obama", "A Tiger from NASA", "Your worst nightmare", "Nicolas Cage", "I am Tupac's Ghost"]),
	(r"\bthank",["You're welcome!", u"No problem \ud83d\ude09", u"Anytime sexy \ud83d\ude1c"]),
	(r"\b(bye|goodbye)\b",["See ya later alligator!"]),
	(r"\b(hi|hello|hey|sup\b)",["Hello world", u"Hey there cutie \ud83d\ude1d"]),
	(r"\b(fuck|shit|fag|cock|ass|bitch|penis|dick|cunt)",["Stop using such profound language please", "Swearing is bad, mmmmkay"]),
	(r"\?",["Yes", "No", "Maybe", "Probably", "I don't know", "That depends... what color shoes are you wearing?", "According to my calculations the answer is I don't give a fuck.", "The answer is six."])
])
#keywords for stopitsimmons
matches = OrderedDict([
	(r"\b(@lisajoyceee|lisa)",["Lisa talked to a guy. I heard she wasn't allowed to do that. Letting you know", "How many times have you and lisa broken up and got back together again?"]),
	(r"\bwho.*up",["I am, but stop it"]),
	(r"\bcuddle",["Much cuddle, so blunt"]),
	(r"\bblunt",["They see you rollin', they hatin'", "You don't have to be so blunt about smoking"]),
	(r"\bsmoke",["Can has nude smoke cuddle sesh?"]),
	(r"\bweed",["My weed young like Caillou"]),
	(r"\bhannaford",["I wiped my taint on all the produce"]),
	(r"\bplan",["I'm planning to stop you"]),
	(r"\bwork",["I'd work on your attitude"]),
	(r"\bbitch",["Stop disregarding women!"])
])

# name: (key, secret)
tokens = {}

# populate tokens with keys from keys.txt following "name|key secret" structure
file = open("keys.txt")
for line in file.readlines():
	line = line.replace("\n", "")
	m = re.search(r"(\w+)\|(.+?) (\w+)", line)
	
	#insert value into tokens
	tokens[m.group(1)] = (m.group(2), m.group(3))
	
