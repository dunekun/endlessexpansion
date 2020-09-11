#import asyncio
import time
import ewutils

from ew import EwUser
#from ewplayer import EwPlayer

"""
	Prank items for Swilldermuk
"""
class EwPrankItem:
	item_type = "item"
	id_item = " "
	
	
	alias = []
	
	context = "prankitem"
	str_name = ""
	str_desc = ""
	
	prank_type = "" # Type of prank item. Can be an instant use, trap, or response item
	prank_desc = "" # A line of text that appears when the prank item gets used
	rarity = "" # Rarity of prank item. Used in determining how often it should spawn
	gambit = 0 # Gambit multiplier
	response_command = "" # All response items need a different command to break out of them
	response_desc_1 = "" # Response items contain additonal text which is indicative of how far the prank has progressed.
	response_desc_2 = ""
	response_desc_3 = ""
	response_desc_4 = ""
	trap_chance = 0 # All trap items only have a certain chance to activate
	trap_stored_credence = 0 # Trap items store half your current credence up front for later
	trap_user_id = "" # Trap items store your user id when you lay them down for later
	side_effect = "" # Some prank items have side-effects. Example: The 'bungis beam' will change a player's name to '[player name] (Bungis)'
	
	ingredients = ""
	acquisition = ""
	vendors = []

	def __init__(
		self,
		id_item=" ",
		alias = [],
		str_name = "",
		str_desc = "",
		prank_type = "",
		prank_desc = "",
		rarity = "",
		gambit = 0,
		response_command = "",
		response_desc_1 = "",
		response_desc_2 = "",
		response_desc_3 = "",
		response_desc_4 = "",
		trap_chance = 0,
		trap_stored_credence = 0,
		trap_user_id = "",
		side_effect = "",
		ingredients = "",
		acquisition = "",
		vendors = [],
	):
		self.item_type = "item"
		self.id_item = id_item
		self.alias = alias
		self.context = "prankitem"
		self.str_name = str_name
		self.str_desc = str_desc
		self.prank_type = prank_type
		self.prank_desc = prank_desc
		self.rarity = rarity
		self.gambit = gambit
		self.response_command = response_command
		self.response_desc_1 = response_desc_1
		self.response_desc_2 = response_desc_2
		self.response_desc_3 = response_desc_3
		self.response_desc_4 = response_desc_4
		self.trap_chance = trap_chance
		self.trap_stored_credence = trap_stored_credence
		self.trap_user_id = trap_user_id
		self.side_effect = side_effect
		self.ingredients = ingredients
		self.acquisition = acquisition
		self.vendors = vendors
		
# A bit of a hack, but at the time I couldn't really import ewcfg without causing other issues, so here these go. 
# It's really the only place they get used anyways.

#SWILLDERMUK
col_id_user_pranker = 'id_user_pranker'
col_id_user_pranked = 'id_user_pranked'
col_prank_count = 'prank_count'
col_id_server = 'id_server'
		
class PrankIndex:
	id_server = -1
	id_user_pranker = -1
	id_user_pranked = -1
	prank_count = 0 # How many times has user 1 (pranker) pranked user 2 (pranked)?
	
	def __init__(
		self,
		id_server = -1,
		id_user_pranker = -1,
		id_user_pranked = -1,
		prank_count = 0,
	):
		self.id_server = id_server
		self.id_user_pranker = id_user_pranker
		self.id_user_pranked = id_user_pranked
		self.prank_count = prank_count

		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Retrieve object
			cursor.execute("SELECT {count} FROM swilldermuk_prank_index WHERE {id_user_pranker} = %s AND {id_user_pranked} = %s AND {id_server} = %s".format(
				count=col_prank_count,
				id_user_pranker=col_id_user_pranker,
				id_user_pranked=col_id_user_pranked,
				id_server=col_id_server,
			), (
				self.id_user_pranker,
				self.id_user_pranked,
				self.id_server,
			))
			result = cursor.fetchone();

			if result != None:
				# Record found: apply the data to this object.
				self.prank_count = result[0]

		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

	def persist(self):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Save the object.
			cursor.execute(
				"REPLACE INTO swilldermuk_prank_index({}, {}, {}, {}) VALUES(%s, %s, %s, %s)".format(
					col_id_server,
					col_id_user_pranker,
					col_id_user_pranked,
					col_prank_count,
				), (
					self.id_server,
					self.id_user_pranker,
					self.id_user_pranked,
					self.prank_count,
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)
			
response_timer = 6 # How long does it take for a response item to send out its attacks
afk_timer = 60 * 60 * 2 # 2 hours

# Use an instant use item
async def prank_item_effect_instantuse(cmd, item):
	item_action= ""
	mentions_user = False
	use_mention_displayname = False
	side_effect = ""
	
	if cmd.mentions_count == 1:
		mentions_user = True
		
	if mentions_user:
		member = cmd.mentions[0]
		
		pranker_data = EwUser(member=cmd.message.author)
		pranked_data = EwUser(member=member)
		
		if pranker_data.id_user == pranked_data.id_user:
			response = "A bit masochistic, don't you think?"
			return item_action, response, use_mention_displayname, side_effect
		
		if pranked_data.time_last_action < (int(time.time()) - afk_timer):
			response = "Whoa whoa WHOA! Slow down there, big guy, this person's practically asleep! Where's the fun in pranking them right now, when you won't even be able to get a reaction out of them?\n**(Hint: {} is AFK! Try pranking someone else.)**".format(member.display_name)
			return item_action, response, use_mention_displayname, side_effect
		
		if pranker_data.poi != pranked_data.poi:
			response = "You need to be in the same place as your target to prank them with that item."
			return item_action, response, use_mention_displayname, side_effect

		# if pranker_data.credence == 0 or pranked_data.credence == 0:
		# 	if pranker_data.credence == 0:
		# 
		# 		response = "You can't prank that person right now, you don't have any credence!"
		# 	else:
		# 		response = "You can't prank that person right now, they don't have any credence!"
		# 
		# 	return item_action, response, use_mention_displayname, side_effect
		
		if (ewutils.active_restrictions.get(pranker_data.id_user) != None and ewutils.active_restrictions.get(pranker_data.id_user) == 2) or (ewutils.active_restrictions.get(pranked_data.id_user) != None and ewutils.active_restrictions.get(pranked_data.id_user) == 2):
			response = "You can't prank that person right now."
			return item_action, response, use_mention_displayname, side_effect
		
		prank_item_data = item
		
		#calculate_gambit_exchange(pranker_data, pranked_data, prank_item_data)
		
		response = prank_item_data.item_props.get('prank_desc')
		
		side_effect = prank_item_data.item_props.get('side_effect')
		
		response = response.format(cmd.message.author.display_name)
		item_action = "delete"
		use_mention_displayname = True
	else:
		response = "You gotta find someone to prank someone with that item, first!\n**(Hint: !use item @player)**"
	
	return item_action, response, use_mention_displayname, side_effect

# Use a response item
async def prank_item_effect_response(cmd, item):
	item_action = ""
	mentions_user = False
	use_mention_displayname = False
	side_effect = ""
	
	if cmd.mentions_count == 1:
		mentions_user = True

	if mentions_user:
		member = cmd.mentions[0]

		pranker_data = EwUser(member=cmd.message.author)
		pranked_data = EwUser(member=member)
		
		if pranker_data.id_user == pranked_data.id_user:
			response = "A bit masochistic, don't you think?"
			return item_action, response, use_mention_displayname, side_effect
		
		if pranked_data.time_last_action < (int(time.time()) - afk_timer):
			response = "Whoa whoa WHOA! Slow down there, big guy, this person's practically asleep! Where's the fun in pranking them right now, when you won't even be able to get a reaction out of them?\n**(Hint: {} is AFK! Try pranking someone else.)**".format(member.display_name)
			return item_action, response, use_mention_displayname, side_effect
		
		if pranker_data.poi != pranked_data.poi:
			response = "You need to be in the same place as your target to prank them with that item."
			return item_action, response, use_mention_displayname, side_effect
		
		# if pranker_data.credence == 0 or pranked_data.credence == 0:
		# 	if pranker_data.credence == 0:
		# 		
		# 		response = "You can't prank that person right now, you don't have any credence!"
		# 	else:
		# 		response = "You can't prank that person right now, they don't have any credence!"
		# 		
		# 	return item_action, response, use_mention_displayname, side_effect
		
		if (ewutils.active_restrictions.get(pranker_data.id_user) != None and ewutils.active_restrictions.get(pranker_data.id_user) == 2) or (ewutils.active_restrictions.get(pranked_data.id_user) != None and ewutils.active_restrictions.get(pranked_data.id_user) == 2):
			response = "You can't prank that person right now."
			return item_action, response, use_mention_displayname, side_effect

		prank_item_data = item

		response = prank_item_data.item_props.get('prank_desc')
		extra_response_1 = prank_item_data.item_props.get('response_desc_1')
		extra_response_2 = prank_item_data.item_props.get('response_desc_2')
		extra_response_3 = prank_item_data.item_props.get('response_desc_3')
		extra_response_4 = prank_item_data.item_props.get('response_desc_4')
		
		possible_responses_list = [
			response,
			extra_response_1,
			extra_response_2,
			extra_response_3,
			extra_response_4,
		]

		# response = response.format(cmd.message.author.display_name)
		
		# Apply restrictions, stop both users in their tracks
		# Restriction level 2 -- No one else can prank you at this time.
		ewutils.active_target_map[pranker_data.id_user] = pranked_data.id_user
		ewutils.active_target_map[pranked_data.id_user] = pranker_data.id_user
		ewutils.moves_active[pranker_data.id_user] = 0
		ewutils.moves_active[pranked_data.id_user] = 0
		ewutils.active_restrictions[pranker_data.id_user] = 2 
		ewutils.active_restrictions[pranked_data.id_user] = 2
		
		# The command needed to remove the response item
		response_command = prank_item_data.item_props.get('response_command')

		use_mention_displayname = True

		# The pranked person has 5 chances to type in the proper command before more and more gambit builds up
		limit = 0
		accepted = 0
		has_escaped = False
		has_escaped_fast = False
		while limit < 6:
			
			limit += 1

			if limit != 6:
				chosen_response = possible_responses_list[limit - 1]
				
				# Some response item messages wont have formatting in them.
				try:
					chosen_response = chosen_response.format(cmd.message.author.display_name)
				except:
					pass
				
				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage((cmd.message.author if use_mention_displayname == False else cmd.mentions[0]), chosen_response))
				#prank_feed_channel = ewutils.get_channel(cmd.guild, 'prank-feed')
				#await ewutils.send_message(cmd.client, prank_feed_channel, ewutils.formatMessage((cmd.message.author if use_mention_displayname == False else cmd.mentions[0]), (chosen_response+"\n`-------------------------`")))

				# The longer time goes on without the pranked person typing in the command, the more gambit they lose
				pranker_data = EwUser(member=cmd.message.author)
				pranked_data = EwUser(member=member)
				
				#calculate_gambit_exchange(pranker_data, pranked_data, prank_item_data, limit)
	
				accepted = 0
				try:
					msg = await cmd.client.wait_for('message', timeout=response_timer,check=lambda message: message.author == member)
	
					if msg != None:
						if msg.content.lower() == "!" + response_command:
							accepted = 1
							
							if limit != 5:
								has_escaped = True
								# if limit == 1:
								# 	has_escaped_fast = True
								
							limit = 6
				except:
					accepted = 0
			
		if accepted == 1 and has_escaped:
			response = "You manage to resist {}'s prank efforts for now.".format(cmd.message.author.display_name)
			# if has_escaped_fast:
			# 	response = "You swiftly dodge {}'s prank attempt!".format(cmd.message.author.display_name)
			# 	limit = 7
		else:
			response = "It's over. The damage {} has done to you will stay with you until your death. Or at least for the rest of the week, whichever comes first.".format(cmd.message.author.display_name)

		pranker_data = EwUser(member=cmd.message.author)
		pranked_data = EwUser(member=member)
		
		#calculate_gambit_exchange(pranker_data, pranked_data, prank_item_data, limit)
		
		# Remove restrictions
		ewutils.active_target_map[pranker_data.id_user] = ""
		ewutils.active_target_map[pranked_data.id_user] = ""
		ewutils.active_restrictions[pranker_data.id_user] = 0
		ewutils.active_restrictions[pranked_data.id_user] = 0
		
		item_action = "delete"
	else:
		response = "You gotta find someone to prank someone with that item, first!\n**(Hint: !use item @player)**"

	return item_action, response, use_mention_displayname, side_effect

# Lay down a trap in a district.
async def prank_item_effect_trap(cmd, item):
	item_action = ""
	mentions_user = False
	use_mention_displayname = False
	side_effect = ""
	
	if cmd.mentions_count == 1:
		mentions_user = True

	if mentions_user:
		response = "You can't use that item on someone else! You gotta lay it down in a district!\n**(Hint: !use item)**"
	else:

		pranker_data = EwUser(member=cmd.message.author)

		# if pranker_data.credence == 0:
		# 	response = "You can't lay down a trap without any credence!"
		# 	return item_action, response, use_mention_displayname, side_effect

		# Store values inside the trap's item_props
		
		# halved_credence = int(pranker_data.credence / 2)
		# if halved_credence == 0:
		# 	halved_credence = 1
		# 
		# pranker_data.credence = halved_credence
		# pranker_data.credence_used += halved_credence

		#item.item_props["trap_stored_credence"] = halved_credence
		item.item_props["trap_stored_credence"] = 0
		item.item_props["trap_user_id"] = str(pranker_data.id_user)
		
		item.persist()
		pranker_data.persist()

		response = "You lay down a {}. Hopefully someone's dumb enough to fall for it.".format(item.item_props.get('item_name'))
		item_action = "drop"

	return item_action, response, use_mention_displayname, side_effect
