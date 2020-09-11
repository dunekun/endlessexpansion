import asyncio
import time
import random

import ewcfg
import ewutils

from ew import EwUser
from ewplayer import EwPlayer

class EwEventDef:
	event_type = ""
	
	str_event_start = ""
	str_event_end = ""

	def __init__(
		self,
		event_type = "",
		str_event_start = "",
		str_event_end = "",
	):
		self.event_type = event_type
		self.str_event_start = str_event_start
		self.str_event_end = str_event_end
		

class EwWorldEvent:
	id_event = -1
	id_server = -1
	event_type = ""
	time_activate = -1
	time_expir = -1

	event_props = None

	def __init__(
		self,
		id_event = None
	):
		if(id_event != None):
			self.id_event = id_event

			self.event_props = {}

			try:
				# Retrieve object
				result = ewutils.execute_sql_query("SELECT {}, {}, {}, {} FROM world_events WHERE id_event = %s".format(
					ewcfg.col_id_server,
					ewcfg.col_event_type,
					ewcfg.col_time_activate,
					ewcfg.col_time_expir,
				), (
					self.id_event,
				))

				if len(result) > 0:
					result = result[0]

					# Record found: apply the data to this object.
					self.id_server = result[0]
					self.event_type = result[1]
					self.time_activate = result[2]
					self.time_expir = result[3]

					# Retrieve additional properties
					props = ewutils.execute_sql_query("SELECT {}, {} FROM world_events_prop WHERE id_event = %s".format(
						ewcfg.col_name,
						ewcfg.col_value
					), (
						self.id_event,
					))

					for row in props:
						# this try catch is only necessary as long as extraneous props exist in the table
						try:
							self.event_props[row[0]] = row[1]
						except:
							ewutils.logMsg("extraneous event_prop row detected.")

				else:
					# Item not found.
					self.id_event = -1
			except:
				ewutils.logMsg("Error while retrieving world event {}".format(id_event))


	""" Save event data object to the database. """
	def persist(self):
		try:
			# Save the object.
			ewutils.execute_sql_query("REPLACE INTO world_events({}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s)".format(
				ewcfg.col_id_event,
				ewcfg.col_id_server,
				ewcfg.col_event_type,
				ewcfg.col_time_activate,
				ewcfg.col_time_expir,
			), (
				self.id_event,
				self.id_server,
				self.event_type,
				self.time_activate,
				self.time_expir,
			))

			# Remove all existing property rows.
			ewutils.execute_sql_query("DELETE FROM world_events_prop WHERE {} = %s".format(
				ewcfg.col_id_event
			), (
				self.id_event,
			))

			# Write out all current property rows.
			for name in self.event_props:
				ewutils.execute_sql_query("INSERT INTO world_events_prop({}, {}, {}) VALUES(%s, %s, %s)".format(
					ewcfg.col_id_event,
					ewcfg.col_name,
					ewcfg.col_value
				), (
					self.id_event,
					name,
					self.event_props[name]
				))
		except:
			ewutils.logMsg("Error while persisting world event {}".format(self.id_event))


def get_world_events(id_server = None, active_only = True):
	world_events = {}
	if id_server == None:
		return world_events

	time_now = int(time.time())
	query = "SELECT {col_id_event}, {col_event_type} FROM world_events WHERE id_server = %s"

	if active_only:
		query_suffix = " AND {col_time_activate} <= {time_now} AND ({col_time_expir} >= {time_now} OR {col_time_expir} < 0)"
		query += query_suffix

	data = ewutils.execute_sql_query(query.format(
		col_id_event = ewcfg.col_id_event,
		col_event_type = ewcfg.col_event_type,
		col_time_activate = ewcfg.col_time_activate,
		col_time_expir = ewcfg.col_time_expir,
		time_now = time_now,
	),(
		id_server,
	))

	for row in data:
		world_events[row[0]] = row[1]

	return world_events

def create_world_event(
	id_server = None,
	event_type = None,
	time_activate = -1,
	time_expir = -1,
	event_props = {}
):
	if id_server == None or event_type == None:
		return -1
	try:
		# Get database handles if they weren't passed.
		conn_info = ewutils.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		# Create the item in the database.

		cursor.execute("INSERT INTO world_events({}, {}, {}, {}) VALUES(%s, %s, %s, %s)".format(
			ewcfg.col_event_type,
			ewcfg.col_id_server,
			ewcfg.col_time_activate,
			ewcfg.col_time_expir,
		), (
			event_type,
			id_server,
			time_activate,
			time_expir
		))

		event_id = cursor.lastrowid
		conn.commit()

		if event_id > 0:
			# If additional properties are specified in the item definition or in this create call, create and persist them.
			event_inst = EwWorldEvent(id_event = event_id)

			event_inst.event_props.update(event_props)

			event_inst.persist()

			conn.commit()
	finally:
		# Clean up the database handles.
		cursor.close()
		ewutils.databaseClose(conn_info)


	return event_id

def delete_world_event(id_event):
	try:
		ewutils.execute_sql_query("DELETE FROM world_events WHERE {id_event} = %s".format(
			id_event = ewcfg.col_id_event,
		),(
			id_event,
		))
	except:
		ewutils.logMsg("Error while deleting world event {}".format(id_event))

async def event_tick_loop(id_server):
	# initialise void connections
	void_connections = get_void_connection_pois(id_server)
	void_poi = ewcfg.id_to_poi.get(ewcfg.poi_id_thevoid)
	for connection_poi in void_connections:
		# add the existing connections as neighbors for the void
		void_poi.neighbors[connection_poi] = ewcfg.travel_time_district
	for _ in range(3 - len(void_connections)):
		# create any missing connections
		create_void_connection(id_server)
	ewutils.logMsg("initialised void connections, current links are: {}".format(tuple(void_poi.neighbors.keys())))

	interval = ewcfg.event_tick_length
	while not ewutils.TERMINATE:
		await asyncio.sleep(interval)
		await event_tick(id_server)

async def event_tick(id_server):
	time_now = int(time.time())
	resp_cont = ewutils.EwResponseContainer(id_server = id_server)
	try:
		data = ewutils.execute_sql_query("SELECT {id_event} FROM world_events WHERE {time_expir} <= %s AND {time_expir} > 0 AND id_server = %s".format(
			id_event = ewcfg.col_id_event,
			time_expir = ewcfg.col_time_expir,
		),(
			time_now,
			id_server,
		))

		for row in data:
			event_data = EwWorldEvent(id_event = row[0])
			event_def = ewcfg.event_type_to_def.get(event_data.event_type)

			response = event_def.str_event_end if event_def else ""
			if event_data.event_type == ewcfg.event_type_minecollapse:
				user_data = EwUser(id_user = event_data.event_props.get('id_user'), id_server = id_server)
				if user_data.poi == event_data.event_props.get('poi'):

					player_data = EwPlayer(id_user=user_data.id_user)
					response = "*{}*: You have lost an arm and a leg in a mining accident. Tis but a scratch.".format(player_data.display_name)

					if random.randrange(4) == 0:
						response = "*{}*: Big John arrives just in time to save you from your mining accident!\nhttps://cdn.discordapp.com/attachments/431275470902788107/743629505876197416/mine2.jpg".format(player_data.display_name)
					else:
						user_data.change_slimes(n = -(user_data.slimes * 0.5))
						user_data.persist()

					
			# check if any void connections have expired, if so pop it and create a new one
			elif event_data.event_type == ewcfg.event_type_voidconnection:
				void_poi = ewcfg.id_to_poi.get(ewcfg.poi_id_thevoid)
				void_poi.neighbors.pop(event_data.event_props.get('poi'), "")
				create_void_connection(id_server)
				
			if len(response) > 0:
				poi = event_data.event_props.get('poi')
				channel = event_data.event_props.get('channel')
				if channel != None:

					# in shambaquarium the event happens in the user's DMs
					if event_data.event_type == ewcfg.event_type_shambaquarium:
						client = ewutils.get_client()
						channel = client.get_guild(id_server).get_member(int(channel))

					resp_cont.add_channel_response(channel, response)
				elif poi != None:
					poi_def = ewcfg.id_to_poi.get(poi)
					if poi_def != None:
						resp_cont.add_channel_response(poi_def.channel, response)

				else:
					for ch in ewcfg.hideout_channels:
						resp_cont.add_channel_response(ch, response)

			delete_world_event(event_data.id_event)

		await resp_cont.post()
					
	except:
		ewutils.logMsg("Error in event tick for server {}".format(id_server))

def create_void_connection(id_server): 
	existing_connections = get_void_connection_pois(id_server)
	new_connection_poi = random.choice([poi.id_poi for poi in ewcfg.poi_list 
		if poi.is_district 
		and not poi.is_gangbase 	
		and poi.id_poi != ewcfg.poi_id_thevoid
		and poi.id_poi not in existing_connections
	])

	# add the new connection's POI as a neighbor for the void
	void_poi = ewcfg.id_to_poi.get(ewcfg.poi_id_thevoid)
	void_poi.neighbors[new_connection_poi] = ewcfg.travel_time_district
	ewutils.logMsg("updated void connections, current links are: {}".format(tuple(void_poi.neighbors.keys())))

	time_now = int(time.time())
	event_props = { "poi": new_connection_poi }
	create_world_event(
		id_server = id_server,
		event_type = ewcfg.event_type_voidconnection,
		time_activate = time_now,
		time_expir = time_now + (60 * random.randrange(20, 60)), # 20 to 60 minutes
		event_props = event_props
	)

def get_void_connection_pois(id_server):
	# in hindsight, doing this in python using get_world_events would've been easier and more future-proof
	return sum(ewutils.execute_sql_query("SELECT {value} FROM world_events_prop WHERE {name} = 'poi' AND {id_event} IN (SELECT {id_event} FROM world_events WHERE {event_type} = %s AND {id_server} = %s)".format(
			value = ewcfg.col_value,
			name = ewcfg.col_name,
			id_event = ewcfg.col_id_event,
			event_type = ewcfg.col_event_type,
			id_server = ewcfg.col_id_server,
		),(
			ewcfg.event_type_voidconnection,
			id_server,
		)), ())