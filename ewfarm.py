import time
import random
import asyncio

import ewcfg
import ewitem
import ewutils
import ewrolemgr

from ew import EwUser
from ewmarket import EwMarket
from ewfood import EwFood
from ewitem import EwItem
from ewslimeoid import EwSlimeoid
from ewdistrict import EwDistrict

class EwFarm:
	id_server = -1
	id_user = -1
	name = ""
	time_lastsow = 0
	phase = 0
	time_lastphase = 0
	slimes_onreap = 0
	action_required = 0
	crop = ""
	# player's life state at sow
	sow_life_state = 0

	def __init__(
		self,
		id_server = None,
		id_user = None,
		farm = None
	):
		if id_server is not None and id_user is not None and farm is not None:
			self.id_server = id_server
			self.id_user = id_user
			self.name = farm

			data = ewutils.execute_sql_query(
				"SELECT {time_lastsow}, {phase}, {time_lastphase}, {slimes_onreap}, {action_required}, {crop}, {life_state} FROM farms WHERE id_server = %s AND id_user = %s AND {col_farm} = %s".format(
					time_lastsow = ewcfg.col_time_lastsow,
					col_farm = ewcfg.col_farm,
					phase = ewcfg.col_phase,
					time_lastphase = ewcfg.col_time_lastphase,
					slimes_onreap = ewcfg.col_slimes_onreap,
					action_required = ewcfg.col_action_required,
					crop = ewcfg.col_crop,
					life_state = ewcfg.col_sow_life_state,
				), (
					id_server,
					id_user,
					farm
				)
			)

			if len(data) > 0:  # if data is not empty, i.e. it found an entry
				# data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
				self.time_lastsow = data[0][0]
				self.phase = data[0][1]
				self.time_lastphase = data[0][2]
				self.slimes_onreap = data[0][3]
				self.action_required = data[0][4]
				self.crop = data[0][5]
				self.sow_life_state = data[0][6]

			else:  # create new entry
				ewutils.execute_sql_query(
					"REPLACE INTO farms (id_server, id_user, {col_farm}) VALUES (%s, %s, %s)".format(
						col_farm = ewcfg.col_farm
					), (
						id_server,
						id_user,
						farm
					)
				)

	def persist(self):
		ewutils.execute_sql_query(
			"REPLACE INTO farms(id_server, id_user, {farm}, {time_lastsow}, {phase}, {time_lastphase}, {slimes_onreap}, {action_required}, {crop}, {life_state}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
				farm = ewcfg.col_farm,
				time_lastsow = ewcfg.col_time_lastsow,
				phase = ewcfg.col_phase,
				time_lastphase = ewcfg.col_time_lastphase,
				slimes_onreap = ewcfg.col_slimes_onreap,
				action_required = ewcfg.col_action_required,
				crop = ewcfg.col_crop,
				life_state = ewcfg.col_sow_life_state,
			), (
				self.id_server,
				self.id_user,
				self.name,
				self.time_lastsow,
				self.phase,
				self.time_lastphase,
				self.slimes_onreap,
				self.action_required,
				self.crop,
				self.sow_life_state,
			)
		)

class EwFarmAction:
	id_action = 0

	action = ""
	
	str_check = ""

	str_execute = ""

	str_execute_fail = ""

	aliases = []

	def __init__(self,
		id_action = 0,
		action = "",
		str_check = "",
		str_execute = "",
		str_execute_fail = "",
		aliases = []
	):
		self.id_action = id_action
		self.action = action
		self.str_check = str_check
		self.str_execute = str_execute
		self.str_execute_fail = str_execute_fail
		self.aliases = aliases


"""
	Reap planted crops.
"""
async def reap(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	forcereap = False
	if cmd.tokens[0] == ewcfg.cmd_reap_alt:
		if cmd.message.author.guild_permissions.administrator:
			forcereap = True
		else:
			return
		

	response = ""
	levelup_response = ""
	mutations = user_data.get_mutations()
	cosmetic_abilites = ewutils.get_cosmetic_abilities(id_user = cmd.message.author.id, id_server = cmd.guild.id)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	# check if the user has a farming tool equipped
	weapon_item = EwItem(id_item=user_data.weapon)
	weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
	has_tool = False
	if weapon is not None:
		if ewcfg.weapon_class_farming in weapon.classes:
			has_tool = True

	# Checking availability of reap action
	if user_data.life_state != ewcfg.life_state_juvenile and not has_tool:
		response = "Only Juveniles of pure heart and with nothing better to do can farm."
	elif cmd.message.channel.name not in [ewcfg.channel_jr_farms, ewcfg.channel_og_farms, ewcfg.channel_ab_farms]:
		response = "Do you remember planting anything here in this barren wasteland? No, you don’t. Idiot."
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		if user_data.poi == ewcfg.poi_id_jr_farms:
			farm_id = ewcfg.poi_id_jr_farms
		elif user_data.poi == ewcfg.poi_id_og_farms:
			farm_id = ewcfg.poi_id_og_farms
		else:  # if it's the farm in arsonbrook
			farm_id = ewcfg.poi_id_ab_farms

		farm = EwFarm(
			id_server = cmd.guild.id,
			id_user = cmd.message.author.id,
			farm = farm_id
		)

		if farm.time_lastsow == 0:
			response = "You missed a step, you haven’t planted anything here yet."
		else:
			cur_time_min = time.time() / 60
			time_grown = cur_time_min - farm.time_lastsow

			if farm.phase != ewcfg.farm_phase_reap and not forcereap:
				response = "Patience is a virtue and you are morally bankrupt. Just wait, asshole."
			else: # Reaping
				if (time_grown > ewcfg.crops_time_to_grow * 16) and not forcereap:  # about 2 days
					response = "You eagerly cultivate your crop, but what’s this? It’s dead and wilted! It seems as though you’ve let it lay fallow for far too long. Pay better attention to your farm next time. You gain no slime."
					farm.time_lastsow = 0  # 0 means no seeds are currently planted
					farm.persist()
				else:
					user_initial_level = user_data.slimelevel

					slime_gain = farm.slimes_onreap

					controlling_faction = ewutils.get_subzone_controlling_faction(user_data.poi, user_data.id_server)

					if controlling_faction != "" and controlling_faction == user_data.faction:
						slime_gain *= 2

					if has_tool and weapon.id_weapon == ewcfg.weapon_id_hoe:
						slime_gain *= 1.5

					if user_data.poi == ewcfg.poi_id_jr_farms:
						slime_gain = int(slime_gain / 4)

					trauma = ewcfg.trauma_map.get(user_data.trauma)
					if trauma != None and trauma.trauma_class == ewcfg.trauma_class_slimegain:
						slime_gain *= (1 - 0.5 * user_data.degradation / 100)

					slime_gain = max(0, round(slime_gain))

					response = "You reap what you’ve sown. Your investment has yielded {:,} slime, ".format(slime_gain)

					# Determine if an item is found.
					unearthed_item = False
					unearthed_item_amount = 0

					unearthed_item_chance = 50 / ewcfg.unearthed_item_rarity  # 1 in 30 chance
					
					if ewcfg.mutation_id_lucky in mutations or ewcfg.cosmeticAbility_id_lucky in cosmetic_abilites:
						unearthed_item_chance *= 1.33

					if random.random() < unearthed_item_chance:
						unearthed_item = True
						unearthed_item_amount = 1 if random.randint(1, 3) != 1 else 2  # 33% chance of extra drop

					if unearthed_item == True:
						# If there are multiple possible products, randomly select one.
						item = random.choice(ewcfg.mine_results)

						item_props = ewitem.gen_item_props(item)

						if item is not None:

							for creation in range(unearthed_item_amount):
								ewitem.item_create(
									item_type = item.item_type,
									id_user = cmd.message.author.id,
									id_server = cmd.guild.id,
									item_props = item_props
								)

						if unearthed_item_amount == 1:
							response += "a {}, ".format(item.str_name)
						elif unearthed_item_amount == 2:
							response += "two {}s, ".format(item.str_name)

					#  Determine what crop is grown.
					vegetable = ewcfg.food_map.get(farm.crop)
					if vegetable is None:
						vegetable = random.choice(ewcfg.vegetable_list)

					item_props = ewitem.gen_item_props(vegetable)

					#  Create and give a bushel of whatever crop was grown, unless it's a metal crop.
					if item_props.get('id_food') in [ewcfg.item_id_metallicaps, ewcfg.item_id_steelbeans, ewcfg.item_id_aushucks]:
						metallic_crop_ammount = 1
						if random.randrange(10) == 0:
							metallic_crop_ammount = 5 if random.randrange(2) == 0 else 6
						
						for vcreate in range(metallic_crop_ammount):
							ewitem.item_create(
								id_user=cmd.message.author.id,
								id_server=cmd.guild.id,
								item_type=vegetable.item_type,
								item_props=item_props
							)
							
						if metallic_crop_ammount == 1:
							response += "and a single {}!".format(vegetable.str_name)
						else:
							response += "and a bushel or two of {}!".format(vegetable.str_name)
						# if random.randrange(10) == 0:
						# 	for vcreate in range(6):
						# 		ewitem.item_create(
						# 			id_user=cmd.message.author.id,
						# 			id_server=cmd.guild.id,
						# 			item_type=vegetable.item_type,
						# 			item_props=item_props
						# 		)
						# 	
						# 	response += "and a bushel of {}!".format(vegetable.str_name)
						# else:
						# 	response += "and a bushel of... hey, what the hell! You didn't reap anything! Must've been some odd seeds..."
					else:
						unearthed_vegetable_amount = 3
						if has_tool and weapon.id_weapon == ewcfg.weapon_id_pitchfork:
							unearthed_vegetable_amount += 3

						for vcreate in range(unearthed_vegetable_amount):
							ewitem.item_create(
								id_user = cmd.message.author.id,
								id_server = cmd.guild.id,
								item_type = vegetable.item_type,
								item_props = item_props
							)
	
						response += "and a bushel of {}!".format(vegetable.str_name)

					levelup_response = user_data.change_slimes(n = slime_gain, source = ewcfg.source_farming)

					was_levelup = True if user_initial_level < user_data.slimelevel else False

					# Tell the player their slime level increased.
					if was_levelup:
						response += "\n\n" + levelup_response

					user_data.hunger += ewcfg.hunger_perfarm
					# Flag the user for PvP
					#enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
					# user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_farm, enlisted)

					user_data.persist()

					farm.time_lastsow = 0  # 0 means no seeds are currently planted
					farm.persist()
					await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)


	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


"""
	Sow seeds that may eventually be !reaped.
"""
async def sow(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	# check if the user has a farming tool equipped
	weapon_item = EwItem(id_item=user_data.weapon)
	weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
	has_tool = False
	if weapon is not None:
		if ewcfg.weapon_class_farming in weapon.classes:
			has_tool = True

	# Checking availability of sow action
	if user_data.life_state != ewcfg.life_state_juvenile and not has_tool:
		response = "Only Juveniles of pure heart and with nothing better to do can farm."

	elif cmd.message.channel.name not in [ewcfg.channel_jr_farms, ewcfg.channel_og_farms, ewcfg.channel_ab_farms]:
		response = "The cracked, filthy concrete streets around you would be a pretty terrible place for a farm. Try again on more arable land."

	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		if user_data.poi == ewcfg.poi_id_jr_farms:
			farm_id = ewcfg.poi_id_jr_farms
		elif user_data.poi == ewcfg.poi_id_og_farms:
			farm_id = ewcfg.poi_id_og_farms
		else:  # if it's the farm in arsonbrook
			farm_id = ewcfg.poi_id_ab_farms

		farm = EwFarm(
			id_server = cmd.guild.id,
			id_user = cmd.message.author.id,
			farm = farm_id
		)

		if farm.time_lastsow > 0:
			response = "You’ve already sown something here. Try planting in another farming location. If you’ve planted in all three farming locations, you’re shit out of luck. Just wait, asshole."
		else:
			# gangsters can only plant poudrins
			if cmd.tokens_count > 1 and user_data.life_state == ewcfg.life_state_juvenile:
				item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
			else:
				item_search = "slimepoudrin"

			item_sought = ewitem.find_item(item_search = item_search, id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None)

			if item_sought == None:
				response = "You don't have anything to plant! Try collecting a poudrin."
			else:
				slimes_onreap = ewcfg.reap_gain
				item_data = EwItem(id_item = item_sought.get("id_item"))
				if item_data.item_type == ewcfg.it_item:
					if item_data.item_props.get("id_item") == ewcfg.item_id_slimepoudrin:
						vegetable = random.choice(ewcfg.vegetable_list)
						slimes_onreap *= 2
					elif item_data.item_props.get("context") == ewcfg.context_slimeoidheart:
						vegetable = random.choice(ewcfg.vegetable_list)
						slimes_onreap *= 2

						slimeoid_data = EwSlimeoid(id_slimeoid = item_data.item_props.get("subcontext"))
						slimeoid_data.delete()
						
					else:
						response = "The soil has enough toxins without you burying your trash here."
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				elif item_data.item_type == ewcfg.it_food:
					food_id = item_data.item_props.get("id_food")
					vegetable = ewcfg.food_map.get(food_id)
					if ewcfg.vendor_farm not in vegetable.vendors:
						response = "It sure would be nice if {}s grew on trees, but alas they do not. Idiot.".format(item_sought.get("name"))
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
					elif user_data.life_state != ewcfg.life_state_juvenile:
						response = "You lack the knowledge required to grow {}.".format(item_sought.get("name"))
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

				else:
					response = "The soil has enough toxins without you burying your trash here."
					return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				
				growth_time = ewcfg.crops_time_to_grow
				if user_data.life_state == ewcfg.life_state_juvenile:
					growth_time /= 2
				
				hours = int(growth_time / 60)
				minutes = int(growth_time % 60)

				str_growth_time = "{} hour{}{}".format(hours, "s" if hours > 1 else "", " and {} minutes".format(minutes) if minutes > 0 else "")

				# Sowing
				response = "You sow a {} into the fertile soil beneath you. It will grow in about {}.".format(item_sought.get("name"), str_growth_time)

				farm.time_lastsow = int(time.time() / 60)  # Grow time is stored in minutes.
				farm.time_lastphase = int(time.time())
				farm.slimes_onreap = slimes_onreap
				farm.crop = vegetable.id_food
				farm.phase = ewcfg.farm_phase_sow
				farm.action_required = ewcfg.farm_action_none
				farm.sow_life_state = user_data.life_state
				ewitem.item_delete(id_item = item_sought.get('id_item'))  # Remove Poudrins

				farm.persist()

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def mill(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	market_data = EwMarket(id_server = user_data.id_server)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search = item_search, id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None)

	# Checking availability of milling
	if user_data.life_state != ewcfg.life_state_juvenile:
		response = "Only Juveniles of pure heart and with nothing better to do can mill their vegetables."
	elif cmd.message.channel.name not in [ewcfg.channel_jr_farms, ewcfg.channel_og_farms, ewcfg.channel_ab_farms]:
		response = "Alas, there doesn’t seem to be an official SlimeCorp milling station anywhere around here. Probably because you’re in the middle of the fucking city. Try looking where you reaped your vegetable in the first place, dumbass."

	# elif user_data.slimes < ewcfg.slimes_permill:
	# 	response = "It costs {} to !mill, and you only have {}.".format(ewcfg.slimes_permill, user_data.slimes)

	elif item_sought:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		items = []
		vegetable = EwItem(id_item = item_sought.get('id_item'))

		for result in ewcfg.mill_results:
			if type(result.ingredients) == str:
				if vegetable.item_props.get('id_food') != result.ingredients:
					pass
				else:
					items.append(result)
			elif type(result.ingredients) == list:
				if vegetable.item_props.get('id_food') not in result.ingredients:
					pass
				else:
					items.append(result)



		if len(items) > 0:
			item = random.choice(items)

			item_props = ewitem.gen_item_props(item)
			
			ewitem.item_create(
				item_type = item.item_type,
				id_user = cmd.message.author.id,
				id_server = cmd.guild.id,
				item_props = item_props
			)

			response = "You walk up to the official ~~SlimeCorp~~ Garden Gankers Milling Station and shove your irradiated produce into the hand-crank. You begin slowly churning them into a glorious, pastry goo. As the goo tosses and turns inside the machine, it solidifies, and after a few moments a {} pops out!".format(item.str_name)

			#market_data.donated_slimes += ewcfg.slimes_permill
			market_data.persist()

			ewitem.item_delete(id_item = item_sought.get('id_item'))
			#user_data.change_slimes(n = -ewcfg.slimes_permill, source = ewcfg.source_spending)
			#user_data.slime_donations += ewcfg.slimes_permill
			user_data.persist()
		else:
			response = "You can only mill fresh vegetables! SlimeCorp obviously wants you to support local farmers."

	else:
		if item_search:  # if they didn't forget to specify an item and it just wasn't found
			response = "You don't have one."
		else:
			response = "Mill which item? (check **!inventory**)"

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def check_farm(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = ""
	levelup_response = ""
	mutations = user_data.get_mutations()

	# Checking availability of check farm action
	if user_data.life_state != ewcfg.life_state_juvenile:
		response = "Only Juveniles of pure heart and with nothing better to do can farm."
	elif cmd.message.channel.name not in [ewcfg.channel_jr_farms, ewcfg.channel_og_farms, ewcfg.channel_ab_farms]:
		response = "Do you remember planting anything here in this barren wasteland? No, you don’t. Idiot."
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		if user_data.poi == ewcfg.poi_id_jr_farms:
			farm_id = ewcfg.poi_id_jr_farms
		elif user_data.poi == ewcfg.poi_id_og_farms:
			farm_id = ewcfg.poi_id_og_farms
		else:  # if it's the farm in arsonbrook
			farm_id = ewcfg.poi_id_ab_farms


		farm = EwFarm(
			id_server = cmd.guild.id,
			id_user = cmd.message.author.id,
			farm = farm_id
		)

		if farm.time_lastsow == 0:
			response = "You missed a step, you haven’t planted anything here yet."
		elif farm.action_required == ewcfg.farm_action_none:
			if farm.phase == ewcfg.farm_phase_reap:
				response = "Your crop is ready for the harvest."
			elif farm.phase == ewcfg.farm_phase_sow:
				response = "You only just planted the seeds. Check back later."
			else:
				if farm.slimes_onreap < ewcfg.reap_gain:
					response = "Your crop looks frail and weak."
				elif farm.slimes_onreap < ewcfg.reap_gain + 3 * ewcfg.farm_slimes_peraction:
					response = "Your crop looks small and generally unremarkable."
				elif farm.slimes_onreap < ewcfg.reap_gain + 6 * ewcfg.farm_slimes_peraction:
					response = "Your crop seems to be growing well."
				else:
					response = "Your crop looks powerful and bursting with nutrients."

		else:
			farm_action = ewcfg.id_to_farm_action.get(farm.action_required)
			response = farm_action.str_check

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def cultivate(cmd):

	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = ""
	levelup_response = ""
	mutations = user_data.get_mutations()

	# Checking availability of irrigate action
	if user_data.life_state != ewcfg.life_state_juvenile:
		response = "Only Juveniles of pure heart and with nothing better to do can tend to their crops."
	elif cmd.message.channel.name not in [ewcfg.channel_jr_farms, ewcfg.channel_og_farms, ewcfg.channel_ab_farms]:
		response = "Do you remember planting anything here in this barren wasteland? No, you don’t. Idiot."
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		if user_data.poi == ewcfg.poi_id_jr_farms:
			farm_id = ewcfg.poi_id_jr_farms
		elif user_data.poi == ewcfg.poi_id_og_farms:
			farm_id = ewcfg.poi_id_og_farms
		else:  # if it's the farm in arsonbrook
			farm_id = ewcfg.poi_id_ab_farms


		farm = EwFarm(
			id_server = cmd.guild.id,
			id_user = cmd.message.author.id,
			farm = farm_id
		)

		
		farm_action = ewcfg.cmd_to_farm_action.get(cmd.tokens[0].lower())

		if farm.time_lastsow == 0:
			response = "You missed a step, you haven’t planted anything here yet."
		elif farm.action_required != farm_action.id_action:
			response = farm_action.str_execute_fail
			farm.slimes_onreap -= ewcfg.farm_slimes_peraction
			farm.slimes_onreap = max(farm.slimes_onreap, 0)
			farm.persist()
		else:
			response = farm_action.str_execute
			# gvs - farm actions award more slime
			farm.slimes_onreap += ewcfg.farm_slimes_peraction * 2
			farm.action_required = ewcfg.farm_action_none
			farm.persist()

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def farm_tick_loop(id_server):
	while not ewutils.TERMINATE:
		await asyncio.sleep(ewcfg.farm_tick_length)
		farm_tick(id_server)


def farm_tick(id_server):
	time_now = int(time.time())
	farms = ewutils.execute_sql_query("SELECT {id_user}, {farm} FROM farms WHERE id_server = %s AND {time_lastsow} > 0 AND {phase} < %s".format(
		id_user = ewcfg.col_id_user,
		farm = ewcfg.col_farm,
		time_lastsow = ewcfg.col_time_lastsow,
		phase = ewcfg.col_phase,
	),(
		id_server,
		ewcfg.farm_phase_reap,
	))

	for row in farms:
		farm_data = EwFarm(id_server = id_server, id_user = row[0], farm = row[1])

		time_nextphase = ewcfg.time_nextphase

		# gvs - juvie's last farming phase lasts 10 minutes
		if farm_data.sow_life_state == ewcfg.life_state_juvenile and farm_data.phase == (ewcfg.farm_phase_reap_juvie - 1):
			time_nextphase = ewcfg.time_lastphase_juvie
		
		if time_now >= farm_data.time_lastphase + time_nextphase:
			farm_data.phase += 1
			farm_data.time_lastphase = time_now

			# gvs - juvies only have 5 farming phases
			if farm_data.sow_life_state == ewcfg.life_state_juvenile and farm_data.phase == ewcfg.farm_phase_reap_juvie:
				farm_data.phase = ewcfg.farm_phase_reap
				
			if farm_data.phase < ewcfg.farm_phase_reap:
				farm_data.action_required = random.choice(ewcfg.farm_action_ids)
			else:
				farm_data.action_required = ewcfg.farm_action_none
			farm_data.persist()
