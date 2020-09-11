import asyncio

import ewcfg
import ewutils
import ewitem

from ewitem import EwItem
from ew import EwUser

"""allow a juvie to join your gang"""
async def vouch(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = ""
	
	if user_data.faction == "":
		response = "You have to join a faction before you can vouch for anyone."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.mentions_count == 0:
		response = "Vouch for whom?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	member = cmd.mentions[0]
	vouchee_data = EwUser(member = member)

	if vouchee_data.faction == user_data.faction:
		response = "{} has already joined your faction.".format(member.display_name)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	vouchers = vouchee_data.get_vouchers()

	if user_data.faction in vouchers:
		response = "A member of your faction has already vouched for {}.".format(member.display_name)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	vouchee_data.vouch(faction = user_data.faction)

	response = "You place your undying trust in {}.".format(member.display_name)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

"""store items in a communal chest in your gang base"""
async def store(cmd):
	
	user_data = EwUser(member=cmd.message.author)
	response = ""

	poi = ewcfg.id_to_poi.get(user_data.poi)
	if poi.community_chest == None:
		response = "There is no community chest here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		if len(poi.factions) > 0 and user_data.faction not in poi.factions:
			response = "Get real, asshole. You haven't even enlisted into this gang yet, so it's not like they'd trust you with a key to their valubles."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

	item_sought = ewitem.find_item(item_search = item_search, id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None)
	
	if item_sought:
		item = EwItem(id_item = item_sought.get("id_item"))

		if not item.soulbound:
			if item.item_type == ewcfg.it_weapon:
				if user_data.weapon >= 0 and item.id_item == user_data.weapon:
					if user_data.weaponmarried:
						weapon = ewcfg.weapon_map.get(item.item_props.get("weapon_type"))
						response = "Your cuckoldry is appreciated, but your {} will always remain faithful to you.".format(item_sought.get('name'))
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
					else:
						user_data.weapon = -1
						user_data.persist()
				elif item.id_item == user_data.sidearm:
					user_data.sidearm = -1
					user_data.persist()

			if item.item_type == ewcfg.it_cosmetic:
				if "adorned" in item.item_props:
					item.item_props["adorned"] = "false"
				if "slimeoid" in item.item_props:
					item.item_props["slimeoid"] = "false"
			
			item.persist()
			ewitem.give_item(id_item = item.id_item, id_server = item.id_server, id_user = poi.community_chest)

			response = "You store your {} in the community chest.".format(item_sought.get("name"))

		else:
			response = "You can't {} soulbound items.".format(cmd.tokens[0])
	else:
		if item_search:
			response = "You don't have one"
		else:
			response = "{} which item? (check **!inventory**)".format(cmd.tokens[0])

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

"""retrieve items from a communal chest in your gang base"""
async def take(cmd):
	
	user_data = EwUser(member=cmd.message.author)
	response = ""

	poi = ewcfg.id_to_poi.get(user_data.poi)
	if poi.community_chest == None:
		response = "There is no community chest here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		if len(poi.factions) > 0 and user_data.faction not in poi.factions:
			response = "Get real, asshole. You haven't even enlisted into this gang yet, so it's not like they'd trust you with a key to their valubles."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

	item_sought = ewitem.find_item(item_search = item_search, id_user = poi.community_chest, id_server = cmd.guild.id if cmd.guild is not None else None)
	
	if item_sought:
		if item_sought.get('item_type') == ewcfg.it_food:
			food_items = ewitem.inventory(
				id_user = cmd.message.author.id,
				id_server = cmd.guild.id,
				item_type_filter = ewcfg.it_food
			)

			if len(food_items) >= user_data.get_food_capacity():
				response = "You can't carry any more food items."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		if item_sought.get('item_type') == ewcfg.it_weapon:
			weapons_held = ewitem.inventory(
				id_user = cmd.message.author.id,
				id_server = cmd.guild.id,
				item_type_filter = ewcfg.it_weapon
			)

			if user_data.life_state == ewcfg.life_state_corpse:
				response = "Ghosts can't hold weapons."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			elif len(weapons_held) >= user_data.get_weapon_capacity():
				response  = "You can't carry any more weapons."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
		ewitem.give_item(id_item = item_sought.get('id_item'), id_server = user_data.id_server, id_user = user_data.id_user)

		response = "You retrieve a {} from the community chest.".format(item_sought.get("name"))

	else:
		if item_search:
			response = "There isn't one here."
		else:
			response = "{} which item? (check **{}**)".format(cmd.tokens[0], ewcfg.cmd_communitychest)

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

