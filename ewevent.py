import ewutils
import ewcfg
import ewstats
import ewitem

"""
	Database persistence object describing some discrete event. Player
	death/resurrection, item discovery, etc.
"""
class EwEvent:
	id_server = -1

	event_type = None

	id_user = None
	id_target = None

	def __init__(
		self,
		id_server = -1,
		event_type = None,
		id_user = None,
		id_target = None
	):
		self.id_server = id_server
		self.event_type = event_type
		self.id_user = id_user
		self.id_target = id_target

	"""
		Write event to the database.
	"""
	def persist(self):
		# TODO
		pass

stat_fn_map = {}
fns_initialized = False

def init_stat_function_map():
	global stat_fn_map
	stat_fn_map = {
		ewcfg.stat_slimesmined: process_slimesmined,
		ewcfg.stat_max_slimesmined: process_max_slimesmined,
		ewcfg.stat_slimesfromkills: process_slimesfromkills,
		ewcfg.stat_max_slimesfromkills: process_max_slimesfromkills,
		ewcfg.stat_kills: process_kills,
		ewcfg.stat_max_kills: process_max_kills,
		ewcfg.stat_ghostbusts: process_ghostbusts,
		ewcfg.stat_max_ghostbusts: process_max_ghostbusts,
		ewcfg.stat_poudrins_looted: process_poudrins_looted,
                ewcfg.stat_slimesfarmed: process_slimesfarmed,
                ewcfg.stat_slimesscavenged: process_slimesscavenged
	}
	global fns_initialized
	fns_initialized = True

def process_stat_change(id_server = None, id_user = None, metric = None, value = None):
	if fns_initialized == False:
		init_stat_function_map()

	fn = stat_fn_map.get(metric)

	if fn != None:
		fn(id_server = id_server, id_user = id_user, value = value)

def process_slimesmined(id_server = None, id_user = None, value = None):
	ewstats.track_maximum(id_server = id_server, id_user = id_user, metric = ewcfg.stat_max_slimesmined, value = value)

def process_max_slimesmined(id_server = None, id_user = None, value = None):
	# TODO give apropriate medal
	pass

def process_slimesfromkills(id_server = None, id_user = None, value = None):
	ewstats.track_maximum(id_server = id_server, id_user = id_user, metric = ewcfg.stat_max_slimesfromkills, value = value)

def process_max_slimesfromkills(id_server = None, id_user = None, value = None):
	# TODO give apropriate medal
	pass

def process_slimesfarmed(id_server = None, id_user = None, value = None):
	ewstats.track_maximum(id_server = id_server, id_user = id_user, metric = ewcfg.stat_max_slimesfarmed, value = value)

def process_slimesscavenged(id_server = None, id_user = None, value = None):
	ewstats.track_maximum(id_server = id_server, id_user = id_user, metric = ewcfg.stat_max_slimesscavenged, value = value)

def process_kills(id_server = None, id_user = None, value = None):
	ewstats.track_maximum(id_server = id_server, id_user = id_user, metric = ewcfg.stat_max_kills, value = value)
	ewstats.increment_stat(id_server = id_server, id_user = id_user, metric = ewcfg.stat_lifetime_kills)

def process_max_kills(id_server = None, id_user = None, value = None):
	# TODO give apropriate medal
	pass

def process_ghostbusts(id_server = None, id_user = None, value = None):
	ewstats.track_maximum(id_server = id_server, id_user = id_user, metric = ewcfg.stat_max_ghostbusts, value = value)
	ewstats.increment_stat(id_server = id_server, id_user = id_user, metric = ewcfg.stat_lifetime_ghostbusts)

def process_max_ghostbusts(id_server = None, id_user = None, value = None):
	# TODO give apropriate medal
	pass

def process_poudrins_looted(id_server = None, id_user = None, value = None):
	poudrin_amount = ewitem.find_poudrin(id_user = id_user, id_server = id_user)

	ewstats.track_maximum(id_user = id_user, id_server = id_server, metric = ewcfg.stat_max_poudrins, value = poudrin_amount)
	ewstats.change_stat(id_user = id_user, id_server = id_server, metric = ewcfg.stat_lifetime_poudrins, n = value)
