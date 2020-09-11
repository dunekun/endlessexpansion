import ewutils
import ewcfg

"""
	EwPlayer is a representation of an actual player discord account. There is
	one record for each person, no matter how many servers they interact with
	endless-war on.

	The id_server column is used to store the last server they were active
	with. This is the server EW will use for direct message commands.
"""
class EwPlayer:
	id_user = -1
	id_server = -1

	avatar = ""
	display_name = ""

	def __init__(
		self,
		id_user = None,
		id_server = None
	):
		if(id_user != None):
			self.id_user = id_user
			self.id_server = id_server

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object
				cursor.execute("SELECT {}, {}, {} FROM players WHERE id_user = %s".format(
					ewcfg.col_id_server,
					ewcfg.col_avatar,
					ewcfg.col_display_name
				), (self.id_user, ))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.id_server = result[0]
					self.avatar = result[1]
					self.display_name = result[2]
				elif id_server != None:
					# Create a new database entry if the object is missing.
					cursor.execute("REPLACE INTO players({}, {}) VALUES(%s, %s)".format(
						ewcfg.col_id_user,
						ewcfg.col_id_server
					), (
						self.id_user,
						self.id_server
					))

					conn.commit()
			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save user data object to the database. """
	def persist(self):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Save the object.
			cursor.execute("REPLACE INTO players({}, {}, {}, {}) VALUES(%s, %s, %s, %s)".format(
				ewcfg.col_id_user,
				ewcfg.col_id_server,
				ewcfg.col_avatar,
				ewcfg.col_display_name
			), (
				self.id_user,
				self.id_server,
				self.avatar,
				self.display_name
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)


""" update the player record with the current data. """
def player_update(member = None, server = None):
	id_server_old = ""

	try:
		conn_info = ewutils.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		# Get existing player info (or create a record if it's a new player)
		player = EwPlayer(
			id_user = member.id,
			id_server = server.id
		)

		# Update values with Member data.
		id_server_old = player.id_server
		player.id_server = server.id
		player.avatar = member.avatar_url
		player.display_name = member.display_name

		# Save the updated data.
		player.persist()

		conn.commit()
	finally:
		cursor.close()
		ewutils.databaseClose(conn_info)

	# Log server changes
	if(server.id != int(id_server_old)):
		
		ewutils.logMsg('active server for {} changed from "{}" to "{}"'.format(
			member.display_name,
			id_server_old,
			server.id
		))
