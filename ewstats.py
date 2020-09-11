import ewutils
import ewcfg
import ewevent

"""
	Utility functions for recording statistics in the database
"""

""" Look up a user statistic by user object or server and user IDs  """
def get_stat(id_server = None, id_user = None, user = None, metric = None):
	if(id_user == None) and (id_server == None):
			if(user != None):
				id_server = user.id_server
				id_user = user.id_user

	result = None

	try:
		conn_info = ewutils.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor();

		cursor.execute("SELECT {value} FROM stats WHERE {metric} = %s AND {id_server} = %s AND {id_user} = %s".format(
			value = ewcfg.col_stat_value,
			metric = ewcfg.col_stat_metric,
			id_server = ewcfg.col_id_server,
			id_user = ewcfg.col_id_user
		), (
			metric,
			id_server,
			id_user
		))

		db_result = cursor.fetchone()

		if db_result == None:
			set_stat(id_server = id_server, id_user = id_user, metric = metric, value = 0)
			result = 0
		else:
			result = db_result[0]

		conn.commit()
	finally:
		# Clean up the database handles.
		cursor.close()
		ewutils.databaseClose(conn_info)

	return result

""" Overwrite a user statistic by user object or server and user IDs  """
def set_stat(id_server = None, id_user = None, user = None, metric = None, value = 0):
	if(id_user == None) and (id_server == None):
			if(user != None):
				id_server = user.id_server
				id_user = user.id_user

	try:
		conn_info = ewutils.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor();

		cursor.execute("REPLACE INTO stats({id_server}, {id_user}, {metric}, {value}) VALUES(%s, %s, %s, %s)".format(
			id_server = ewcfg.col_id_server,
			id_user = ewcfg.col_id_user,
			metric = ewcfg.col_stat_metric,
			value = ewcfg.col_stat_value
		), (
			id_server,
			id_user,
			metric,
			value
		))

		conn.commit()
	finally:
		# Clean up the database handles.
		cursor.close()
		ewutils.databaseClose(conn_info)

	ewevent.process_stat_change(id_server = id_server, id_user = id_user, metric = metric, value = value)

""" Increase/Decrease a stat by a given value """
def change_stat(id_server = None, id_user = None, user = None, metric = None, n = 0):
	if(id_user == None) and (id_server == None) and (user != None):
		id_server = user.id_server
		id_user = user.id_user

	if (id_user == None) or (id_server == None):
		return

	old_value = get_stat(id_server = id_server, id_user = id_user, metric = metric)
	set_stat(id_server = id_server, id_user = id_user, metric = metric, value = old_value + n)


def increment_stat(id_server = None, id_user = None, user = None, metric = None):
	change_stat(id_server = id_server, id_user = id_user, user = user, metric = metric, n = 1)

""" Update a user statistic only if the new value is higher. return True if change occurred """
def track_maximum(id_server = None, id_user = None, user = None, metric = None, value = 0):
	if(id_user == None) and (id_server == None):
			if(user != None):
				id_server = user.id_server
				id_user = user.id_user

	try:
		conn_info = ewutils.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor();

		old_value = get_stat(id_server = id_server, id_user = id_user, metric = metric)
		if old_value < value: 
			set_stat(id_server = id_server, id_user = id_user, metric = metric, value = value)

		conn.commit()
	finally:
		# Clean up the database handles.
		cursor.close()
		ewutils.databaseClose(conn_info)

""" Set to zero stats that need to clear on death """
def clear_on_death(id_server = None, id_user = None):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			for metric in ewcfg.stats_clear_on_death:
				cursor.execute("REPLACE INTO stats({id_server}, {id_user}, {metric}, {value}) VALUES(%s, %s, %s, %s)".format(
					id_server = ewcfg.col_id_server,
					id_user = ewcfg.col_id_user,
					metric = ewcfg.col_stat_metric,
					value = ewcfg.col_stat_value
				), (
					id_server,
					id_user,
					metric,
					0
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)
