"""
	Commands for kingpins only.
"""
import ewitem
import ewutils
import ewcfg
import ewrolemgr
import ewmap
from ew import EwUser

"""
	Release the specified player from their commitment to their faction.
	Returns enlisted players to juvenile.
"""
async def pardon(cmd):
	user_data = EwUser(member = cmd.message.author)

	if user_data.life_state != ewcfg.life_state_kingpin:
		response = "Only the Rowdy Fucker {} and the Cop Killer {} can do that.".format(ewcfg.emote_rowdyfucker, ewcfg.emote_copkiller)
	else:
		member = None
		if cmd.mentions_count == 1:
			member = cmd.mentions[0]
			if member.id == cmd.message.author.id:
				member = None

		if member == None:
			response = "Who?"
		else:
			member_data = EwUser(member = member)
			member_data.unban(faction = user_data.faction)

			if member_data.faction == "":
				response = "{} has been allowed to join the {} again.".format(member.display_name, user_data.faction)
			else:
				faction_old = member_data.faction
				member_data.faction = ""

				if member_data.life_state == ewcfg.life_state_enlisted:
					member_data.life_state = ewcfg.life_state_juvenile
					member_data.weapon = -1

				response = "{} has been released from their association with the {}.".format(member.display_name, faction_old)

			member_poi = ewcfg.id_to_poi.get(member_data.poi)
			if ewmap.inaccessible(user_data = member_data, poi = member_poi):
				member_data.poi = ewcfg.poi_id_downtown
			member_data.persist()
			await ewrolemgr.updateRoles(client = cmd.client, member = member)

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def banish(cmd):
	user_data = EwUser(member = cmd.message.author)

	if user_data.life_state != ewcfg.life_state_kingpin:
		response = "Only the Rowdy Fucker {} and the Cop Killer {} can do that.".format(ewcfg.emote_rowdyfucker, ewcfg.emote_copkiller)
	else:
		member = None
		if cmd.mentions_count == 1:
			member = cmd.mentions[0]
			if member.id == cmd.message.author.id:
				member = None

		if member == None:
			response = "Who?"
		else:
			member_data = EwUser(member = member)
			member_data.ban(faction = user_data.faction)
			member_data.unvouch(faction = user_data.faction)

			if member_data.faction == user_data.faction:
				member_data.faction = ""
				if member_data.life_state == ewcfg.life_state_enlisted:
					member_data.life_state = ewcfg.life_state_juvenile

			member_poi = ewcfg.id_to_poi.get(member_data.poi)
			if ewmap.inaccessible(user_data = member_data, poi = member_poi):
				member_data.poi = ewcfg.poi_id_downtown
			member_data.persist()
			response = "{} has been banned from enlisting in the {}".format(member.display_name, user_data.faction)
			await ewrolemgr.updateRoles(client = cmd.client, member = member)

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

""" Destroy a megaslime of your own for lore reasons. """
async def deadmega(cmd):
	response = ""
	user_data = EwUser(member = cmd.message.author)

	if user_data.life_state != ewcfg.life_state_kingpin:
		response = "Only the Rowdy Fucker {} and the Cop Killer {} can do that.".format(ewcfg.emote_rowdyfucker, ewcfg.emote_copkiller)
	else:
		value = 1000000
		user_slimes = 0

		if value > user_data.slimes:
			response = "You don't have that much slime to lose ({:,}/{:,}).".format(user_data.slimes, value)
		else:
			user_data.change_slimes(n = -value)
			user_data.persist()
			response = "Alas, poor megaslime. You have {:,} slime remaining.".format(user_data.slimes)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

"""
	Command that creates a princeps cosmetic item
"""
async def create(cmd):
	#if not cmd.message.author.guild_permissions.administrator:
	if EwUser(member = cmd.message.author).life_state != ewcfg.life_state_kingpin:
		response = 'Lowly Non-Kingpins cannot hope to create items with their bare hands.'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if len(cmd.tokens) != 4:
		response = 'Usage: !create "<item_name>" "<item_desc>" <recipient>'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	item_name = cmd.tokens[1]
	item_desc = cmd.tokens[2]

	if cmd.mentions[0]:
		recipient = cmd.mentions[0]
	else:
		response = 'You need to specify a recipient. Usage: !create "<item_name>" "<item_desc>" <recipient>'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	item_props = {
		"cosmetic_name": item_name,
		"cosmetic_desc": item_desc,
		"adorned": "false",
		"rarity": "princeps"
	}

	new_item_id = ewitem.item_create(
		id_server = cmd.guild.id,
		id_user = recipient.id,
		item_type = ewcfg.it_cosmetic,
		item_props = item_props
	)

	ewitem.soulbind(new_item_id)

	response = 'Item "{}" successfully created.'.format(item_name)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

"""
	Command that grants someone a specific cosmetic for an event.
"""
# async def exalt(cmd):
# 	author = cmd.message.author
# 	user_data = EwUser(member=author)
# 
# 	if not author.guild_permissions.administrator and user_data.life_state != ewcfg.life_state_kingpin:
# 		response = "You do not have the power within you worthy of !exalting another player."
# 		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 
# 	if cmd.mentions_count > 0:
# 		recipient = cmd.mentions[0]
# 	else:
# 		response = 'You need to specify a recipient. Usage: !exalt @[recipient].'
# 		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 	
# 	recipient_data = EwUser(member=recipient)
# 	
# 	DOUBLE HALLOWEEN
# 
# 	# Gather the Medallion
# 	medallion_results = []
# 	for m in ewcfg.cosmetic_items_list:
# 		if m.ingredients == 'HorsemanSoul':
# 			medallion_results.append(m)
# 		else:
# 			pass
# 
# 	medallion = medallion_results[0]
# 	medallion_props = ewitem.gen_item_props(medallion)
# 
# 	medallion_id = ewitem.item_create(
# 		item_type=medallion.item_type,
# 		id_user=recipient.id,
# 		id_server=cmd.guild.id,
# 		item_props=medallion_props
# 	)
# 
# 	# Soulbind the medallion. A player can get at most twice, but later on a new command could be added to destroy them/trade them in.
# 	# I imagine this would be something similar to how players can destroy Australium Wrenches in TF2, which broadcasts a message to everyone in the game, or something.
# 	ewitem.soulbind(medallion_id)
# 
# 	response = "**{} has been gifted the Double Halloween Medallion!!**\n".format(recipient.display_name)
# 	
# 	SWILLDERMUK
# 	
# 	if recipient_data.gambit > 0:
# 		# Give the user the Janus Mask
# 
# 		mask_results = []
# 		for m in ewcfg.cosmetic_items_list:
# 			if m.ingredients == 'SwilldermukFinalGambit':
# 				mask_results.append(m)
# 			else:
# 				pass
# 
# 		mask = mask_results[0]
# 		mask_props = ewitem.gen_item_props(mask)
# 
# 		mask_id = ewitem.item_create(
# 			item_type=mask.item_type,
# 			id_user=recipient.id,
# 			id_server=cmd.guild.id,
# 			item_props=mask_props
# 		)
# 
# 		ewitem.soulbind(mask_id)
# 
# 		response = "In light of their supreme reign over Swilldermuk, and in honor of their pranking prowess, {} recieves the Janus Mask!".format(recipient.display_name)
# 
# 	else:
# 		# Give the user the Sword of Seething
# 		sword_results = []
# 		for s in ewcfg.item_list:
# 			if s.context == 'swordofseething':
# 				sword_results.append(s)
# 			else:
# 				pass
# 
# 		sword = sword_results[0]
# 		sword_props = ewitem.gen_item_props(sword)
# 
# 		sword_id = ewitem.item_create(
# 			item_type=sword.item_type,
# 			id_user=recipient.id,
# 			id_server=cmd.guild.id,
# 			item_props=sword_props
# 		)
# 
# 		ewitem.soulbind(sword_id)
# 
# 		response = "In response to their unparalleled ability to let everything go to shit and be the laughingstock of all of NLACakaNM, {} recieves the SWORD OF SEETHING! God help us all...".format(recipient.display_name)
# 
# 	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
