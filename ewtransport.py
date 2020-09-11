import asyncio
import time

import ewutils
import ewcfg
import ewmap
import ewrolemgr

from ew import EwUser
from ewdistrict import EwDistrict


"""
	Database Object for public transportation vehicles, such as ferries or subway trains
"""
class EwTransport:
	# server id
	id_server = -1

	# id of the EwPoi object for this transport
	poi = ""

	# string describing the kind of vehicle it is
	transport_type = ""

	# which line the vehicle follows. see EwTransportLine object
	current_line = ""

	# connection to the world map
	current_stop = ""

	""" Retrieve object from database, or initialize it, if it doesn't exist yet """
	def __init__(self, id_server = None, poi = None):
		if id_server is not None and poi is not None:
			self.id_server = id_server
			self.poi = poi
			try:
				data = ewutils.execute_sql_query("SELECT {transport_type}, {current_line}, {current_stop} FROM transports WHERE {id_server} = %s AND {poi} = %s".format(
						transport_type = ewcfg.col_transport_type,
						current_line = ewcfg.col_current_line,
						current_stop = ewcfg.col_current_stop,
						id_server = ewcfg.col_id_server,
						poi = ewcfg.col_poi
					),(
						self.id_server,
						self.poi
					))
				# Retrieve data if the object was found
				if len(data) > 0:
					self.transport_type = data[0][0]
					self.current_line = data[0][1]
					self.current_stop = data[0][2]
				# initialize it per the Poi default otherwise
				else:
					poi_data = ewcfg.id_to_poi.get(self.poi)
					if poi_data is not None:
						self.transport_type = poi_data.transport_type
						self.current_line = poi_data.default_line
						self.current_stop = poi_data.default_stop

						self.persist()
			except:
				ewutils.logMsg("Failed to retrieve transport {} from database.".format(self.poi))

	""" Write object to database """
	def persist(self):

		try:
			ewutils.execute_sql_query("REPLACE INTO transports ({id_server}, {poi}, {transport_type}, {current_line}, {current_stop}) VALUES (%s, %s, %s, %s, %s)".format(
					id_server = ewcfg.col_id_server,
					poi = ewcfg.col_poi,
					transport_type = ewcfg.col_transport_type,
					current_line = ewcfg.col_current_line,
					current_stop = ewcfg.col_current_stop
				),(
					self.id_server,
					self.poi,
					self.transport_type,
					self.current_line,
					self.current_stop
				))
		except:
			ewutils.logMsg("Failed to write transport {} to database.".format(self.poi))

	""" Makes the object move across the world map. Called once at client startup for every object """
	async def move_loop(self):
		response = ""
		poi_data = ewcfg.id_to_poi.get(self.poi)
		last_messages = []
		while not ewutils.TERMINATE:

			district_data = EwDistrict(district = self.poi, id_server = self.id_server)

			if district_data.is_degraded():
				return

			transport_line = ewcfg.id_to_transport_line[self.current_line]
			client = ewutils.get_client()
			resp_cont = ewutils.EwResponseContainer(client = client, id_server = self.id_server)

			if self.current_stop == transport_line.last_stop:
				self.current_line = transport_line.next_line
				self.persist()
			else:
				schedule = transport_line.schedule[self.current_stop]
				await asyncio.sleep(schedule[0])
				for message in last_messages:
					try:
						await message.delete()
						pass
					except:
						ewutils.logMsg("Failed to delete message while moving transport {}.".format(transport_line.str_name))
				self.current_stop = schedule[1]
				self.persist()

				stop_data = ewcfg.id_to_poi.get(self.current_stop)

				# announce new stop inside the transport
				# if stop_data.is_subzone:
				# 	stop_mother = ewcfg.id_to_poi.get(stop_data.mother_district)
				# 	response = "We have reached {}.".format(stop_mother.str_name)
				# else:
				response = "We have reached {}.".format(stop_data.str_name)

				next_line = transport_line

				if stop_data.is_transport_stop:
					response += " You may exit now."

				if stop_data.id_poi == transport_line.last_stop:
					next_line = ewcfg.id_to_transport_line[transport_line.next_line]
					response += " This {} will proceed on {}.".format(self.transport_type, next_line.str_name.replace("The", "the"))
				else:
					next_stop = ewcfg.id_to_poi.get(transport_line.schedule.get(stop_data.id_poi)[1])
					if next_stop.is_transport_stop:
						# if next_stop.is_subzone:
						# 	stop_mother = ewcfg.id_to_poi.get(next_stop.mother_district)
						# 	response += " The next stop is {}.".format(stop_mother.str_name)
						# else:
						response += " The next stop is {}.".format(next_stop.str_name)
				resp_cont.add_channel_response(poi_data.channel, response)

				# announce transport has arrived at the stop
				if stop_data.is_transport_stop:
					response = "{} has arrived. You may board now.".format(next_line.str_name)
					resp_cont.add_channel_response(stop_data.channel, response)
				elif self.transport_type == ewcfg.transport_type_ferry:
					response = "{} sails by.".format(next_line.str_name)
					resp_cont.add_channel_response(stop_data.channel, response)
				elif self.transport_type == ewcfg.transport_type_blimp:
					response = "{} flies overhead.".format(next_line.str_name)
					resp_cont.add_channel_response(stop_data.channel, response)


				last_messages = await resp_cont.post()


""" Object that defines a public transportation line """
class EwTransportLine:

	# name of the transport line
	id_line = ""

	# alternative names
	alias = []

	# Nice name for output
	str_name = ""

	# which stop the line starts at
	first_stop = ""

	# which stop the line ends at
	last_stop = ""

	# which line transports switch to after the last stop
	next_line = ""

	# how long to stay at each stop, and which stop follows
	schedule = {}

	def __init__(self,
		id_line = "",
		alias = [],
		str_name = "",
		first_stop = "",
		last_stop = "",
		next_line = "",
		schedule = {}
		):
		self.id_line = id_line
		self.alias = alias
		self.str_name = str_name
		self.first_stop = first_stop
		self.last_stop = last_stop
		self.next_line = next_line
		self.schedule = schedule


""" Starts movement of all transports. Called once at client startup """
async def init_transports(id_server = None):
	if id_server is not None:
		for poi in ewcfg.transports:
			transport_data = EwTransport(id_server = id_server, poi = poi)
			asyncio.ensure_future(transport_data.move_loop())

""" Returns a list of Poi IDs """
def get_transports_at_stop(id_server, stop):
	result = []
	try:
		data = ewutils.execute_sql_query("SELECT {poi} FROM transports WHERE {id_server} = %s AND {current_stop} = %s".format(
				poi = ewcfg.col_poi,
				id_server = ewcfg.col_id_server,
				current_stop = ewcfg.col_current_stop
			),(
				id_server,
				stop
			))
		for row in data:
			result.append(row[0])

	except:
		ewutils.logMsg("Failed to retrieve transports at stop {}.".format(stop))
	finally:
		return result

""" Enter a transport vehicle from a transport stop """
async def embark(cmd):
	# can only use movement commands in location channels
	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))

	user_data = EwUser(member = cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = cmd.guild.id)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = ""

	if ewutils.active_restrictions.get(user_data.id_user) != None and ewutils.active_restrictions.get(user_data.id_user) > 0:
		response = "You can't do that right now."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.get_inhabitee():
		# prevent ghosts currently inhabiting other players from moving on their own
		response = "You might want to **{}** of the poor soul you've been tormenting first.".format(ewcfg.cmd_letgo)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	#poi = ewmap.fetch_poi_if_coordless(cmd.message.channel.name)

	# must be at a transport stop to enter a transport
	if poi != None and poi.id_poi in ewcfg.transport_stops:
		transport_ids = get_transports_at_stop(id_server = user_data.id_server, stop = poi.id_poi)

		# can't embark, when there's no vehicles to embark on
		if len(transport_ids) == 0:
			response = "There are currently no transport vehicles to embark on here."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		# automatically embark on the only transport at the station, if no arguments were provided
		elif len(transport_ids) == 1 and cmd.tokens_count < 2:
			transport_data = EwTransport(id_server = user_data.id_server, poi = transport_ids[0])
			target_name = transport_data.current_line

		# get target name from command arguments
		else:
			target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])

		# report failure, if the vehicle to be boarded couldn't be ascertained
		if target_name == None or len(target_name) == 0:
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Which transport line?"))

		transport_line = ewcfg.id_to_transport_line.get(target_name)

		# report failure, if an invalid argument was given
		if transport_line == None:
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Never heard of it."))

		for transport_id in transport_ids:
			transport_data = EwTransport(id_server = user_data.id_server, poi = transport_id)

			# check if one of the vehicles at the stop matches up with the line, the user wants to board
			if transport_data.current_line == transport_line.id_line:
				last_stop_poi = ewcfg.id_to_poi.get(transport_line.last_stop)
				response = "Embarking on {}.".format(transport_line.str_name)
				# schedule tasks for concurrent execution
				message_task = asyncio.ensure_future(ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response)))
				wait_task = asyncio.ensure_future(asyncio.sleep(5))

				# Take control of the move for this player.
				ewmap.move_counter += 1
				move_current = ewutils.moves_active[cmd.message.author.id] = ewmap.move_counter
				await message_task
				await wait_task

				# check if the user entered another movement command while waiting for the current one to be completed
				if move_current == ewutils.moves_active[cmd.message.author.id]:
					user_data = EwUser(member = cmd.message.author)

					transport_data = EwTransport(id_server = user_data.id_server, poi = transport_id)

					# check if the transport is still at the same stop
					if transport_data.current_stop == poi.id_poi:
						user_data.poi = transport_data.poi
						user_data.persist()

						transport_poi = ewcfg.id_to_poi.get(transport_data.poi)

						response = "You enter the {}.".format(transport_data.transport_type)
						await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
						await user_data.move_inhabitants(id_poi = transport_data.poi)
						return await ewutils.send_message(cmd.client, ewutils.get_channel(cmd.guild, transport_poi.channel), ewutils.formatMessage(cmd.message.author, response))
					else:
						response = "The {} starts moving just as you try to get on.".format(transport_data.transport_type)
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		response = "There is currently no vehicle following that line here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	else:
		response = "No transport vehicles stop here. Try going to a subway station or a ferry port."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" Exit a transport vehicle into its current stop """
async def disembark(cmd):
	# can only use movement commands in location channels
	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))
	user_data = EwUser(member = cmd.message.author)
	response = ""
	resp_cont = ewutils.EwResponseContainer(client = cmd.client, id_server = user_data.id_server)

	# prevent ghosts currently inhabiting other players from moving on their own
	if user_data.get_inhabitee():
		response = "You might want to **{}** of the poor soul you've been tormenting first.".format(ewcfg.cmd_letgo)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	# can only disembark when you're on a transport vehicle
	elif user_data.poi in ewcfg.transports:
		transport_data = EwTransport(id_server = user_data.id_server, poi = user_data.poi)
		response = "{}ing.".format(cmd.tokens[0][1:].lower()).capitalize()

		stop_poi = ewcfg.id_to_poi.get(transport_data.current_stop)
		# if stop_poi.is_subzone:
		# 	stop_poi = ewcfg.id_to_poi.get(stop_poi.mother_district)

		if ewmap.inaccessible(user_data = user_data, poi = stop_poi):
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're not allowed to go there (bitch)."))

		# schedule tasks for concurrent execution
		message_task = asyncio.ensure_future(ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response)))
		wait_task = asyncio.ensure_future(asyncio.sleep(5))

		# Take control of the move for this player.
		ewmap.move_counter += 1
		move_current = ewutils.moves_active[cmd.message.author.id] = ewmap.move_counter
		await message_task
		await wait_task


		# check if the user entered another movement command while waiting for the current one to be completed
		if move_current != ewutils.moves_active[cmd.message.author.id]:
			return

		user_data = EwUser(member = cmd.message.author)
		transport_data = EwTransport(id_server = user_data.id_server, poi = transport_data.poi)

		# cancel move, if the user has left the transport while waiting for movement to be completed (e.g. by dying)
		if user_data.poi != transport_data.poi:
			return

		stop_poi = ewcfg.id_to_poi.get(transport_data.current_stop)

		# juvies can't swim
		if transport_data.current_stop == ewcfg.poi_id_slimesea and user_data.life_state != ewcfg.life_state_corpse:
			if user_data.life_state == ewcfg.life_state_kingpin:
				response = "You try to heave yourself over the railing as you're hit by a sudden case of sea sickness. You puke into the sea and sink back on deck."
				response = ewutils.formatMessage(cmd.message.author, response)
				return await ewutils.send_message(cmd.client, cmd.message.channel, response)
			user_data.poi = ewcfg.poi_id_slimesea
			user_data.trauma = ewcfg.trauma_id_environment
			die_resp = user_data.die(cause = ewcfg.cause_drowning)
			user_data.persist()
			resp_cont.add_response_container(die_resp)

			response = "{} jumps over the railing of the ferry and promptly drowns in the slime sea.".format(cmd.message.author.display_name)
			resp_cont.add_channel_response(channel = ewcfg.channel_slimesea, response = response)
			resp_cont.add_channel_response(channel = ewcfg.channel_ferry, response = response)
			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
		# they also can't fly
                
		elif transport_data.transport_type == ewcfg.transport_type_blimp and not stop_poi.is_transport_stop and user_data.life_state != ewcfg.life_state_corpse:
			user_mutations = user_data.get_mutations()
			if user_data.life_state == ewcfg.life_state_kingpin:
				response = "Your life flashes before your eyes, as you plummet towards your certain death. A lifetime spent being a piece of shit and playing videogames all day. You close your eyes and... BOING! You open your eyes again to see a crew of workers transporting the trampoline that broke your fall. You get up and dust yourself off, sighing heavily."
				response = ewutils.formatMessage(cmd.message.author, response)
				resp_cont.add_channel_response(channel = stop_poi.channel, response = response)
				user_data.poi = stop_poi.id_poi
				user_data.persist()
				await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
				return await resp_cont.post()
			
			elif ewcfg.mutation_id_lightasafeather in user_mutations:
				response = "With a running jump you launch yourself out of the blimp and begin falling to your soon-to-be demise... but then a strong updraft breaks your fall and you land unscathed. "
				response = ewutils.formatMessage(cmd.message.author, response)
				resp_cont.add_channel_response(channel = stop_poi.channel, response = response)
				user_data.poi = stop_poi.id_poi
				user_data.persist()
				await user_data.move_inhabitants(id_poi = stop_poi.id_poi)
				await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
				return await resp_cont.post()
			district_data = EwDistrict(id_server = user_data.id_server, district = stop_poi.id_poi)
			district_data.change_slimes(n = user_data.slimes)
			district_data.persist()
			user_data.poi = stop_poi.id_poi
			user_data.trauma = ewcfg.trauma_id_environment
			die_resp = user_data.die(cause = ewcfg.cause_falling)
			user_data.persist()
			resp_cont.add_response_container(die_resp)
			response = "SPLAT! A body collides with the asphalt with such force, that it is utterly annihilated, covering bystanders in blood and slime and guts."
			resp_cont.add_channel_response(channel = stop_poi.channel, response = response)
			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

		# update user location, if move successful
		else:
			# if stop_poi.is_subzone:
			# 	stop_poi = ewcfg.id_to_poi.get(stop_poi.mother_district)

			if ewmap.inaccessible(user_data = user_data, poi = stop_poi):
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're not allowed to go there (bitch)."))

			user_data.poi = stop_poi.id_poi
			user_data.persist()
			await user_data.move_inhabitants(id_poi = stop_poi.id_poi)
			response = "You enter {}".format(stop_poi.str_name)
			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
			await ewutils.send_message(cmd.client, ewutils.get_channel(cmd.guild, stop_poi.channel), ewutils.formatMessage(cmd.message.author, response))

			# SWILLDERMUK
			await ewutils.activate_trap_items(stop_poi.id_poi, user_data.id_server, user_data.id_user)
			
			return
		return await resp_cont.post()
	else:
		response = "You are not currently riding any transport."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def check_schedule(cmd):
	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))
	user_data = EwUser(member = cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)
	response = ""


	if poi.is_transport_stop:
		response = "The following public transit lines stop here:"
		for line in poi.transport_lines:
			line_data = ewcfg.id_to_transport_line.get(line)
			response += "\n-" + line_data.str_name
	elif poi.is_transport:
		transport_data = EwTransport(id_server = user_data.id_server, poi = poi.id_poi)
		transport_line = ewcfg.id_to_transport_line.get(transport_data.current_line)
		response = "This {} is following {}.".format(transport_data.transport_type, transport_line.str_name.replace("The", "the"))
	else:
		response = "There is no schedule to check here."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
