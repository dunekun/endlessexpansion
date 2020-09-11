import ewutils
import ewcfg

"""
	EwServer is a representation of a server, if the name of the server or
	other meta data is needed in a scope where it's not normally available.
"""
class EwServer:
	id_server = -1

	name = ""
	icon = ""

	def __init__(
		self,
		id_server = None
	):
		if(id_server != None):
			self.id_server = id_server

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object
				cursor.execute("SELECT {}, {} FROM servers WHERE id_server = %s".format(
					ewcfg.col_name,
					ewcfg.col_icon
				), (self.id_server, ))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.name = result[0]
				else:
					# Create a new database entry if the object is missing.
					cursor.execute("REPLACE INTO servers({}) VALUES(%s)".format(
						ewcfg.col_id_server
					), (
						self.id_server,
					))

					conn.commit()
			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save server data object to the database. """
	def persist(self):
		if self.icon == None:
			self.icon = ""

		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Save the object.
			cursor.execute("REPLACE INTO servers({}, {}, {}) VALUES(%s, %s, %s)".format(
				ewcfg.col_id_server,
				ewcfg.col_name,
				ewcfg.col_icon
			), (
				self.id_server,
				self.name,
				self.icon
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)


""" update the server record with the current data. """
def server_update(server = None):
	try:
		conn_info = ewutils.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		dbserver = EwServer(
			id_server = server.id
		)

		# Update values with Member data.
		dbserver.name = server.name
		dbserver.icon = server.icon_url

		dbserver.persist()

		conn.commit()
	finally:
		cursor.close()
		ewutils.databaseClose(conn_info)
