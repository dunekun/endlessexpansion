import sys
import traceback
import collections

import MySQLdb
import datetime
import time
import re
import random
import string
import asyncio
import math

import ewstats
import ewitem
import ewhunting
import ewrolemgr

import discord

import ewcfg
import ewwep
from ew import EwUser
from ewdistrict import EwDistrict
from ewplayer import EwPlayer
from ewhunting import EwEnemy, EwOperationData
from ewmarket import EwMarket
from ewstatuseffects import EwStatusEffect
from ewstatuseffects import EwEnemyStatusEffect
from ewitem import EwItem
#from ewprank import calculate_gambit_exchange

TERMINATE = False
DEBUG = False

db_pool = {}
db_pool_id = 0

# Map of user IDs to their course ID.
moves_active = {}

food_multiplier = {}

# Contains who players are trading with and the state of the trades
active_trades = {}
# Contains the items being offered by players
trading_offers = {}

# Map of users to their target. This includes apartments, potential Russian Roulette players, potential Slimeoid Battle players, etc.
active_target_map = {}
# Map of users to their restriction level, typically in a mini-game. This prevents people from moving, teleporting, boarding, retiring, or suiciding in Russian Roulette/Duels
active_restrictions = {}


class Message:
	# Send the message to this exact channel by name.
	channel = None

	# Send the message to the channel associated with this point of interest.
	id_poi = None

	# Should this message echo to adjacent points of interest?
	reverb = None
	message = ""

	def __init__(
		self,
		channel = None,
		reverb = False,
		message = "",
		id_poi = None
	):
		self.channel = channel
		self.reverb = reverb
		self.message = message
		self.id_poi = id_poi

"""
	Class for storing, passing, editing and posting channel responses and topics
"""
class EwResponseContainer:
	client = None
	id_server = -1
	channel_responses = {}
	channel_topics = {}
	members_to_update = []

	def __init__(self, client = None, id_server = None):
		self.client = client
		self.id_server = id_server
		self.channel_responses = {}
		self.channel_topics = {}
		self.members_to_update = []

	def add_channel_response(self, channel, response):
		if channel in self.channel_responses:
			self.channel_responses[channel].append(response)
		else:
			self.channel_responses[channel] = [response]

	def add_channel_topic(self, channel, topic):
		self.channel_topics[channel] = topic

	def add_member_to_update(self, member):
		for update_member in self.members_to_update:
			if update_member.id == member.id:
				return

		self.members_to_update.append(member)

	def add_response_container(self, resp_cont):
		for ch in resp_cont.channel_responses:
			responses = resp_cont.channel_responses[ch]
			for r in responses:
				self.add_channel_response(ch, r)

		for ch in resp_cont.channel_topics:
			self.add_channel_topic(ch, resp_cont.channel_topics[ch])

		for member in resp_cont.members_to_update:
			self.add_member_to_update(member)

	def format_channel_response(self, channel, member):
		if channel in self.channel_responses:
			for i in range(len(self.channel_responses[channel])):
				self.channel_responses[channel][i] = formatMessage(member, self.channel_responses[channel][i])

	async def post(self, channel=None):
		self.client = get_client()
		messages = []

		if self.client == None:
			logMsg("Couldn't find client")
			return messages
			
		server = self.client.get_guild(self.id_server)
		if server == None:
			logMsg("Couldn't find server with id {}".format(self.id_server))
			return messages

		for member in self.members_to_update:
			await ewrolemgr.updateRoles(client = self.client, member = member)

		for ch in self.channel_responses:
			if channel == None:
				current_channel = get_channel(server = server, channel_name = ch)
				if current_channel == None:
					current_channel = ch
			else:
				current_channel = channel
			try:
				response = ""
				while len(self.channel_responses[ch]) > 0:
					if len(response) == 0 or len("{}\n{}".format(response, self.channel_responses[ch][0])) < ewcfg.discord_message_length_limit:
						response += "\n" + self.channel_responses[ch].pop(0)
					else:
						message = await send_message(self.client, current_channel, response)
						messages.append(message)
						response = ""
				message = await send_message(self.client, current_channel, response)
				messages.append(message)
			except:
				logMsg('Failed to send message to channel {}: {}'.format(ch, self.channel_responses[ch]))
				

		# for ch in self.channel_topics:
		# 	channel = get_channel(server = server, channel_name = ch)
		# 	try:
		# 		await channel.edit(topic = self.channel_topics[ch])
		# 	except:
		# 		logMsg('Failed to set channel topic for {} to {}'.format(ch, self.channel_topics[ch]))

		return messages

class EwVector2D:
	vector = [0, 0]

	def __init__(self, vector):
		self.vector = vector

	def scalar_product(self, other_vector):
		result = 0

		for i in range(2):
			result += self.vector[i] * other_vector.vector[i]

		return result

	def add(self, other_vector):
		result = []

		for i in range(2):
			result.append( self.vector[i] + other_vector.vector[i] )

		return EwVector2D(result)

	def subtract(self, other_vector):
		result = []

		for i in range(2):
			result.append( self.vector[i] - other_vector.vector[i] )

		return EwVector2D(result)

	def norm (self):
		result = self.scalar_product(self)
		result = result ** 0.5
		return result

	def normalize(self):
		result = []

		norm = self.norm()

		if norm == 0:
			return EwVector2D([0, 0])

		for i in range(2):
			result.append(round(self.vector[i] / norm, 3))

		return EwVector2D(result)

def readMessage(fname):
	msg = Message()

	try:
		f = open(fname, "r")
		f_lines = f.readlines()

		count = 0
		for line in f_lines:
			line = line.rstrip()
			count += 1
			if len(line) == 0:
				break

			args = line.split('=')
			if len(args) == 2:
				field = args[0].strip().lower()
				value = args[1].strip()

				if field == "channel":
					msg.channel = value.lower()
				elif field == "poi":
					msg.poi = value.lower()
				elif field == "reverb":
					msg.reverb = True if (value.lower() == "true") else False
			else:
				count -= 1
				break

		for line in f_lines[count:]:
			msg.message += (line.rstrip() + "\n")
	except:
		logMsg('failed to parse message.')
		traceback.print_exc(file = sys.stdout)
	finally:
		f.close()

	return msg

""" Write the string to stdout with a timestamp. """
def logMsg(string):
	print("[{}] {}".format(datetime.datetime.now(), string))

	return string

""" read a file named fname and return its contents as a string """
def getValueFromFileContents(fname):
	token = ""

	try:
		f_token = open(fname, "r")
		f_token_lines = f_token.readlines()

		for line in f_token_lines:
			line = line.rstrip()
			if len(line) > 0:
				token = line
	except IOError:
		token = ""
		print("Could not read {} file.".format(fname))
	finally:
		f_token.close()

	return token

""" get the Discord API token from the config file on disk """
def getToken():
	return getValueFromFileContents("token")

""" get the Twitch client ID from the config file on disk """
def getTwitchClientId():
	return getValueFromFileContents("twitch_client_id")

""" print a list of strings with nice comma-and grammar """
def formatNiceList(names = [], conjunction = "and"):
	l = len(names)

	if l == 0:
		return ''

	if l == 1:
		return names[0]
	
	return ', '.join(names[0:-1]) + '{comma} {conj} '.format(comma = (',' if l > 2 else ''), conj = conjunction) + names[-1]

def formatNiceTime(seconds = 0, round_to_minutes = False, round_to_hours = False):
	try:
		seconds = int(seconds)
	except:
		seconds = 0

	if round_to_minutes:
		minutes = round(seconds / 60)
	else:
		minutes = int(seconds / 60)

	if round_to_hours:
		hours = round(minutes / 60)
	else:
		hours = int(minutes / 60)

	minutes = minutes % 60
	seconds = seconds % 60
	time_tokens = []
	if hours > 0:
		if hours == 1:
			token_hours = "1 hour"
		else:
			token_hours = "{} hours".format(hours)
		time_tokens.append(token_hours)

	if round_to_hours:
		if len(time_tokens) == 0:
			time_tokens.append("0 hours")
		return formatNiceList(names = time_tokens, conjunction = "and")

	if minutes > 0:
		if minutes == 1:
			token_mins = "1 minute"
		else:
			token_mins = "{} minutes".format(minutes)
		time_tokens.append(token_mins)
	
	if round_to_minutes:
		if len(time_tokens) == 0:
			time_tokens.append("0 minutes")
		return formatNiceList(names = time_tokens, conjunction = "and")

	if seconds > 0:
		if seconds == 1:
			token_secs = "1 second"
		else:
			token_secs = "{} seconds".format(seconds)
		time_tokens.append(token_secs)

	if len(time_tokens) == 0:
		time_tokens.append("0 seconds")
	return formatNiceList(names = time_tokens, conjunction = "and")

""" weighted choice. takes a dict of element -> weight and returns a random element """
def weightedChoice(weight_map):
	weight_sum = 0
	elem_list = []
	weight_sums = []
	for elem in weight_map:
		weight_sum += weight_map.get(elem)
		elem_list.append(elem)
		weight_sums.append(weight_sum)

	rand = random.random() * weight_sum

	for i in range(len(weight_sums)):
		weight = weight_sums[i]
		if rand < weight:
			return elem_list[i]
	
""" turn a list of Users into a list of their respective names """
def userListToNameString(list_user):
	names = []

	for user in list_user:
		names.append(user.display_name)

	return formatNiceList(names)

""" turn a list of Roles into a map of name = >Role """
def getRoleMap(roles):
	roles_map = {}

	for role in roles:
		roles_map[mapRoleName(role.name)] = role

	return roles_map

""" turn a list of Roles into a map of id = >Role """
def getRoleIdMap(roles):
	roles_map = {}

	for role in roles:
		roles_map[mapRoleName(role.id)] = role

	return roles_map

""" canonical lowercase no space name for a role """
def mapRoleName(roleName):
	if type(roleName) == int:
		return roleName
	return roleName.replace(" ", "").lower()

""" connect to the database """
def databaseConnect():
	conn_info = None

	conn_id_todelete = []

	global db_pool
	global db_pool_id

	# Iterate through open connections and find the currently active one.
	for pool_id in db_pool:
		conn_info_iter = db_pool.get(pool_id)

		if conn_info_iter['closed'] == True:
			if conn_info_iter['count'] <= 0:
				conn_id_todelete.append(pool_id)
		else:
			conn_info = conn_info_iter

	# Close and remove dead connections.
	if len(conn_id_todelete) > 0:
		for pool_id in conn_id_todelete:
			conn_info_iter = db_pool[pool_id]
			conn_info_iter['conn'].close()

			del db_pool[pool_id]

	# Create a new connection.
	if conn_info == None:
		db_pool_id += 1
		conn_info = {
		'conn': MySQLdb.connect(host = "localhost", user = "rfck-bot", passwd = "rfck" , db = ewcfg.database, charset = "utf8"),
			'created': int(time.time()),
			'count': 1,
			'closed': False
		}
		db_pool[db_pool_id] = conn_info
	else:
		conn_info['count'] += 1

	return conn_info

""" close (maybe) the active database connection """
def databaseClose(conn_info):
	conn_info['count'] -= 1

	# Expire old database connections.
	if (conn_info['created'] + 60) < int(time.time()):
		conn_info['closed'] = True

""" format responses with the username: """
def formatMessage(user_target, message):
	# If the display name belongs to an unactivated raid boss, hide its name while it's counting down.
	try:
		if user_target.life_state == ewcfg.enemy_lifestate_alive:
			
			if user_target.enemyclass == ewcfg.enemy_class_gaiaslimeoid:
				return "**{} ({}):** {}".format(user_target.display_name, user_target.gvs_coord, message)
			else:
				# Send messages for normal enemies, and allow mentioning with @
				if user_target.identifier != '':
					return "**{} [{}] ({}):** {}".format(user_target.display_name, user_target.identifier, user_target.gvs_coord, message)
				else:
					return "**{}:** {}".format(user_target.display_name, message)

		elif user_target.display_name in ewcfg.raid_boss_names and user_target.life_state == ewcfg.enemy_lifestate_unactivated:
			return "{}".format(message)

	# If user_target isn't an enemy, catch the exception.
	except:
		return "*{}:* {}".format(user_target.display_name, message).replace("@", "{at}")

""" Decay slime totals for all users, with the exception of Kingpins"""
def decaySlimes(id_server = None):
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("SELECT id_user, life_state FROM users WHERE id_server = %s AND {slimes} > 1 AND NOT {life_state} = {life_state_kingpin}".format(
				slimes = ewcfg.col_slimes,
				life_state = ewcfg.col_life_state,
				life_state_kingpin = ewcfg.life_state_kingpin
			), (
				id_server,
			))

			users = cursor.fetchall()
			total_decayed = 0

			for user in users:
				user_data = EwUser(id_user = user[0], id_server = id_server)
				slimes_to_decay = user_data.slimes - (user_data.slimes * (.5 ** (ewcfg.update_market / ewcfg.slime_half_life)))

				#round up or down, randomly weighted
				remainder = slimes_to_decay - int(slimes_to_decay)
				if random.random() < remainder: 
					slimes_to_decay += 1 
				slimes_to_decay = int(slimes_to_decay)

				if slimes_to_decay >= 1:
					user_data.change_slimes(n = -slimes_to_decay, source = ewcfg.source_decay)
					user_data.persist()
					total_decayed += slimes_to_decay

			cursor.execute("SELECT district FROM districts WHERE id_server = %s AND {slimes} > 1".format(
				slimes = ewcfg.col_district_slimes
			), (
				id_server,
			))

			districts = cursor.fetchall()

			for district in districts:
				district_data = EwDistrict(district = district[0], id_server = id_server)
				slimes_to_decay = district_data.slimes - (district_data.slimes * (.5 ** (ewcfg.update_market / ewcfg.slime_half_life)))

				#round up or down, randomly weighted
				remainder = slimes_to_decay - int(slimes_to_decay)
				if random.random() < remainder: 
					slimes_to_decay += 1 
				slimes_to_decay = int(slimes_to_decay)

				if slimes_to_decay >= 1:
					district_data.change_slimes(n = -slimes_to_decay, source = ewcfg.source_decay)
					district_data.persist()
					total_decayed += slimes_to_decay

			cursor.execute("UPDATE markets SET {decayed} = ({decayed} + %s) WHERE {server} = %s".format(
				decayed = ewcfg.col_decayed_slimes,
				server = ewcfg.col_id_server
			), (
				total_decayed,
				id_server
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

"""
	Kills users who have left the server while the bot was offline
"""
def kill_quitters(id_server = None):
	if id_server != None:
		try:
			client = get_client()
			server = client.get_guild(id_server)
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND ( life_state > 0 OR slimes < 0 )".format(
			), (
				id_server,
			))

			users = cursor.fetchall()

			for user in users:
				member = server.get_member(user[0])

				# Make sure to kill players who may have left while the bot was offline.
				if member is None:
					try:
						user_data = EwUser(id_user = user[0], id_server = id_server)

						user_data.trauma = ewcfg.trauma_id_suicide
						user_data.die(cause=ewcfg.cause_leftserver)
						user_data.persist()

						logMsg('Player with id {} killed for leaving the server.'.format(user[0]))
					except:
						logMsg('Failed to kill member who left the server.')

		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

""" Flag all users in the Outskirts for PvP """
async def flag_outskirts(id_server = None):
	if id_server != None:
		try:
			client = get_client()
			server = client.get_guild(id_server)
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND poi IN %s".format(
			), (
				id_server,
				tuple(ewcfg.outskirts)

			))

			users = cursor.fetchall()

			for user in users:
				user_data = EwUser(id_user = user[0], id_server = id_server)
				# Flag the user for PvP
				enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
				user_data.time_expirpvp = calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_vulnerable_districts, enlisted)
				user_data.persist()
				await ewrolemgr.updateRoles(client = client, member = server.get_member(user_data.id_user))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

"""
	Flag all users in vulnerable territory, defined as capturable territory (streets) and outskirts.
"""
async def flag_vulnerable_districts(id_server = None):
	if id_server != None:
		try:
			client = get_client()
			server = client.get_guild(id_server)
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND poi IN %s".format(
			), (
				id_server,
				tuple(ewcfg.vulnerable_districts)

			))

			users = cursor.fetchall()

			for user in users:
				user_data = EwUser(id_user = user[0], id_server = id_server)
				member = server.get_member(user_data.id_user)

				# Flag the user for PvP
				enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
				user_data.time_expirpvp = calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_vulnerable_districts, enlisted)
				user_data.persist()
				
				await ewrolemgr.updateRoles(client = client, member = member, remove_or_apply_flag = 'apply')

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

"""
	Coroutine that continually calls bleedSlimes; is called once per server, and not just once globally
"""
async def bleed_tick_loop(id_server):
	interval = ewcfg.bleed_tick_length
	# causes a capture tick to happen exactly every 10 seconds (the "elapsed" thing might be unnecessary, depending on how long capture_tick ends up taking on average)
	while not TERMINATE:
		await bleedSlimes(id_server = id_server)
		await enemyBleedSlimes(id_server = id_server)
		# ewutils.logMsg("Capture tick happened on server %s." % id_server + " Timestamp: %d" % int(time.time()))

		await asyncio.sleep(interval)

""" Bleed slime for all users """
async def bleedSlimes(id_server = None):
	if id_server != None:
		try:
			client = get_client()
			server = client.get_guild(id_server)
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND {bleed_storage} > 1".format(
				bleed_storage = ewcfg.col_bleed_storage
			), (
				id_server,
			))

			users = cursor.fetchall()
			total_bled = 0
			deathreport = ""
			resp_cont = EwResponseContainer(id_server = id_server)
			for user in users:
				user_data = EwUser(id_user = user[0], id_server = id_server)
				member = server.get_member(user_data.id_user)
				
				slimes_to_bleed = user_data.bleed_storage * (
							1 - .5 ** (ewcfg.bleed_tick_length / ewcfg.bleed_half_life))
				slimes_to_bleed = max(slimes_to_bleed, ewcfg.bleed_tick_length * 1000)
				slimes_dropped = user_data.totaldamage + user_data.slimes

				trauma = ewcfg.trauma_map.get(user_data.trauma)
				bleed_mod = 1
				if trauma != None and trauma.trauma_class == ewcfg.trauma_class_bleeding:
					bleed_mod += 0.5 * user_data.degradation / 100

				# round up or down, randomly weighted
				remainder = slimes_to_bleed - int(slimes_to_bleed)
				if random.random() < remainder:
					slimes_to_bleed += 1
				slimes_to_bleed = int(slimes_to_bleed)

				slimes_to_bleed = min(slimes_to_bleed, user_data.bleed_storage)

				if slimes_to_bleed >= 1:

					real_bleed = round(slimes_to_bleed * bleed_mod)

					user_data.bleed_storage -= slimes_to_bleed
					user_data.change_slimes(n=- real_bleed, source=ewcfg.source_bleeding)

					district_data = EwDistrict(id_server=id_server, district=user_data.poi)
					district_data.change_slimes(n=real_bleed, source=ewcfg.source_bleeding)
					district_data.persist()

					if user_data.slimes < 0:
						user_data.trauma = ewcfg.trauma_id_environment
						die_resp = user_data.die(cause=ewcfg.cause_bleeding)
						# user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
						player_data = EwPlayer(id_server=user_data.id_server, id_user=user_data.id_user)
						resp_cont.add_response_container(die_resp)
					user_data.persist()

					total_bled += real_bleed

				await ewrolemgr.updateRoles(client=client, member=member)

			await resp_cont.post()

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)		

""" Bleed slime for all enemies """
async def enemyBleedSlimes(id_server = None):
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("SELECT id_enemy FROM enemies WHERE id_server = %s AND {bleed_storage} > 1".format(
				bleed_storage = ewcfg.col_enemy_bleed_storage
			), (
				id_server,
			))

			enemies = cursor.fetchall()
			total_bled = 0
			resp_cont = EwResponseContainer(id_server = id_server)
			for enemy in enemies:
				enemy_data = EwEnemy(id_enemy = enemy[0], id_server = id_server)
				slimes_to_bleed = enemy_data.bleed_storage * (1 - .5 ** (ewcfg.bleed_tick_length / ewcfg.bleed_half_life))
				slimes_to_bleed = max(slimes_to_bleed, ewcfg.bleed_tick_length * 1000)
				slimes_to_bleed = min(slimes_to_bleed, enemy_data.bleed_storage)

				district_data = EwDistrict(id_server = id_server, district = enemy_data.poi)

				#round up or down, randomly weighted
				remainder = slimes_to_bleed - int(slimes_to_bleed)
				if random.random() < remainder:
					slimes_to_bleed += 1
				slimes_to_bleed = int(slimes_to_bleed)

				if slimes_to_bleed >= 1:
					enemy_data.bleed_storage -= slimes_to_bleed
					enemy_data.change_slimes(n = - slimes_to_bleed, source = ewcfg.source_bleeding)
					enemy_data.persist()
					district_data.change_slimes(n = slimes_to_bleed, source = ewcfg.source_bleeding)
					district_data.persist()
					total_bled += slimes_to_bleed

					if enemy_data.slimes <= 0:
						ewhunting.delete_enemy(enemy_data)

			await resp_cont.post()
			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

""" Increase hunger for every player in the server. """
def pushupServerHunger(id_server = None):
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Save data
			cursor.execute("UPDATE users SET {hunger} = {hunger} + {tick} WHERE life_state > 0 AND id_server = %s AND hunger < {limit}".format(
				hunger = ewcfg.col_hunger,
				tick = ewcfg.hunger_pertick,
				# this function returns the bigger of two values; there is no simple way to do this in sql and we can't calculate it within this python script
				limit = "0.5 * (({val1} + {val2}) + ABS({val1} - {val2}))".format(
					val1 = ewcfg.min_stamina,
					val2 = "POWER(" + ewcfg.col_slimelevel + ", 2)"
				)
			), (
				id_server,
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

""" Reduce inebriation for every player in the server. """
def pushdownServerInebriation(id_server = None):
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Save data
			cursor.execute("UPDATE users SET {inebriation} = {inebriation} - {tick} WHERE id_server = %s AND {inebriation} > {limit}".format(
				inebriation = ewcfg.col_inebriation,
				tick = ewcfg.inebriation_pertick,
				limit = 0
			), (
				id_server,
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

"""
	Coroutine that continually calls burnSlimes; is called once per server, and not just once globally
"""
async def burn_tick_loop(id_server):
	interval = ewcfg.burn_tick_length
	while not TERMINATE:
		await burnSlimes(id_server = id_server)
		await enemyBurnSlimes(id_server = id_server)
		await asyncio.sleep(interval)

""" Burn slime for all users """
async def burnSlimes(id_server = None):
	if id_server != None:
		time_now = int(time.time())
		client = get_client()
		server = client.get_guild(id_server)
		status_origin = 'user'

		results = {}

		# Get users with harmful status effects
		data = execute_sql_query("SELECT {id_user}, {value}, {source}, {id_status} from status_effects WHERE {id_status} IN %s and {id_server} = %s".format(
			id_user = ewcfg.col_id_user,
			value = ewcfg.col_value,
			id_status = ewcfg.col_id_status,
			id_server = ewcfg.col_id_server,
			source = ewcfg.col_source
		), (
			tuple(ewcfg.harmful_status_effects),
			id_server
		))

		resp_cont = EwResponseContainer(id_server = id_server)
		for result in data:
			user_data = EwUser(id_user = result[0], id_server = id_server)
			member = server.get_member(user_data.id_user)

			slimes_dropped = user_data.totaldamage + user_data.slimes
			used_status_id = result[3]

			# Deal 10% of total slime to burn every second
			slimes_to_burn = math.ceil(int(float(result[1])) * ewcfg.burn_tick_length / ewcfg.time_expire_burn)

			# Check if a status effect originated from an enemy or a user.
			killer_data = EwUser(id_server=id_server, id_user=result[2])
			if killer_data == None:
				killer_data = EwEnemy(id_server=id_server, id_enemy=result[2])
				if killer_data != None:
					status_origin = 'enemy'
				else:
					# For now, skip over any status that did not originate from a user or an enemy. This might be changed in the future.
					continue
					
			if status_origin == 'user':
				# Damage stats
				ewstats.change_stat(user=killer_data, metric=ewcfg.stat_lifetime_damagedealt, n=slimes_to_burn)

			# Player died
			if user_data.slimes - slimes_to_burn < 0:
				weapon = ewcfg.weapon_map.get(ewcfg.weapon_id_molotov)

				player_data = EwPlayer(id_server=user_data.id_server, id_user=user_data.id_user)
				killer = EwPlayer(id_server=id_server, id_user=killer_data.id_user)
				poi = ewcfg.id_to_poi.get(user_data.poi)

				# Kill stats
				if status_origin == 'user':
					ewstats.increment_stat(user = killer_data, metric = ewcfg.stat_kills)
					ewstats.track_maximum(user = killer_data, metric = ewcfg.stat_biggest_kill, value = int(slimes_dropped))
	
					if killer_data.slimelevel > user_data.slimelevel:
						ewstats.increment_stat(user = killer_data, metric = ewcfg.stat_lifetime_ganks)
					elif killer_data.slimelevel < user_data.slimelevel:
						ewstats.increment_stat(user = killer_data, metric = ewcfg.stat_lifetime_takedowns)

					# Collect bounty
					coinbounty = int(user_data.bounty / ewcfg.slimecoin_exchangerate)  # 100 slime per coin
					
					if user_data.slimes >= 0:
						killer_data.change_slimecoin(n = coinbounty, coinsource = ewcfg.coinsource_bounty)

				# Kill player
				if status_origin == 'user':
					user_data.id_killer = killer_data.id_user
				elif status_origin == 'enemy':
					user_data.id_killer = killer_data.id_enemy
					
				user_data.trauma = ewcfg.trauma_id_environment
				die_resp = user_data.die(cause=ewcfg.cause_burning)
				# user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)

				resp_cont.add_response_container(die_resp)

				if used_status_id == ewcfg.status_burning_id:
					deathreport = "{} has burned to death.".format(player_data.display_name)
				elif used_status_id == ewcfg.status_acid_id:
					deathreport = "{} has been melted to death by acid.".format(player_data.display_name)
				elif used_status_id == ewcfg.status_spored_id:
					deathreport = "{} has been overrun by spores.".format(player_data.display_name)
				else:
					deathreport = ""
				resp_cont.add_channel_response(poi.channel, deathreport)

				user_data.trauma = weapon.id_weapon

				user_data.persist()
				await ewrolemgr.updateRoles(client=client, member=member)
			else:
				user_data.change_slimes(n=-slimes_to_burn, source=ewcfg.source_damage)
				user_data.persist()
				

		await resp_cont.post()	

async def enemyBurnSlimes(id_server):
	if id_server != None:
		time_now = int(time.time())
		client = get_client()
		server = client.get_guild(id_server)
		status_origin = 'user'

		results = {}

		# Get enemies with harmful status effects
		data = execute_sql_query("SELECT {id_enemy}, {value}, {source}, {id_status} from enemy_status_effects WHERE {id_status} IN %s and {id_server} = %s".format(
			id_enemy = ewcfg.col_id_enemy,
			value = ewcfg.col_value,
			id_status = ewcfg.col_id_status,
			id_server = ewcfg.col_id_server,
			source = ewcfg.col_source
		), (
			ewcfg.harmful_status_effects,
			id_server
		))

		resp_cont = EwResponseContainer(id_server = id_server)
		for result in data:
			enemy_data = EwEnemy(id_enemy = result[0], id_server = id_server)
			
			slimes_dropped = enemy_data.totaldamage + enemy_data.slimes
			used_status_id = result[3]

			# Deal 10% of total slime to burn every second
			slimes_to_burn = math.ceil(int(float(result[1])) * ewcfg.burn_tick_length / ewcfg.time_expire_burn)

			# Check if a status effect originated from an enemy or a user.
			killer_data = EwUser(id_server=id_server, id_user=result[2])
			if killer_data == None:
				killer_data = EwEnemy(id_server=id_server, id_enemy=result[2])
				if killer_data != None:
					status_origin = 'enemy'
				else:
					# For now, skip over any status that did not originate from a user or an enemy. This might be changed in the future.
					continue
			
			if status_origin == 'user':
				ewstats.change_stat(user = killer_data, metric = ewcfg.stat_lifetime_damagedealt, n = slimes_to_burn)

			if enemy_data.slimes - slimes_to_burn <= 0:
				ewhunting.delete_enemy(enemy_data)

				if used_status_id == ewcfg.status_burning_id:
					response = "{} has burned to death.".format(enemy_data.display_name)
				elif used_status_id == ewcfg.status_acid_id:
					response = "{} has been melted to death by acid.".format(enemy_data.display_name)
				elif used_status_id == ewcfg.status_spored_id:
					response = "{} has been overrun by spores.".format(enemy_data.display_name)
				else:
					response = ""
				resp_cont.add_channel_response(ewcfg.id_to_poi.get(enemy_data.poi).channel, response)
				
				district_data = EwDistrict(id_server = id_server, district = enemy_data.poi)
				resp_cont.add_response_container(ewhunting.drop_enemy_loot(enemy_data, district_data))
			else:
				enemy_data.change_slimes(n = -slimes_to_burn, source=ewcfg.source_damage)
				enemy_data.persist()
			
		await resp_cont.post()

async def remove_status_loop(id_server):
	interval = ewcfg.removestatus_tick_length
	while not TERMINATE:
		removeExpiredStatuses(id_server = id_server)
		enemyRemoveExpiredStatuses(id_server = id_server)
		await asyncio.sleep(interval)

""" Remove expired status effects for all users """
def removeExpiredStatuses(id_server = None):
	if id_server != None:
		time_now = int(time.time())

		#client = get_client()
		#server = client.get_server(id_server)

		statuses = execute_sql_query("SELECT {id_status},{id_user} FROM status_effects WHERE id_server = %s AND {time_expire} < %s".format(
			id_status = ewcfg.col_id_status,
			id_user = ewcfg.col_id_user,
			time_expire = ewcfg.col_time_expir
		), (
			id_server,
			time_now
		))

		for row in statuses:
			status = row[0]
			id_user = row[1]
			user_data = EwUser(id_user = id_user, id_server = id_server)
			status_def = ewcfg.status_effects_def_map.get(status)
			status_effect = EwStatusEffect(id_status=status, user_data = user_data)
	
			if status_def.time_expire > 0:
				if status_effect.time_expire < time_now:
					user_data.clear_status(id_status=status)

			# Status that expire under special conditions
			else:
				if status == ewcfg.status_stunned_id:
					if int(status_effect.value) < time_now:
						user_data.clear_status(id_status=status)
					
def enemyRemoveExpiredStatuses(id_server = None):
	if id_server != None:
		time_now = int(time.time())

		statuses = execute_sql_query("SELECT {id_status}, {id_enemy} FROM enemy_status_effects WHERE id_server = %s AND {time_expire} < %s".format(
			id_status = ewcfg.col_id_status,
			id_enemy = ewcfg.col_id_enemy,
			time_expire = ewcfg.col_time_expir
		), (
			id_server,
			time_now
		))

		for row in statuses:
			status = row[0]
			id_enemy = row[1]
			enemy_data = EwEnemy(id_enemy = id_enemy, id_server = id_server)
			status_def = ewcfg.status_effects_def_map.get(status)
			status_effect = EwEnemyStatusEffect(id_status=status, enemy_data = enemy_data)
	
			if status_def.time_expire > 0:
				if status_effect.time_expire < time_now:
					enemy_data.clear_status(id_status=status)

			# Status that expire under special conditions
			else:
				if status == ewcfg.status_stunned_id:
					if int(status_effect.value) < time_now:
						enemy_data.clear_status(id_status=status)

""" Parse a list of tokens and return an integer value. If allow_all, return -1 if the word 'all' is present. """
def getIntToken(tokens = [], allow_all = False, negate = False):
	value = None

	for token in tokens[1:]:
		try:
			value = int(token.replace(",", ""))
			if value < 0 and not negate:
				value = None
			elif value > 0 and negate:
				value = None
			elif negate:
				value = -value
			break
		except:
			if allow_all and ("{}".format(token)).lower() == 'all':
				return -1
			else:
				value = None

	return value

""" Get the map of weapon skills for the specified player. """
def weaponskills_get(id_server = None, id_user = None, member = None):
	weaponskills = {}

	if member != None:
		id_server = member.guild.id
		id_user = member.id

	if id_server != None and id_user != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("SELECT {weapon}, {weaponskill} FROM weaponskills WHERE {id_server} = %s AND {id_user} = %s".format(
				weapon = ewcfg.col_weapon,
				weaponskill = ewcfg.col_weaponskill,
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user
			), (
				id_server,
				id_user
			))

			data = cursor.fetchall()
			if data != None:
				for row in data:
					weaponskills[row[0]] = {
						'skill': row[1]
					}
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

	return weaponskills

""" Set an individual weapon skill value for a player. """
def weaponskills_set(id_server = None, id_user = None, member = None, weapon = None, weaponskill = 0):
	if member != None:
		id_server = member.guild.id
		id_user = member.id

	if id_server != None and id_user != None and weapon != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("REPLACE INTO weaponskills({id_server}, {id_user}, {weapon}, {weaponskill}) VALUES(%s, %s, %s, %s)".format(
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user,
				weapon = ewcfg.col_weapon,
				weaponskill = ewcfg.col_weaponskill
			), (
				id_server,
				id_user,
				weapon,
				weaponskill
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

""" Clear all weapon skills for a player (probably called on death). """
def weaponskills_clear(id_server = None, id_user = None, member = None, weaponskill = None):
	if member != None:
		id_server = member.guild.id
		id_user = member.id

	if id_server != None and id_user != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Clear any records that might exist.
			cursor.execute("UPDATE weaponskills SET {weaponskill} = %s WHERE {weaponskill} > %s AND {id_server} = %s AND {id_user} = %s".format(
				weaponskill = ewcfg.col_weaponskill,
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user
			), (
				weaponskill,
				weaponskill,
				id_server,
				id_user
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

re_flattener = re.compile("[ '\"!@#$%^&*().,/?{}\[\];:]")

"""
	Turn an array of tokens into a single word (no spaces or punctuation) with all lowercase letters.
"""
def flattenTokenListToString(tokens):
	global re_flattener
	target_name = ""

	if type(tokens) == list:
		for token in tokens:
			if token.startswith('<@') == False:
				target_name += re_flattener.sub("", token.lower())
	elif tokens.startswith('<@') == False:
		target_name = re_flattener.sub("", tokens.lower())

	return target_name


"""
	Execute a given sql_query. (the purpose of this function is to minimize repeated code and keep functions readable)
"""
def execute_sql_query(sql_query = None, sql_replacements = None):
	data = None

	try:
		conn_info = databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()
		cursor.execute(sql_query, sql_replacements)
		if sql_query.lower().startswith("select"):
			data = cursor.fetchall()
		conn.commit()
	finally:
		# Clean up the database handles.
		cursor.close()
		databaseClose(conn_info)

	return data


"""
	Send a message to multiple chat channels at once. "channels" can be either a list of discord channel objects or strings
"""
async def post_in_channels(id_server, message, channels = None):
	client = get_client()
	server = client.get_guild(id = id_server)

	if channels is None and server is not None:
		channels = server.channels

	for channel in channels:
		if type(channel) is str:  # if the channels are passed as strings instead of discord channel objects
			channel = get_channel(server, channel)
		if channel is not None and channel.type == discord.ChannelType.text:
			await channel.send(content=message)
	return

"""
	Find a chat channel by name in a server.
"""
def get_channel(server = None, channel_name = ""):
	channel = None

	for chan in server.channels:
		if chan.name == channel_name:
			channel = chan
	
	if channel == None:
		logMsg('Error: In get_channel(), could not find channel using channel_name "{}"'.format(channel_name))

	return channel

"""
	Return the role name of a user's faction. Takes user data object or life_state and faction tag
"""
def get_faction(user_data = None, life_state = 0, faction = ""):
	life_state = life_state
	faction = faction
	if user_data != None:
		life_state = user_data.life_state
		faction = user_data.faction

	faction_role = ewcfg.role_corpse

	if life_state == ewcfg.life_state_juvenile:
		faction_role = ewcfg.role_flatfreak

	elif life_state == ewcfg.life_state_enlisted:
		if faction == ewcfg.faction_milkers:
			faction_role = ewcfg.role_milker

		elif faction == ewcfg.faction_boober:
			faction_role = ewcfg.role_boober

		else:
			faction_role = ewcfg.role_flatfreak

	elif life_state == ewcfg.life_state_kingpin:
		faction_role = ewcfg.role_kingpin

	elif life_state == ewcfg.life_state_grandfoe:
		faction_role = ewcfg.role_grandfoe

	elif life_state == ewcfg.life_state_executive:
		faction_role = ewcfg.role_slimecorp

	elif life_state == ewcfg.life_state_lucky:
		faction_role = ewcfg.role_slimecorp
	
	elif life_state == ewcfg.life_state_shambler:
		faction_role = ewcfg.role_shambler

	return faction_role

def get_faction_symbol(faction = "", faction_raw = ""):
	result = None

	if faction == ewcfg.role_kingpin:
		if faction_raw == ewcfg.faction_boober:
			result = ewcfg.emote_rowdyfucker
		elif faction_raw == ewcfg.faction_milkers:
			result = ewcfg.emote_copkiller

	if result == None:
		if faction == ewcfg.role_corpse:
			result = ewcfg.emote_ghost
		elif faction == ewcfg.role_flatfreak:
			result = ewcfg.emote_slime3
		elif faction == ewcfg.role_boober:
			result = ewcfg.emote_ck
		elif faction == ewcfg.role_milkers:
			result = ewcfg.emote_rf
		elif faction == ewcfg.role_shambler:
			result = ewcfg.emote_slimeskull
		else:
			result = ewcfg.emote_blank

	return result


"""
	Calculate the slime amount needed to reach a certain level
"""
def slime_bylevel(slimelevel):
	return int(slimelevel ** 4)


"""
	Calculate what level the player should be at, given their slime amount
"""
def level_byslime(slime):
	return int(abs(slime) ** 0.25)


"""
	Calculate the maximum sap amount a player can have at their given slime level
"""
def sap_max_bylevel(slimelevel):
	return int(1.6 * slimelevel ** 0.75)

"""
	Calculate the maximum hunger level at the player's slimelevel
"""
def hunger_max_bylevel(slimelevel):
	# note that when you change this formula, you'll also have to adjust its sql equivalent in pushupServerHunger
	return max(ewcfg.min_stamina, slimelevel ** 2)


"""
	Calculate how much more stamina activities should cost
"""
def hunger_cost_mod(slimelevel):
	return hunger_max_bylevel(slimelevel) / 200


"""
	Calculate how much food the player can carry
"""
def food_carry_capacity_bylevel(slimelevel):
	return math.ceil(slimelevel / ewcfg.max_food_in_inv_mod)
		
"""
	Calculate how many weapons the player can carry
"""
def weapon_carry_capacity_bylevel(slimelevel):
	return math.floor(slimelevel / ewcfg.max_weapon_mod) + 1

def max_adornspace_bylevel(slimelevel):
	if slimelevel < 4:
		adorn_space = 0
	else:
		adorn_space = math.floor(math.sqrt(slimelevel- 2) - 0.40)

	return adorn_space

"""
	Returns an EwUser object of the selected kingpin
"""
def find_kingpin(id_server, kingpin_role):
	data = execute_sql_query("SELECT id_user FROM users WHERE id_server = %s AND {life_state} = %s AND {faction} = %s".format(
		life_state = ewcfg.col_life_state,
		faction = ewcfg.col_faction
	), (
		id_server,
		ewcfg.life_state_kingpin,
		ewcfg.faction_boober if kingpin_role == ewcfg.role_bigboober else ewcfg.faction_milkers
	))

	kingpin = None

	if len(data) > 0:
		id_kingpin = data[0][0]
		kingpin = EwUser(id_server = id_server, id_user = id_kingpin)

	return kingpin


"""
	Posts a message both in CK and RR.
"""
async def post_in_hideouts(id_server, message):
	await post_in_channels(
		id_server = id_server,
		message = message,
		channels = [ewcfg.channel_copkilltown, ewcfg.channel_rowdyroughhouse]
	)

"""
	gets the discord client the bot is running on
"""
def get_client():
	return ewcfg.get_client()


"""
	Proxy to discord.py channel.send with exception handling.
"""
async def send_message(client, channel, text, delete_after=None):
	try:
		return await channel.send(content=text, delete_after=delete_after)
	except discord.errors.Forbidden:
		logMsg('Could not message user: {}\n{}'.format(channel, text))
		raise
	except:
		logMsg('Failed to send message to channel: {}\n{}'.format(channel, text))

"""
	Proxy to discord.py message.edit() with exception handling.
"""
async def edit_message(client, message, text):
	try:
		return await message.edit(content=str(text))
	except:
		logMsg('Failed to edit message. Updated text would have been:\n{}'.format(text))

"""
	Returns a list of slimeoid ids in the district
"""
def get_slimeoids_in_poi(id_server = None, poi = None, sltype = None):
	slimeoids = []
	if id_server is None:
		return slimeoids

	query = "SELECT {id_slimeoid} FROM slimeoids WHERE {id_server} = %s".format(
		id_slimeoid = ewcfg.col_id_slimeoid,
		id_server = ewcfg.col_id_server
	)

	if sltype is not None:
		query += " AND {} = '{}'".format(ewcfg.col_type, sltype)

	if poi is not None:
		query += " AND {} = '{}'".format(ewcfg.col_poi, poi)

	data = execute_sql_query(query,(
		id_server,
	))

	for row in data:
		slimeoids.append(row[0])

	return slimeoids

async def decrease_food_multiplier(id_user):
	await asyncio.sleep(5)
	if id_user in food_multiplier:
		food_multiplier[id_user] = max(0, food_multiplier.get(id_user) - 1)

async def spawn_enemies(id_server = None):
	if random.randrange(3) == 0:
		weathertype = ewcfg.enemy_weathertype_normal
		market_data = EwMarket(id_server=id_server)
		
		# If it's raining, an enemy has  2/3 chance to spawn as a bicarbonate enemy, which doesn't take rain damage
		if market_data.weather == ewcfg.weather_bicarbonaterain:
			if random.randrange(3) < 2:
				weathertype = ewcfg.enemy_weathertype_rainresist
		
		resp_cont = ewhunting.spawn_enemy(id_server=id_server, pre_chosen_weather=weathertype)

		await resp_cont.post()

async def spawn_enemies_tick_loop(id_server):
	interval = ewcfg.enemy_spawn_tick_length
	# Causes the possibility of an enemy spawning every 10 seconds
	while not TERMINATE:
		await asyncio.sleep(interval)
		await spawn_enemies(id_server = id_server)


async def enemy_action_tick_loop(id_server):
	interval = ewcfg.enemy_attack_tick_length
	# Causes hostile enemies to attack every tick.
	while not TERMINATE:
		await asyncio.sleep(interval)
		# resp_cont = EwResponseContainer(id_server=id_server)
		if ewcfg.gvs_active:
			await ewhunting.enemy_perform_action_gvs(id_server)
		else:
			await ewhunting.enemy_perform_action(id_server)
			
async def gvs_gamestate_tick_loop(id_server):
	interval = ewcfg.gvs_gamestate_tick_length
	# Causes various events to occur during a Garden or Graveyard ops in Gankers Vs. Shamblers
	while not TERMINATE:
		await asyncio.sleep(interval)
		await ewhunting.gvs_update_gamestate(id_server)


# Clears out id_target in enemies with defender ai. Primarily used for when players die or leave districts the defender is in.
def check_defender_targets(user_data, enemy_data):
	defending_enemy = EwEnemy(id_enemy=enemy_data.id_enemy)
	searched_user = EwUser(id_user=user_data.id_user, id_server=user_data.id_server)

	if (defending_enemy.poi != searched_user.poi) or (searched_user.life_state == ewcfg.life_state_corpse):
		defending_enemy.id_target = ""
		defending_enemy.persist()
		return False
	else:
		return True

def get_move_speed(user_data):
	time_now = int(time.time())
	mutations = user_data.get_mutations()
	statuses = user_data.getStatusEffects()
	market_data = EwMarket(id_server = user_data.id_server)
	trauma = ewcfg.trauma_map.get(user_data.trauma)
	move_speed = 1.05 ** user_data.speed

	if user_data.life_state == ewcfg.life_state_shambler:
		if market_data.weather == ewcfg.weather_bicarbonaterain:
			move_speed *= 2
		else:
			move_speed *= 0.5

	if ewcfg.status_injury_legs_id in statuses:
		status_data = EwStatusEffect(id_status = ewcfg.status_injury_legs_id, user_data = user_data)
		try:
			move_speed *= max(0, (1 - 0.2 * int(status_data.value) / 10))
		except:
			logMsg("failed int conversion while getting move speed for user {}".format(user_data.id_user))

	if (trauma != None) and (trauma.trauma_class == ewcfg.trauma_class_movespeed):
		move_speed *= max(0, (1 - 0.5 * user_data.degradation / 100))

	if ewcfg.mutation_id_organicfursuit in mutations and check_fursuit_active(user_data.id_server):
		move_speed *= 2
	if ewcfg.mutation_id_lightasafeather in mutations and market_data.weather == "windy":
		move_speed *= 2
	if ewcfg.mutation_id_fastmetabolism in mutations and user_data.hunger / user_data.get_hunger_max() < 0.4:
		move_speed *= 1.33
		
	#move_speed *= 2

	move_speed = max(0.1, move_speed)

	return move_speed


""" Damage all players in a district """
def explode(damage = 0, district_data = None, market_data = None):
	id_server = district_data.id_server
	poi = district_data.name

	if market_data == None:
		market_data = EwMarket(id_server = district_data.id_server)

	client = get_client()
	server = client.get_guild(id_server)

	resp_cont = EwResponseContainer(id_server = id_server)
	response = ""
	channel = ewcfg.id_to_poi.get(poi).channel

	life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_executive, ewcfg.life_state_shambler]
	users = district_data.get_players_in_district(life_states = life_states, pvp_only = True)

	enemies = district_data.get_enemies_in_district()

	# damage players
	for user in users:
		user_data = EwUser(id_user = user, id_server = id_server, data_level = 1)
		mutations = user_data.get_mutations()

		user_weapon = None
		user_weapon_item = None
		if user_data.weapon >= 0:
			user_weapon_item = EwItem(id_item = user_data.weapon)
			user_weapon = ewcfg.weapon_map.get(user_weapon_item.item_props.get("weapon_type"))

		# apply defensive mods
		slimes_damage_target = damage * ewwep.damage_mod_defend(
			shootee_data = user_data,
			shootee_mutations = mutations,
			shootee_weapon = user_weapon,
			market_data = market_data
		)

		# apply sap armor
		sap_armor = ewwep.get_sap_armor(shootee_data = user_data, sap_ignored = 0)
		slimes_damage_target *= sap_armor
		slimes_damage_target = int(max(0, slimes_damage_target))

		player_data = EwPlayer(id_user = user_data.id_user)
		response = "{} is blown back by the explosion’s sheer force! They lose {:,} slime!!".format(player_data.display_name, slimes_damage_target)
		resp_cont.add_channel_response(channel, response)
		slimes_damage = slimes_damage_target
		if user_data.slimes < slimes_damage + user_data.bleed_storage:
			# die in the explosion
			district_data.change_slimes(n = user_data.slimes, source = ewcfg.source_killing)
			district_data.persist()
			slimes_dropped = user_data.totaldamage + user_data.slimes

			user_data.trauma = ewcfg.trauma_id_environment
			user_data.die(cause = ewcfg.cause_killing)
			#user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
			user_data.persist()

			response = "Alas, {} was caught too close to the blast. They are consumed by the flames, and die in the explosion.".format(player_data.display_name)
			resp_cont.add_channel_response(channel, response)

			resp_cont.add_member_to_update(server.get_member(user_data.id_user))
		else:
			# survive
			slime_splatter = 0.5 * slimes_damage
			district_data.change_slimes(n = slime_splatter, source = ewcfg.source_killing)
			district_data.persist()
			slimes_damage -= slime_splatter
			user_data.bleed_storage += slimes_damage
			user_data.change_slimes(n = -slime_splatter, source = ewcfg.source_killing)
			user_data.persist()

	# damage enemies
	for enemy in enemies:
		enemy_data = EwEnemy(id_enemy = enemy, id_server = id_server)

		response = "{} is blown back by the explosion’s sheer force! They lose {:,} slime!!".format(enemy_data.display_name, damage)
		resp_cont.add_channel_response(channel, response)

		slimes_damage_target = damage
			
		# apply sap armor
		sap_armor = ewwep.get_sap_armor(shootee_data = enemy_data, sap_ignored = 0)
		slimes_damage_target *= sap_armor
		slimes_damage_target = int(max(0, slimes_damage_target))

		slimes_damage = slimes_damage_target
		if enemy_data.slimes < slimes_damage + enemy_data.bleed_storage:
			# die in the explosion
			district_data.change_slimes(n = enemy_data.slimes, source = ewcfg.source_killing)
			district_data.persist()
			# slimes_dropped = enemy_data.totaldamage + enemy_data.slimes
			# explode_damage = ewutils.slime_bylevel(enemy_data.level)

			response = "Alas, {} was caught too close to the blast. They are consumed by the flames, and die in the explosion.".format(enemy_data.display_name)
			resp_cont.add_response_container(ewhunting.drop_enemy_loot(enemy_data, district_data))
			resp_cont.add_channel_response(channel, response)

			enemy_data.life_state = ewcfg.enemy_lifestate_dead
			enemy_data.persist()

		else:
			# survive
			slime_splatter = 0.5 * slimes_damage
			district_data.change_slimes(n = slime_splatter, source = ewcfg.source_killing)
			district_data.persist()
			slimes_damage -= slime_splatter
			enemy_data.bleed_storage += slimes_damage
			enemy_data.change_slimes(n = -slime_splatter, source = ewcfg.source_killing)
			enemy_data.persist()
	return resp_cont

def is_otp(user_data):
	poi = ewcfg.id_to_poi.get(user_data.poi)
	return user_data.poi not in [ewcfg.poi_id_thesewers, ewcfg.poi_id_juviesrow, ewcfg.poi_id_copkilltown, ewcfg.poi_id_rowdyroughhouse] and (not poi.is_apartment)


async def delete_last_message(client, last_messages, tick_length):
	if len(last_messages) == 0:
		return
	await asyncio.sleep(tick_length)
	try:
		msg = last_messages[-1]
		await msg.delete()
		pass
	except:
		logMsg("failed to delete last message")

def check_accept_or_refuse(string):
	if string.content.lower() == ewcfg.cmd_accept or string.content.lower() == ewcfg.cmd_refuse:
		return True

def check_confirm_or_cancel(string):
	if string.content.lower() == ewcfg.cmd_confirm or string.content.lower() == ewcfg.cmd_cancel:
		return True
	
def check_trick_or_treat(string):
	if string.content.lower() == ewcfg.cmd_treat or string.content.lower() == ewcfg.cmd_trick:
		return True
	
def check_is_command(string):
	if string.content.startswith(ewcfg.cmd_prefix):
		return True
	
def end_trade(id_user):
	# Cancel an ongoing trade
	if active_trades.get(id_user) != None and len(active_trades.get(id_user)) > 0:
		trader = active_trades.get(id_user).get("trader")
		
		active_trades[id_user] = {}
		active_trades[trader] = {}
		
		trading_offers[trader] = []
		trading_offers[id_user] = []

def text_to_regional_indicator(text):
	# note that inside the quotes below is a zero-width space, 
	# used to prevent the regional indicators from turning into flags
	# also note that this only works for digits and english letters
  
	###return "‎".join([chr(0x1F1E6 + string.ascii_uppercase.index(c)) for c in text.upper()])
	return "‎".join([c + '\ufe0f\u20e3' if c.isdigit() else chr(0x1F1E6 + string.ascii_uppercase.index(c)) for c in text.upper()])

def generate_captcha_random(length = 4):
	return "".join([random.choice(ewcfg.alphabet) for _ in range(length)]).upper()

def generate_captcha(length = 4):
	try:
		return random.choice([captcha for captcha in ewcfg.captcha_dict if len(captcha) == length])
	except:
		return generate_captcha_random(length)

async def sap_tick_loop(id_server):
	interval = ewcfg.sap_tick_length
	# causes a capture tick to happen exactly every 10 seconds (the "elapsed" thing might be unnecessary, depending on how long capture_tick ends up taking on average)
	while not TERMINATE:
		await asyncio.sleep(interval)
		sap_tick(id_server)

def sap_tick(id_server):

	try:
		users = execute_sql_query("SELECT {id_user} FROM users WHERE {id_server} = %s AND {life_state} > 0 AND {sap} + {hardened_sap} < {level}".format(
			id_user = ewcfg.col_id_user,
			life_state = ewcfg.col_life_state,
			sap = ewcfg.col_sap,
			hardened_sap = ewcfg.col_hardened_sap,
			level = ewcfg.col_slimelevel,
			id_server = ewcfg.col_id_server,
		),(
			id_server,
		))

		for user in users:
			user_data = EwUser(id_user = user[0], id_server = id_server)
			trauma = ewcfg.trauma_map.get(user_data.trauma)
			sap_chance = 1
			if trauma != None and trauma.trauma_class == ewcfg.trauma_class_sapregeneration:
				sap_chance -= 0.5 * user_data.degradation / 100

			if random.random() < sap_chance:
				user_data.sap += 1

			user_data.limit_fix()
			user_data.persist()

		enemies = execute_sql_query("SELECT {id_enemy} FROM enemies WHERE {id_server} = %s AND {hardened_sap} < {level} / 2".format(
			id_enemy = ewcfg.col_id_enemy,
			hardened_sap = ewcfg.col_enemy_hardened_sap,
			level = ewcfg.col_enemy_level,
			id_server = ewcfg.col_id_server,
		),(
			id_server,
		))

		for enemy in enemies:
			if random.random() < 0.5:
				enemy_data = EwEnemy(id_enemy = enemy[0])
				enemy_data.hardened_sap += 1
				enemy_data.persist()
	except:
		logMsg("An error occured in sap tick for server {}".format(id_server))
		
async def spawn_prank_items_tick_loop(id_server):
	#DEBUG
	# interval = 10
	
	# If there are more active people, items spawn more frequently, and less frequently if there are less active people.
	interval = 180
	new_interval = 0
	while not TERMINATE:
		if new_interval > 0:
			interval = new_interval
			
		#print("newinterval:{}".format(new_interval))
		
		await asyncio.sleep(interval)
		new_interval = await spawn_prank_items(id_server = id_server)

async def spawn_prank_items(id_server):
	new_interval = 0
	base_interval = 60
	
	try:
		active_users_count = 0

		if id_server != None:
			try:
				conn_info = databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				cursor.execute(
					"SELECT id_user FROM users WHERE id_server = %s AND {poi} in %s AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin}) AND {time_last_action} > %s".format(
						life_state=ewcfg.col_life_state,
						poi=ewcfg.col_poi,
						life_state_corpse=ewcfg.life_state_corpse,
						life_state_kingpin=ewcfg.life_state_kingpin,
						time_last_action=ewcfg.col_time_last_action,
					), (
						id_server,
						ewcfg.capturable_districts,
						(int(time.time()) - ewcfg.time_kickout),
					))

				users = cursor.fetchall()

				active_users_count = len(users)

				conn.commit()
			finally:
				# Clean up the database handles.
				cursor.close()
				databaseClose(conn_info)
		
		# Avoid division by 0
		if active_users_count == 0:
			active_users_count = 1
		else:
			#print(active_users_count)
			pass
		
		new_interval = (math.ceil(base_interval/active_users_count) * 5) # 5 active users = 1 minute timer, 10 = 30 second timer, and so on.
		
		district_id = random.choice(ewcfg.capturable_districts)
		
		#Debug
		#district_id = 'wreckington'
		
		district_channel_name = ewcfg.id_to_poi.get(district_id).channel
		
		client = get_client()
		
		server = client.get_guild(id_server)
	
		district_channel = get_channel(server=server, channel_name=district_channel_name)
		
		pie_or_prank = random.randrange(3)
		
		if pie_or_prank == 0:
			swilldermuk_food_item = random.choice(ewcfg.swilldermuk_food)

			item_props = ewitem.gen_item_props(swilldermuk_food_item)

			swilldermuk_food_item_id = ewitem.item_create(
				item_type=swilldermuk_food_item.item_type,
				id_user=district_id,
				id_server=id_server,
				item_props=item_props
			)

			#print('{} with id {} spawned in {}!'.format(swilldermuk_food_item.str_name, swilldermuk_food_item_id, district_id))

			response = "That smell... it's unmistakeable!! Someone's left a fresh {} on the ground!".format(swilldermuk_food_item.str_name)
			await send_message(client, district_channel, response)
		else:
			rarity_roll = random.randrange(10)
			
			if rarity_roll > 3:
				prank_item = random.choice(ewcfg.prank_items_heinous)
			elif rarity_roll > 0:
				prank_item = random.choice(ewcfg.prank_items_scandalous)
			else:
				prank_item = random.choice(ewcfg.prank_items_forbidden)
				
			#Debug
			#prank_item = ewcfg.prank_items_heinous[1] # Chinese Finger Trap
		
			item_props = ewitem.gen_item_props(prank_item)
		
			prank_item_id = ewitem.item_create(
				item_type=prank_item.item_type,
				id_user=district_id,
				id_server=id_server,
				item_props=item_props
			)
		
			# print('{} with id {} spawned in {}!'.format(prank_item.str_name, prank_item_id, district_id))
	
			response = "An ominous wind blows through the streets. You think you hear someone drop a {} on the ground nearby...".format(prank_item.str_name)
			await send_message(client, district_channel, response)

	except:
		logMsg("An error occured in spawn prank items tick for server {}".format(id_server))
		
	return new_interval
		
async def generate_credence_tick_loop(id_server):
	# DEBUG
	# interval = 10
	
	while not TERMINATE:
		interval = (random.randrange(121) + 120)  # anywhere from 2-4 minutes
		await asyncio.sleep(interval)
		await generate_credence(id_server)
		
async def generate_credence(id_server):
	#print("CREDENCE GENERATED")
	
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();
	
			cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND {poi} in %s AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin}) AND {time_last_action} > %s".format(
				life_state = ewcfg.col_life_state,
				poi = ewcfg.col_poi,
				life_state_corpse = ewcfg.life_state_corpse,
				life_state_kingpin = ewcfg.life_state_kingpin,
				time_last_action = ewcfg.col_time_last_action,
			), (
				id_server,
				ewcfg.capturable_districts,
				(int(time.time()) - ewcfg.time_afk_swilldermuk),
			))
	
			users = cursor.fetchall()
	
			for user in users:
				user_data = EwUser(id_user = user[0], id_server = id_server)
				added_credence = 0
				lowered_credence_used = 0
				
				if user_data.credence >= 1000:
					added_credence = 1 + random.randrange(5)
				elif user_data.credence >= 500:
					added_credence = 10 + random.randrange(41)
				elif user_data.credence >= 100:
					added_credence = 25 + random.randrange(76)
				else:
					added_credence = 50 + random.randrange(151)
					
				if user_data.credence_used > 0:
					lowered_credence_used = int(user_data.credence_used/10)
					
					if lowered_credence_used == 1:
						lowered_credence_used = 0
						
					user_data.credence_used = lowered_credence_used
					
				added_credence = max(0, added_credence - lowered_credence_used)
				user_data.credence += added_credence
					
				user_data.persist()
				
	
			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)
			
async def activate_trap_items(district, id_server, id_user):
	# Return if --> User has 0 credence, there are no traps, or if the trap setter is the one who entered the district.
	#print("TRAP FUNCTION")
	trap_was_dud = False
	
	user_data = EwUser(id_user=id_user, id_server=id_server)
	# if user_data.credence == 0:
	# 	#print('no credence')
	# 	return
	
	if user_data.life_state == ewcfg.life_state_corpse:
		#print('get out ghosts reeeee!')
		return
	
	try:
		conn_info = databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor();

		district_channel_name = ewcfg.id_to_poi.get(district).channel

		client = get_client()

		server = client.get_guild(id_server)
		
		member = server.get_member(id_user)

		district_channel = get_channel(server=server, channel_name=district_channel_name)
		
		searched_id = district + '_trap'
		
		cursor.execute("SELECT id_item, id_user FROM items WHERE id_user = %s AND id_server = %s".format(
			id_item = ewcfg.col_id_item,
			id_user = ewcfg.col_id_user
		), (
			searched_id,
			id_server,
		))

		traps = cursor.fetchall()
		
		if len(traps) == 0:
			#print('no traps')
			return
		
		trap_used = traps[0]
		
		trap_id_item = trap_used[0]
		#trap_id_user = trap_used[1]
		
		trap_item_data = EwItem(id_item=trap_id_item)
		
		trap_chance = int(trap_item_data.item_props.get('trap_chance'))
		trap_user_id = trap_item_data.item_props.get('trap_user_id')
		
		if int(trap_user_id) == user_data.id_user:
			#print('trap same user id')
			return
		
		if random.randrange(101) < trap_chance:
			# Trap was triggered!
			pranker_data = EwUser(id_user=int(trap_user_id), id_server=id_server)
			pranked_data = user_data

			response = trap_item_data.item_props.get('prank_desc')

			side_effect = trap_item_data.item_props.get('side_effect')

			if side_effect != None:
				response += await ewitem.perform_prank_item_side_effect(side_effect, member=member)
			
			#calculate_gambit_exchange(pranker_data, pranked_data, trap_item_data, trap_used=True)
		else:
			# Trap was a dud.
			trap_was_dud = True
			response = "Close call! You were just about to eat shit and fall right into someone's {}, but luckily, it was a dud.".format(trap_item_data.item_props.get('item_name'))
		
		ewitem.item_delete(trap_id_item)
		
	finally:
		# Clean up the database handles.
		cursor.close()
		databaseClose(conn_info)
	await send_message(client, district_channel, formatMessage(member, response))
	
	# if not trap_was_dud:
	# 	client = get_client()
	# 	server = client.get_server(id_server)
	# 
	# 	prank_feed_channel = get_channel(server, 'prank-feed')
	# 
	# 	response += "\n`-------------------------`"
	# 	await send_message(client, prank_feed_channel, formatMessage(member, response))


def check_fursuit_active(id_server):
	market_data = EwMarket(id_server=id_server)
	if (market_data.day % 31 == 0 and market_data.clock >= 20
	or market_data.day % 31 == 1 and market_data.clock < 6):
		return True
	else:
		return False

def create_death_report(cause = None, user_data = None):
	
	client = ewcfg.get_client()
	server = client.get_guild(user_data.id_server)

	# User display name is used repeatedly later, grab now
	user_member = server.get_member(user_data.id_user)
	user_player = EwPlayer(id_user = user_data.id_user)
	user_nick = user_player.display_name

	deathreport = "You arrive among the dead. {}".format(ewcfg.emote_slimeskull)
	deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

	report_requires_killer = [ewcfg.cause_killing, ewcfg.cause_busted, ewcfg.cause_burning, ewcfg.cause_killing_enemy]
	if(cause in report_requires_killer): # Only deal with enemy data if necessary
		killer_isUser = cause in [ewcfg.cause_killing, ewcfg.cause_busted, ewcfg.cause_burning]
		killer_isEnemy = cause in [ewcfg.cause_killing_enemy]
		if(killer_isUser): # Generate responses for dying to another player
			# Grab user data
			killer_data = EwUser(id_user = user_data.id_killer, id_server = user_data.id_server)
			player_data = EwPlayer(id_user = user_data.id_killer)		

			# Get killer weapon
			weapon_item = EwItem(id_item = killer_data.weapon)
			weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))

			killer_nick = player_data.display_name

			if (cause == ewcfg.cause_killing) and (weapon != None): # Response for dying to another player
				deathreport = "You were {} by {}. {}".format(weapon.str_killdescriptor, killer_nick, ewcfg.emote_slimeskull)
				deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

			if (cause == ewcfg.cause_busted): # Response for being busted
				deathreport = "Your ghost has been busted by {}. {}".format(killer_nick, ewcfg.emote_bustin)
				deathreport = "{} ".format(ewcfg.emote_bustin) + formatMessage(user_player, deathreport)

			if (cause == ewcfg.cause_burning): # Response for burning to death
				deathreport = "You were {} by {}. {}".format(ewcfg.weapon_map.get(ewcfg.weapon_id_molotov).str_killdescriptor, killer_nick, ewcfg.emote_slimeskull)
				deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

		if(killer_isEnemy): # Generate responses for being killed by enemy
			# Grab enemy data
			killer_data = ewhunting.EwEnemy(id_enemy = user_data.id_killer, id_server = user_data.id_server)

			if killer_data.attacktype != ewcfg.enemy_attacktype_unarmed:
				used_attacktype = ewcfg.attack_type_map.get(killer_data.attacktype)
			else:
				used_attacktype = ewcfg.enemy_attacktype_unarmed
			if (cause == ewcfg.cause_killing_enemy): # Response for dying to enemy attack
				# Get attack kill description
				kill_descriptor = "beaten to death"
				if used_attacktype != ewcfg.enemy_attacktype_unarmed:
					kill_descriptor = used_attacktype.str_killdescriptor

				# Format report
				deathreport = "You were {} by {}. {}".format(kill_descriptor, killer_data.display_name, ewcfg.emote_slimeskull)
				deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

	if (cause == ewcfg.cause_donation): # Response for overdonation
		deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, "You have died in a medical mishap. {}".format(ewcfg.emote_slimeskull))

	if (cause == ewcfg.cause_suicide): # Response for !suicide
		deathreport = "You arrive among the dead by your own volition. {}".format(ewcfg.emote_slimeskull)
		deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

	if (cause == ewcfg.cause_drowning): # Response for disembarking into the slime sea
		deathreport = "You have drowned in the slime sea. {}".format(ewcfg.emote_slimeskull)
		deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

	if (cause == ewcfg.cause_falling): # Response for disembarking blimp over the city
		deathreport = "You have fallen to your death. {}".format(ewcfg.emote_slimeskull)
		deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

	if (cause == ewcfg.cause_bleeding): # Response for bleed death
		deathreport = "{skull} *{uname}*: You have succumbed to your wounds. {skull}".format(skull = ewcfg.emote_slimeskull, uname = user_nick)

	if (cause == ewcfg.cause_weather): # Response for death by bicarbonate rain
		deathreport = "{skull} *{uname}*: You have been cleansed by the bicarbonate rain. {skull}".format(skull = ewcfg.emote_slimeskull, uname = user_nick)

	if (cause == ewcfg.cause_cliff): # Response for falling or being pushed off cliff
		deathreport = "You fell off a cliff. {}".format(ewcfg.emote_slimeskull)
		deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

	if (cause == ewcfg.cause_backfire): # Response for death by self backfire
		weapon_item = EwItem(id_item = user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
		deathreport = "{} killed themselves with their own {}. Dumbass.".format(user_nick, weapon.str_name)

	if (cause == ewcfg.cause_praying): # Response for praying
		deathreport = formatMessage(user_member, "{} owww yer frickin bones man {}".format(ewcfg.emote_slimeskull, ewcfg.emote_slimeskull))

	return(deathreport)

# Get the current kingpin of slimernalia
def get_slimernalia_kingpin(server):
	data = execute_sql_query("SELECT {id_user} FROM users WHERE {id_server} = %s AND {slimernalia_kingpin} = true".format(
		id_user = ewcfg.col_id_user,
		id_server = ewcfg.col_id_server,
		slimernalia_kingpin = ewcfg.col_slimernalia_kingpin
	),(
		server.id,
	))

	if len(data) > 0:
		return data[0][0]

	return None

# Get the player with the most festivity
def get_most_festive(server):
	data = execute_sql_query(
	"SELECT users.{id_user}, FLOOR({festivity}) + COALESCE(sigillaria, 0) + FLOOR({festivity_from_slimecoin}) as total_festivity FROM users "\
	"LEFT JOIN (SELECT {id_user}, {id_server}, COUNT(*) * 1000 as sigillaria FROM items INNER JOIN items_prop ON items.{id_item} = items_prop.{id_item} WHERE {name} = %s AND {value} = %s GROUP BY items.{id_user}, items.{id_server}) f on users.{id_user} = f.{id_user} AND users.{id_server} = f.{id_server} "\
	"WHERE users.{id_server} = %s ORDER BY total_festivity DESC LIMIT 1".format(
		id_user = ewcfg.col_id_user,
		id_server = ewcfg.col_id_server,
		festivity = ewcfg.col_festivity,
		festivity_from_slimecoin = ewcfg.col_festivity_from_slimecoin,
		name = ewcfg.col_name,
		value = ewcfg.col_value,
		id_item = ewcfg.col_id_item,
	),(
		"id_furniture",
		ewcfg.item_id_sigillaria,
		server.id,
	))

	return data[0][0]

def check_user_has_role(server, member, checked_role_name):

	checked_role = discord.utils.get(server.roles, name=checked_role_name)
	if checked_role not in member.roles:
		return False
	else:
		return True
	
def return_server_role(server, role_name):
	return discord.utils.get(server.roles, name=role_name)

""" Returns the latest value, so that short PvP timer actions don't shorten remaining PvP time. """
def calculatePvpTimer(current_time_expirpvp, timer, enlisted = False):
	if enlisted:
		timer *= 1
		#timer *= 4

	desired_time_expirpvp = int(time.time()) + timer

	if desired_time_expirpvp > current_time_expirpvp:
		return desired_time_expirpvp

	return current_time_expirpvp

""" add the PvP flag role to a member """
async def add_pvp_role(cmd = None):
	member = cmd.message.author
	roles_map_user = getRoleMap(member.roles)

	if ewcfg.role_milkers in roles_map_user and ewcfg.role_milkers_pvp not in roles_map_user:
		await member.add_roles(cmd.roles_map[ewcfg.role_milkers_pvp])
	elif ewcfg.role_boober in roles_map_user and ewcfg.role_boober_pvp not in roles_map_user:
		await member.add_roles(cmd.roles_map[ewcfg.role_boober_pvp])
	elif ewcfg.role_flatfreak in roles_map_user and ewcfg.role_flatfreak_pvp not in roles_map_user:
		await member.add_roles(cmd.roles_map[ewcfg.role_flatfreak_pvp])
		
"""
	Returns true if the specified name is used by any POI.
"""
def channel_name_is_poi(channel_name):
	if channel_name != None:
		return channel_name in ewcfg.chname_to_poi

	return False

def get_cosmetic_abilities(id_user, id_server):
	active_abilities = []

	cosmetic_items = ewitem.inventory(
		id_user = id_user,
		id_server = id_server,
		item_type_filter = ewcfg.it_cosmetic
	)

	for item in cosmetic_items:
		i = EwItem(item.get('id_item'))
		if i.item_props['adorned'] == "true" and i.item_props['ability'] is not None:
			active_abilities.append(i.item_props['ability'])
		else:
			pass

	return active_abilities

def get_outfit_info(id_user, id_server, wanted_info = None):
	cosmetic_items = ewitem.inventory(
		id_user = id_user,
		id_server = id_server,
		item_type_filter = ewcfg.it_cosmetic
	)

	adorned_cosmetics = []
	adorned_ids = []

	adorned_styles = []
	dominant_style = None

	adorned_hues = []

	total_freshness = 0

	for cosmetic in cosmetic_items:
		c = EwItem(id_item = cosmetic.get('id_item'))

		if c.item_props['adorned'] == 'true':
			adorned_styles.append(c.item_props.get('fashion_style'))

			hue = ewcfg.hue_map.get(c.item_props.get('hue'))
			adorned_hues.append(c.item_props.get('hue'))

			if c.item_props['id_cosmetic'] not in adorned_ids:
				total_freshness += int(c.item_props.get('freshness'))

			adorned_ids.append(c.item_props['id_cosmetic'])
			adorned_cosmetics.append((hue.str_name + " " if hue != None else "") + cosmetic.get('name'))

	if len(adorned_cosmetics) != 0:
		# Assess if there's a cohesive style
		if len(adorned_styles) != 0:
			counted_styles = collections.Counter(adorned_styles)
			dominant_style = max(counted_styles, key = counted_styles.get)

			relative_style_amount = round(int(counted_styles.get(dominant_style) / len(adorned_cosmetics) * 100))
			# If the outfit has a dominant style
			if relative_style_amount >= 60:
				total_freshness *= int(relative_style_amount / 10) # If relative amount is 60 --> multiply by 6. 70 --> 7, 80 --> 8, etc. Rounds down, so 69 --> 6.

	if wanted_info is not None and wanted_info == "dominant_style" and dominant_style is not None:
		return dominant_style
	elif wanted_info is not None and wanted_info == "total_freshness":
		return total_freshness
	else:
		outfit_map = {
			'dominant_style': dominant_style,
			'total_freshness': total_freshness
		}
		return outfit_map

def get_style_freshness_rating(user_data, dominant_style = None):
	if dominant_style == None:
		dominant_style = "fresh"

	if user_data.freshness < ewcfg.freshnesslevel_1:
		response = "Your outfit is starting to look pretty fresh, but you’ve got a long way to go if you wanna be NLACakaNM’s next top model."
	else:
		if user_data.freshness < ewcfg.freshnesslevel_2:
			response = "Your outfit is low-key on point, not gonna lie. You’re goin’ places, kid."
		elif user_data.freshness < ewcfg.freshnesslevel_3:
			response = "Your outfit is lookin’ fresh as hell, goddamn! You shop so much you can probably speak Italian."
		elif user_data.freshness < ewcfg.freshnesslevel_4:
			response = "Your outfit is straight up **GOALS!** Like, honestly. I’m being, like, totally sincere right now. Your Instragrime has attracted a small following."
		else:
			response = "Holy shit! Your outfit is downright, positively, without a doubt, 100% **ON FLEEK!!** You’ve blown up on Instragrime, and you’ve got modeling gigs with fashion labels all across the city."

		if dominant_style == ewcfg.style_cool:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " You’re lookin’ wicked cool, dude. Like, straight up radical, man. For real, like, ta-haaa, seriously? Damn, bro. Sick."
			else:
				response += " Hey, kids, the world just got cooler. You’re the swingingest thing from coast-to-coast, and that ain’t no boast. You’re every slimegirl’s dream, you know what I mean? You’re where it’s at, and a far-out-happenin’ cat to boot. Man, it must hurt to be this hip."
		elif dominant_style == ewcfg.style_tough:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " You’re lookin’ tough as hell. Juveniles of all affiliations are starting to act nervous around you."
			else:
				response += " You’re just about the toughest-lookin' juveniledelinquent in the whole detention center. Ain’t nobody gonna pick a fight with you anymore, goddamn."
		elif dominant_style == ewcfg.style_smart:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " You’re starting to look like a real hipster, wearing all these smartypants garments. You love it, the people around you hate it."
			else:
				response += " You know extensive facts about bands that are so underground they’ve released their albums through long-since-expired Vocaroo links. You’re a leading hashtag warrior on various internet forums, and your opinions are well known by everyone who has spoken to you for more than five minutes. Everyone wants to knock your lights out, but… you’re just too fresh. "
		elif dominant_style == ewcfg.style_beautiful:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " You’re looking extremely handsome in all of those beautiful garments. If only this refined, elegant reflected in your manners when cracking into a Arizonian Kingpin Crab."
			else:
				response += " You’re the belle of the ball at every ball you attend, which has never happened. But, if you *were* to ever attend one, your beautiful outfit would surely distinguish you from the crowd. Who knows, you might even find TRUE LOVE because of it and get MARRIED. That is, if you weren’t already married to slime."
		elif dominant_style == ewcfg.style_cute:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " Awwwhhh, look at you! You’re sooo cute~, oh my gosh. I could just eat you up, and then vomit you back up after I read back the previous line I’ve just written."
			else:
				response += " It is almost kowai how kawaii you are right now. Your legions of fans slobber all over each new post on Instragrime and leave very strange comments. You’re stopped for autographs in public now, and there hasn’t been a selfie taken with you that hasn’t featured a hover hand."

	return response


def get_subzone_controlling_faction(subzone_id, id_server):
	
	subzone = ewcfg.id_to_poi.get(subzone_id)
	
	if subzone == None:
		return
	else:
		if not subzone.is_subzone:
			return
	
	mother_pois = subzone.mother_districts

	# Get all the mother pois of a subzone in order to find the father poi, which is either one of the mother pois or the father poi of the mother poi
	# Subzones such as the food court will have both a district poi and a street poi as one of their mother pois
	district_data = None

	for mother_poi in mother_pois:
		
		mother_poi_data = ewcfg.id_to_poi.get(mother_poi)
		
		if mother_poi_data.is_district:
			# One of the mother pois was a district, get its controlling faction
			district_data = EwDistrict(district=mother_poi, id_server=id_server)
			break
		else:
			# One of the mother pois was a street, get the father district of that street and its controlling faction
			father_poi = mother_poi_data.father_district
			district_data = EwDistrict(district=father_poi, id_server=id_server)
			break

	if district_data != None:
		faction = district_data.all_streets_taken()
		return faction

def get_street_list(str_poi):
	poi = ewcfg.id_to_poi.get(str_poi)
	neighbor_list = poi.neighbors
	poi_list = []
	if poi.is_district == False:
		return poi_list
	else:
		for neighbor in neighbor_list.keys():
			neighbor_poi = ewcfg.id_to_poi.get(neighbor)
			if neighbor_poi.is_street == True:
				poi_list.append(neighbor)
		return poi_list
	
async def collect_topics(cmd):
	
	if not cmd.message.author.guild_permissions.administrator:
		return
	
	client = get_client()
	server = client.get_guild(cmd.guild.id)
	topic_count = 0
	
	for channel in server.channels:
		
		if channel.type != discord.ChannelType.text:
			continue
		elif channel.topic == None or channel.topic == '':
			continue
		elif channel.topic == '(Closed indefinitely) Currently controlled by no one.':
			continue
			
		found_poi = False
		for poi in ewcfg.poi_list:
			if channel.name == poi.channel:
				found_poi = True
				break
				
		if found_poi:
			topic_count += 1
			print('\n{}\n=================\n{}'.format(channel.name, channel.topic))
			
	print('POI topics found: {}'.format(topic_count))
	
	
async def sync_topics(cmd):
	
	if not cmd.message.author.guild_permissions.administrator:
		return
	
	
	for poi in ewcfg.poi_list:

		poi_has_blank_topic = False
		if poi.topic == None or poi.topic == '':
			poi_has_blank_topic = True
		
		channel = get_channel(cmd.guild, poi.channel)
		
		if channel == None:
			logMsg('Failed to get channel for {}'.format(poi.id_poi))
			continue
		
		if channel.topic == poi.topic:
			continue
			
		if (poi_has_blank_topic and channel.topic == None) or (poi_has_blank_topic and channel.topic == ''):
			continue

		if poi_has_blank_topic:
			new_topic = ''
			debug_info = 'be a blank topic.'
		else:
			new_topic = poi.topic
			debug_info = poi.topic
			
		try:
			await asyncio.sleep(2)
			await channel.edit(topic = new_topic)
			logMsg('Changed channel topic for {} to {}'.format(channel, debug_info))
		except:
			logMsg('Failed to set channel topic for {} to {}'.format(channel, debug_info))
			
	logMsg('Finished syncing topics.')
	
async def shut_down_bot(cmd):
	
	if not cmd.message.author.guild_permissions.administrator:
		return await ewwep.suicide(cmd=cmd)
	
	logMsg('Goodbye!')
	await asyncio.sleep(2)
	
	while True:
		sys.exit()
		
async def check_bot(cmd):
	if not cmd.message.author.guild_permissions.administrator:
		return
	
	logMsg('TERMINATE is currently: {}'.format(TERMINATE))
	
	return
	sys.exit()

def gvs_create_gaia_grid_mapping(user_data):
	grid_map = {}

	# Grid print mapping and shambler targeting use different priority lists. Don't get these mixed up
	printgrid_low_priority = [ewcfg.enemy_type_gaia_rustealeaves]
	printgrid_mid_priority = [ewcfg.enemy_type_gaia_steelbeans]
	printgrid_high_priority = []
	for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
		if enemy_id not in printgrid_low_priority and enemy_id not in printgrid_mid_priority:
			printgrid_high_priority.append(enemy_id)

	gaias = execute_sql_query(
		"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1 AND {enemyclass} = %s".format(
			id_enemy=ewcfg.col_id_enemy,
			enemytype=ewcfg.col_enemy_type,
			poi=ewcfg.col_enemy_poi,
			life_state=ewcfg.col_enemy_life_state,
			gvs_coord=ewcfg.col_enemy_gvs_coord,
			enemyclass=ewcfg.col_enemy_class,
		), (
			user_data.id_server,
			user_data.poi,
			ewcfg.enemy_class_gaiaslimeoid
		))
	
	grid_conditions = execute_sql_query(
		"SELECT coord, grid_condition FROM gvs_grid_conditions WHERE district = %s".format(
		), (
			user_data.poi,
		))
	
	for condition in grid_conditions:
		grid_map[condition[0]] = condition[1]
	
	for gaia in gaias:
		try:
			gaia_in_coord = grid_map[gaia[2]]
			# No key error: Gaia is in coord already, check for priority
			is_filled = True
		except KeyError:
			gaia_in_coord = ''
			# Key error: Gaia was not in coord
			is_filled = False
			
		if is_filled:
			if gaia_in_coord in printgrid_low_priority and (gaia[1] in printgrid_mid_priority or gaia[1] in printgrid_high_priority):
				grid_map[gaia[2]] = gaia[1]
			if gaia_in_coord in printgrid_mid_priority and gaia[1] in printgrid_high_priority:
				grid_map[gaia[2]] = gaia[1]
		else:
			grid_map[gaia[2]] = gaia[1]
		
	return grid_map


def gvs_create_gaia_lane_mapping(user_data, row_used):

	# Grid print mapping and shambler targeting use different priority lists. Don't get these mixed up
	printlane_low_priority = [ewcfg.enemy_type_gaia_rustealeaves]
	printlane_mid_priority = []
	printlane_high_priority = [ewcfg.enemy_type_gaia_steelbeans]
	for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
		if enemy_id not in printlane_low_priority and enemy_id not in printlane_high_priority:
			printlane_mid_priority.append(enemy_id)

	gaias = execute_sql_query(
		"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} IN %s".format(
			id_enemy=ewcfg.col_id_enemy,
			enemytype=ewcfg.col_enemy_type,
			poi=ewcfg.col_enemy_poi,
			life_state=ewcfg.col_enemy_life_state,
			gvs_coord=ewcfg.col_enemy_gvs_coord,
			enemyclass=ewcfg.col_enemy_class,
		), (
			user_data.id_server,
			user_data.poi,
			ewcfg.enemy_class_gaiaslimeoid,
			tuple(row_used)
		))

	grid_conditions = execute_sql_query(
		"SELECT coord, grid_condition FROM gvs_grid_conditions WHERE district = %s AND coord IN %s".format(
		), (
			user_data.poi,
			tuple(row_used)
		))
	
	coord_sets = []

	for coord in row_used:
		current_coord_set = [] 
		for enemy in printlane_low_priority:
			for gaia in gaias:
				if gaia[1] == enemy and gaia[2] == coord:
					current_coord_set.append(gaia[0])
					
		for enemy in printlane_mid_priority:
			for gaia in gaias:
				if gaia[1] == enemy and gaia[2] == coord:
					current_coord_set.append(gaia[0])
					
		for enemy in printlane_high_priority:
			for gaia in gaias:
				if gaia[1] == enemy and gaia[2] == coord:
					current_coord_set.append(gaia[0])
					
		for condition in grid_conditions:
			if condition[0] == coord:
				if condition[1] == 'frozen':
					current_coord_set.append('frozen')
					
		coord_sets.append(current_coord_set)
	

	return coord_sets


def gvs_check_gaia_protected(enemy_data):
	is_protected = False
	
	low_attack_priority = [ewcfg.enemy_type_gaia_rustealeaves]
	high_attack_priority = [ewcfg.enemy_type_gaia_steelbeans]
	mid_attack_priority = []
	for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
		if enemy_id not in low_attack_priority and enemy_id not in high_attack_priority:
			mid_attack_priority.append(enemy_id)
	
	checked_coords = []
	enemy_coord = enemy_data.gvs_coord
	for row in ewcfg.gvs_valid_coords_gaia:
		if enemy_coord in row:
			index = row.index(enemy_coord)
			row_length = len(ewcfg.gvs_valid_coords_gaia)
			for i in range(index+1, row_length):
				checked_coords.append(ewcfg.gvs_valid_coords_gaia[i])
				
	gaias_in_front_coords = execute_sql_query(
		"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} IN %s".format(
			id_enemy=ewcfg.col_id_enemy,
			enemytype=ewcfg.col_enemy_type,
			life_state=ewcfg.col_enemy_life_state,
			gvs_coord=ewcfg.col_enemy_gvs_coord,
			enemyclass=ewcfg.col_enemy_class,
		), (
			ewcfg.enemy_class_gaiaslimeoid,
			tuple(checked_coords)
		))
	
	if len(gaias_in_front_coords) > 0:
		is_protected = True
	else:
		gaias_in_same_coord = execute_sql_query(
			"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} = %s".format(
				id_enemy=ewcfg.col_id_enemy,
				enemytype=ewcfg.col_enemy_type,
				life_state=ewcfg.col_enemy_life_state,
				gvs_coord=ewcfg.col_enemy_gvs_coord,
				enemyclass=ewcfg.col_enemy_class,
			), (
				ewcfg.enemy_class_gaiaslimeoid,
				enemy_coord
			))
		if len(gaias_in_same_coord) > 1:
			same_coord_gaias_types = []
			for gaia in gaias_in_same_coord:
				same_coord_gaias_types.append(gaia[1])
				
			for type in same_coord_gaias_types:
				if enemy_data.enemy_type in high_attack_priority:
					is_protected = False
					break
				elif enemy_data.enemy_type in mid_attack_priority and type in high_attack_priority:
					is_protected = True
					break
				elif enemy_data.enemy_type in low_attack_priority and (type in mid_attack_priority or type in high_attack_priority):
					is_protected = True
					break
	
		else:
			is_protected = False
	
	return is_protected

def gvs_check_operation_duplicate(id_user, district, enemytype, faction):
	entry = None
	
	if faction == ewcfg.psuedo_faction_gankers:
		entry = execute_sql_query(
			"SELECT * FROM gvs_ops_choices WHERE id_user = %s AND district = %s AND enemytype = %s AND faction = %s".format(
			), (
				id_user, 
				district, 
				enemytype, 
				faction
			))
	elif faction == ewcfg.psuedo_faction_shamblers:
		entry = execute_sql_query(
			"SELECT * FROM gvs_ops_choices WHERE district = %s AND enemytype = %s AND faction = %s".format(
			), (
				district,
				enemytype,
				faction
			))

	if len(entry) > 0:
		return True
	else:
		return False
	
def gvs_check_operation_limit(id_user, district, enemytype, faction):
	
	limit_hit = False
	tombstone_limit = 0
	
	if faction == ewcfg.psuedo_faction_gankers:
		data = execute_sql_query(
			"SELECT id_user FROM gvs_ops_choices WHERE id_user = %s AND district = %s AND faction = %s".format(
			), (
				id_user, 
				district,
				faction
			))
		
		if len(data) >= 6:
			limit_hit = True
		else:
			limit_hit = False
		
	elif faction == ewcfg.psuedo_faction_shamblers:
		sh_data = execute_sql_query(
			"SELECT enemytype FROM gvs_ops_choices WHERE district = %s AND faction = %s".format(
			), (
				district,
				faction
			))
		
		gg_data = execute_sql_query(
			"SELECT id_user FROM gvs_ops_choices WHERE district = %s AND faction = %s".format(
			), (
				district,
				enemytype,
			))
		
		gg_id_list = []
		for gg in gg_data:
			gg_id_list.append(gg[0])
			
		gg_id_set = set(gg_id_list) # Remove duplicate user IDs
		
		if len(gg_id_set) == 0:
			tombstone_limit = 3
		elif len(gg_id_set) <= 3:
			tombstone_limit = 6
		elif len(gg_id_set) <= 6:
			tombstone_limit = 10
		else:
			tombstone_limit = 12
		
		if len(sh_data) >= tombstone_limit:
			limit_hit = True
		else:
			limit_hit = False
			
	return limit_hit, tombstone_limit

def gvs_check_if_in_operation(user_data):
	
	op_data = execute_sql_query(
		"SELECT id_user, district FROM gvs_ops_choices WHERE id_user = %s".format(
		), (
			user_data.id_user,
		))

	if len(op_data) > 0:
		return True, op_data[0][1]
	else:
		return False, None

def gvs_get_gaias_from_coord(poi, checked_coord):
	gaias = execute_sql_query(
		"SELECT id_enemy, enemytype FROM enemies WHERE poi = %s AND gvs_coord = %s".format(
		), (
			poi,
			checked_coord
		))
	
	gaias_id_to_type_map = {}
	
	for gaia in gaias:
		if gaia[1] in ewcfg.gvs_enemies_gaiaslimeoids:
			gaias_id_to_type_map[gaia[0]] = gaia[1]
	
	return gaias_id_to_type_map

# If there are no player operations, spawn in ones that the bot uses
def gvs_insert_bot_ops(id_server, district, enemyfaction):
	bot_id = 56709
	
	if enemyfaction == ewcfg.psuedo_faction_gankers:
		possible_bot_types = [
			ewcfg.enemy_type_gaia_pinkrowddishes,
			ewcfg.enemy_type_gaia_purplekilliflower,
			ewcfg.enemy_type_gaia_poketubers,
			ewcfg.enemy_type_gaia_razornuts
		]
		for type in possible_bot_types:
			execute_sql_query("REPLACE INTO gvs_ops_choices({}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_user,
				ewcfg.col_district,
				ewcfg.col_enemy_type,
				ewcfg.col_faction,
				ewcfg.col_id_item,
				ewcfg.col_shambler_stock,
			), (
				bot_id,
				district,
				type,
				enemyfaction,
				-1,
				0,
			))
			
			# To increase the challenge, a column of suganmanuts is placed down.
			for coord in ['A6', 'B6', 'C6', 'D6', 'E6']:
				ewhunting.spawn_enemy(
					id_server=id_server,
					pre_chosen_type=ewcfg.enemy_type_gaia_suganmanuts,
					pre_chosen_level=50,
					pre_chosen_poi=district,
					pre_chosen_identifier='',
					pre_chosen_faction=ewcfg.psuedo_faction_gankers,
					pre_chosen_owner=bot_id,
					pre_chosen_coord=coord,
					manual_spawn=True,
				)
		
	elif enemyfaction == ewcfg.psuedo_faction_shamblers:
		possible_bot_types = [
			ewcfg.enemy_type_defaultshambler,
			ewcfg.enemy_type_bucketshambler,
		]
		for type in possible_bot_types:
			execute_sql_query("REPLACE INTO gvs_ops_choices({}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_user,
				ewcfg.col_district,
				ewcfg.col_enemy_type,
				ewcfg.col_faction,
				ewcfg.col_id_item,
				ewcfg.col_shambler_stock,
			), (
				bot_id,
				district,
				type,
				enemyfaction,
				-1,
				20,
			))
			
async def degrade_districts(cmd):
	
	if not cmd.message.author.guild_permissions.administrator:
		return

	gvs_districts = []

	for poi in ewcfg.poi_list:
		if poi.is_district and not poi.id_poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown, ewcfg.poi_id_juviesrow, ewcfg.poi_id_oozegardens, ewcfg.poi_id_thevoid]:
			gvs_districts.append(poi.id_poi)

	execute_sql_query("UPDATE districts SET degradation = 0")
	execute_sql_query("UPDATE districts SET time_unlock = 0")
	execute_sql_query("UPDATE districts SET degradation = 10000 WHERE district IN {}".format(tuple(gvs_districts)))
	logMsg('Set proper degradation values.')
	