import math
import time
import asyncio

import ewcfg
import ewitem
import ewutils
import ewmap
import random
import ewrolemgr
import ewstatuseffects
from ew import EwUser
from ewplayer import EwPlayer
from ewmarket import EwMarket, EwCompany, EwStock
from ewitem import EwItem
from ewdistrict import EwDistrict

""" Food model object """
class EwFood:
	item_type = "food"

	# The main name of this food.
	id_food = ""

	# A list of alternative names.
	alias = []

	# Hunger reduced by eating this food.
	recover_hunger = 0

	# Cost in SlimeCoin to eat this food.
	price = 0

	# A nice string name describing this food.
	str_name = ""

	# Names of the vendors selling this food in the food court.
	vendors = []

	# Flavor text displayed when you eat this food.
	str_eat = ""

	# Alcoholic effect
	inebriation = 0

	# Flavor text displayed when you inspect this food.
	str_desc = ""

	# Expiration time (can be left blank for standard expiration time)
	time_expir = 0

	# The ingredients necessary to make this item via it's acquisition method
	ingredients = ""

	# The way that you can acquire this item. If blank, it's not relevant.
	acquisition = ""

	# Whether or not the item expires
	perishable = True

	#Timestamp when an item was fridged.

	time_fridged = 0

	def __init__(
		self,
		id_food = "",
		alias = [],
		recover_hunger = 0,
		price = 0,
		str_name = "",
		vendors = [],
		str_eat = "",
		inebriation = 0,
		str_desc = "",
		time_expir = 0,
		time_fridged =0,
		ingredients = "",
		acquisition = "",
		perishable = True
	):
		self.item_type = ewcfg.it_food

		self.id_food = id_food
		self.alias = alias
		self.recover_hunger = recover_hunger
		self.price = price
		self.str_name = str_name
		self.vendors = vendors
		self.str_eat = str_eat
		self.inebriation = inebriation
		self.str_desc = str_desc
		self.time_expir = time_expir if time_expir > 0 else ewcfg.std_food_expir
		self.time_fridged = time_fridged
		self.ingredients = ingredients
		self.acquisition = acquisition
		self.perishable = perishable


""" show all available food items """
async def menu(cmd):
	user_data = EwUser(member = cmd.message.author, data_level = 2)
	if user_data.life_state == ewcfg.life_state_shambler and user_data.poi != ewcfg.poi_id_nuclear_beach_edge:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	market_data = EwMarket(id_server = cmd.guild.id)
	#poi = ewmap.fetch_poi_if_coordless(cmd.message.channel.name)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	if poi is None or len(poi.vendors) == 0 or ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		# Only allowed in the food court.
		response = "There’s nothing to buy here. If you want to purchase some items, go to a sub-zone with a vendor in it, like the food court, the speakeasy, or the bazaar."
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		
		mother_district_data = None
		for mother_poi in poi.mother_districts:

			mother_poi_data = ewcfg.id_to_poi.get(mother_poi)

			if mother_poi_data.is_district:
				# One of the mother pois was a district, get its controlling faction
				mother_district_data = EwDistrict(district=mother_poi, id_server=user_data.id_server)
				break
			else:
				# One of the mother pois was a street, get the father district of that street and its controlling faction
				father_poi = mother_poi_data.father_district
				mother_district_data = EwDistrict(district=father_poi, id_server=user_data.id_server)
				break

		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)
		#mother_district_data = EwDistrict(district = destination_poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded() and poi.id_poi != ewcfg.poi_id_nuclear_beach_edge:
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
		controlling_faction = ewutils.get_subzone_controlling_faction(user_data.poi, user_data.id_server)
		
		response = "{} Menu:\n\n".format(poi.str_name)

		vendors_list = poi.vendors

		for vendor in vendors_list:
			if vendor == ewcfg.vendor_secretbodega:
				if user_data.freshness < ewcfg.freshnesslevel_4:
					continue
				else:
					response += '\nThe hipster behind the counter nearly falls out of his chair after laying eyes on the sheer, unadulterated freshness before him.\n"S-Sir! Your outfit... i-it is positively ***on fleek!!*** As I see you are a fashion enthusiast like myself, let me show you the good stuff…"\n'

			items = []
			# If the vendor is the bazaar get the current rotation of items from the market_data
			vendor_inv = ewcfg.vendor_inv[vendor] if vendor != ewcfg.vendor_bazaar else market_data.bazaar_wares.values()
			for item_name in vendor_inv:
				item_item = ewcfg.item_map.get(item_name)
				food_item = ewcfg.food_map.get(item_name)
				cosmetic_item = ewcfg.cosmetic_map.get(item_name)
				furniture_item = ewcfg.furniture_map.get(item_name)
				weapon_item = ewcfg.weapon_map.get(item_name)

				# increase profits for the stock market
				stock_data = None
				if vendor in ewcfg.vendor_stock_map:
					stock = ewcfg.vendor_stock_map.get(vendor)
					stock_data = EwStock(id_server = user_data.id_server, stock = stock)

				value = 0

				if item_item:
					value = item_item.price

				if food_item:
					value = food_item.price

				if cosmetic_item:
					value = cosmetic_item.price

				if furniture_item:
					value = furniture_item.price

				if weapon_item:
					value = weapon_item.price

				if stock_data != None:
					value *= (stock_data.exchange_rate / ewcfg.default_stock_exchange_rate) ** 0.2

				
				if mother_district_data != None:
					if mother_district_data.all_streets_taken() != "" and poi.id_poi != ewcfg.poi_id_nuclear_beach_edge:
						# prices are halved for the controlling gang
						if mother_district_data.all_streets_taken() == user_data.faction:
							value /= 2
	
						# and 4 times as much for enemy gangsters
						elif user_data.faction != "":
							value *= 4

				value = int(value)

				if value != 0:
					items.append('{name} ({price})'.format(name = item_name, price = value))
				else:
					items.append(item_name)

			response += "**{}**: *{}*\n".format(vendor, ewutils.formatNiceList(names = items))

			if vendor == ewcfg.vendor_bodega:
				if user_data.freshness < ewcfg.freshnesslevel_1:
					response += "\nThe hipster behind the counter is utterly repulsed by the fashion disaster in front of him. Looks like you just aren’t fresh enough for him."
			if user_data.has_soul == 0:
				if vendor == ewcfg.vendor_dojo:
					response += "\n\nThe Dojo master looks at your soulless form with pity."
				elif vendor == ewcfg.vendor_bar:
					response += "\n\nThe bartender, sensing your misery, asks if you're okay."
				elif vendor == ewcfg.vendor_diner:
					response += "\n\nThe cook gives you a concerned look as he throws down another helping of flapjacks."
				elif vendor == ewcfg.vendor_seafood:
					response += "\n\nThe waiter sneers at how soulless and unkempt you look. You try to ignore him."
				elif vendor == ewcfg.vendor_bazaar:
					response += "\n\nAll the shops seem so lively. You wish you had a soul so you could be like them."
				elif vendor == ewcfg.vendor_beachresort or vendor == ewcfg.vendor_countryclub:
					response += "\n\nEverything looks so fancy here, but it doesn't really appeal to you since you don't have a soul."
				elif vendor == ewcfg.vendor_bodega:
					if user_data.freshness < ewcfg.freshnesslevel_1:
						response += ".. and you probably never will be."
				elif vendor == ewcfg.vendor_glocksburycomics:
					response += "\n\nThe cashier here tries to start up a conversation about life being worth living. You're having none of it."
				elif vendor == ewcfg.vendor_basedhardware:
					response += "\n\nSo many industrial metals here... You contemplate which you could use to kill yourself..."
				elif vendor == ewcfg.vendor_basedhardware:
					response += "\n\nNot even waffles could hope to make your emptiness go away."
				elif vendor == ewcfg.vendor_greencakecafe:
					response += "\n\nThe barista behind the counter pauses to look at your soulless misery for a second, but decides you're not worth it and gets back to work."
				elif vendor == ewcfg.vendor_slimypersuits:
					response += "\n\nYour mere presence in here ruins the cheery atmosphere."

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

# Buy items.
async def order(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler and user_data.poi != ewcfg.poi_id_nuclear_beach_edge:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	market_data = EwMarket(id_server = cmd.guild.id)
	currency_used = 'slime'
	current_currency_amount = user_data.slimes
	#poi = ewmap.fetch_poi_if_coordless(cmd.message.channel.name)
	poi = ewcfg.id_to_poi.get(user_data.poi)
	if poi is None or len(poi.vendors) == 0 or ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		# Only allowed in the food court.
		response = "There’s nothing to buy here. If you want to purchase some items, go to a sub-zone with a vendor in it, like the food court, the speakeasy, or the bazaar."
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded() and poi.id_poi != ewcfg.poi_id_nuclear_beach_edge:
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		#value = ewutils.flattenTokenListToString(cmd.tokens[1:2])

		#if cmd.tokens_count > 1:
		#	value = cmd.tokens[1]
		#	value = value.lower()

		value = None

		togo = False
		if cmd.tokens_count > 1:
			for token in cmd.tokens[1:]:
				if token.startswith('<@') == False and token.lower() not in "togo":  # togo can be spelled together or separate
					value = token
					break

			for token in cmd.tokens[1:]:
				if token.lower() in "togo":  # lets people get away with just typing only to or only go (or only t etc.) but whatever
					togo = True
					break

		# Finds the item if it's an EwGeneralItem.

		if value == "mylittleponyfigurine":
			value = random.choice(ewcfg.furniture_pony)

		item = ewcfg.item_map.get(value)

		item_type = ewcfg.it_item
		if item != None:
			item_id = item.id_item
			name = item.str_name

		# Finds the item if it's an EwFood item.
		if item == None:
			item = ewcfg.food_map.get(value)
			item_type = ewcfg.it_food
			if item != None:
				item_id = item.id_food
				name = item.str_name

		# Finds the item if it's an EwCosmeticItem.
		if item == None:
			item = ewcfg.cosmetic_map.get(value)
			item_type = ewcfg.it_cosmetic
			if item != None:
				item_id = item.id_cosmetic
				name = item.str_name

		if item == None:
			item = ewcfg.furniture_map.get(value)
			item_type = ewcfg.it_furniture
			if item != None:
				item_id = item.id_furniture
				name = item.str_name
				if item_id in ewcfg.furniture_pony:
					item.vendors = [ewcfg.vendor_bazaar]

		if item == None:
			item = ewcfg.weapon_map.get(value)
			item_type = ewcfg.it_weapon
			if item != None: 
				item_id = item.id_weapon
				name = item.str_weapon


		if item != None:
			item_type = item.item_type
			# Gets a vendor that the item is available and the player currently located in
			try:
				current_vendor = (set(item.vendors).intersection(set(poi.vendors))).pop()
			except:
				current_vendor = None


			# Check if the item is available in the current bazaar item rotation
			if current_vendor == ewcfg.vendor_bazaar:
				if item_id not in market_data.bazaar_wares.values():
					if item_id in ewcfg.furniture_pony and "mylittleponyfigurine" in market_data.bazaar_wares.values():
						pass
					else:
						current_vendor = None
						
			if current_vendor == ewcfg.vendor_downpourlaboratory:
				currency_used = 'brainz'
				current_currency_amount = user_data.gvs_currency

			if current_vendor is None or len(current_vendor) < 1:
				response = "Check the {} for a list of items you can {}.".format(ewcfg.cmd_menu, ewcfg.cmd_order)

			else:
				response = ""

				value = item.price
				premium_purchase = True if item_id in ewcfg.premium_items else False
				if premium_purchase:
					togo = True # Just in case they order a premium food item, don't make them eat it right then and there.
					
					if ewcfg.cd_premium_purchase > (int(time.time()) - user_data.time_lastpremiumpurchase):
						response = "That item is in very limited stock! The vendor asks that you refrain from purchasing it for a day or two."
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

					elif ewcfg.cd_new_player > (int(time.time()) - user_data.time_joined):
						response = "You've only been in the city for a few days. The vendor doesn't trust you with that item very much..."
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

				stock_data = None
				company_data = None
				# factor in the current stocks
				for vendor in item.vendors:
					if vendor in ewcfg.vendor_stock_map:
						stock = ewcfg.vendor_stock_map.get(vendor)
						company_data = EwCompany(id_server = user_data.id_server, stock = stock)
						stock_data = EwStock(id_server = user_data.id_server, stock = stock)

				if stock_data is not None:
					value *= (stock_data.exchange_rate / ewcfg.default_stock_exchange_rate) ** 0.2

				controlling_faction = ewutils.get_subzone_controlling_faction(user_data.poi, user_data.id_server)

				if controlling_faction != "" and poi.id_poi != ewcfg.poi_id_nuclear_beach_edge:
					# prices are halved for the controlling gang
					if controlling_faction == user_data.faction:
						value /= 2

					# and 4 times as much for enemy gangsters
					elif user_data.faction != "":
						value *= 4
				
				# Raise the price for togo ordering. This gets lowered back down later if someone does togo ordering on a non-food item by mistake.
				if togo:
					value *= 1.5
					
				value = int(value)

				food_ordered = False
				target_data = None

				# Kingpins eat free.
				if (user_data.life_state == ewcfg.life_state_kingpin or user_data.life_state == ewcfg.life_state_grandfoe) and item_type == ewcfg.it_food:
					value = 0

				if value > current_currency_amount:
					# Not enough money.
					response = "A {} costs {:,} {}, and you only have {:,}.".format(name, value, currency_used, current_currency_amount)
				else:
					if item_type == ewcfg.it_food:
						food_ordered = True

						food_items = ewitem.inventory(
							id_user = cmd.message.author.id,
							id_server = cmd.guild.id,
							item_type_filter = ewcfg.it_food
						)

						target = None
						target_data = None
						if not togo:  # cant order togo for someone else, you can just give it to them in person
							if cmd.mentions_count == 1:
								target = cmd.mentions[0]
								if target.id == cmd.message.author.id:
									target = None

						if target != None:
							target_data = EwUser(member=target)
							if target_data.life_state == ewcfg.life_state_corpse and target_data.get_weapon_possession():
								response = "How are you planning to feed a weapon?"
								return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
							elif target_data.poi != user_data.poi:
								response = "You can't order anything for them because they aren't here!"
								return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

						if len(food_items) >= user_data.get_food_capacity() and target_data == None and togo:
							# user_data never got persisted so the player won't lose money unnecessarily
							response = "You can't carry any more food than that."
							return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

					elif item_type == ewcfg.it_weapon:
						weapons_held = ewitem.inventory(
							id_user = user_data.id_user,
							id_server = cmd.guild.id,
							item_type_filter = ewcfg.it_weapon
						)

						has_weapon = False

						# Thrown weapons are stackable
						if ewcfg.weapon_class_thrown in item.classes:
							# Check the player's inventory for the weapon and add amount to stack size. Create a new item the max stack size has been reached
							for wep in weapons_held:
								weapon = EwItem(id_item=wep.get("id_item"))
								if weapon.item_props.get("weapon_type") == item.id_weapon and weapon.stack_size < weapon.stack_max:
									has_weapon = True
									weapon.stack_size += 1
									weapon.persist()
									
									if value == 0:
										response = "You swipe a {} from the counter at {}.".format(item.str_weapon, current_vendor)
									else:
										response = "You slam {:,} slime down on the counter at {} for {}.".format(value, current_vendor, item.str_weapon)
									
									user_data.change_slimes(n=-value, source=ewcfg.source_spending)
									user_data.persist()
									return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

						if has_weapon == False:
							if len(weapons_held) >= user_data.get_weapon_capacity():
								response = "You can't carry any more weapons."
								return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


							elif user_data.life_state == ewcfg.life_state_corpse:
								response = "Ghosts can't hold weapons."
								return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

					item_props = ewitem.gen_item_props(item)

					customtext = cmd.message.content[(len(cmd.tokens[0]) + len(cmd.tokens[1]) + 2):]

					if item.item_type == ewcfg.it_furniture and "custom" in item_props.get('id_furniture'):
						if customtext == "":
							response = "You need to specify the customization text before buying a custom item. Come on, isn't that self-evident?"
							return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

					# Only food should have the value multiplied. If someone togo orders a non-food item by mistake, lower it back down.
					if not food_ordered and togo:
						value = int(value/1.5)

					if currency_used == 'slime':
						user_data.change_slimes(n=-value, source=ewcfg.source_spending)
					elif currency_used == 'brainz':
						user_data.gvs_currency -= value

					if company_data is not None:
						company_data.recent_profits += value
						company_data.persist()

					if item.str_name == "arcade cabinet":
						item_props['furniture_desc'] = random.choice(ewcfg.cabinets_list)
					elif item.item_type == ewcfg.it_furniture:
						if "custom" in item_props.get('id_furniture'):
							item_props['furniture_name'] = item_props['furniture_name'].format(custom = customtext)
							item_props['furniture_desc'] = item_props['furniture_desc'].format(custom=customtext)
							item_props['furniture_look_desc'] = item_props['furniture_look_desc'].format(custom=customtext)
							item_props['furniture_place_desc'] = item_props['furniture_place_desc'].format(custom=customtext)
							item.str_name = item.str_name.format(custom = customtext)


					id_item = ewitem.item_create(
						item_type = item_type,
						id_user = cmd.message.author.id,
						id_server = cmd.guild.id,
						stack_max = 20 if item_type == ewcfg.it_weapon and ewcfg.weapon_class_thrown in item.classes else -1,
						stack_size = 1 if item_type == ewcfg.it_weapon and ewcfg.weapon_class_thrown in item.classes else 0,
						item_props = item_props
					)
					
					if value == 0:
						response = "You swipe a {} from the counter at {}.".format(item.str_name, current_vendor)
					else:
						response = "You slam {:,} {} down on the counter at {} for {}.".format(value, currency_used, current_vendor, item.str_name)

					if food_ordered and not togo:
						item_data = EwItem(id_item=id_item)

						# Eat food on the spot!
						if target_data != None:

							target_player_data = EwPlayer(id_user=target_data.id_user)
							
							if value == 0:
								response = "You swipe a {} from the counter at {} and give it to {}.".format(item.str_name, current_vendor, target_player_data.display_name)
							else:
								response = "You slam {:,} slime down on the counter at {} for {} and give it to {}.".format(value, current_vendor, item.str_name, target_player_data.display_name)

							response += "\n\n*{}*: ".format(target_player_data.display_name) + target_data.eat(item_data)
							target_data.persist()
							asyncio.ensure_future(ewutils.decrease_food_multiplier(user_data.id_user))
						else:
							
							if value == 0:
								response = "You swipe a {} from the counter at {} and eat it right on the spot.".format(item.str_name, current_vendor)
							else:
								response = "You slam {:,} slime down on the counter at {} for {} and eat it right on the spot.".format(value, current_vendor, item.str_name)

							user_player_data = EwPlayer(id_user=user_data.id_user)

							response += "\n\n*{}*: ".format(user_player_data.display_name) + user_data.eat(item_data)
							user_data.persist()
							asyncio.ensure_future(ewutils.decrease_food_multiplier(user_data.id_user))
							
					if premium_purchase:
						user_data.time_lastpremiumpurchase = int(time.time())

					user_data.persist()

		else:
			response = "Check the {} for a list of items you can {}.".format(ewcfg.cmd_menu, ewcfg.cmd_order)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
