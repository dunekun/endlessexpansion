import math
import random

import ewcfg
import ewitem
import ewutils
import asyncio

from ew import EwUser
from ewitem import EwItem

"""
	Cosmetic item model object
"""
class EwCosmeticItem:
	item_type = "cosmetic"

	# The proper name of the cosmetic item
	id_cosmetic = ""

	# The string name of the cosmetic item
	str_name = ""

	# The text displayed when you !inspect it
	str_desc = ""

	# The text displayed when you !adorn it
	str_onadorn = ""

	# The text displayed when you take it off
	str_unadorn = ""

	# The text displayed when it breaks! Oh no!
	str_onbreak = ""

	# How rare the item is, can be "Plebeian", "Patrician", or "Princeps"
	rarity = ""

	# The stats the item increases/decreases
	stats = {}

	# Some items have special abilities that act like less powerful Mutations
	ability = ""

	# While !adorn'd, this item takes damage-- If this reaches 0, it breaks
	durability = 0

	# How much space this item takes up on your person-- You can only wear so many items at a time, the amount is determined by your level
	size = 0

	# What fashion style the cosmetic belongs to: Goth, jock, prep, nerd
	style = ""

	# How fresh a cosmetic is, in other words how fleek, in other words how godDAMN it is, in other words how good it looks
	freshness = 0

	# The ingredients necessary to make this item via it's acquisition method
	ingredients = ""

	# Cost in SlimeCoin to buy this item.
	price = 0

	# Names of the vendors selling this item.
	vendors = []

	#Whether a cosmetic is a hat or not
	is_hat = False

	def __init__(
		self,
		id_cosmetic = "",
		str_name = "",
		str_desc = "",
		str_onadorn = "",
		str_unadorn = "",
		str_onbreak = "",
		rarity = "",
		stats = {},
		ability = "",
		durability = 0,
		size = 0,
		style = "",
		freshness = 0,
		ingredients = "",
		acquisition = "",
		price = 0,
		vendors = [],
		is_hat = False,

	):
		self.item_type = ewcfg.it_cosmetic

		self.id_cosmetic = id_cosmetic
		self.str_name = str_name
		self.str_desc = str_desc
		self.str_onadorn = str_onadorn
		self.str_unadorn = str_unadorn
		self.str_onbreak = str_onbreak
		self.rarity = rarity
		self.stats = stats
		self.ability = ability
		self.durability = durability
		self.size = size
		self.style = style
		self.freshness = freshness
		self.ingredients = ingredients
		self.acquisition = acquisition
		self.price = price
		self.vendors = vendors
		self.is_hat = is_hat

async def adorn(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Check to see if you even have the item you want to repair
	item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

	try:
		item_id_int = int(item_id)
	except:
		item_id_int = None

	if item_id is not None and len(item_id) > 0:
		response = "You don't have one."

		cosmetic_items = ewitem.inventory(
			id_user = cmd.message.author.id,
			id_server = cmd.guild.id,
			item_type_filter = ewcfg.it_cosmetic
		)

		item_sought = None
		item_from_slimeoid = None
		already_adorned = False
		space_adorned = 0

		for item in cosmetic_items:
			i = EwItem(item.get('id_item'))
			# Get space used adorned cosmetics
			if i.item_props['adorned'] == 'true':
				space_adorned += int(i.item_props['size'])

		# Check all cosmetics found
		for item in cosmetic_items:
			i = EwItem(item.get('id_item'))

			# Search for desired cosmetic
			if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):

				if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
					item_from_slimeoid = i
					continue
				if i.item_props.get("adorned") == 'true':
					already_adorned = True
				elif i.item_props.get("context") == 'costume':
					if not ewutils.check_fursuit_active(i.id_server):
						response = "You can't adorn your costume right now."
					else:
						item_sought = i
						break
				else:
					item_sought = i
					break

		if item_sought == None:
			item_sought = item_from_slimeoid

		# If the cosmetic you want to adorn is found
		if item_sought != None:

			# Calculate how much space you'll have after adorning...
			if int(item_sought.item_props['size']) > 0:
				space_adorned += int(item_sought.item_props['size'])

			# If you don't have enough space, abort
			if space_adorned > ewutils.max_adornspace_bylevel(user_data.slimelevel):
				response = "Oh yeah? And, pray tell, just how do you expect to do that? You’re out of space, you can’t adorn any more garments!"

			# If you have enough space, adorn
			else:
				item_sought.item_props['adorned'] = 'true'


				# Take the hat from your slimeoid if necessary
				if item_sought.item_props.get('slimeoid') == 'true':
					item_sought.item_props['slimeoid'] = 'false'
					response = "You take your {} from your slimeoid and successfully adorn it.".format(item_sought.item_props.get('cosmetic_name'))
				else:
					onadorn_response = item_sought.item_props['str_onadorn']
					response = onadorn_response.format(item_sought.item_props['cosmetic_name'])

				item_sought.persist()
				user_data.persist()

		elif already_adorned:
			response = "You already have that garment adorned!"

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Adorn which cosmetic? Check your **!inventory**.'))

async def dedorn(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Check to see if you even have the item you want to repair
	item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

	try:
		item_id_int = int(item_id)
	except:
		item_id_int = None

	if item_id is not None and len(item_id) > 0:
		response = "You don't have one."

		cosmetic_items = ewitem.inventory(
			id_user = cmd.message.author.id,
			id_server = cmd.guild.id,
			item_type_filter = ewcfg.it_cosmetic
		)

		item_sought = None
		already_adorned = False

		# Check all cosmetics found
		for item in cosmetic_items:
			i = EwItem(item.get('id_item'))

			# Search for desired cosmetic
			if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
				if i.item_props.get("adorned") == 'true':
					already_adorned = True
					item_sought = i
					break

		# If the cosmetic you want to adorn is found
		if item_sought != None:

			# Unadorn the cosmetic
			if already_adorned:
				item_sought.item_props['adorned'] = 'false'

				unadorn_response = str(item_sought.item_props['str_unadorn'])

				response = unadorn_response.format(item_sought.item_props['cosmetic_name'])


				item_sought.persist()
				user_data.persist()

			# That garment has not be adorned..
			else:
				response = "You haven't adorned that garment in the first place! How can you dedorn something you haven't adorned? You disgust me."

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Adorn which cosmetic? Check your **!inventory**.'))


async def dye(cmd):
	hat_id = ewutils.flattenTokenListToString(cmd.tokens[1:2])
	dye_id = ewutils.flattenTokenListToString(cmd.tokens[2:])

	try:
		hat_id_int = int(hat_id)
	except:
		hat_id_int = None
		
	try:
		dye_id_int = int(dye_id)
	except:
		dye_id_int = None

	if hat_id != None and len(hat_id) > 0 and dye_id != None and len(dye_id) > 0:
		response = "You don't have one."

		items = ewitem.inventory(
			id_user = cmd.message.author.id,
			id_server = cmd.guild.id,
		)

		cosmetic = None
		dye = None
		for item in items:
			
			if int(item.get('id_item')) == hat_id_int or hat_id in ewutils.flattenTokenListToString(item.get('name')):
				if item.get('item_type') == ewcfg.it_cosmetic and cosmetic is None:
					cosmetic = item

			if int(item.get('id_item')) == dye_id_int or dye_id in ewutils.flattenTokenListToString(item.get('name')):
				if item.get('item_type') == ewcfg.it_item and item.get('name') in ewcfg.dye_map and dye is None:
					dye = item	

			if cosmetic != None and dye != None:
				break

		if cosmetic != None:
			if dye != None:
				cosmetic_item = EwItem(id_item=cosmetic.get("id_item"))
				dye_item = EwItem(id_item=dye.get("id_item"))

				hue = ewcfg.hue_map.get(dye_item.item_props.get('id_item'))

				response = "You dye your {} in {} paint!".format(cosmetic_item.item_props.get('cosmetic_name'), hue.str_name)
				cosmetic_item.item_props['hue'] = hue.id_hue

				cosmetic_item.persist()
				ewitem.item_delete(id_item=dye.get('id_item'))
			else:
				response = 'Use which dye? Check your **!inventory**.'
		else:
			response = 'Dye which cosmetic? Check your **!inventory**.'
		
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'You need to specify which cosmetic you want to paint and which dye you want to use! Check your **!inventory**.'))

async def smoke(cmd):
	usermodel = EwUser(member=cmd.message.author)
	#item_sought = ewitem.find_item(item_search="cigarette", id_user=cmd.message.author.id, id_server=usermodel.id_server)
	item_sought = None
	space_adorned = 0
	item_stash = ewitem.inventory(id_user=cmd.message.author.id, id_server=usermodel.id_server)
	for item_piece in item_stash:
		item = EwItem(id_item=item_piece.get('id_item'))
		if item.item_props.get('adorned') == 'true':
			space_adorned += int(item.item_props.get('size'))

		if item_piece.get('item_type') == ewcfg.it_cosmetic and (item.item_props.get('id_cosmetic') == "cigarette" or item.item_props.get('id_cosmetic') == "cigar") and "lit" not in item.item_props.get('cosmetic_desc'):
			item_sought = item_piece


	if item_sought:
		item = EwItem(id_item=item_sought.get('id_item'))
		if item_sought.get('item_type') == ewcfg.it_cosmetic and item.item_props.get('id_cosmetic') == "cigarette":
			if int(item.item_props.get('size')) > 0:
				space_adorned += int(item.item_props.get('size'))

			if space_adorned < ewutils.max_adornspace_bylevel(usermodel.slimelevel):
				response = "You light a cig and bring it to your mouth. So relaxing. So *cool*. All those naysayers and PSAs in Health class can go fuck themselves."
				item.item_props['cosmetic_desc'] = "A single lit cigarette sticking out of your mouth. You huff these things down in seconds but you’re never seen without one. Everyone thinks you’re really, really cool."
				item.item_props['adorned'] = "true"
				item.persist()


				usermodel.persist()


				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				await asyncio.sleep(60)
				item = EwItem(id_item=item_sought.get('id_item'))

				response = "The cigarette fizzled out."

				item.item_props['cosmetic_desc'] = "It's a cigarette butt. What kind of hoarder holds on to these?"
				item.item_props['adorned'] = "false"
				item.item_props['id_cosmetic'] = "cigarettebutt"
				item.item_props['cosmetic_name'] = "cigarette butt"
				item.persist()


				usermodel.persist()

			else:
				response = "Sadly, you cannot smoke the cigarette. To smoke it, you'd have to have it inbetween your lips for approximately a minute, which technically counts as adorning something. " \
						   "And, seeing as you are out of adornable cosmetic space, you cannot do that. Sorry. Weird how this message doesn't show up when you suck all that dick though, huh?"

		elif item_sought.get('item_type') == ewcfg.it_cosmetic and item.item_props.get('id_cosmetic') == "cigar":
			if int(item.item_props['size']) > 0:
				space_adorned += int(item.item_props['size'])

			if space_adorned < ewutils.max_adornspace_bylevel(usermodel.slimelevel):
				response = "You light up your stogie and bring it to your mouth. So relaxing. So *cool*. All those naysayers and PSAs in Health class can go fuck themselves."
				item.item_props['cosmetic_desc'] = "A single lit cigar sticking out of your mouth. These thing take their time to kick in, but it's all worth it to look like a supreme gentleman."
				item.item_props['adorned'] = "true"

				item.persist()


				usermodel.persist()

				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				await asyncio.sleep(300)
				item = EwItem(id_item=item_sought.get('id_item'))

				response = "The cigar fizzled out."

				item.item_props['cosmetic_desc'] = "It's a cigar stump. It's seen better days."
				item.item_props['adorned'] = "false"
				item.item_props['id_cosmetic'] = "cigarstump"
				item.item_props['cosmetic_name'] = "cigar stump"
				item.persist()


				usermodel.persist()

			else:
				response = "Sadly, you cannot smoke the cigar. To smoke it, you'd have to have it inbetween your lips for approximately a minute, which technically counts as adorning something. " \
						   "And, seeing as you are out of adornable cosmetic space, you cannot do that. Sorry. Weird how this message doesn't show up when you suck all that dick though, huh?"
		else:
			response = "You can't smoke that."
	else:
		response = "There aren't any usable cigarettes or cigars in your inventory."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


def dedorn_all_costumes():
	costumes = ewutils.execute_sql_query("SELECT id_item FROM items_prop WHERE name = 'context' AND value = 'costume' AND id_item IN (SELECT id_item FROM items_prop WHERE (name = 'adorned' OR name = 'slimeoid') AND value = 'true')")
	costume_count = 0

	for costume_id in costumes:
		costume_item = EwItem(id_item=costume_id)

		usermodel = EwUser(id_user = costume_item.id_owner, id_server = costume_item.id_server)
		
		costume_item.item_props['adorned'] = 'false'

		if costume_item.item_props['slimeoid'] == 'false':

			usermodel.persist()

		costume_item.item_props['slimeoid'] = 'false'
		costume_item.persist()
		
		costume_count += 1
		
	ewutils.logMsg("Dedorned {} costumes after full moon ended.".format(costume_count))

async def sew(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Player must be at the Bodega
	if user_data.poi == ewcfg.poi_id_bodega:
		item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

		try:
			item_id_int = int(item_id)
		except:
			item_id_int = None

		# Check to see if you even have the item you want to repair
		if item_id != None and len(item_id) > 0:
			response = "You don't have one."

			cosmetic_items = ewitem.inventory(
				id_user = cmd.message.author.id,
				id_server = cmd.guild.id,
				item_type_filter = ewcfg.it_cosmetic
			)

			item_sought = None
			item_from_slimeoid = None

			for item in cosmetic_items:
				if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
					i = EwItem(item.get('id_item'))

					if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
						item_from_slimeoid = i
						continue
					else:
						item_sought = i
						break

			if item_sought == None:
				item_sought = item_from_slimeoid

			# If the cosmetic you want to have repaired is found
			if item_sought != None:
				# Can't repair items without durability limits, since they couldn't have been damaged in the first place
				if item_sought.item_props['durability'] is None:
					response = "I'm sorry, but I can't repair that piece of clothing!"

				else:
					if item_sought.item_props['id_cosmetic'] == 'soul':
						original_durability = ewcfg.soul_durability

					elif item_sought.item_props['id_cosmetic'] == 'scalp':
						if 'original_durability' not in item_sought.item_props.keys(): # If it's a scalp created before this update
							original_durability = ewcfg.generic_scalp_durability
						else:
							original_durability = int(float(item_sought.item_props['original_durability'])) # If it's a scalp created after

					else: # Find the mold of the item in ewcfg.cosmetic_items_list
						if item_sought.item_props.get('rarity') == ewcfg.rarity_princeps:
							original_durability = ewcfg.base_durability * 100
							original_item = None # Princeps do not have existing templates
						else:
							try:
								original_item = ewcfg.cosmetic_map.get(item_sought.item_props['id_cosmetic'])
								original_durability = original_item.durability
							except:
								original_durability = ewcfg.base_durability

					current_durability = int(float(item_sought.item_props['durability']))

					# If the cosmetic is actually damaged at all
					if current_durability < original_durability:
						difference = abs(current_durability - original_durability)

						# cost_ofrepair = difference * 4 # NO ONE SAID IT WOULD BE EASY
						cost_ofrepair = 10000 # I did...

						if cost_ofrepair > user_data.slimes:
							response = 'The hipster behind the counter narrows his gaze, his thick-rimmed glasses magnify his hatred of your ignoble ancestry.\n"Sir… it would cost {:,} to sew this garment back together. That’s more slime than you or your clan could ever accrue. Good day, sir. I SAID GOOD DAY. Come back when you’re a little, mmmmhh, *richer*."'.format(cost_ofrepair)
						else:
							response ='"Let’s see, all told… including tax… plus gratuity… and a hefty tip, of course… your total comes out to {}, sir."'.format(cost_ofrepair)
							response += "\n**!accept** or **!refuse** the deal."

							await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

							# Wait for an answer
							accepted = False

							try:
								message = await cmd.client.wait_for('message', timeout = 20, check=lambda message: message.author == cmd.message.author and 
																message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

								if message != None:
									if message.content.lower() == ewcfg.cmd_accept:
										accepted = True
									if message.content.lower() == ewcfg.cmd_refuse:
										accepted = False
							except:
								accepted = False

							# Cancel deal if the hat is no longer in user's inventory
							if item_sought.id_owner != str(user_data.id_user):
								accepted = False

							# Cancel deal if the user has left Krak Bay
							if user_data.poi != ewcfg.poi_id_bodega:
								accepted = False

							# Candel deal if the user doesn't have enough slime anymore
							if cost_ofrepair > user_data.slimes:
								accepted = False

							if accepted == True:
								user_data.change_slimes(n=-cost_ofrepair, source=ewcfg.source_spending)
								user_data.persist()

								item_sought.item_props['durability'] = original_durability
								item_sought.persist()

								response = '"Excellent. Just a moment… one more stitch and-- there, perfect! Your {}, sir. It’s good as new, no? Well, no refunds in any case."'.format(item_sought.item_props['cosmetic_name'])

							else:
								response = '"Oh, yes, of course. I understand, sir. No, really that’s okay. I get it. I totally get it. That’s your decision. Really, it’s okay. No problem here. Yep. Yup. Uh-huh, uh-huh. Yep. It’s fine, sir. That’s completely fine. For real. Seriously. I understand, sir. It’s okay. I totally get it. Yep. Uh-huh. Yes, sir. Really, it’s okay. Some people just don’t care how they look. I understand, sir."'
					else:
						response = 'The hipster behind the counter looks over your {} with the thoroughness that a true man would only spend making sure all the blood really was wrung from his most recent hunt’s neck or all the cum was ejactulated from his partner’s throbbing cock…\n"Sir," he begins to say, turning back to you before almost vomiting at the sight. After he regains his composure, he continues, "I understand you are an, shall we say, uneducated peasant, to put it delicately, but even still you should be able to tell that your {} is in mint condition. Please, do not bother me with such wastes of my boss’ time again. I do enough of that on my own."'.format(item_sought.item_props['cosmetic_name'], item_sought.item_props['cosmetic_name'])
		else:
			response = "Sew which cosmetic? Check your **!inventory**."
	else:
		response = "Heh, yeah right. What kind of self-respecting juvenile delinquent knows how to sew? Sewing totally fucking lame, everyone knows that! Even people who sew know that! You’re gonna have to find some nerd to do it for you."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def retrofit(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Player must be at the Bodega
	if user_data.poi == ewcfg.poi_id_bodega:
		item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

		try:
			item_id_int = int(item_id)
		except:
			item_id_int = None

		# Check to see if you even have the item you want to retrofit
		if item_id != None and len(item_id) > 0:
			response = "You don't have one."

			cosmetic_items = ewitem.inventory(
				id_user = cmd.message.author.id,
				id_server = cmd.guild.id,
				item_type_filter = ewcfg.it_cosmetic
			)

			item_sought = None
			item_from_slimeoid = None

			for item in cosmetic_items:
				if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
					i = EwItem(item.get('id_item'))

					if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
						item_from_slimeoid = i
						continue
					else:
						item_sought = i
						break

			if item_sought == None:
				item_sought = item_from_slimeoid

			# If the cosmetic you want to have repaired is found
			if item_sought != None:
				if item_sought.item_props.get('id_cosmetic') == 'soul' or item_sought.item_props.get('id_cosmetic') == 'scalp':
					response = 'The hipster behind the counter is taken aback by your total lack of self awareness. "By Doctor Who!" He exclaims. "This is a place where fine clothing is sold, sir. Not a common circus freak show for ill-bred worms to feed upon the suffering of others, where surely someone of your morally bankrupt description must surely have originated! That or the whore house, oh my Rainbow Dash..." He begins to tear up. "Just… go. Take your {} and go. Do come back if you want it sewn back together, though."'.format(item_sought.item_props['cosmetic_name'])
				else:
					current_item_stats = {}
					# Get the current stats of your cosmetic
					for stat in ewcfg.playerstats_list:
						if stat in item_sought.item_props.keys():
							if abs(int(item_sought.item_props[stat])) > 0:
								current_item_stats[stat] = int(item_sought.item_props[stat])

					if 'ability' in item_sought.item_props.keys():
						current_item_stats['ability'] = item_sought.item_props['ability']

					# Get the stats retrofitting would give you from the item model in ewcfg.cosmetic_items_list
					desired_item = ewcfg.cosmetic_map.get(item_sought.item_props['id_cosmetic'])
					
					if desired_item == None:
						response = "The hipster behind the counter doesn't really know what to do with that cosmetic, it's simply too outdated and worn out. He thinks you should just take it home and stuff it inside a box as a souvenir."
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

					desired_item_stats = {}

					for stat in ewcfg.playerstats_list:
						if stat in desired_item.stats.keys():
							if abs(int(desired_item.stats[stat])) > 0:
								desired_item_stats[stat] = desired_item.stats[stat]

					if desired_item.ability is not None:
						desired_item_stats['ability'] = desired_item.ability

					# Check to see if the cosmetic is actually outdated
					if current_item_stats != desired_item_stats:
						cost_ofretrofit = 100 # This is a completely random number that I arbitrarily pulled out of my ass

						if cost_ofretrofit > user_data.slimes:
							response = 'The hipster behind the counter narrows his gaze, his thick-rimmed glasses magnify his hatred of your ignoble ancestry.\n"Sir… it would cost {:,} to retrofit this garment with updated combat abilities. That’s more slime than you or your clan could ever accrue. Good day, sir. I SAID GOOD DAY. Come back when you’re a little, mmmmhh, *richer*."'.format(cost_ofretrofit)
						else:
							response = '"Let’s see, all told… including tax… plus gratuity… and a hefty tip, of course… your total comes out to {}, sir."'.format(cost_ofretrofit)
							response += "\n**!accept** or **!refuse** the deal."

							await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

							# Wait for an answer
							accepted = False

							try:
								message = await cmd.client.wait_for('message', timeout = 20, check=lambda message: message.author == cmd.message.author and 
																message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

								if message != None:
									if message.content.lower() == ewcfg.cmd_accept:
										accepted = True
									if message.content.lower() == ewcfg.cmd_refuse:
										accepted = False
							except:
								accepted = False

							# Cancel deal if the hat is no longer in user's inventory
							if item_sought.id_owner != str(user_data.id_user):
								accepted = False

							# Cancel deal if the user has left Krak Bay
							if user_data.poi != ewcfg.poi_id_bodega:
								accepted = False

							# Candel deal if the user doesn't have enough slime anymore
							if cost_ofretrofit > user_data.slimes:
								accepted = False

							if accepted == True:
								for stat in ewcfg.playerstats_list:
									if stat in desired_item_stats.keys():
										item_sought.item_props[stat] = desired_item_stats[stat]

								item_sought.persist()

								user_data.slimes -= cost_ofretrofit


								user_data.persist()

								response = '"Excellent. Just a moment… one more iron press and-- there, perfect! Your {}, sir. It’s like you just smelted it, no? Well, no refunds in any case."'.format(item_sought.item_props['cosmetic_name'])

							else:
								response = '"Oh, yes, of course. I understand, sir. No, really that’s okay. I get it. I totally get it. That’s your decision. Really, it’s okay. No problem here. Yep. Yup. Uh-huh, uh-huh. Yep. It’s fine, sir. That’s completely fine. For real. Seriously. I understand, sir. It’s okay. I totally get it. Yep. Uh-huh. Yes, sir. Really, it’s okay. Some people just don’t care how they look. I understand, sir."'
					else:
						response = 'The hipster behind the counter looks over your {} with the thoroughness that a true man would only spend making sure all the blood really was wrung from his most recent hunt’s neck or all the cum was ejactulated from his partner’s throbbing cock…\n"Sir," he begins to say, turning back to you before almost vomiting at the sight. After he regains his composure, he continues, "I understand you are an, shall we say, uneducated peasant, to put it delicately, but even still you should be able to tell that your {} is already completely up-to-date. Please, do not bother me with such wastes of my boss’ time again. I do enough of that on my own."'.format(item_sought.item_props['cosmetic_name'], item_sought.item_props['cosmetic_name'])
		else:
			response = "Sew which cosmetic? Check your **!inventory**."
	else:
		response = "Heh, yeah right. What kind of self-respecting juvenile delinquent knows how to sew? Sewing totally lame, everyone knows that! Even people who sew know that! Looks like you’re gonna have to find some nerd to do it for you."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


def update_hues():
	for hue in ewcfg.hue_list:
			
		hue_props = {
			ewcfg.col_hue_analogous_1 : '',
			ewcfg.col_hue_analogous_2 : '',
			ewcfg.col_hue_splitcomp_1 : '',
			ewcfg.col_hue_splitcomp_2 : '',
			ewcfg.col_hue_fullcomp_1 : '',
			ewcfg.col_hue_fullcomp_2 : '',
		}

		for h in hue.effectiveness:
			effect = hue.effectiveness.get(h)

			if effect == ewcfg.hue_analogous:

				if hue_props.get(ewcfg.col_hue_analogous_1) == '':
					hue_props[ewcfg.col_hue_analogous_1] = h

				elif hue_props.get(ewcfg.col_hue_analogous_2) == '':
					hue_props[ewcfg.col_hue_analogous_2] = h

			elif effect == ewcfg.hue_atk_complementary:

				if hue_props.get(ewcfg.col_hue_splitcomp_1) == '':
					hue_props[ewcfg.col_hue_splitcomp_1] = h

			elif effect == ewcfg.hue_special_complementary:

				if hue_props.get(ewcfg.col_hue_splitcomp_2) == '':
					hue_props[ewcfg.col_hue_splitcomp_2] = h

			elif effect == ewcfg.hue_full_complementary:

				if hue_props.get(ewcfg.col_hue_fullcomp_1) == '':
					hue_props[ewcfg.col_hue_fullcomp_1] = h

				elif hue_props.get(ewcfg.col_hue_fullcomp_2) == '':
					hue_props[ewcfg.col_hue_fullcomp_2] = h



		ewutils.execute_sql_query("REPLACE INTO hues ({}, {}, {}, {}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)".format(
			ewcfg.col_id_hue,
			ewcfg.col_is_neutral,
			ewcfg.col_hue_analogous_1,
			ewcfg.col_hue_analogous_2,
			ewcfg.col_hue_splitcomp_1,
			ewcfg.col_hue_splitcomp_2,
			ewcfg.col_hue_fullcomp_1,
			ewcfg.col_hue_fullcomp_2,
		), (
			hue.id_hue,
			1 if hue.is_neutral else 0,
			hue_props.get(ewcfg.col_hue_analogous_1),
			hue_props.get(ewcfg.col_hue_analogous_2),
			hue_props.get(ewcfg.col_hue_splitcomp_1),
			hue_props.get(ewcfg.col_hue_splitcomp_2),
			hue_props.get(ewcfg.col_hue_fullcomp_1),
			hue_props.get(ewcfg.col_hue_fullcomp_2),
		))
			



