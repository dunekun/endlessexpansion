import asyncio
import math
import time
import random

import discord

import ewcfg
import ewstats
import ewutils
import ewitem
from ewmarket import EwMarket

from ew import EwUser
from ewstatuseffects import EwStatusEffect
from ewdistrict import EwDistrict

class EwMutationFlavor:

	# The mutation's name
	id_mutation = ""

	# String used to describe the mutation when you !data yourself
	str_describe_self = ""

	# String used to describe the mutation when you !data another player
	str_describe_other = ""

	# String used when you acquire the mutation
	str_acquire = ""

	def __init__(self,
		id_mutation = "",
		str_describe_self = "",
		str_describe_other = "",
		str_acquire = ""):

		self.id_mutation = id_mutation

		if str_describe_self == "":
			str_describe_self = "You have the {} mutation.".format(self.id_mutation)
		self.str_describe_self = str_describe_self

		if str_describe_other == "":
			str_describe_other = "They have the {} mutation.".format(self.id_mutation)
		self.str_describe_other = str_describe_other

		if str_acquire == "":
			str_acquire = "You have acquired the {} mutation.".format(self.id_mutation)
		self.str_acquire = str_acquire


class EwMutation:
	id_server = -1
	id_user = -1
	id_mutation = ""

	data = ""

	# unique id for every instance of a mutation. auto increments
	# a counter of -1 means the player doesn't have this mutation
	mutation_counter = -1

	""" Create a new EwMutation and optionally retrieve it from the database. """
	def __init__(self, id_user = None, id_server = None, id_mutation = None):
		# Retrieve the object from the database if the user is provided.
		if(id_user != None) and (id_server != None) and (id_mutation != None):
			self.id_server = id_server
			self.id_user = id_user
			self.id_mutation = id_mutation

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				# Retrieve object
				cursor.execute("SELECT {data}, {mutation_counter} FROM mutations WHERE id_user = %s AND id_server = %s AND {id_mutation} = %s".format(
					data = ewcfg.col_mutation_data,
					mutation_counter = ewcfg.col_mutation_counter,
					id_mutation = ewcfg.col_id_mutation
				), (
					id_user,
					id_server,
					id_mutation
				))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.data = result[0]
					self.mutation_counter = result[1]

			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save this mutation object to the database. """
	def persist(self):
	
		try:
			# Get database handles if they weren't passed.
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();


			# Save the object.
			cursor.execute("REPLACE INTO mutations(id_user, id_server, {id_mutation}, {data}, {mutation_counter}) VALUES(%s, %s, %s, %s, %s)".format(
					id_mutation = ewcfg.col_id_mutation,
					data = ewcfg.col_mutation_data,
					mutation_counter = ewcfg.col_mutation_counter
				), (
					self.id_user,
					self.id_server,
					self.id_mutation,
					self.data,
					self.mutation_counter
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

	def clear(self):
		try:
			ewutils.execute_sql_query("DELETE FROM mutations WHERE {mutation_counter} = %s".format(
					mutation_counter = ewcfg.col_mutation_counter
				),(
					self.mutation_counter
				))
		except:
			ewutils.logMsg("Failed to clear mutation {} for user {}.".format(self.id_mutation, self.id_user))

async def reroll_last_mutation(cmd):
	last_mutation_counter = -1
	last_mutation = ""
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	market_data = EwMarket(id_server = user_data.id_server)
	response = ""

	if cmd.message.channel.name != ewcfg.channel_slimeoidlab:
		response = "You require the advanced equipment at the Slimeoid Lab to modify your mutations."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	if user_data.life_state == ewcfg.life_state_corpse:
		response = "How do you expect to mutate without exposure to slime, dumbass?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	mutations = user_data.get_mutations()
	if len(mutations) == 0:
		response = "You have not developed any specialized mutations yet."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	for id_mutation in mutations:
		mutation_data = EwMutation(id_server = user_data.id_server, id_user = user_data.id_user, id_mutation = id_mutation)
		if mutation_data.mutation_counter > last_mutation_counter:
			last_mutation_counter = mutation_data.mutation_counter
			last_mutation = id_mutation

	reroll_fatigue = EwStatusEffect(id_status = ewcfg.status_rerollfatigue_id, user_data = user_data)

	poudrins_needed = int(1.5 ** int(reroll_fatigue.value))

	poudrins = ewitem.find_item_all(item_search = ewcfg.item_id_slimepoudrin, id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None, item_type_filter = ewcfg.it_item)

	poudrins_have = len(poudrins)

	if poudrins_have < poudrins_needed:
		response = "You need {} slime poudrin{} to replace a mutation, but you only have {}.".format(poudrins_needed, "" if poudrins_needed == 1 else "s", poudrins_have)

		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		for delete in range(poudrins_needed):
			ewitem.item_delete(id_item = poudrins.pop(0).get('id_item'))  # Remove Poudrins
		market_data.donated_poudrins += poudrins_needed
		market_data.persist()
		user_data.poudrin_donations += poudrins_needed
		user_data.persist()
		reroll_fatigue.value = int(reroll_fatigue.value) + 1
		reroll_fatigue.persist()

	mutation_data = EwMutation(id_server = user_data.id_server, id_user = user_data.id_user, id_mutation = last_mutation)
	new_mutation = random.choice(list(ewcfg.mutation_ids))
	while new_mutation in mutations:
		new_mutation = random.choice(list(ewcfg.mutation_ids))

	mutation_data.id_mutation = new_mutation
	mutation_data.time_lastuse = int(time.time())
	mutation_data.persist()

	response = "After several minutes long elevator descents, in the depths of some basement level far below the laboratory's lobby, you lay down on a reclined medical chair. A SlimeCorp employee finishes the novel length terms of service they were reciting and asks you if you have any questions. You weren’t listening so you just tell them to get on with it so you can go back to getting slime. They oblige.\nThey grab a butterfly needle and carefully stab you with it, draining some strangely colored slime from your bloodstream. Almost immediately, the effects of your last mutation fade away… but, this feeling of respite is fleeting. The SlimeCorp employee writes down a few notes, files away the freshly drawn sample, and soon enough you are stabbed with syringes. This time, it’s already filled with some bizarre, multi-colored serum you’ve never seen before. The effects are instantaneous. {}\nYou hand off {} of your hard-earned poudrins to the SlimeCorp employee for their troubles.".format(ewcfg.mutations_map[new_mutation].str_acquire, poudrins_needed)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def clear_mutations(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	market_data = EwMarket(id_server = user_data.id_server)
	response = ""
	if cmd.message.channel.name != ewcfg.channel_slimeoidlab:
		response = "You require the advanced equipment at the Slimeoid Lab to modify your mutations."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "How do you expect to mutate without exposure to slime, dumbass?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	mutations = user_data.get_mutations()
	if len(mutations) == 0:
		response = "You have not developed any specialized mutations yet."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poudrin = ewitem.find_item(item_search = "slimepoudrin", id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None, item_type_filter = ewcfg.it_item)

	if poudrin == None:
		response = "You need a slime poudrin to replace a mutation."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		ewitem.item_delete(id_item = poudrin.get('id_item'))  # Remove Poudrins
		market_data.donated_poudrins += 1
		market_data.persist()
		user_data.poudrin_donations += 1
		user_data.persist()

	user_data.clear_mutations()
	response = "After several minutes long elevator descents, in the depths of some basement level far below the laboratory's lobby, you lay down on a reclined medical chair. A SlimeCorp employee finishes the novel length terms of service they were reciting and asks you if you have any questions. You weren’t listening so you just tell them to get on with it so you can go back to getting slime. They oblige.\nThey grab a random used syringe with just a dash of black serum still left inside it. They carefully stab you with it, injecting the mystery formula into your bloodstream. Almost immediately, normalcy returns to your inherently abnormal life… your body returns to whatever might be considered normal for your species. You hand off one of your hard-earned poudrins to the SlimeCorp employee for their troubles."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
