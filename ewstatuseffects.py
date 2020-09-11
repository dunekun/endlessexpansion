import time
import math

import ewcfg
import ewutils

class EwStatusEffectDef:
	id_status = ""
	# Time until expiration, negative values have specific expiration conditions
	time_expire = -1
    
	str_acquire = ""
	str_describe = ""
	str_describe_self = ""
	dmg_mod_self = 0
	miss_mod_self = 0
	crit_mod_self = 0
	dmg_mod = 0
	miss_mod = 0
	crit_mod = 0

	def __init__(
		self,
		id_status = "",
		time_expire = -1,
		str_acquire = "",
		str_describe = "",
		str_describe_self = "",
		dmg_mod_self = 0,
		miss_mod_self = 0,
		crit_mod_self = 0,
		dmg_mod = 0,
		miss_mod = 0,
		crit_mod = 0
	):
		self.id_status = id_status
		self.time_expire = time_expire
		self.str_acquire = str_acquire
		self.str_describe = str_describe
		self.str_describe_self = str_describe_self
		self.dmg_mod_self = dmg_mod_self
		self.miss_mod_self = miss_mod_self
		self.crit_mod_self = crit_mod_self
		self.dmg_mod = dmg_mod
		self.miss_mod = miss_mod
		self.crit_mod = crit_mod

class EwStatusEffect:
	id_server = -1
	id_user = -1
	id_status = ""
	
	time_expire = -1
	value = 0
	source = ""
	id_target = -1

	def __init__(
		self,
		id_status = None,
		user_data = None,
		time_expire = 0,
		value = 0,
		source = "",
		id_user = None,
		id_server = None,
		id_target = -1,
	):
		if user_data != None:
			id_user = user_data.id_user
			id_server = user_data.id_server

		if id_status != None and id_user != None and id_server != None:
			self.id_server = id_server
			self.id_user = id_user
			self.id_status = id_status
			self.time_expire = time_expire
			self.value = value
			self.source = source
			self.id_target = id_target
			time_now = int(time.time())

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object
				cursor.execute("SELECT {time_expire}, {value}, {source}, {id_target} FROM status_effects WHERE {id_status} = %s and {id_server} = %s and {id_user} = %s".format(
					time_expire = ewcfg.col_time_expir,
					id_status = ewcfg.col_id_status,
					id_server = ewcfg.col_id_server,
					id_user = ewcfg.col_id_user,
					value = ewcfg.col_value,
					source = ewcfg.col_source,
					id_target = ewcfg.col_status_target,
				), (
					self.id_status,
					self.id_server,
					self.id_user
				))
				result = cursor.fetchone()

				if result != None:
					self.time_expire = result[0]
					self.value = result[1]
					self.source = result[2]

				else:
					# Save the object.
					cursor.execute("REPLACE INTO status_effects({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
						ewcfg.col_id_server,
						ewcfg.col_id_user,
						ewcfg.col_id_status,
						ewcfg.col_time_expir,
						ewcfg.col_value,
						ewcfg.col_source,
						ewcfg.col_status_target,
					), (
						self.id_server,
						self.id_user,
						self.id_status,
						(self.time_expire + time_now) if self.time_expire > 0 else self.time_expire,
						self.value,
						self.source,
						self.id_target,
					))

					self.time_expire = (self.time_expire + time_now) if self.time_expire > 0 else self.time_expire

					conn.commit()

			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save item data object to the database. """
	def persist(self):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Save the object.
			cursor.execute("REPLACE INTO status_effects({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_server,
				ewcfg.col_id_user,
				ewcfg.col_id_status,
				ewcfg.col_time_expir,
				ewcfg.col_value,
				ewcfg.col_source,
				ewcfg.col_status_target,
			), (
				self.id_server,
				self.id_user,
				self.id_status,
				self.time_expire,
				self.value,
				self.source,
				self.id_target,
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

class EwEnemyStatusEffect:
	id_server = -1
	id_enemy = -1
	id_status = ""
	
	time_expire = -1
	value = 0
	source = ""
	id_target = -1

	def __init__(
		self,
		id_status = None,
		enemy_data = None,
		time_expire = 0,
		value = 0,
		source = "",
		id_enemy = None,
		id_server = None,
		id_target = -1,
	):
		if enemy_data != None:
			id_enemy = enemy_data.id_enemy
			id_server = enemy_data.id_server

		if id_status != None and id_enemy != None and id_server != None:
			self.id_server = id_server
			self.id_enemy = id_enemy
			self.id_status = id_status
			self.time_expire = time_expire
			self.value = value
			self.source = source
			self.id_target = id_target
			time_now = int(time.time())

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object
				cursor.execute("SELECT {time_expire}, {value}, {source}, {id_target} FROM enemy_status_effects WHERE {id_status} = %s and {id_server} = %s and {id_enemy} = %s".format(
					time_expire = ewcfg.col_time_expir,
					id_status = ewcfg.col_id_status,
					id_server = ewcfg.col_id_server,
					id_enemy = ewcfg.col_id_enemy,
					value = ewcfg.col_value,
					source = ewcfg.col_source,
					id_target = ewcfg.col_status_target,
				), (
					self.id_status,
					self.id_server,
					self.id_enemy
				))
				result = cursor.fetchone()

				if result != None:
					self.time_expire = result[0]
					self.value = result[1]
					self.source = result[2]

				else:
					# Save the object.
					cursor.execute("REPLACE INTO enemy_status_effects({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
						ewcfg.col_id_server,
						ewcfg.col_id_enemy,
						ewcfg.col_id_status,
						ewcfg.col_time_expir,
						ewcfg.col_value,
						ewcfg.col_source,
						ewcfg.col_status_target,
					), (
						self.id_server,
						self.id_enemy,
						self.id_status,
						(self.time_expire + time_now) if self.time_expire > 0 else self.time_expire,
						self.value,
						self.source,
						self.id_target,
					))

					self.time_expire = (self.time_expire + time_now) if self.time_expire > 0 else self.time_expire

					conn.commit()

			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save item data object to the database. """
	def persist(self):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Save the object.
			cursor.execute("REPLACE INTO enemy_status_effects({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_server,
				ewcfg.col_id_enemy,
				ewcfg.col_id_status,
				ewcfg.col_time_expir,
				ewcfg.col_value,
				ewcfg.col_source,
				ewcfg.col_status_target,
			), (
				self.id_server,
				self.id_enemy,
				self.id_status,
				self.time_expire,
				self.value,
				self.source,
				self.id_target,
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

