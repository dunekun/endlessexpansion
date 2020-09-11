import random
import asyncio
import time
import collections

import ewcfg
import ewutils
import ewitem
import ewcmd

from ew import EwUser
from ewmarket import EwMarket
from ewdistrict import EwDistrict

async def set_race(cmd):
	response = ""
	user_data = EwUser(member = cmd.message.author)
	time_now = int(time.time())

	forbidden_races = [
		'retard',
		'anime',
		'animegirl',
		'white',
		'black',
		'aryan',
		'epic', # this one is for you, meaty
	]

	if time_now > user_data.time_racialability:
		if len(cmd.tokens) > 1:
			desired_race = cmd.tokens[1]
			if desired_race in ewcfg.races.values() or desired_race in forbidden_races:
				if desired_race == ewcfg.races["humanoid"]:
					response = "ENDLESS WAR acknowledges you as a boring humanoid. Your lame and uninspired figure allows you to do nothing but **{}**.".format(ewcfg.cmd_exist)
				elif desired_race == ewcfg.races["amphibian"]:
					response = "ENDLESS WAR acknowledges you as some denomination of amphibian. You may now **{}** to let the world hear your fury.".format(ewcfg.cmd_ree)
				elif desired_race == ewcfg.races["food"]:
					response = "ENDLESS WAR acknowledges you as a member of the food race. If you must, you may now give in to your deepest desires, and **{}**.".format(ewcfg.cmd_autocannibalize)
				elif desired_race == ewcfg.races["skeleton"]:
					response = "ENDLESS WAR acknowledges you as a being of bone. You may now **{}** to intimidate your enemies or soothe yourself.".format(ewcfg.cmd_rattle)
				elif desired_race == ewcfg.races["robot"]:
					response = '\n```python\nplayer_data.race = "robot"	#todo: change to an ID\nplayer_data.unlock_command("{}")```'.format(ewcfg.cmd_beep)
				elif desired_race == ewcfg.races["furry"]:
					response = "ENDLESS WAR reluctantly acknowledges you as a furry. Yes, you can **{}** now, but please do it in private.".format(ewcfg.cmd_yiff)
				elif desired_race == ewcfg.races["scalie"]:
					response = "ENDLESS WAR acknowledges you as a scalie. You may now **{}** at your enemies as a threat.".format(ewcfg.cmd_hiss)
				elif desired_race == ewcfg.races["slime-derived"]:
					response = "ENDLESS WAR acknowledges you as some sort of slime-derived lifeform. **{}** to your heart's content, you goopy bastard.".format(ewcfg.cmd_jiggle)
				elif desired_race == ewcfg.races["monster"]:
					response = 'ENDLESS WAR acknowledges you as a monstrosity. Go on a **{}**, you absolute beast.'.format(ewcfg.cmd_rampage)
				elif desired_race == ewcfg.races["critter"]:
					response = "ENDLESS WAR acknowledges you as a little critter. You may **{}**s from others now. Adorable.".format(ewcfg.cmd_request_petting)
				elif desired_race == ewcfg.races["avian"]:
					response = "ENDLESS WAR acknowledges you as some kind of bird creature. You can now **{}** to fly away for a quick escape.".format(ewcfg.cmd_flutter)
				elif desired_race == ewcfg.races["other"]:
					response = 'ENDLESS WAR struggles to categorize you, and files you under "other". Your peculiar form can be used to **{}** those around you.'.format(ewcfg.cmd_confuse)
				elif desired_race in forbidden_races:
					response = 'In its infinite wisdom, ENDLESS WAR sees past your attempt at being funny and acknowledges you for what you _truly_ are: **a fucking retard**.'

				# only set the cooldown if the user is switching race, rather than setting it up for the first time
				if user_data.race: 
					user_data.time_racialability = time_now + ewcfg.cd_change_race
				user_data.race = desired_race
				user_data.persist()
			else:
				response = '"{}" is not an officially recognized race in NLACakaNM. Try one of the following instead: {}.'.format(desired_race, ", ".join(["**{}**".format(race) for race in ewcfg.races.values()]))
		else:
			response = "Please select a race from the following: {}.".format(", ".join(["**{}**".format(race) for race in ewcfg.races.values()]))
	else:
		response = "You have either changed your race recently, or just used your racial ability. Try again later, race traitor."
	
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def exist(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["humanoid"]:
		responses = [
			"You look at the sky and wonder how the weather will be tomorrow. Maybe you'll get to see the sun for once.",
			"You take a deep breath and reminisce about your childhood. Mom, I miss you...",
			"You suddenly remember something funny you did with your friends many years ago, and break into a bittersweet smile. Man, those were the times.",
			"You contemplate what to have for dinner tomorrow. If only you had someone to share it with.",
			"You almost trip, but quickly react to avoid falling. God, I hope no one saw that.",
			"You catch a whiff of body odour, and stealthily check if it's coming from you. Did you forget to put on deodorant this morning?",
			"You come up with a witty reply to an argument you had last week. If only you were always this clever.",
		]
		response = random.choice(responses)
	else:
		response = "You people are not allowed to do that."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def ree(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["amphibian"]:
		response = "*{}* lets out a sonorous warcry.\n".format(cmd.message.author.display_name)
		roll = random.randrange(50)
		if roll == 0:
			response += "https://youtu.be/cBkWhkAZ9ds"
		else:
			response += "**R{}**".format(random.randrange(200, 500) * "E")
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)
	else:
		response = "You people are not allowed to do that."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def autocannibalize(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["food"]:
		time_now = int(time.time())
		if time_now > user_data.time_racialability:
			response = "You give in to the the existential desire all foods have, and take a small bite out of yourself. It hurts like a bitch, but God **DAMN** you're tasty."
			user_data.time_racialability = time_now + ewcfg.cd_autocannibalize
			user_data.hunger = max(user_data.hunger - (user_data.get_hunger_max() * 0.01), 0)
			user_data.change_slimes(n = -user_data.slimes * 0.001)
			user_data.persist()
		else:
			response = "You're too full of yourself right now, try again later."
	else:
		response = "You people are not allowed to do that."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def rattle(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.race == ewcfg.races["skeleton"]:
		time_now = int(time.time())
		if (time_now > user_data.time_racialability) and random.randrange(10) == 0:
			bone_item = next(i for i in ewcfg.item_list if i.context == "player_bone")
			ewitem.item_create(
				item_type = ewcfg.it_item,
				id_user = user_data.poi,
				id_server = cmd.guild.id,
				item_props={
					'id_item': bone_item.id_item,
					'context': bone_item.context,
					'item_name': bone_item.str_name,
					'item_desc': bone_item.str_desc,
				}
			)
			user_data.time_racialability = time_now + ewcfg.cd_drop_bone
			user_data.persist()

		if cmd.mentions_count == 1:
			responses = [
				", sending a shiver down their spine.",
				", who clearly does not appreciate it.",
				". They almost faint in shock.",
				", scaring them so bad they pee themselves a little.",
				". **NYEEEH!**",
				", trying to appeal to the bones deep within them.",
				" a little bit too hard. Oof ouch owie.",
				" so viciously they actually get offended.",
				" in an attempt to socialize, but they don't think you should.",
			]
			response = "You rattle your bones at {}{}".format(cmd.mentions[0].display_name, random.choice(responses))
		else:
			response = "You rattle your bones."
	else:
		response = "You people are not allowed to do that."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def beep(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["robot"]:
		roll = random.randrange(100)
		responses = []
		if roll > 19:
			responses = [
				"**BEEP**",
				"**BOOP**",
				"**BRRRRRRT**",
				"**CLICK CLICK**",
				"**BZZZZT**",
				"**WHIRRRRRRR**",
			]
		elif roll > 0:
			responses = [
				"`ERROR: 'yiff' not in function library in ewrobot.py ln 366`",
				"`ERROR: 418 I'm a teapot`",
				"`ERROR: list index out of range`",
				"`ERROR: 'response' is undefined`",
				"https://youtu.be/7nQ2oiVqKHw",
				"https://youtu.be/Gb2jGy76v0Y"
			]
		else:
			resp = await ewcmd.start(cmd = cmd)
			response = "```CRITICAL ERROR: 'life_state' NOT FOUND\nINITIATING LIFECYCLE TERMINATION SEQUENCE IN "
			await ewutils.edit_message(cmd.client, resp, ewutils.formatMessage(cmd.message.author, response + "10 SECONDS...```"))
			for i in range(10, 0, -1):
				await asyncio.sleep(1)
				await ewutils.edit_message(cmd.client, resp, ewutils.formatMessage(cmd.message.author, response + "{} SECONDS...```".format(i)))
			await asyncio.sleep(1)
			await ewutils.edit_message(cmd.client, resp, ewutils.formatMessage(cmd.message.author, response + "0 SECONDS...```"))
			await asyncio.sleep(1)
			await ewutils.edit_message(cmd.client, resp, ewutils.formatMessage(cmd.message.author, response + "0 SECONDS...\nERROR: 'reboot' not in function library in ewrobot.py ln 459```"))
			return
		response = random.choice(responses)
	else:
		response = "You people are not allowed to do that."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def yiff(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["furry"]:
		if cmd.mentions_count == 1:
			target_data = EwUser(member = cmd.mentions[0])
			if target_data.race == ewcfg.races["furry"]:
				poi = ewcfg.id_to_poi.get(user_data.poi)
				if (target_data.poi == user_data.poi) and poi.is_apartment: # low effort
					responses = [
						"Wow.",
						"Mhmm.",
						"You yiff.",
						"Yikes.",
						"🤮",
						"Yup."
						"Congratulations."
					]
					response = random.choice(responses)
				else:
					response = "Out here, in the streets? Fuck no, what's wrong with you?"
			else:
				response = "Only furries can yiff, better find another partner."
			pass
		elif cmd.mentions_count == 0:
			response = "You can't yiff by yourself."
		elif cmd.mentions_count > 1:
			response = "The world is not prepared for a furry orgy."
	else:
		response = "You people are not allowed to do that."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def hiss(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["scalie"]:
		response = "*{}* lets out a piercing hiss.\n".format(cmd.message.author.display_name)
		sssss = random.randrange(200, 500) * "s" # sssssssss
		response += "**HIS{}**".format(''.join(random.choice((str.upper, str.lower))(s) for s in sssss))
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)
	else:
		response = "You people are not allowed to do that."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def jiggle(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["slime-derived"]:
		if cmd.mentions_count == 0:
			response = "You pleasantly jiggle by yourself."
		if cmd.mentions_count > 1:
			response = "You jiggle at the crowd."
		if cmd.mentions_count == 1:
			target_member = cmd.mentions[0]
			target_data = EwUser(member = target_member)
			if target_data.race == ewcfg.races["slime-derived"]:
				response = "You jiggle along with {}.".format(target_member.display_name)
			elif target_data.life_state == ewcfg.life_state_corpse and user_data.life_state != ewcfg.life_state_corpse:
				response = "You jiggle in fear of {}.".format(target_member.display_name)
			elif target_data.life_state == ewcfg.life_state_kingpin:
				if target_data.life_state == ewcfg.life_state_enlisted and target_data.faction != user_data.faction:
					response = "You spitefully jiggle at {}.".format(target_member.display_name)
				else:
					response = "You jiggle in awe of {}.".format(target_member.display_name)
			elif target_data.life_state == ewcfg.life_state_enlisted:
				if target_data.faction == user_data.faction:
					response = "You jiggle at {} as a gesture of friendship.".format(target_member.display_name)
				else:
					response = "You jiggle at {} menacingly.".format(target_member.display_name)
			else:
				response = "You jiggle at {}.".format(target_member.display_name)
	else:
		response = "You people are not allowed to do that."
		
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def request_petting(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["critter"]:
		if cmd.mentions_count == 0:
			response = "Request petting from who?"
		if cmd.mentions_count > 1:
			response = "You would die of overpetting."
		if cmd.mentions_count == 1:
			target_member = cmd.mentions[0]
			proposal_response = "You rub against {}'s leg and look at them expectantly. Will they **{}** and give you a rub, or do they **{}** your affection?".format(target_member.display_name, ewcfg.cmd_accept, ewcfg.cmd_refuse)
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, proposal_response))
    
			accepted = False
			try:
				msg = await cmd.client.wait_for('message', timeout = 30, check=lambda message: message.author == target_member and 
														message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])
				if msg != None:
					if msg.content.lower() == ewcfg.cmd_accept:
						accepted = True
					elif msg.content.lower() == ewcfg.cmd_refuse:
						accepted = False
			except:
				accepted = False

			if accepted:
				responses = [
					"{user} gets on their back, and {target} gives them a thorough belly rub!",
					"{target} cups {user}'s head between their hands, rubbing near their little ears with their thumbs.",
					"{target} picks {user} up and carries them over the place for a little while, so they can see things from above.",
					"{target} sits down next to {user}, who gets on their lap. They both lie there for a while, comforting one another.",
					"{target} gets on the floor and starts petting the heck out of {user}!",
				]
				accepted_response = random.choice(responses).format(user = cmd.message.author.display_name, target = target_member.display_name)
				await ewutils.send_message(cmd.client, cmd.message.channel, accepted_response)
			else:
				response = "The pain of rejection will only make you stronger, {}.".format(cmd.message.author.display_name)
	else:
		response = "You people are not allowed to do that."
	if response:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def rampage(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["monster"]:
		responses = [
			"You repeatedly stomp on the ground with all your savage fury, causing a minor tremor.",
			"You let out a **R" + (random.randrange(10, 100) * "O" ) + (random.randrange(10, 100) * "A") + "R**.",
			"You bare your teeth and ***SLAM*** the ground below you with your fists.",
			"You fling yourself all over the place while screaming, just to let off some of your primal anger.",
			"You get so fucking furious in such a short period of time you actually just pass out for a second.",
		]
		response = random.choice(responses)
	else:
		response = "You people are not allowed to do that."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def flutter(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.race == ewcfg.races["avian"]:
		district_data = EwDistrict(district = user_data.poi, id_server = cmd.guild.id)
		market_data = EwMarket(id_server=cmd.guild.id)
		response = "You flap your wings in an attempt to fly, but "
		excuses = []

		if market_data.weather == ewcfg.weather_lightning:
			excuses.append("the current weather would make that a bit dangerous, so you decide not to.")
		if ewcfg.mutation_id_bigbones in user_data.get_mutations():
			excuses.append("your bones are too big for you to get off the ground.")
		if ewcfg.mutation_id_lightasafeather in user_data.get_mutations():
			excuses.append("your wings are too skinny to generate enough lift.")

		if 6 <= market_data.clock >= 20:
			excuses.append("it's not safe to fly at night, so you decide not to.")
		else:
			excuses.append("flying in plain daylight might get you shot off the sky, so you decide not to.")

		if user_data.slimes > 1000000:
			excuses.append("you have too much slime on you, so you don't even get off the ground.")
		else:
			excuses.append("you're too weak for this right now, gonna need to get more slime.")

		if user_data.life_state == ewcfg.life_state_corpse:
			excuses.append("your incorporeal wings generate no lift.")
		elif user_data.life_state == ewcfg.life_state_juvenile:
			excuses.append("you lack the moral fiber to do so.")
		else:
			if user_data.faction == ewcfg.faction_boober:
				excuses.append("you end up thrashing with your wings in an unorganized fashion.")
			if user_data.faction == ewcfg.faction_milkers:
				excuses.append("you end up doing rapid dabs instead.")

		if len(district_data.get_players_in_district()) > 1:
			excuses.append("it's embarassing to do so with other people around.")
		else:
			excuses.append("you can't be bothered if there's no one here to see you do it.")

		if user_data.hunger / user_data.get_hunger_max() < 0.5:
			excuses.append("you're too hungry, and end up looking for worms instead.")
		else:
			excuses.append("you're too full from your last meal for such vigorous exercise.")

		response += random.choice(excuses)
	else:
		response = "You people are not allowed to do that."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def confuse(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.race == ewcfg.races["other"]:
		if cmd.mentions_count == 0:
			if random.randrange(20) == 0:
				response = "ENDLESS WAR takes a cursory glance at you. It still doesn't know what the fuck you are."
			else:
				response = "You confuse yourself. What?"
		if cmd.mentions_count > 1:
			response = "The crowd looks at you, winces slightly, and looks away."
		if cmd.mentions_count == 1:
			target_member = cmd.mentions[0]
			target_data = EwUser(member = target_member)
			if target_data.race == ewcfg.races["other"]:
				response = "You and {} actually understand each other in a way, despite your differences.".format(target_member.display_name)
			else:
				responses = [
					"{} doesn't know what on earth they're looking at.".format(target_member.display_name),
					"{} stares at you, expressionless, then turns away.".format(target_member.display_name),
					"{} gets a little dizzy from staring at you for too long.".format(target_member.display_name),
					"{} wonders how you're even alive. Are you?".format(target_member.display_name),
					"{} has seen some shit. Now they've seen some more.".format(target_member.display_name)
				]
				response = random.choice(responses)
	else:
		response = "You people are not allowed to do that."
		
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
