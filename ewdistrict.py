import asyncio
import math
import time

import discord

import ewcfg
import ewstats
import ewutils
import ewrolemgr

from ew import EwUser



"""
	district data model for database persistence
"""
class EwDistrict:
	id_server = -1

	# The district's identifying string
	name = ""

	# The faction currently controlling this district
	controlling_faction = ""

	# The faction currently capturing this district
	capturing_faction = ""

	# The amount of progress made on the capture
	capture_points = 0

	# The property class of the district
	property_class = ""

	# The amount of CP it takes for the district to be captured
	max_capture_points = 0

	# The amount of slime in the district
	slimes = 0

	# Time until the district unlocks for capture again
	time_unlock = 0


	#Amount of influence in a district

	cap_side = ""

	# determines if the zone is functional
	degradation = 0
	
	# a timestamp for when a shambler can next plant a tombstone
	horde_cooldown = 0
	
	# the amount of gaiaslime the garden gankers have at their disposal
	gaiaslime = 0

	def __init__(self, id_server = None, district = None):
		if id_server is not None and district is not None:
			self.id_server = id_server
			self.name = district

			# find the district's property class
			for poi in ewcfg.poi_list:
				if poi.id_poi == self.name:
					self.property_class = poi.property_class.lower()

			if len(self.property_class) > 0:
				self.max_capture_points = ewcfg.max_capture_points[self.property_class]
			else:
				self.max_capture_points = 0


			data = ewutils.execute_sql_query("SELECT {controlling_faction}, {capturing_faction}, {capture_points},{slimes}, {time_unlock}, {cap_side}, {degradation}, {horde_cooldown}, {gaiaslime} FROM districts WHERE id_server = %s AND {district} = %s".format(

				controlling_faction = ewcfg.col_controlling_faction,
				capturing_faction = ewcfg.col_capturing_faction,
				capture_points = ewcfg.col_capture_points,
				district = ewcfg.col_district,
				slimes = ewcfg.col_district_slimes,
				time_unlock = ewcfg.col_time_unlock,
				cap_side = ewcfg.col_cap_side,
				degradation = ewcfg.col_degradation,
				horde_cooldown = ewcfg.col_horde_cooldown,
				gaiaslime = ewcfg.col_gaiaslime,
			), (
				id_server,
				district
			))

			if len(data) > 0:  # if data is not empty, i.e. it found an entry
				# data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
				self.controlling_faction = data[0][0]
				self.capturing_faction = data[0][1]
				self.capture_points = data[0][2]
				self.slimes = data[0][3]
				self.time_unlock = data[0][4]
				self.cap_side = data[0][5]
				self.degradation = data[0][6]
				self.horde_cooldown = data[0][7]
				self.gaiaslime = data[0][8]

				# ewutils.logMsg("EwDistrict object '" + self.name + "' created.  Controlling faction: " + self.controlling_faction + "; Capture progress: %d" % self.capture_points)
			else:  # create new entry
				ewutils.execute_sql_query("REPLACE INTO districts ({id_server}, {district}) VALUES (%s, %s)".format(
					id_server = ewcfg.col_id_server,
					district = ewcfg.col_district
				), (
					id_server,
					district
				))

	def persist(self):
		ewutils.execute_sql_query("REPLACE INTO districts(id_server, {district}, {controlling_faction}, {capturing_faction}, {capture_points}, {slimes}, {time_unlock}, {cap_side}, {degradation}, {horde_cooldown}, {gaiaslime}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
			district = ewcfg.col_district,
			controlling_faction = ewcfg.col_controlling_faction,
			capturing_faction = ewcfg.col_capturing_faction,
			capture_points = ewcfg.col_capture_points,
			slimes = ewcfg.col_district_slimes,
			time_unlock = ewcfg.col_time_unlock,
			cap_side = ewcfg.col_cap_side,
			degradation = ewcfg.col_degradation,
			horde_cooldown = ewcfg.col_horde_cooldown,
			gaiaslime = ewcfg.col_gaiaslime,
		), (
			self.id_server,
			self.name,
			self.controlling_faction,
			self.capturing_faction,
			self.capture_points,
			self.slimes,
			self.time_unlock,
			self.cap_side,
			self.degradation,
			self.horde_cooldown,
			self.gaiaslime
		))
	
	def get_number_of_friendly_neighbors(self):
		if self.controlling_faction == "":
			return 0
		neighbors = ewcfg.poi_neighbors[self.name]
		friendly_neighbors = 0

		for neighbor_id in neighbors:
			neighbor_data = EwDistrict(id_server = self.id_server, district = neighbor_id)
			if neighbor_data.controlling_faction == self.controlling_faction:
				friendly_neighbors += 1
		return friendly_neighbors

	def all_neighbors_friendly(self):
		rival_gang_poi = "none"
		if self.controlling_faction == "":
			return False
		elif self.controlling_faction == ewcfg.faction_milkers:
			rival_gang_poi = ewcfg.poi_id_rowdyroughhouse
		elif self.controlling_faction == ewcfg.faction_boober:
			rival_gang_poi = ewcfg.poi_id_copkilltown


		neighbors = ewcfg.poi_neighbors[self.name]
		for neighbor_id in neighbors:
			neighbor_poi = ewcfg.id_to_poi.get(neighbor_id)
			neighbor_data = EwDistrict(id_server = self.id_server, district = neighbor_id)
			if neighbor_data.controlling_faction != self.controlling_faction and not neighbor_poi.is_subzone and not neighbor_poi.is_outskirts and not neighbor_poi.is_district:
				return False
			elif neighbor_poi.id_poi == rival_gang_poi:
				return False
		return True

	def all_streets_taken(self):
		street_name_list = ewutils.get_street_list(self.name)
		
		if self.name == ewcfg.poi_id_rowdyroughhouse:
			return ewcfg.faction_boober
		elif self.name == ewcfg.poi_id_copkilltown:
			return ewcfg.faction_milkers

		faction_list = []
		for name in street_name_list:
			district_data = EwDistrict(id_server=self.id_server, district=name)
			faction_list.append(district_data.controlling_faction)
	
		if len(faction_list) > 0 and all(faction == faction_list[0] for faction in faction_list):
			return faction_list[0]
		else:
			return ""

	def get_players_in_district(self,
			min_level = 0,
			max_level = math.inf,
			life_states = [],
			factions = [],
			min_slimes = -math.inf,
			max_slimes = math.inf,
			ignore_offline = False,
			pvp_only = False
		):
		client = ewutils.get_client()
		server = client.get_guild(self.id_server)
		if server == None:
			ewutils.logMsg("error: couldn't find server with id {}".format(self.id_server))
			return []
		time_now = int(time.time())

		players = ewutils.execute_sql_query("SELECT {id_user}, {slimes}, {slimelevel}, {faction}, {life_state}, {time_expirpvp} FROM users WHERE id_server = %s AND {poi} = %s".format(
			id_user = ewcfg.col_id_user,
			slimes = ewcfg.col_slimes,
			slimelevel = ewcfg.col_slimelevel,
			faction = ewcfg.col_faction,
			life_state = ewcfg.col_life_state,
			poi = ewcfg.col_poi,
			time_expirpvp = ewcfg.col_time_expirpvp
		),(
			self.id_server,
			self.name
		))

		filtered_players = []
		for player in players:
			id_user = player[0]
			slimes = player[1]
			slimelevel = player[2]
			faction = player[3]
			life_state = player[4]
			time_expirpvp = player[5]
			
			member = server.get_member(id_user)

			if member != None:
				if max_level >= slimelevel >= min_level \
				and max_slimes >= slimes >= min_slimes \
				and (len(life_states) == 0 or life_state in life_states) \
				and (len(factions) == 0 or faction in factions) \
				and not (ignore_offline and member.status == discord.Status.offline) \
				and not (pvp_only and time_expirpvp < time_now and life_state != ewcfg.life_state_shambler):
					filtered_players.append(id_user)

		return filtered_players

	def get_enemies_in_district(self,
			min_level = 0,
			max_level = math.inf,
			min_slimes = -math.inf,
			max_slimes = math.inf,
			scout_used = False,
			classes = None,
		):

		client = ewutils.get_client()
		server = client.get_guild(self.id_server)
		if server == None:
			ewutils.logMsg("error: couldn't find server with id {}".format(self.id_server))
			return []

		enemies = ewutils.execute_sql_query("SELECT {id_enemy}, {slimes}, {level}, {enemytype}, {enemyclass} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1".format(
			id_enemy = ewcfg.col_id_enemy,
			slimes = ewcfg.col_enemy_slimes,
			level = ewcfg.col_enemy_level,
			enemytype = ewcfg.col_enemy_type,
			enemyclass = ewcfg.col_enemy_class,
			poi = ewcfg.col_enemy_poi,
			life_state = ewcfg.col_enemy_life_state
		),(
			self.id_server,
			self.name
		))

		filtered_enemies = []
		for enemy_data_column in enemies:

			fetched_id_enemy = enemy_data_column[0] # data from id_enemy column in enemies table
			fetched_slimes = enemy_data_column[1] # data from slimes column in enemies table
			fetched_level = enemy_data_column[2] # data from level column in enemies table
			fetched_type = enemy_data_column[3] # data from enemytype column in enemies table
			fetched_class = enemy_data_column[4] # data from enemyclass column in enemies table

			# Append the enemy to the list if it meets the requirements
			if max_level >= fetched_level >= min_level \
			and max_slimes >= fetched_slimes >= min_slimes:
				if classes != None:
					if fetched_class in classes:
						filtered_enemies.append(fetched_id_enemy)
				else:
					filtered_enemies.append(fetched_id_enemy)
				
			# Don't show sandbags on !scout
			if scout_used and fetched_type == ewcfg.enemy_type_sandbag:
				filtered_enemies.remove(fetched_id_enemy)

		return filtered_enemies

	def decay_capture_points(self):
		resp_cont_decay = ewutils.EwResponseContainer(client = ewutils.get_client(), id_server = self.id_server)
		if self.capture_points > 0:
				#and self.time_unlock == 0:

			neighbors = ewcfg.poi_neighbors[self.name]
			all_neighbors_friendly = self.all_neighbors_friendly()

			decay = -math.ceil(ewcfg.limit_influence_a / (ewcfg.ticks_per_day * ewcfg.decay_modifier))
			#decay = -math.ceil(ewcfg.max_capture_points_a / (ewcfg.ticks_per_day * ewcfg.decay_modifier))

			slimeoids = ewutils.get_slimeoids_in_poi(poi = self.name, id_server = self.id_server, sltype = ewcfg.sltype_nega)
			
			nega_present = len(slimeoids) > 0

			poi = ewcfg.id_to_poi.get(self.name)
			father_poi = ewcfg.id_to_poi.get(poi.father_district)
			num_districts = len(ewutils.get_street_list(poi.father_district))

			if nega_present:
				decay *= 1.5
			if self.capture_points + (decay * 3) > (ewcfg.limit_influence[father_poi.property_class])/num_districts:
				decay *= 3

			if self.controlling_faction == "" or (not self.all_neighbors_friendly() and self.capture_points > ewcfg.limit_influence[father_poi.property_class]/num_districts) or nega_present:  # don't decay if the district is completely surrounded by districts controlled by the same faction
				# reduces the capture progress at a rate with which it arrives at 0 after 1 in-game day
				#if (self.capture_points + int(decay) < ewcfg.min_influence[self.property_class] and self.capture_points >= ewcfg.min_influence[self.property_class]) and not nega_present and self.controlling_faction != "":
				#	responses = self.change_capture_points(self.capture_points - ewcfg.min_influence[self.property_class], ewcfg.actor_decay)
				#else:
				responses = self.change_capture_points(int(decay), ewcfg.actor_decay)
				resp_cont_decay.add_response_container(responses)

		#if self.capture_points < 0:
		#	self.capture_points = 0

		if self.capture_points <= 0:
			if self.controlling_faction != "":  # if it was owned by a faction

				message = "The {faction} have lost control over {district} because of sheer negligence.".format(
					faction = self.controlling_faction,
					district = ewcfg.id_to_poi[self.name].str_name
				)
				channels = [ewcfg.id_to_poi[self.name].channel] + ewcfg.hideout_channels
				for ch in channels:
					resp_cont_decay.add_channel_response(channel = ch, response = message)
			responses = self.change_ownership("", ewcfg.actor_decay)
			resp_cont_decay.add_response_container(responses)
			self.capturing_faction = ""
		return resp_cont_decay

	def change_capture_lock(self, progress):
		resp_cont = ewutils.EwResponseContainer(id_server = self.id_server)

		progress_before = self.time_unlock

		self.time_unlock += progress

		if self.time_unlock < 0:
			self.time_unlock == 0

		progress_after = self.time_unlock

		if (progress_after // ewcfg.capture_lock_milestone) != (progress_before // ewcfg.capture_lock_milestone):
			time_mins = ewutils.formatNiceTime(seconds = progress_after, round_to_minutes = True)
			if progress < 0:
				if progress_before >= 15 * 60 >= progress_after:
					message = "{district} will unlock for capture in {time}.".format(
						district = ewcfg.id_to_poi[self.name].str_name,
						time = time_mins
					)
					channels = ewcfg.hideout_channels

					for ch in channels:
						resp_cont.add_channel_response(channel = ch, response = message)
				
				elif progress_before >= 5 * 60 >= progress_after:
					message = "{district} will unlock for capture in {time}.".format(
						district = ewcfg.id_to_poi[self.name].str_name,
						time = time_mins
					)
					channels = ewcfg.hideout_channels

					for ch in channels:
						resp_cont.add_channel_response(channel = ch, response = message)
				
				message = "{district} will unlock for capture in {time}.".format(
					district = ewcfg.id_to_poi[self.name].str_name,
					time = time_mins
				)

				channels = [ewcfg.id_to_poi[self.name].channel]

				for ch in channels:
					resp_cont.add_channel_response(channel = ch, response = message)

		if self.time_unlock == 0 and progress < 0:
			chip_cont = self.change_capture_points(progress = -1, actor = ewcfg.actor_decay)
			resp_cont.add_response_container(chip_cont)

		return resp_cont

	def change_capture_points(self, progress, actor, num_lock = 0):  # actor can either be a faction or "decay"
		street_poi = ewcfg.id_to_poi.get(self.name)
		district_poi = ewcfg.id_to_poi.get(street_poi.father_district)
		num_districts = len(ewutils.get_street_list(street_poi.father_district))

		max_capture = ewcfg.limit_influence[district_poi.property_class]/num_districts
		progress_percent_before = int(self.capture_points / max_capture * 100)

		self.capture_points += progress



		resp_cont_change_cp = ewutils.EwResponseContainer(client = ewutils.get_client(), id_server = self.id_server)

		# ensures that the value doesn't exceed the bounds
		if self.capture_points < 0:
			self.capture_points = 0



		if self.cap_side == "" and actor != ewcfg.actor_decay:
			self.cap_side = actor
		if self.capture_points <= 0:
			self.cap_side = ""
			self.controlling_faction = ""


		#elif self.capture_points > self.max_capture_points:
		#	self.capture_points = self.max_capture_points
		#where we're going we don't need roads

		progress_percent_after = int(self.capture_points / max_capture * 100)

		#if num_lock > 0 \
		#and self.capture_points == max_capture \
		#and progress > 0 \
		#and self.property_class in ewcfg.capture_locks \
		#and self.time_unlock == 0:
		#	base_time_unlock = ewcfg.capture_locks.get(self.property_class)
		#	responses = self.change_capture_lock(base_time_unlock + (num_lock - 1) * ewcfg.capture_lock_per_gangster)
		#	resp_cont_change_cp.add_response_container(responses)

		if actor != ewcfg.actor_decay:
			self.capturing_faction = actor



		if self.controlling_faction == "" and progress > 0 and self.cap_side == actor and self.capture_points + progress > (ewcfg.min_influence[district_poi.property_class]/num_districts):
			self.controlling_faction = actor



		# display a message if it's reached a certain amount
		if (progress_percent_after // ewcfg.capture_milestone) != (progress_percent_before // ewcfg.capture_milestone):  # if a progress milestone was reached
			if progress > 0:  # if it was a positive change
				if ewcfg.capture_milestone <= progress_percent_after < ewcfg.capture_milestone * 2:  # if its the first milestone
					message = "{faction} have started capturing {district}. Current progress: {progress}%".format(
						faction = self.capturing_faction.capitalize(),
						district = ewcfg.id_to_poi[self.name].str_name,
						progress = progress_percent_after
					)
					channels = [ewcfg.id_to_poi[self.name].channel]

					for ch in channels:
						resp_cont_change_cp.add_channel_response(channel = ch, response = message)
				else:
					# alert both factions of significant capture progress
					if progress_percent_after >= 30 > progress_percent_before:  # if the milestone of 30% was just reached
						message = "{faction} are capturing {district}.".format(
							faction = self.capturing_faction.capitalize(),
							district = ewcfg.id_to_poi[self.name].str_name,
							progress = progress_percent_after
						)
						if self.controlling_faction == ewcfg.faction_boober:
							channels = [ewcfg.channel_rowdyroughhouse]
						elif self.controlling_faction == ewcfg.faction_milkers:
							channels = [ewcfg.channel_copkilltown]
						else:
							channels = ewcfg.hideout_channels

						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)

					if self.controlling_faction != actor:  # if it's not already owned by that faction
						message = "{faction} continue to capture {district}. Current progress: {progress}%".format(
							faction = self.capturing_faction.capitalize(),
							district = ewcfg.id_to_poi[self.name].str_name,
							progress = progress_percent_after
						)
						channels = [ewcfg.id_to_poi[self.name].channel]
						
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)
					else:
						message = "{faction} are renewing their grasp on {district}. Current control level: {progress}%".format(
							faction = self.capturing_faction.capitalize(),
							district = ewcfg.id_to_poi[self.name].str_name,
							progress = progress_percent_after
						)
						channels = [ewcfg.id_to_poi[self.name].channel]
						
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)
			else:  # if it was a negative change
				if self.controlling_faction != "":  # if the district is owned by a faction
					if progress_percent_after < 50 <= progress_percent_before:
						message = "{faction}' control of {district} is slipping.".format(
							faction = self.controlling_faction.capitalize(),
							district = ewcfg.id_to_poi[self.name].str_name,
							progress = progress_percent_after
						)
						channels = ewcfg.hideout_channels
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)

					elif progress_percent_after < 75 <= progress_percent_before and actor != ewcfg.actor_decay:
						message = "{faction} are de-capturing {district}.".format(
							faction = actor.capitalize(),
							district = ewcfg.id_to_poi[self.name].str_name,
							progress = progress_percent_after
						)
						channels = ewcfg.hideout_channels
						
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)

					message = "{faction}' control of {district} has decreased. Remaining control level: {progress}%".format(
						faction = self.controlling_faction.capitalize(),
						district = ewcfg.id_to_poi[self.name].str_name,
						progress = progress_percent_after
					)
					channels = [ewcfg.id_to_poi[self.name].channel]
					
					for ch in channels:
						resp_cont_change_cp.add_channel_response(channel = ch, response = message)
				else:  # if it's an uncontrolled district
					message = "{faction}' capture progress of {district} has decreased. Remaining progress: {progress}%".format(
						faction = self.capturing_faction.capitalize(),
						district = ewcfg.id_to_poi[self.name].str_name,
						progress = progress_percent_after
					)
					channels = [ewcfg.id_to_poi[self.name].channel]
					
					for ch in channels:
						resp_cont_change_cp.add_channel_response(channel = ch, response = message)

		if progress < 0 and self.capture_points == 0:
			self.capturing_faction = ""

		# if capture_points is at its maximum value (or above), assign the district to the capturing faction
		#if self.capture_points > max_capture:
		#	responses = self.change_ownership(self.capturing_faction, actor)
		#	resp_cont_change_cp.add_response_container(responses)

		# if the district has decayed or been de-captured and it wasn't neutral anyway, make it neutral
		#elif self.capture_points == 0 and self.controlling_faction != "":
		#	responses = self.change_ownership("", actor)
		#	resp_cont_change_cp.add_response_container(responses)
		#return
		return resp_cont_change_cp

	"""
		Change who controls the district. Can be used to update the channel topic by passing the already controlling faction as an arg.
	"""
	def change_ownership(self, new_owner, actor, client = None):  # actor can either be a faction, "decay", or "init"
		resp_cont_owner = ewutils.EwResponseContainer(client = ewutils.get_client(), id_server = self.id_server)

		factions = ["", ewcfg.faction_milkers, ewcfg.faction_boober]

		if new_owner in factions:
			server = ewcfg.server_list[self.id_server]
			channel_str = ewcfg.id_to_poi[self.name].channel
			channel = ewutils.get_channel(server = server, channel_name = channel_str)

			if channel is not None and channel.topic:  # tests if the topic is neither None nor empty
				initialized = False

				# initialize channel topic control statuses
				for faction in factions:
					if ewcfg.control_topics[faction] in channel.topic:
						initialized = True

				if not initialized:
					new_topic = channel.topic + " " + ewcfg.control_topics[new_owner]

				# replace the the string of the previously controlling faction with that of the new one.
				else:
					new_topic = channel.topic.replace(ewcfg.control_topics[self.controlling_faction], ewcfg.control_topics[new_owner])

				if client is None:
					client = ewutils.get_client()


				if client is not None:
					resp_cont_owner.add_channel_topic(channel = channel_str, topic = new_topic)

			if self.controlling_faction != new_owner:  # if the controlling faction actually changed
				if new_owner != "":  # if it was captured by a faction instead of being de-captured or decayed
					countdown_message = ""
					if self.time_unlock > 0:
						countdown_message = "It will unlock for capture again in {}.".format(ewutils.formatNiceTime(seconds = self.time_unlock, round_to_minutes = True))
					message = "{faction} just captured {district}. {countdown}".format(
						faction = self.capturing_faction.capitalize(),
						district = ewcfg.id_to_poi[self.name].str_name,
						countdown = countdown_message
					)
					channels = [ewcfg.id_to_poi[self.name].channel] + ewcfg.hideout_channels
					
					for ch in channels:
						resp_cont_owner.add_channel_response(channel = ch, response = message)
				else:  # successful de-capture or full decay
					if actor != ewcfg.actor_decay:
						message = "{faction} just wrested control over {district} from the {other_faction}.".format(
							faction = actor.capitalize(),
							district = ewcfg.id_to_poi[self.name].str_name,
							other_faction = self.controlling_faction  # the faction that just lost control
						)
						channels = [ewcfg.id_to_poi[self.name].channel] + ewcfg.hideout_channels
						
						for ch in channels:
							resp_cont_owner.add_channel_response(channel = ch, response = message)

				self.controlling_faction = new_owner

		return resp_cont_owner

	""" add or remove slime """
	def change_slimes(self, n = 0, source = None):
		change = int(n)
		self.slimes += change

	""" wether the district is still functional """
	def is_degraded(self):
		checked_poi = ewcfg.id_to_poi.get(self.name)
		if checked_poi is None:
			return True
		
		poi = None
		
		# In the Gankers Vs. Shamblers event, importance is placed on districts
		# As a result, if a district is degraded, then all of its subzones/streets are also now degraded
		if checked_poi.is_district:
			poi = checked_poi
		elif checked_poi.is_street:
			poi = ewcfg.id_to_poi.get(checked_poi.father_district)
		elif checked_poi.is_subzone:
			# Subzones are a more complicated affair to check for degradation.
			# Look to see if its mother district is a district or a street, then check for degradation of the appropriate district.
			for mother_poi_id in checked_poi.mother_districts:
				mother_poi = ewcfg.id_to_poi.get(mother_poi_id)
				
				if mother_poi.is_district:
					# First mother POI found is a district. Break here and check for its degradation.
					poi = mother_poi
					break
				elif mother_poi.is_street:
					# First mother POI found is a street. Break here and check for its father district's degradation.
					poi = ewcfg.id_to_poi.get(mother_poi.father_district)
					break
		else:
			poi = checked_poi

		# print('poi checked was {}. looking for {} degradation.'.format(self.name, poi.id_poi))
		poi_district_data = EwDistrict(district = poi.id_poi, id_server = self.id_server)
		return poi_district_data.degradation >= poi.max_degradation

"""
	Informs the player about their current zone's capture progress
"""
async def capture_progress(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""

	poi = ewcfg.id_to_poi.get(user_data.poi)
	response += "**{}**: ".format(poi.str_name)



	if not user_data.poi in ewcfg.capturable_districts:
		response += "This zone cannot be captured."
		if poi.is_district == True:
			response += " To take this district, you need to enter into the streets."
			district_data = EwDistrict(district=user_data.poi, id_server=user_data.id_server)
			if district_data.all_streets_taken() != "":
				response += " {} have a stranglehold over this entire district.".format(district_data.all_streets_taken().capitalize())

		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	district_data = EwDistrict(id_server=user_data.id_server, district=poi.father_district)
	street_data = EwDistrict(id_server=user_data.id_server, district=user_data.poi)


	if street_data.controlling_faction != "":
		response += "{} control this street. ".format(street_data.controlling_faction.capitalize())
	elif street_data.capturing_faction != "" and street_data.cap_side != street_data.capturing_faction:
		response += "{} are de-capturing this street. ".format(street_data.capturing_faction.capitalize())
	elif street_data.capturing_faction != "":
		response += "{} are capturing this street. ".format(street_data.capturing_faction.capitalize())
	else:
		response += "Nobody has staked a claim to this street yet. ".format(street_data.controlling_faction.capitalize())


	num_streets = len(ewutils.get_street_list(poi.father_district))
	response += "\n\n**Current influence: {:,}**\nMinimum influence: {:,}\nMaximum influence: {:,}\nPercentage to maximum influence: {:,}%".format(abs(street_data.capture_points), int(ewcfg.min_influence[district_data.property_class]/num_streets), int(ewcfg.limit_influence[district_data.property_class]/num_streets), round((abs(street_data.capture_points) * 100/(ewcfg.limit_influence[district_data.property_class]/num_streets)), 1))

	if district_data.all_streets_taken() != "":
		response += "\n{} have a stranglehold over this entire district.".format(
			district_data.all_streets_taken().capitalize())

	#if district_data.time_unlock > 0:


		#response += "\nThis district cannot be captured currently. It will unlock in {}.".format(ewutils.formatNiceTime(seconds = district_data.time_unlock, round_to_minutes = True))
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


"""async def annex(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = ""
	resp_cont = ewutils.EwResponseContainer(id_server = cmd.guild.id)
	time_now = int(time.time())

	poi = ewcfg.id_to_poi.get(user_data.poi)

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "You ineffectively try shaking your can of spraypaint to whip up some sick graffiti. Alas, you’re all outta slime. " \
                   "They should really make these things compatible with ectoplasm."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if not (len(user_data.faction) > 0 and user_data.life_state == ewcfg.life_state_enlisted):
		response = "Juveniles are too chickenshit to make graffiti and risk getting busted by the cops. Fuckin’ losers."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown]:
		response = "There’s no point, the rest of your gang has already covered this place in spraypaint. Focus on exporting your graffiti instead."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.poi == ewcfg.poi_id_juviesrow:
		response = "Nah, the Rowdys and Killers have both agreed this is neutral ground. You don’t want to start a diplomatic crisis, " \
                   "just stick to spraying down sick graffiti and splattering your rival gang across the pavement in the other districts."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if not user_data.poi in ewcfg.capturable_districts:
		response = "This zone cannot be captured."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	district_data = EwDistrict(id_server = user_data.id_server, district = user_data.poi)


	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	if district_data.time_unlock > 0:
		response = "You can’t spray graffiti here yet, it’s too soon after your rival gang extended their own cultural dominance over it. Try again in {}.".format(ewutils.formatNiceTime(seconds = district_data.time_unlock, round_to_minutes = True))
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if district_data.all_neighbors_friendly():
		response = "What the hell are you doing, dude? You can’t put down any graffiti here, it’s been completely overrun by your rival gang. " \
                   "You can only spray districts that have at least one unfriendly neighbor, duh!"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	users_in_district = district_data.get_players_in_district(
		life_states = [ewcfg.life_state_enlisted],
		ignore_offline = True,
		pvp_only = True
	)

	allies_in_district = district_data.get_players_in_district(
		factions = [user_data.faction],
		life_states = [ewcfg.life_state_enlisted],
		ignore_offline = True,
		pvp_only = True
	)

	if len(users_in_district) > len(allies_in_district):
		response = "Holy shit, deal with your rival gangsters first! You can’t spray graffiti while they’re on the prowl!"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	mutations = user_data.get_mutations()

	slimes_spent = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)
	capture_discount = 1

	if ewcfg.mutation_id_lonewolf in mutations:
		if user_data.time_expirpvp > time_now:
			if len(users_in_district) == 1:
				capture_discount *= 0.8
		else:
			if len(users_in_district) == 0:
				capture_discount *= 0.8

	if ewcfg.mutation_id_patriot in mutations:
		capture_discount *= 0.8

	if slimes_spent == None:
		response = "How much slime do you want to spend on spraying graffiti in this district?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if slimes_spent < 0:
		slimes_spent = user_data.slimes

	if slimes_spent > user_data.slimes:
		response = "You don't have that much slime, retard."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	num_lock = len(allies_in_district)
	if user_data.time_expirpvp < time_now:
		num_lock += 1

	if (district_data.controlling_faction not in ["", user_data.faction]) or (district_data.capturing_faction not in ["", user_data.faction]):
		slimes_decap = min(district_data.capture_points, int(slimes_spent / capture_discount))
		decap_resp = district_data.change_capture_points(
			progress = -slimes_decap,
			actor = user_data.faction,
			num_lock = num_lock
		)
		resp_cont.add_response_container(decap_resp)
		
		user_data.change_slimes(n = -slimes_decap * capture_discount, source = ewcfg.source_spending)
		slimes_spent -= slimes_decap * capture_discount

	slimes_cap = min(district_data.max_capture_points - district_data.capture_points, int(slimes_spent / capture_discount))
	cap_resp = district_data.change_capture_points(
		progress = slimes_cap,
		actor = user_data.faction,
		num_lock = num_lock
	)
	resp_cont.add_response_container(cap_resp)
		
	user_data.change_slimes(n = -slimes_cap * capture_discount, source = ewcfg.source_spending)

	# Flag the user for PvP
	# user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_annex, True)

	user_data.persist()
	district_data.persist()
	await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

	return await resp_cont.post()
"""
async def shamble(cmd):

	user_data = EwUser(member = cmd.message.author)

	if user_data.life_state != ewcfg.life_state_shambler and user_data.poi != ewcfg.poi_id_assaultflatsbeach:
		response = "You have too many higher brain functions left to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif user_data.life_state in [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted] and user_data.poi == ewcfg.poi_id_assaultflatsbeach:
		response = "You feel an overwhelming sympathy for the plight of the Shamblers and decide to join their ranks."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		await asyncio.sleep(5)
		
		user_data = EwUser(member=cmd.message.author)
		user_data.life_state = ewcfg.life_state_shambler
		user_data.degradation = 100

		ewutils.moves_active[user_data.id_user] = 0

		user_data.poi = ewcfg.poi_id_nuclear_beach_edge
		user_data.persist()
		
		member = cmd.message.author
		
		base_poi_channel = ewutils.get_channel(cmd.message.guild, 'nuclear-beach-edge')

		response = 'You arrive inside the facility and are injected with a unique strain of the Modelovirus. Not long after, a voice on the intercom chimes in.\n**"Welcome, {}. Welcome to Downpour Laboratories. It\'s safer here. Please treat all machines and facilities with respect, they are precious to our cause."**'.format(member.display_name)

		await ewrolemgr.updateRoles(client=cmd.client, member=member)
		return await ewutils.send_message(cmd.client, base_poi_channel, ewutils.formatMessage(cmd.message.author, response))
	
	else:
		pass

	# Rest in fucking pieces

	# if poi is None:
	# 	return
	# elif not poi.is_district:
	# 	response = "This doesn't seem like an important place to be shambling. Try a district zone instead."
	# 	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	# elif poi.id_poi == ewcfg.poi_id_oozegardens:
	# 	response = "The entire district is covered in Brightshades! You have no business shambling this part of town!"
	# 	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	# 
	# in_operation, op_poi = ewutils.gvs_check_if_in_operation(user_data)
	# if in_operation:
	# 	if op_poi != user_data.poi:
	# 		response = "You aren't allowed to !shamble this district, per Dr. Downpour's orders.\n(**!goto {}**)".format(op_poi)
	# 		return await ewutils.send_message(cmd.client, cmd.message.channel,  ewutils.formatMessage(cmd.message.author, response))
	# else:
	# 	response = "You aren't even in a Graveyard Op yet!\n(**!joinops [tombstone]**)"
	# 	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	# 
	# if (time_now - user_data.time_lasthaunt) < ewcfg.cd_shambler_shamble:
	# 	response = "You know, you really just don't have the energy to shamble this place right now. Try again in {} seconds.".format(int(ewcfg.cd_shambler_shamble-(time_now-user_data.time_lasthaunt)))
	# 	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	# 
	# district_data = EwDistrict(district = poi.id_poi, id_server = cmd.guild.id)
	# 
	# if district_data.degradation < poi.max_degradation:
	# 	district_data.degradation += 1
	# 	# user_data.degradation += 1
	# 	user_data.time_lasthaunt = time_now
	# 	district_data.persist()
	# 	user_data.persist()
	# 	
	# 	response = "You shamble {}.".format(poi.str_name)
	# 	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	# 
	# 	if district_data.degradation == poi.max_degradation:
	# 		response = ewcfg.str_zone_degraded.format(poi = poi.str_name)
	# 		await ewutils.send_message(cmd.client, cmd.message.channel, response)

async def rejuvenate(cmd):
	user_data = EwUser(member=cmd.message.author)

	if user_data.life_state == ewcfg.life_state_shambler and user_data.poi != ewcfg.poi_id_oozegardens:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif user_data.life_state == ewcfg.life_state_shambler and user_data.poi == ewcfg.poi_id_oozegardens:
		response = "You decide to change your ways and become one of the Garden Gankers in order to overthrow your old master."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		await asyncio.sleep(5)

		user_data = EwUser(member=cmd.message.author)
		user_data.life_state = ewcfg.life_state_juvenile
		user_data.degradation = 0
		user_data.gvs_currency = 0

		ewutils.moves_active[user_data.id_user] = 0

		user_data.poi = ewcfg.poi_id_og_farms
		user_data.persist()

		client = ewutils.get_client()
		server = client.get_guild(user_data.id_server)
		member = server.get_member(user_data.id_user)
		
		base_poi_channel = ewutils.get_channel(cmd.message.guild, ewcfg.channel_og_farms)

		response = "You enter into Atomic Forest inside the farms of Ooze Gardens and are sterilized of the Modelovirus. Hortisolis gives you a big hug and says he's glad you've overcome your desire for vengeance in pursuit of deposing Downpour."

		await ewrolemgr.updateRoles(client=cmd.client, member=member)
		return await ewutils.send_message(cmd.client, base_poi_channel, ewutils.formatMessage(cmd.message.author, response))

	else:
		pass


"""
	Updates/Increments the capture_points values of all districts every time it's called
"""

async def capture_tick(id_server):
	# the variables might apparently be accessed before assignment if i didn't declare them here
	cursor = None
	conn_info = None

	resp_cont_capture_tick = ewutils.EwResponseContainer(client = ewutils.get_client(), id_server = id_server)

	all_districts = ewcfg.capturable_districts


	if len(all_districts) > 0:  # if all_districts isn't empty
		server = ewcfg.server_list[id_server]
		time_old = time.time()

		for district in all_districts:
			district_name = district
			dist = EwDistrict(id_server = id_server, district = district_name)

			if dist.time_unlock > 0 and not dist.all_neighbors_friendly():
				responses = dist.change_capture_lock(progress = -ewcfg.capture_tick_length)
				resp_cont_capture_tick.add_response_container(responses)
				dist.persist()

			if dist.time_unlock > 0:
				continue

			# no more automatic capping
			continue

			controlling_faction = dist.controlling_faction

			gangsters_in_district = dist.get_players_in_district(min_slimes = ewcfg.min_slime_to_cap, life_states = [ewcfg.life_state_enlisted], ignore_offline = True)
					

			slimeoids = ewutils.get_slimeoids_in_poi(poi = district_name, id_server = id_server, sltype = ewcfg.sltype_nega)
			
			nega_present = len(slimeoids) > 0
#			if nega_present:
#				continue

			# the faction that's actively capturing the district this tick
			# if no players are present, it's None, if only players of one faction (ignoring juvies and ghosts) are,
			# it's the faction's name, i.e. 'rowdys' or 'killers', and if both are present, it's 'both'
			faction_capture = None

			# how much progress will be made. is higher the more people of one faction are in a district, and is 0 if both teams are present
			capture_speed = 0

			# number of players actively capturing
			num_capturers = 0

			dc_stat_increase_list = []

			# checks if any players are in the district and if there are only players of the same faction, i.e. progress can happen
			for player in gangsters_in_district:
				player_id = player
				user_data = EwUser(id_user = player_id, id_server = id_server)
				player_faction = user_data.faction

				mutations = user_data.get_mutations()

				try:
					player_online = server.get_member(player_id).status != discord.Status.offline
				except:
					player_online = False

				#ewutils.logMsg("Online status checked. Time elapsed: %f" % (time.time() - time_old) + " Server: %s" % id_server + " Player: %s" % player_id + " Status: %s" % ("online" if player_online else "offline"))

				if player_online:
					if faction_capture not in [None, player_faction]:  # if someone of the opposite faction is in the district
						faction_capture = 'both'  # standstill, gang violence has to happen
						capture_speed = 0
						num_capturers = 0
						dc_stat_increase_list.clear()

					else:  # if the district isn't already controlled by the player's faction and the capture isn't halted by an enemy
						faction_capture = player_faction
						player_capture_speed = 1
						if ewcfg.mutation_id_lonewolf in mutations and len(gangsters_in_district) == 1:
							player_capture_speed *= 2
						if ewcfg.mutation_id_patriot in mutations:
							player_capture_speed *= 2
							

						capture_speed += player_capture_speed
						num_capturers += 1
						dc_stat_increase_list.append(player_id)


			if faction_capture not in ['both', None]:  # if only members of one faction is present
				if district_name in ewcfg.capturable_districts:
					friendly_neighbors = dist.get_number_of_friendly_neighbors()
					if dist.all_neighbors_friendly():
						capture_speed = 0
					elif dist.controlling_faction == faction_capture:
						capture_speed *= 1 + 0.1 * friendly_neighbors
					else:
						capture_speed /= 1 + 0.1 * friendly_neighbors

					capture_progress = dist.capture_points

					if faction_capture != dist.capturing_faction:
						capture_progress *= -1

					capture_speed *= ewcfg.baseline_capture_speed


					if dist.capture_points < dist.max_capture_points:
						for stat_recipient in dc_stat_increase_list:
							ewstats.change_stat(
								id_server = id_server,
								id_user = stat_recipient,
								metric = ewcfg.stat_capture_points_contributed,
								n = ewcfg.capture_tick_length * capture_speed
							)

					if faction_capture == dist.capturing_faction:  # if the faction is already in the process of capturing, continue
						responses = dist.change_capture_points(ewcfg.capture_tick_length * capture_speed, faction_capture, num_capturers)
						resp_cont_capture_tick.add_response_container(responses)

					elif dist.capture_points == 0 and dist.controlling_faction == "":  # if it's neutral, start the capture
						responses =  dist.change_capture_points(ewcfg.capture_tick_length * capture_speed, faction_capture, num_capturers)
						resp_cont_capture_tick.add_response_container(responses)

						dist.capturing_faction = faction_capture

					# lower the enemy faction's progress to revert it to neutral (or potentially get it onto your side without becoming neutral first)
					else:  # if the (de-)capturing faction is not in control
						responses =  dist.change_capture_points(-(ewcfg.capture_tick_length * capture_speed * ewcfg.decapture_speed_multiplier), faction_capture)
						resp_cont_capture_tick.add_response_container(responses)

					dist.persist()

	# await resp_cont_capture_tick.post()

"""
	Coroutine that continually calls capture_tick; is called once per server, and not just once globally
"""
async def capture_tick_loop(id_server):
	interval = ewcfg.capture_tick_length
	# causes a capture tick to happen exactly every 10 seconds (the "elapsed" thing might be unnecessary, depending on how long capture_tick ends up taking on average)
	while not ewutils.TERMINATE:
		await capture_tick(id_server = id_server)
		# ewutils.logMsg("Capture tick happened on server %s." % id_server + " Timestamp: %d" % int(time.time()))

		await asyncio.sleep(interval)

"""
	Gives both kingpins the appropriate amount of slime for how many districts they own and lowers the capture_points property of each district by a certain amount, turning them neutral after a while
"""
async def give_kingpins_slime_and_decay_capture_points(id_server):
	resp_cont_decay_loop = ewutils.EwResponseContainer(client = ewutils.get_client(), id_server = id_server)

	for kingpin_role in [ewcfg.role_bigboober, ewcfg.role_mommymilker]:
		kingpin = ewutils.find_kingpin(id_server = id_server, kingpin_role = kingpin_role)

		if kingpin is not None:
			total_slimegain = 0
			for id_district in ewcfg.capturable_districts:

				district = EwDistrict(id_server = id_server, district = id_district)

				# if the kingpin is controlling this district give the kingpin slime based on the district's property class
				if district.controlling_faction == (ewcfg.faction_milkers if kingpin.faction == ewcfg.faction_milkers else ewcfg.faction_boober):
					poi = ewcfg.id_to_poi.get(id_district)
					num_streets = len(ewutils.get_street_list(poi.father_district))
					father_district = EwDistrict(district=poi.father_district)

					slimegain = ewcfg.district_control_slime_yields[district.property_class]/num_streets

					# increase slimeyields by 10 percent per friendly neighbor
					friendly_mod = 1 + 0.1 * district.get_number_of_friendly_neighbors()
					total_slimegain += slimegain * friendly_mod

			kingpin.change_slimes(n = total_slimegain)
			kingpin.persist()

			ewutils.logMsg(kingpin_role + " just received %d" % total_slimegain + " slime for their captured districts.")

	# Decay capture points.
	for id_district in ewcfg.capturable_districts:
		district = EwDistrict(id_server = id_server, district = id_district)

		responses =  district.decay_capture_points()
		resp_cont_decay_loop.add_response_container(responses)
		district.persist()
	# await resp_cont_decay_loop.post()

async def change_spray(cmd):
	user_data = EwUser(member=cmd.message.author)
	newspray = cmd.message.content[(len(ewcfg.cmd_changespray)):].strip()

	if newspray == "":
		response = "You need to add an image link to change your spray."
	elif len(newspray) > 400:
		response = "Fucking christ, are you painting the Sistine Chapel? Use a shorter link."
	else:
		response = "Got it. Spray set."
		user_data.spray = newspray
		user_data.persist()

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def tag(cmd):
	user_data = EwUser(member=cmd.message.author)

	if user_data.life_state in(ewcfg.life_state_enlisted, ewcfg.life_state_kingpin):
		response = user_data.spray
	else:
		response = "Save the spraying for the gangsters. You're either too gay or dead to participate in this sort of thing."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


