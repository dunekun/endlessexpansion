import asyncio
import time
import math
import heapq
import random
import discord

from copy import deepcopy

import ewutils
import ewcmd
import ewrolemgr
import ewcfg
import ewapt
import ewads

from ew import EwUser
from ewdistrict import EwDistrict
from ewtransport import EwTransport
from ewmarket import EwMarket
from ewmutation import EwMutation
from ewslimeoid import EwSlimeoid
from ewplayer import EwPlayer
from ewads import EwAd
from ewitem import EwItem

from ewhunting import EwEnemy, spawn_enemy
from ewworldevent import get_void_connection_pois

move_counter = 0


"""
	Returns true if the specified point of interest is a PvP zone.
"""
def poi_is_pvp(poi_name = None):
	poi = ewcfg.id_to_poi.get(poi_name)

	if poi != None:
		return poi.pvp
	
	return False



"""
	Returns data for POI if it isn't on the map.
"""
def fetch_poi_if_coordless(channel_name):
	if channel_name != None:
		poi = ewcfg.chname_to_poi.get(channel_name)
		
		if poi != None and poi.coord is None:
			return poi

	return None


"""
	Returns the fancy display name of the specified POI.
"""

def poi_id_to_display_name(poi_name = None):
	poi = ewcfg.id_to_poi.get(poi_name)

	if poi != None:
		return poi.str_name

	return "the city"

"""
	Point of Interest (POI) data model
"""
class EwPoi:
	# The typable single-word ID of this location.
	id_poi = ""

	# Acceptable alternative typable single-word names for this place.
	alias = []

	# The nice name for this place.
	str_name = ""

	# You find yourself $str_in $str_name
	str_in = "in"

	# You $str_enter $str_name
	str_enter = "enter"

	# A description provided when !look-ing here.
	str_desc = ""

	# (X, Y) location on the map (left, top) zero-based origin.
	coord = None
	coord_alias = []

	# Channel name associated with this POI
	channel = ""

	# Discord role associated with this zone (control channel visibility).
	role = None
	
	# Role that controls LAN voice/text channel visibility for any street/subzone/district - 6/6/20
	major_role = None
	
	# Role that controls subzone visibility for streets/districts - 6/6/20
	minor_role = None
	
	# Discord permissions associated with this zone (control channel visibility) - 5/28/20
	permissions = None

	# Zone allows PvP combat and interactions.
	pvp = True

	# Factions allowed in this zone.
	factions = []

	# Life states allowed in this zone.
	life_states = []

	# If true, the zone is inaccessible.
	closed = False

	# Message shown before entering the zone fails when it's closed.
	str_closed = None

	# Vendor names available at this POI.
	vendors = []

	# The value of the district
	property_class = ""
	
	# If the zone is a district
	is_district = False
	
	# If the zone is a gang base (Juvie's Row included)
	is_gangbase = False

	# If true, the zone is a district that can be controlled/captured
	is_capturable = False

	# If it's a subzone
	is_subzone = False

	#If it's an apartment
	is_apartment = False
	
	# if this zone is a street within a district
	is_street = False

	# What District/street each subzone is in. Subzones could potentially have multiple mother districts if they are between streets/districts.
	mother_districts = []
	
	# What District each street is attatched to
	father_district = ""

	# If it's a mobile zone
	is_transport = False

	# which type of transport
	transport_type = ""
	
	# default line to follow, if it's a transport
	default_line = ""

	# default station to start at, if it's a transport
	default_stop = ""
	
	# If a transport line stops here
	is_transport_stop = True

	# which transport lines stop here
	transport_lines = set()

	# if this zone belongs to the outskirts
	is_outskirts = False

	# id for the zone's community chest, if it has one
	community_chest = None

	# if you can fish in the zone
	is_pier = False

	# if the pier is in fresh slime or salt slime
	pier_type = None

	# if the poi is part of the tutorial
	is_tutorial = False

	# whether to show ads here
	has_ads = False

	# if you can write zines here
	write_manuscript = False

	# maximum degradation - zone ceases functioning when this value is reached
	max_degradation = 0

	# dict EwPoi -> int, that defines travel times into adjacent pois
	neighbors = None
	
	# The topic associated with that poi's channel
	topic = ""
	
	# The wiki page associated with that poi
	wikipage = ""

	def __init__(
		self,
		id_poi = "unknown", 
		alias = [],
		str_name = "Unknown",
		str_desc = "...",
		str_in = "in",
		str_enter = "enter",
		coord = None,
		coord_alias = [],
		channel = "",
		role = None,
		major_role = None,
		minor_role = None,
		permissions = None,
		pvp = True,
		factions = [],
		life_states = [],
		closed = False,
		str_closed = None,
		vendors = [],
		property_class = "",
		is_district = False,
		is_gangbase = False,
		is_capturable = False,
		is_subzone = False,
		is_apartment = False,
		is_street = False,
		mother_districts = [],
		father_district = "",
		is_transport = False,
		transport_type = "",
		default_line = "",
		default_stop = "",
		is_transport_stop = False,
		transport_lines = None,
		is_outskirts = False,
		community_chest = None,
		is_pier = False,
		pier_type = None,
		is_tutorial = False,
		has_ads = False,
		write_manuscript = False,
		max_degradation = 10000,
		neighbors = None,
		topic = "",
		wikipage = "",
	):
		self.id_poi = id_poi
		self.alias = alias
		self.str_name = str_name
		self.str_desc = str_desc
		self.str_in = str_in
		self.str_enter = str_enter
		self.coord = coord
		self.coord_alias = coord_alias
		self.channel = channel
		self.role = role
		self.major_role = major_role
		self.minor_role = minor_role
		self.permissions = permissions
		self.pvp = pvp
		self.factions = factions
		self.life_states = life_states
		self.closed = closed
		self.str_closed = str_closed
		self.vendors = vendors
		self.property_class = property_class
		self.is_district = is_district
		self.is_gangbase = is_gangbase
		self.is_capturable = is_capturable
		self.is_subzone = is_subzone
		self.is_apartment = is_apartment
		self.is_street = is_street
		self.mother_districts = mother_districts
		self.father_district = father_district
		self.is_transport = is_transport
		self.transport_type = transport_type
		self.default_line = default_line
		self.default_stop = default_stop
		self.is_transport_stop = is_transport_stop
		self.transport_lines = transport_lines
		self.is_outskirts = is_outskirts
		self.community_chest = community_chest
		self.is_pier = is_pier
		self.pier_type = pier_type
		self.is_tutorial = is_tutorial
		self.has_ads = has_ads
		self.write_manuscript = write_manuscript
		self.max_degradation = max_degradation
		self.topic = topic
		self.wikipage = wikipage
		
		self.neighbors = neighbors
		if self.neighbors == None:
			self.neighbors = {}

	#  0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54
map_world = [
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #0
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #1
	[ -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,120, -3, -3, -3, -3, -2,120,  0,  0,  0,  0,  0,  0,  0,  0,120, -3, -3, -3, -3, -2,120,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #2
	[ -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 60, -1, 60, -1, 60, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 60, -1, 60, -1, 60, -1, -1,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #3
	[ -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0, -1,  0, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0, -1,  0, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1 ], #4
	[ -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1,  0, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1,120, -1, -1, -1, -1, -1, -1, -1 ], #5
	[ -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, 60, -1, -1,  0,  0,  0,  0,  0,  0,  0, -1,  0, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1 ], #6
	[ -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -2, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, 60, -1, -1, -1, -1, -1, -1, 60, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -3, -1, -1, -1, -1, -1, -1, -1 ], #7
	[ -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, 30, -1, -1, 60, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -2, 30,  0,  0,  0,  0, 30, -2, 30,  0,  0,  0,  0, -1, -1, 60, -1, -1, -1, -1, -1, 60, -1, -1, -1, -1, -1, -1, -1 ], #8
	[ -1, -1, -1,120, -1, -1, -1, -1, -1, -1, -1,  0,  0, 30, -2, 30,  0,  0,  0,  0,  0, -1,  0, -1, -1, -1, 30, -1, -1, -1,  0, -1, -1, 30, -1, -1, -1, -1,  0,  0, 30, -2, 30,  0,  0,  0, -1,  0, -1, -1, -1, -1, -1, -1, -1 ], #9
	[ -1, -1, -1, -2, 60,  0,  0,  0,  0,  0, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, 60, -1,  0,  0,  0,  0, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, 30, -1,  0, -1, -1, -1, -1, -1, -1, -1 ], #10
	[ -1, -1, -1, -3, -1, -1, -1, -1, -1,  0, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0, 30, -2, 30,  0, -1, -1,  0, -1, -1, 30, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -2, 60,  0, -1, -1, -1, -1, -1, -1, -1 ], #11
	[ -1, -1, -1, -3, 60,  0,  0,  0, -1,  0, -1,  0, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, 30, -1, -1, -1, -1,  0, -1, -1, -2, 30,  0,  0,  0, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #12
	[ -1, -1, -1, -3, -1, -1, -1,  0, -1,  0, -1, 30, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1,  0, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #13
	[ -1, -1, -1, -3, 60,  0, -1,  0, -1,  0, 60, -2, 30,  0,  0,  0,  0, 30, -2, -1, -1, -1,  0, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1,  0,  0, 30, -2, 30,  0,  0,  0,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #14
	[ -1, -1, -1,120, -1,  0, -1,  0, -1, -1, -1, 30, -1, -1, -1,  0, -1, -1, 30, -1, -1, -1,  0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, 30, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #15
	[ -1, -1, -1,  0, -1,  0, -1,  0, -1, -1, -1,  0, -1, -1, -1, 30, -1, -1,  0, -1, -1, -1,  0,  0,  0,  0,  0, 30, -2, 30,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0,  0, 30, -2, 30,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #16
	[ -1, -1, -1,  0, -1,  0, -1,  0, -1,  0,  0,  0,  0,  0, 30, -2, -1, -1,  0, -1, -1, -1, 30, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #17
	[ -1, -1, -1,  0, -1,  0, -1,  0, -1, 30, -1, -1, -1, -1, -1, 30, -1, -1,  0,  0,  0, 30, -2, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #18
	[ -1, -1, -1,  0, -1,  0, -1,  0, 60, -2, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1,  0, -1,  0,  0,  0, 30, -2, 30,  0,  0,  0,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #19
	[ -1, -1, -1,  0, -1,  0, -1, -1, -1, 30, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, 30, -1, 30, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #20
	[ -1, -1, -1,  0, -1,  0, -1, -1, -1,  0,  0,  0,  0, 30, -2, 30,  0,  0,  0,  0, -1, -1,  0,  0,  0,  0,  0, 30, -2, -3, -3, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1,  0,  0, 30, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #21
	[ -1, -1, -1,  0, -1,  0, -1, -1, -1,  0, -1, -1, -1, -1, 30, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, 30, -1, -3, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #22
	[ -1, -1, -1,  0, -1,  0, -1, -1, -1,  0, -1, -1, -1, -1,  0, -1, 30, -1, -1,  0, -1, -1, -1, -1,  0,  0,  0,  0,  0, -1, -3, -1, -1, -1, -1, -1, 30, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #23
	[ -1, -1, -1,  0, -1,  0, -1, -1, -1, 30, 30,  0,  0,  0,  0, 30, -2, -1, -1,  0, 30, -2, 30,  0,  0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #24
	[ -1, -1, -1,  0, -1,  0,  0,  0, 60, -2, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, 30, -1, -1,  0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #25
	[ -1, -1, -1,  0, -1, -1, -1, -1, -1, 30,  0,  0,  0, 30, -2, 30,  0, 30, -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -2, 30,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #26
	[ -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, 60, -1, -1, -2, 30,  0,  0,  0, -1, -1, 30, -1,  0,  0,  0,  0, 30, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #27
	[ -1, -1, -1,  0, -1, -1,  0,  0,  0, 60, -2, -1, -1, -1,  0, -1, -1, 60, -1,  0, -1, -1,  0, 30, -2, 30,  0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #28
	[ -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1, 30, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, 60,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #29
	[ -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1, -2, 30,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 30, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #30
	[ -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1, 60, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #31
	[ -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #32
	[ -1, -1, -1,  0, -1, -1,  0, -1,  0,  0,  0,  0,  0,  0,  0, -1, -1,  0, -1,  0, -1, -1,  0, 30, -2, 30,  0,  0,  0,  0,  0,  0,  0, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #33
	[ -1, -1, -1,  0, -1, -1,  0, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1,  0, -1, -1, -1, -1, 60, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #34
	[ -1, -1, -1,  0, -1, -1,  0, -1,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #35
	[ -1, -1, -1,  0, -1, -1, 60, -1, 60, -1, 60, -1, -1, -1, -1, -1, -1, -1, -1, 60, -1, 60, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #36
	[ -1, -1, -1,  0,  0,120, -2, -3, -3, -3, -3,120,  0,  0,  0,  0,  0,  0,120, -2, -3, -3, 60,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #37
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ], #38
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2 ], #39
]
map_width = len(map_world[0])
map_height = len(map_world)


sem_wall = -1
sem_city = -2
sem_city_alias = -3

landmarks = {}

def pairToString(pair):
	return "({},{})".format("{}".format(pair[0]).rjust(2), "{}".format(pair[1]).ljust(2))

"""
	Find the cost to move through ortho-adjacent cells.
"""
def neighbors(coord):
	neigh = []

	if coord[1] > 0 and map_world[coord[1] - 1][coord[0]] != sem_wall:
		neigh.append((coord[0], coord[1] - 1))
	if coord[1] < (map_height - 1) and map_world[coord[1] + 1][coord[0]] != sem_wall:
		neigh.append((coord[0], coord[1] + 1))

	if coord[0] > 0 and map_world[coord[1]][coord[0] - 1] != sem_wall:
		neigh.append((coord[0] - 1, coord[1]))
	if coord[0] < (map_width - 1) and map_world[coord[1]][coord[0] + 1] != sem_wall:
		neigh.append((coord[0] + 1, coord[1]))

	return neigh


"""
	Directions and cost from coord to arrive at a destination.
"""
class EwPath:
	visited = None
	steps = None
	cost = 0
	iters = 0
	pois_visited = None

	def __init__(
		self,
		path_from = None,
		steps = [],
		cost = 0,
		visited = {},
		pois_visited = None
	):
		if path_from != None:
			self.steps = deepcopy(path_from.steps)
			self.cost = path_from.cost
			self.visited = deepcopy(path_from.visited)
			self.pois_visited = deepcopy(path_from.pois_visited)
		else:
			self.steps = steps
			self.cost = cost
			self.visited = visited
			if pois_visited == None:
				self.pois_visited = set()
			else:
				self.pois_visited = pois_visited
			

"""
	Add coord_next to the path.
"""
def path_step(path, poi_next, cost_next,  user_data, poi_end, landmark_mode = False):


	next_poi = poi_next

	if inaccessible(user_data = user_data, poi = next_poi):
			return False
	else:
		# check if we already got the movement bonus/malus for this district
		if not poi_next.id_poi in path.pois_visited:
			path.pois_visited.add(next_poi.id_poi)
			if len(user_data.faction) > 0 and next_poi.id_poi != poi_end.id_poi and next_poi.id_poi != path.steps[0].id_poi:
				district = EwDistrict(
					id_server = user_data.id_server,
					district = next_poi.id_poi
				)

				if district != None and len(district.controlling_faction) > 0:
					if user_data.faction == district.controlling_faction:
						cost_next -= ewcfg.territory_time_gain
					else:
						cost_next += ewcfg.territory_time_gain

	path.steps.append(poi_next)


	if landmark_mode and cost_next > ewcfg.territory_time_gain:
		cost_next -= ewcfg.territory_time_gain

	path.cost += cost_next

	return True

"""
	Returns a new path including all of path_base, with the next step coord_next.
"""
def path_branch(path_base, poi_next, cost_next, user_data, poi_end, landmark_mode = False):
	path_next = EwPath(path_from = path_base)

	if path_step(path_next, poi_next, cost_next, user_data, poi_end, landmark_mode) == False:
		return None
	
	return path_next

def score_map_from(
	poi_start = None,
	user_data = None,
	landmark_mode = False
):
	score_golf = math.inf
	score_map = {}
	for poi in ewcfg.poi_list:
		score_map[poi.id_poi] = score_golf

	paths_finished = []
	paths_walking = []

	poi_start = ewcfg.id_to_poi.get(poi_start)
	poi_end = None
	poi_end = None


	path_base = EwPath(
		steps = [ poi_start ],
		cost = 0,
		pois_visited = set([poi_start.id_poi]),
	)


	paths_walking.append(path_base)

	count_iter = 0
	while len(paths_walking) > 0:
		count_iter += 1

		paths_walking_new = []

		for path in paths_walking:
			step_last = path.steps[-1]
			score_current = score_map.get(step_last.id_poi)
			if path.cost >= score_current:
				continue

			score_map[step_last.id_poi] = path.cost

			step_penult = path.steps[-2] if len(path.steps) >= 2 else None


			path_base = path
			neighs = list(step_last.neighbors.keys())

			if step_penult != None and step_penult.id_poi in neighs:
				neighs.remove(step_penult.id_poi)

			num_neighbors = len(neighs)
			for i in range(num_neighbors):

				neigh = ewcfg.id_to_poi.get(neighs[i])
				neigh_cost = step_last.neighbors.get(neigh.id_poi)

				if neigh_cost == None:
					continue

				if i < num_neighbors - 1:
					branch = path_branch(path_base, neigh, neigh_cost, user_data, poi_end, landmark_mode)
					if branch != None:
						paths_walking_new.append(branch)

				else:
					if path_step(path_base, neigh, neigh_cost, user_data, poi_end, landmark_mode):
						paths_walking_new.append(path_base)


		paths_walking = paths_walking_new

	return score_map

def path_to(
	poi_start = None,
	poi_end = None,
	user_data = None,
	safe_path = None
):
	#ewutils.logMsg("beginning pathfinding")
	score_golf = math.inf
	score_map = {}
	for poi in ewcfg.poi_list:
		score_map[poi.id_poi] = math.inf

	paths_finished = []
	paths_walking = []

	pois_adjacent = []

	poi_start = ewcfg.id_to_poi.get(poi_start)
	poi_end = ewcfg.id_to_poi.get(poi_end)


	path_base = EwPath(
		steps = [ poi_start ],
		cost = 0,
		pois_visited = set([poi_start.id_poi]),
	)


	path_id = 0
	heapq.heappush(paths_walking, (path_base.cost + landmark_heuristic(path_base, poi_end), path_id, path_base))
	path_id += 1

	count_iter = 0
	while len(paths_walking) > 0:
		count_iter += 1

		path_tuple = heapq.heappop(paths_walking)

		path = path_tuple[-1]

		if path is not None:
			step_last = path.steps[-1]
			score_current = score_map.get(step_last.id_poi)
			if safe_path == True and (step_last.is_street or step_last.is_outskirts):
				continue
			if path.cost >= score_current:
				continue

			score_map[step_last.id_poi] = path.cost
			#ewutils.logMsg("visiting " + str(step_last))

			step_penult = path.steps[-2] if len(path.steps) >= 2 else None


			if poi_end != None:
				# Arrived at the actual destination?
				if step_last.id_poi == poi_end.id_poi:
					path_final = path
					if path_final.cost < score_golf:
						score_golf = path_final.cost
						paths_finished = []
					if path_final.cost <= score_golf:
						paths_finished.append(path_final)
					break

			else:
				# Looking for adjacent points of interest.
				poi_adjacent = step_last

				if poi_adjacent.id_poi != poi_start.id_poi:

					pois_adjacent.append(poi_adjacent)
					continue

			path_base = path
			neighs = list(step_last.neighbors.keys())
			
			if step_penult != None and step_penult.id_poi in neighs:
				neighs.remove(step_penult.id_poi)

			num_neighbors = len(neighs)
			i = 0
			for i in range(num_neighbors):

				neigh = ewcfg.id_to_poi.get(neighs[i])
				neigh_cost = step_last.neighbors.get(neigh.id_poi)
					
				if neigh_cost == None:
					continue

				if i < num_neighbors - 1:
					branch = path_branch(path_base, neigh, neigh_cost, user_data, poi_end)
					if branch != None:
						heapq.heappush(paths_walking, (branch.cost + landmark_heuristic(branch, poi_end), path_id, branch))
						path_id += 1
				else:
					if path_step(path_base, neigh, neigh_cost, user_data, poi_end):
						heapq.heappush(paths_walking, (path_base.cost + landmark_heuristic(path_base, poi_end), path_id, path_base))
						path_id += 1
						

	#ewutils.logMsg("finished pathfinding")

	if poi_end != None:
		path_true = None
		if len(paths_finished) > 0:
			path_true = paths_finished[0]
			path_true.iters = count_iter
		if path_true is None:
			ewutils.logMsg("Could not find a path.")
		return path_true
	else:
		return pois_adjacent

def landmark_heuristic(path, poi_end):
	if len(landmarks) == 0 or poi_end is None:
		return 0
	else:
		last_step = path.steps[-1]
		scores = []
		for lm in landmarks:
			score_map = landmarks.get(lm)
			score_path = score_map.get(last_step.id_poi)
			score_goal = score_map.get(poi_end.id_poi)
			scores.append(abs(score_path - score_goal))

		return max(scores)
			
	

def replace_with_inf(n):
	return math.inf

"""
	Debug method to draw the map, optionally with a path/route on it.
"""
def map_draw(path = None, coord = None):
	y = 0
	for row in map_world:
		outstr = ""
		x = 0

		for col in row:
			if col == sem_wall:
				col = "  "
			elif col == sem_city:
				col = "CT"
			elif col == sem_city_alias:
				col = "ct"
			elif col == 0:
				col = "██"
			elif col == 30:
				col = "[]"
			elif col == 20:
				col = "••"
			elif col == 60:
				col = "<>"
			elif col == 120:
				col = "=="

			if path != None:
				visited_set_y = path.visited.get(x)
				if visited_set_y != None and visited_set_y.get(y) != None:
					col = "." + col[-1]

			if coord != None and coord == (x, y):
				col = "O" + col[-1]
					
			outstr += "{}".format(col)
			x += 1

		print(outstr)
		y += 1

def inaccessible(user_data = None, poi = None):

	if poi == None or user_data == None:
		return True

	if user_data.life_state == ewcfg.life_state_observer:
		return False
	
	if user_data.life_state == ewcfg.life_state_shambler and poi.id_poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown, ewcfg.poi_id_juviesrow]:
		return True

	bans = user_data.get_bans()
	vouchers = user_data.get_vouchers()

	locked_districts_list = retrieve_locked_districts(user_data.id_server)

	if(
		len(poi.factions) > 0 and
		(set(vouchers).isdisjoint(set(poi.factions)) or user_data.faction != "") and
		user_data.faction not in poi.factions
	) or (
		len(poi.life_states) > 0 and
		user_data.life_state not in poi.life_states
	):
		return True
	elif(
		len(poi.factions) > 0 and 
		len(bans) > 0 and 
		set(poi.factions).issubset(set(bans))
	):
		return True
	elif poi.id_poi in locked_districts_list and user_data.life_state not in [ewcfg.life_state_executive, ewcfg.life_state_lucky]:
		return True
	else:
		return False
	
def retrieve_locked_districts(id_server):
	locked_districts_list = []
	
	locked_districts = ewutils.execute_sql_query(
		"SELECT {district} FROM global_locks WHERE id_server = %s AND {locked_status} = %s".format(
			district=ewcfg.col_district,
			locked_status=ewcfg.col_locked_status
		), (
			id_server,
			'true'
		))
	for district in locked_districts:
		locked_districts_list.append(district[0])
		
	return locked_districts_list



"""
	Go down the rabbit hole
"""
async def descend(cmd):
	user_data = EwUser(member = cmd.message.author, data_level = 1)
	void_connections = get_void_connection_pois(cmd.guild.id)

	# enter the void
	if user_data.poi in void_connections:
		travel_duration = int(ewcfg.travel_time_district / user_data.move_speed)
		response = "You descend down the flight of stairs and begin walking down a lengthy tunnel towards an identical set of ascending stairs. You will arrive on the other side in {} seconds.".format(travel_duration)
		descent_message = await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		global move_counter
		move_current = ewutils.moves_active.get(cmd.message.author.id)
		move_counter += 1
		move_current = ewutils.moves_active[cmd.message.author.id] = move_counter

		life_state = user_data.life_state
		faction = user_data.faction
		await asyncio.sleep(travel_duration)

		if user_data.life_state != life_state or faction != user_data.faction:
			try:
				await descent_message.delete()
				pass
			except:
				pass
			return

		user_data.poi = ewcfg.poi_id_thevoid
		user_data.time_lastenter = int(time.time())

		enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
		user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_vulnerable_districts, enlisted)
		
		user_data.persist()
		ewutils.end_trade(user_data.id_user)
		await ewrolemgr.updateRoles(client = ewutils.get_client(), member = cmd.message.author)
		await user_data.move_inhabitants(id_poi = ewcfg.poi_id_thevoid)
		try:
			await descent_message.delete()
			pass
		except:
			pass

		void_poi = ewcfg.id_to_poi.get(ewcfg.poi_id_thevoid)
		response = "You go up the flight of stairs and find yourself in {}.".format(void_poi.str_name)
		msg = await ewutils.send_message(cmd.client, ewutils.get_channel(cmd.guild, void_poi.channel), ewutils.formatMessage(cmd.message.author, response))
		await asyncio.sleep(20)
		try:
			await msg.delete()
			pass
		except:
			pass
		return
	else:
		return await move(cmd)
	
"""
	Player command to move themselves from one place to another.
"""
async def move(cmd = None, isApt = False):
	
	safe_path = False
	if cmd.tokens[0] == ewcfg.cmd_move_alt4 or cmd.tokens[0] == ewcfg.cmd_move_alt5:
		safe_path = True
	
	time_move_start = int(time.time())
	
	if isApt == False and ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))

	target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
	if target_name == None or len(target_name) == 0:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Where to?"))
	
	if target_name in ewcfg.streets:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "https://www.goodreads.com/quotes/106313-the-beginning-of-wisdom-is-to-call-things-by-their ...bitch"))

	player_data = EwPlayer(id_user=cmd.message.author.id)
	user_data = EwUser(id_user = cmd.message.author.id, id_server=player_data.id_server, data_level = 1)
	poi_current = ewcfg.id_to_poi.get(user_data.poi)
	poi = ewcfg.id_to_poi.get(target_name)
	if poi_current.is_apartment == True:
		isApt = True
	server_data = ewcfg.server_list[user_data.id_server]
	client = ewutils.get_client()
	member_object = server_data.get_member(user_data.id_user)

	movement_method = ""

	if user_data.get_inhabitee():
    # prevent ghosts currently inhabiting other players from moving on their own
		response = "You might want to **{}** of the poor soul you've been tormenting first.".format(ewcfg.cmd_letgo)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if ewutils.active_restrictions.get(user_data.id_user) != None and ewutils.active_restrictions.get(user_data.id_user) > 0:
		response = "You can't do that right now."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if poi == None:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Never heard of it."))

	if not ewutils.DEBUG and ewcfg.chname_to_poi.get(cmd.message.channel.name).id_poi != user_data.poi:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in your current district.").format(cmd.tokens[0]))

	if user_data.poi == ewcfg.debugroom:
		movement_method = "descending"
		try:
			if poi.id_poi == ewcfg.poi_id_slimeoidlab:
				movement_method = "walking"
		except:
			pass
	else:
		movement_method = "walking"

	if user_data.poi == ewcfg.debugroom and cmd.tokens[0] != (ewcfg.cmd_descend) and poi.id_poi != ewcfg.poi_id_slimeoidlab:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You can't move forwards or backwards in an {}, bitch.".format(ewcfg.debugroom_short)))
	elif user_data.poi != ewcfg.debugroom and cmd.tokens[0] == (ewcfg.cmd_descend):
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You can't move downwards on a solid surface, bitch."))

	# if fetch_poi_if_coordless(poi.channel) is not None: # Triggers if your destination is a sub-zone.
	# 	poi = fetch_poi_if_coordless(poi.channel)
	# 	mother_poi = ewcfg.id_to_poi.get(poi.mother_district)
	# 	if mother_poi is not None: # Reroute you to the sub-zone's mother district if possible.
	# 		target_name = poi.mother_district
	# 		poi = mother_poi

	if poi.id_poi == user_data.poi:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're already there, bitch."))
	elif isApt and poi.id_poi == user_data.poi[3:]:
		return await ewapt.depart(cmd=cmd)

	if inaccessible(user_data = user_data, poi = poi):
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're not allowed to go there (bitch)."))

	if user_data.life_state == ewcfg.life_state_corpse and user_data.poi == ewcfg.poi_id_thesewers:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You need to {} in the city before you can wander its streets.".format(ewcfg.cmd_manifest)))
	if isApt:
		poi_current = ewcfg.id_to_poi.get(user_data.poi[3:])

	#if poi.coord == None or poi_current == None or poi_current.coord == None:
	if len(poi.neighbors.keys()) == 0 or poi_current == None or len(poi_current.neighbors.keys()) == 0:
		if user_data.life_state == ewcfg.life_state_corpse and poi.id_poi == ewcfg.poi_id_thesewers:
			path = EwPath(cost = 60)
		else:
			path = None
	else:
		path = path_to(
			poi_start = poi_current.id_poi,
			poi_end = target_name,
			user_data = user_data,
			safe_path = safe_path
		)

		if path != None:
			path.cost = int(path.cost / user_data.move_speed)

	if path == None:
		if safe_path == True:
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "It's too dangerous to get there just by {}-ing.".format(cmd.tokens[0])))
		else:
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You don't know how to get there."))
	if isApt:
		path.cost += 20
	global move_counter

	# Check if we're already moving. If so, cancel move and change course. If not, register this course.
	move_current = ewutils.moves_active.get(cmd.message.author.id)
	move_counter += 1

	# Take control of the move for this player.
	move_current = ewutils.moves_active[cmd.message.author.id] = move_counter
	
	# Hard lock path costs to not be lower than 5 seconds.
	path.cost = max(path.cost, 5)

	minutes = int(path.cost / 60)
	seconds = path.cost % 60

	if user_data.has_soul == 1:
		walk_text = "walking"
	else:
		walk_text = "hopelessly trudging"
	
	if movement_method == "descending":
		msg_walk_start = await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You press the button labeled {}. You will arrive in {} seconds.".format(poi.str_name, seconds)))
	else:
		msg_walk_start = await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You begin {} to {}.{}".format(
			walk_text,
			poi.str_name,
			(" It's {} minute{}{} away.".format(
				minutes,
				("s" if minutes != 1 else ""),
				(" and {} seconds".format(seconds) if seconds > 4 else "")
			) if minutes > 0 else (" It's {} seconds away.".format(seconds) if seconds > 4 else ""))
		)))
		if isApt:
			await ewapt.depart(cmd=cmd, isGoto=True, movecurrent = move_current)

	time_move_end = int(time.time())

	#print('pathfinding in move function took {} seconds'.format(time_move_end - time_move_start))


	life_state = user_data.life_state
	faction = user_data.faction

	# Moving to or from a place not on the map (e.g. the sewers)
	#if poi.coord == None or poi_current == None or poi_current.coord == None:
	if len(poi.neighbors.keys()) == 0 or poi_current == None or len(poi_current.neighbors.keys()) == 0:
		if path.cost > 0:
			await asyncio.sleep(path.cost)

		if ewutils.moves_active[cmd.message.author.id] != move_current:
			return

		user_data = EwUser(id_user = cmd.message.author.id, id_server=player_data.id_server)

		# If the player dies or enlists or whatever while moving, cancel the move.
		if user_data.life_state != life_state or faction != user_data.faction:
			try:
				await msg_walk_start.delete()
				pass
			except:
				pass

			return

		user_data.poi = poi.id_poi
		user_data.time_lastenter = int(time.time())

		if user_data.poi in ewcfg.vulnerable_districts:
			enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
			user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_vulnerable_districts, enlisted)
		
		user_data.persist()

		ewutils.end_trade(user_data.id_user)

		await ewrolemgr.updateRoles(client = client, member = member_object)

		channel = cmd.message.channel

		# Send the message in the channel for this POI if possible, else in the origin channel for the move.

		for ch in server_data.channels:
			if ch.name == poi.channel:
				channel = ch
				break

		msg_walk_enter = await ewutils.send_message(cmd.client, 
			channel,
			ewutils.formatMessage(
				cmd.message.author,
				"You {} {}.".format(poi.str_enter, poi.str_name)
			)
		)
		
		try:
			await msg_walk_start.delete()
			await asyncio.sleep(30)
			await msg_walk_enter.delete()
			pass
		except:
			pass

	else:
		boost = 0
		
		step_list = []
		for step in path.steps:
			step_list.append(step.str_name)
		#print('path steps: {}'.format(step_list))

		# Perform move.
		for i in range(1, len(path.steps)):

			step = path.steps[i]

			val = poi_current.neighbors.get(step.id_poi)

			poi_current = step

			user_data = EwUser(id_user = cmd.message.author.id, id_server=player_data.id_server, data_level = 1)
			#mutations = user_data.get_mutations()
			if poi_current != None:


				if len(user_data.faction) > 0 and user_data.poi in ewcfg.capturable_districts:
					district = EwDistrict(
						id_server = user_data.id_server,
						district = user_data.poi
					)

					if district != None and len(district.controlling_faction) > 0 and i < (len(path.steps) - 1):
						if user_data.faction == district.controlling_faction:
							val -= ewcfg.territory_time_gain
						else:
							val += ewcfg.territory_time_gain

				val = int(val / user_data.move_speed)
				await asyncio.sleep(val)

				# Check to see if we have been interrupted and need to not move any farther.
				if ewutils.moves_active[cmd.message.author.id] != move_current:
					break

				user_data = EwUser(id_user = cmd.message.author.id, id_server=player_data.id_server)

				# If the player dies or enlists or whatever while moving, cancel the move.
				if user_data.life_state != life_state or faction != user_data.faction:
					try:
						await msg_walk_start.delete()
						pass
					except:
						pass

					return

				channel = cmd.message.channel

				# Prevent access to the zone if it's closed.
				if poi_current.closed == True:
					try:
						if poi_current.str_closed != None:
							message_closed = poi_current.str_closed
						else:
							message_closed = "The way into {} is blocked.".format(poi_current.str_name)

						# Send the message in the player's current if possible, else in the origin channel for the move.
						poi_current = ewcfg.id_to_poi.get(user_data.poi)
						for ch in server_data.channels:
							if ch.name == poi_current.channel:
								channel = ch
								break
					finally:
						return await ewutils.send_message(cmd.client, 
							channel,
							ewutils.formatMessage(
								cmd.message.author,
								message_closed
							)
						)

				# Send the message in the channel for this POI if possible, else in the origin channel for the move.
				for ch in server_data.channels:
					if ch.name == poi_current.channel:
						channel = ch
						break

				if user_data.poi != poi_current.id_poi:
					
					poi_previous = user_data.poi
					#print('previous poi: {}'.format(poi_previous))
					
					user_data.poi = poi_current.id_poi
					user_data.time_lastenter = int(time.time())

					if user_data.poi in ewcfg.vulnerable_districts:
						enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
						user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_vulnerable_districts, enlisted)
						
					user_data.persist()

					ewutils.end_trade(user_data.id_user)

					await ewrolemgr.updateRoles(client = client, member = member_object)

					# also move any ghosts inhabiting the player
					await user_data.move_inhabitants(id_poi = poi_current.id_poi)

					try:
						await msg_walk_start.delete()
						pass
					except:
						pass

					msg_walk_start = await ewutils.send_message(cmd.client, 
						channel,
						ewutils.formatMessage(
							cmd.message.author,
							"You {} {}.".format(poi_current.str_enter, poi_current.str_name)
						)
					)

					# SWILLDERMUK
					await ewutils.activate_trap_items(poi.id_poi, user_data.id_server, user_data.id_user)

					if poi_current.has_ads:
						ads = ewads.get_ads(id_server = user_data.id_server)
						if len(ads) > 0:
							id_ad = random.choice(ads)
							ad_data = EwAd(id_ad = id_ad)
							ad_response = ewads.format_ad_response(ad_data)
							await ewutils.send_message(cmd.client, channel, ewutils.formatMessage(cmd.message.author, ad_response))


		await asyncio.sleep(30)
		try:
			await msg_walk_start.delete()
			pass
		except:
			pass


"""
	Cancel any in progress move.
"""
async def halt(cmd):
	ewutils.moves_active[cmd.message.author.id] = 0
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You {} dead in your tracks.".format(cmd.cmd[1:])))

async def teleport(cmd):
	
	blj_used = False
	if cmd.tokens[0] == (ewcfg.cmd_prefix + 'blj'):
		blj_used = True
	
	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))

	time_now = int(time.time())
	user_data = EwUser(member = cmd.message.author)
	poi_now = user_data.poi
	mutations = user_data.get_mutations()
	response = ""
	resp_cont = ewutils.EwResponseContainer(id_server = cmd.guild.id)
	target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
	
	if ewutils.active_restrictions.get(user_data.id_user) != None and ewutils.active_restrictions.get(user_data.id_user) > 0:
		response = "You can't do that right now."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if ewcfg.mutation_id_quantumlegs in mutations:
		mutation_data = EwMutation(id_user = user_data.id_user, id_server = user_data.id_server, id_mutation = ewcfg.mutation_id_quantumlegs)
		if len(mutation_data.data) > 0:
			time_lastuse = int(mutation_data.data)
		else:
			time_lastuse = 0

		if time_lastuse + 180*60 > time_now:
			response = "You can't do that again yet. Try again in about {} minute(s)".format(math.ceil((time_lastuse + 180*60 - time_now)/60))
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		if cmd.tokens_count < 2 and not blj_used:
			response = "Teleport where?"
			return await ewutils.send_message(cmd.client, cmd.message.channel,ewutils.formatMessage(cmd.message.author, response))
		elif cmd.tokens_count < 2 and blj_used:
			response = "Backwards Long Jump where?"
			return await ewutils.send_message(cmd.client, cmd.message.channel,ewutils.formatMessage(cmd.message.author, response))

		poi = ewcfg.id_to_poi.get(target_name)

		if poi is None:
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Never heard of it."))

		if poi.id_poi == user_data.poi:
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're already there, bitch."))

		if inaccessible(user_data=user_data, poi=poi):
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're not allowed to go there (bitch)."))
			
		valid_destinations = set()
		neighbors = ewcfg.poi_neighbors.get(user_data.poi)
		for neigh in neighbors:
			valid_destinations.add(neigh)
			valid_destinations.update(ewcfg.poi_neighbors.get(neigh))

		if poi.id_poi not in valid_destinations:
			response = "You can't {} that far.".format(cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		# 30 second windup before teleport goes through
		windup_finished = True
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You get a running start to charge up your Quantum Legs..."))
		try:
			msg = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and 
														cmd.message.content.startswith(ewcfg.cmd_prefix))

			if msg != None:
				windup_finished = False
				
		except:
			windup_finished = True

		user_data = EwUser(member=cmd.message.author)
			
		if windup_finished and user_data.poi == poi_now:
			mutation_data = EwMutation(id_user=user_data.id_user, id_server=user_data.id_server, id_mutation=ewcfg.mutation_id_quantumlegs)

			mutation_data.data = str(time_now)
			mutation_data.persist()
			
			if not blj_used:
				response = "WHOOO-"
			else:
				response = "YAHOO! YAHOO! Y-Y-Y-Y-Y-"
				
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			
			poi_channel = ewutils.get_channel(cmd.guild, poi.channel)

			await ewutils.send_message(cmd.client, poi_channel, "A rift in time and space is pouring open! Something's coming through!!")
			
			await asyncio.sleep(5)
			
			if not blj_used:
				response = "-OOOP!"
			else:
				response = "-AHOO!"

			user_data = EwUser(member=cmd.message.author)

			ewutils.moves_active[cmd.message.author.id] = 0
			user_data.poi = poi.id_poi
			user_data.time_lastenter = int(time.time())

			if user_data.poi in ewcfg.vulnerable_districts:
				enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
				user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_vulnerable_districts, enlisted)
			
			user_data.persist()

			await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
			await user_data.move_inhabitants(id_poi = poi.id_poi)
			resp_cont.add_channel_response(poi.channel, ewutils.formatMessage(cmd.message.author, response))
			await resp_cont.post()

			# SWILLDERMUK
			await ewutils.activate_trap_items(poi.id_poi, user_data.id_server, user_data.id_user)
			
			return
		else:
			mutation_data = EwMutation(id_user=user_data.id_user, id_server=user_data.id_server, id_mutation=ewcfg.mutation_id_quantumlegs)

			mutation_data.data = str(time_now)
			mutation_data.persist()
			
			# Get the channel for the poi the user is currently in, just in case they've moved to a different poi before the teleportation went through.
			current_poi = ewcfg.id_to_poi.get(user_data.poi)
			current_channel = ewutils.get_channel(cmd.guild, current_poi.channel)
			
			response = "You slow down before the teleportation goes through."
			return await ewutils.send_message(cmd.client, current_channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		
		if not blj_used:
			response = "You don't have any toilet paper."
		else:
			response = "You don't even know what that MEANS."
			
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def teleport_player(cmd):
	author = cmd.message.author
	user_data = EwUser(member=author)
	
	if ewutils.DEBUG or author.guild_permissions.administrator or user_data.life_state == ewcfg.life_state_kingpin:
		pass
	else:
		return
	
	if cmd.mentions_count == 1:
		target = cmd.mentions[0]
	else:
		return
	
	destination = cmd.tokens[2].lower()
	
	new_poi = ewcfg.id_to_poi.get(destination)
	
	if target != None and new_poi != None:
		target_user = EwUser(member=target)
		target_player = EwPlayer(id_user=target_user.id_user)

		ewutils.moves_active[target_user.id_user] = 0

		target_user.poi = new_poi.id_poi
		target_user.persist()
		
		response = "{} has been teleported to {}".format(target_player.display_name, new_poi.id_poi)
		
		await ewrolemgr.updateRoles(client = cmd.client, member = target)
		
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))



"""
	Dump out the visual description of the area you're in.
"""
async def look(cmd):
	user_data = EwUser(member = cmd.message.author)

	poi = ewcfg.id_to_poi.get(user_data.poi)

	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	degrade_resp = ""
	if district_data.degradation >= poi.max_degradation:
		degrade_resp = ewcfg.str_zone_degraded.format(poi = poi.str_name) + "\n\n"
	void_resp = get_void_connections_resp(poi.id_poi, user_data.id_server)

	if poi.is_apartment:
		return await ewapt.apt_look(cmd=cmd)

	if poi.is_subzone or poi.id_poi == ewcfg.poi_id_thevoid: # Triggers if you input the command in the void or a sub-zone.

		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
			"You stand {} {}.\n\n{}\n\n<{}>\n{}\n\n{}".format(
				poi.str_in,
				poi.str_name,
				poi.str_desc,
				poi.wikipage,
				void_resp,
				degrade_resp,
			)
		))

	slimes_resp = get_slimes_resp(district_data)
	players_resp = get_players_look_resp(user_data, district_data)
	enemies_resp = get_enemies_look_resp(user_data, district_data)
	slimeoids_resp = get_slimeoids_resp(cmd.guild.id, poi)
	soul_resp = ""

	if slimeoids_resp != "":
		slimeoids_resp = "\n" + slimeoids_resp
	if poi.is_apartment:
		slimes_resp = ""
		players_resp = ""
		slimeoids_resp = ""
	if user_data.has_soul == 0:
		soul_resp = "\n\nYour soul brought color to the world. Now it all looks so dull."
	else:
		soul_resp = ""

	ad_resp = ""
	ad_formatting = ""
	if poi.has_ads:
		ads = ewads.get_ads(id_server = user_data.id_server)
		if len(ads) > 0:
			id_ad = random.choice(ads)
			ad_data = EwAd(id_ad = id_ad)
			ad_resp = ewads.format_ad_response(ad_data)
			ad_formatting = "\n\n..."

	# post result to channel
	if poi != None:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"You stand {} {}.\n\n{}\n\n<{}>{}\n\n{}...".format(
				poi.str_in,
				poi.str_name,
				poi.str_desc,
				poi.wikipage,
				void_resp,
				degrade_resp,
			)
		))

		if poi.id_poi == ewcfg.poi_id_thesphere:
			return

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"{}{}{}{}{}{}{}".format(
				slimes_resp,
				players_resp,
				slimeoids_resp,
				enemies_resp,
				soul_resp,
				("\n\n{}".format(
					ewcmd.weather_txt(cmd.guild.id)
				) if cmd.guild != None else ""),
				ad_formatting
			) #+ get_random_prank_item(user_data, district_data) # SWILLDERMUK
		))
		if len(ad_resp) > 0:
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
				cmd.message.author,
				ad_resp
			))

async def survey(cmd):
	user_data = EwUser(member=cmd.message.author)
	district_data = EwDistrict(district=user_data.poi, id_server=user_data.id_server)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	slimes_resp = get_slimes_resp(district_data)
	players_resp = get_players_look_resp(user_data, district_data)
	enemies_resp = get_enemies_look_resp(user_data, district_data)
	slimeoids_resp = get_slimeoids_resp(cmd.guild.id, poi)

	if slimeoids_resp != "":
		slimeoids_resp = "\n" + slimeoids_resp
	if poi.is_apartment:
		slimes_resp = ""
		players_resp = ""
		slimeoids_resp = ""

	# post result to channel
	if poi != None:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"You stand {} {}.\n\n{}{}{}{}{}".format(
				poi.str_in,
				poi.str_name,
				slimes_resp,
				players_resp,
				slimeoids_resp,
				enemies_resp,
				("\n\n{}".format(
					ewcmd.weather_txt(cmd.guild.id)
				) if cmd.guild != None else "")
			) #+ get_random_prank_item(user_data, district_data) # SWILLDERMUK
		))
		
		
	
"""
	Get information about an adjacent zone.
"""
async def scout(cmd):
	user_data = EwUser(member=cmd.message.author)
	user_poi = ewcfg.id_to_poi.get(user_data.poi)
	
	if ewutils.channel_name_is_poi(str(cmd.message.channel)) is False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))

	market_data = EwMarket(id_server = cmd.guild.id)
	mutations = user_data.get_mutations()

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "Who cares? These meatbags all look the same to you."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	# if no arguments given, scout own location
	if not len(cmd.tokens) > 1:
		poi = user_poi
	else:
		target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
		poi = ewcfg.id_to_poi.get(target_name)

	if poi == None:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Never heard of it."))

	else:
		# if scouting own location, treat as a !look alias
		#if poi.id_poi == user_poi.id_poi:
		#	return await look(cmd)

		# check if district is in scouting range
		is_neighbor = user_poi.id_poi in ewcfg.poi_neighbors[poi.id_poi] and poi.id_poi in ewcfg.poi_neighbors[user_poi.id_poi]
		is_current_transport_station = False
		if user_poi.is_transport:
			transport_data = EwTransport(id_server = user_data.id_server, poi = user_poi.id_poi)
			is_current_transport_station = transport_data.current_stop == poi.id_poi
		is_transport_at_station = False
		if poi.is_transport:
			transport_data = EwTransport(id_server = user_data.id_server, poi = poi.id_poi)
			is_transport_at_station = transport_data.current_stop == user_poi.id_poi

		#is_subzone = poi.is_subzone and poi.mother_district == user_poi.id_poi
		#is_mother_district = user_poi.is_subzone and user_poi.mother_district == poi.id_poi

		if (not is_neighbor) and (not is_current_transport_station) and (not is_transport_at_station) and (not poi.id_poi == user_poi.id_poi) and (not user_data.poi in poi.mother_districts) and (not poi.id_poi in user_poi.mother_districts):
			response = "You can't scout that far."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		if user_poi.id_poi in poi.mother_districts:
			response = "Why scout? Just pop your head in!"
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		# don't show low level players or enemies
		min_level = math.ceil((1/10) ** 0.25 * user_data.slimelevel)

		life_states = [ewcfg.life_state_enlisted]
		# get information about players in the district
		players_in_district = district_data.get_players_in_district(min_level = min_level, life_states = life_states)
		if user_data.id_user in players_in_district:
			players_in_district.remove(user_data.id_user)


		num_players = 0
		players_resp = "\n"
		detailed_players_resp = "You pick up the scent of the following gangsters:"
		for player in players_in_district:
			scoutee_data = EwUser(id_user = player, id_server = user_data.id_server)
			scoutee_player = EwPlayer(id_user = player)
			scoutee_mutations = scoutee_data.get_mutations()
			if ewcfg.mutation_id_whitenationalist in scoutee_mutations and market_data.weather == "snow":
				continue
			if ewcfg.mutation_id_threesashroud in scoutee_mutations and scoutee_data.life_state == ewcfg.life_state_enlisted:
				allies_in_district = district_data.get_players_in_district(min_level = min_level, life_states = [ewcfg.life_state_enlisted], factions = [scoutee_data.faction])
				if len(allies_in_district) > 3:
					continue
			if ewcfg.mutation_id_chameleonskin in scoutee_mutations:
				member = cmd.guild.get_member(scoutee_data.id_user)
				if member == None or member.status == discord.Status.offline:
					continue

			if ewcfg.mutation_id_aposematicstench in scoutee_mutations:
				num_players += math.floor(scoutee_data.slimelevel / 5)
				continue


			detailed_players_resp += "\n" + scoutee_player.display_name

			num_players += 1

		# No filtering is done on enemies themselves. Enemies that pose a threat to the player are filtered instead.
		enemies_in_district = district_data.get_enemies_in_district(scout_used=True)
		threats_in_district = district_data.get_enemies_in_district(min_level=min_level, scout_used=True)

		num_enemies = 0
		enemies_resp = ""
		
		num_threats = len(threats_in_district)
		threats_resp = ""

		detailed_enemies_resp = "You pick up the scent of the following enemies:\n"
		for enemy in enemies_in_district:
			enemy_data = EwEnemy(id_enemy=enemy)
			detailed_enemies_resp += "\n**{}**\n".format(enemy_data.display_name)
			num_enemies += 1

		if num_players == 0:
			players_resp += "You don’t notice any activity from this district."
		elif num_players == 1:
			players_resp += "You can hear the occasional spray of a spray can from a gangster in this district."
		elif num_players <= 5:
			players_resp += "You can make out a distant conversation between a few gangsters in this district."
		elif num_players <= 10:
			players_resp += "You can hear shouting and frequent gunshots from a group of gangsters in this district."
		else:
			players_resp += "You feel the ground rumble from a stampeding horde of gangsters in this district."

		if ewcfg.mutation_id_keensmell in mutations and num_players >= 1:
			players_resp += " " + detailed_players_resp

		# to avoid visual clutter, no scouting message is sent out for 0 enemies, and by extension, threats.
		if num_enemies == 0:
			enemies_resp = ""
		elif num_enemies == 1:
			enemies_resp += "You can faintly hear the bleating of an enemy coming from this district."
		elif num_enemies <= 5:
			enemies_resp += "You manage to pick up the sound of a few enemies howling amongst each other in this district."
		elif num_enemies <= 10:
			enemies_resp += "Your nerves tense due to the incredibly audible savagery coming from several enemies in this district."
		else:
			enemies_resp += "You feel shivers down your spine from the sheer amount of enemies ramping and raving within this district."

		if ewcfg.mutation_id_keensmell in mutations and num_enemies >= 1:
			enemies_resp += " " + detailed_enemies_resp

		if num_threats == 0:
			threats_resp = "The district doesn't really give off any strong sense of radiation."
		elif num_threats == 1:
			threats_resp += "You feel a small tingling sensation from nearby radiation."
		elif num_threats <= 5:
			threats_resp += "The radiation emanating from the district is giving you a slight headache."
		elif num_threats <= 10:
			threats_resp += "The radiation seeping in from the district is overwhelming. You feel like you're gonna puke."
		else:
			threats_resp += "Your skin begins to peel like a potato from the sheer amount of radiation close by!"

		if num_players == 0 and num_enemies >= 1:
			players_resp = ""
		elif num_players >= 1 and num_enemies == 0:
			enemies_resp = ""
			threats_resp = ""			
		elif num_players == 0 and num_enemies == 0:
			threats_resp = ""

		# post result to channel
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"**{}**:{}\n{}\n{}".format(
				poi.str_name,
				players_resp,
				enemies_resp,
				threats_resp,
			)
		))

"""
	Kicks idle players from subzones. Called every 15 minutes.
"""
async def kick(id_server):
	# Gets data for all living players from the database
	all_living_players = ewutils.execute_sql_query("SELECT {poi}, {id_user} FROM users WHERE id_server = %s AND {life_state} > 0 AND {time_last_action} < %s".format(
		poi = ewcfg.col_poi,
		id_user = ewcfg.col_id_user,
		time_last_action = ewcfg.col_time_last_action,
		life_state = ewcfg.col_life_state
	), (
		id_server,
		(int(time.time()) - ewcfg.time_kickout)
	))

	client = ewutils.get_client()

	for player in all_living_players:
		try:
			poi = ewcfg.id_to_poi[player[0]]
			id_user = player[1]
			user_data = EwUser(id_user = id_user, id_server = id_server)

			# checks if the player should be kicked from the subzone and kicks them if they should.
			if poi.is_subzone and poi.id_poi not in [ewcfg.poi_id_thesphere, ewcfg.poi_id_og_farms, ewcfg.poi_id_nuclear_beach_edge]:
				
				# Some subzones could potentially have multiple mother districts.
				# Make sure to get one that's accessible before attempting a proper kickout.
				mother_district_chosen = random.choice(poi.mother_districts)
				
				if inaccessible(user_data=user_data, poi=ewcfg.id_to_poi.get(mother_district_chosen)):
					# If the randomly chosen mother district is inaccessible, make one more attempt.
					mother_district_chosen = random.choice(poi.mother_districts)
				else:
					pass
				
				if not inaccessible(user_data=user_data, poi=ewcfg.id_to_poi.get(mother_district_chosen)):
				
					if user_data.life_state not in [ewcfg.life_state_kingpin, ewcfg.life_state_lucky, ewcfg.life_state_executive]:
						server = ewcfg.server_list[id_server]
						member_object = server.get_member(id_user)
	
						user_data.poi = mother_district_chosen
						user_data.time_lastenter = int(time.time())
						user_data.persist()
						await ewrolemgr.updateRoles(client = client, member = member_object)
	
						mother_district_channel = ewutils.get_channel(server, ewcfg.id_to_poi[mother_district_chosen].channel)
						response = "You have been kicked out for loitering! You can only stay in a sub-zone and twiddle your thumbs for 1 hour at a time."
						await ewutils.send_message(client, mother_district_channel, ewutils.formatMessage(member_object, response))
		except:
			ewutils.logMsg('failed to move inactive player out of subzone with poi {}: {}'.format(player[0], player[1]))

def get_slimes_resp(district_data):
	# get information about slime levels in the district
	
	slimes_resp = ""
	
	slimes = district_data.slimes
	if slimes < 10000:
		slimes_resp += "There are a few specks of slime splattered across the city streets."
	elif slimes < 100000:
		slimes_resp += "There are sparse puddles of slime filling potholes in the cracked city streets."
	elif slimes < 1000000:
		slimes_resp += "There are good amounts of slime pooling around storm drains and craters in the rundown city streets."
	else:
		slimes_resp += "There are large heaps of slime shoveled into piles to clear the way for cars and pedestrians on the slime-soaked city streets."

	return slimes_resp

def get_players_look_resp(user_data, district_data):
	# get information about players in the district
	
	# don't show low level players
	min_level = math.ceil((1 / 10) ** 0.25 * user_data.slimelevel)

	life_states = [ewcfg.life_state_corpse, ewcfg.life_state_juvenile, ewcfg.life_state_enlisted]
	
	players_in_district = district_data.get_players_in_district(min_level=min_level, life_states=life_states)
	if user_data.id_user in players_in_district:
		players_in_district.remove(user_data.id_user)

	num_players = len(players_in_district)
	players_resp = "\n\n"
	if num_players == 0:
		players_resp += "You don’t notice any activity from this district."
	elif num_players == 1:
		players_resp += "You can hear the occasional spray of a spray can from a gangster in this district."
	elif num_players <= 5:
		players_resp += "You can make out a distant conversation between a few gangsters in this district."
	elif num_players <= 10:
		players_resp += "You can hear shouting and frequent gunshots from a group of gangsters in this district."
	else:
		players_resp += "You feel the ground rumble from a stampeding horde of gangsters in this district."
	
	return players_resp
	
def get_enemies_look_resp(user_data, district_data):
	# lists off enemies in district
	
	# identifiers are converted into lowercase, then into emoticons for visual clarity.
	# server emoticons are also used for clarity
	
	enemies_in_district = district_data.get_enemies_in_district(classes=[ewcfg.enemy_class_normal, ewcfg.enemy_class_shambler])

	num_enemies = len(enemies_in_district)

	enemies_resp = "\n\n"

	if num_enemies == 0:
		enemies_resp = ""
	# enemies_resp += "You don't find any enemies in this district."
	elif num_enemies == 1:
		found_enemy_data = EwEnemy(id_enemy=enemies_in_district[0])

		if found_enemy_data.identifier != '':
			identifier_text = " {}".format(":regional_indicator_{}:".format(found_enemy_data.identifier.lower()))
		else:
			identifier_text = ""
			
		if found_enemy_data.ai == ewcfg.enemy_ai_coward or found_enemy_data.ai == ewcfg.enemy_ai_sandbag or (found_enemy_data.ai == ewcfg.enemy_ai_defender and found_enemy_data.id_target != user_data.id_user) or (found_enemy_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler) or (found_enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state != ewcfg.life_state_shambler):
			threat_emote = ewcfg.emote_slimeheart
		else:
			threat_emote = ewcfg.emote_slimeskull

		enemies_resp += ("You look around and find a\n{} **{}" + identifier_text + "**\nin this location.").format(threat_emote, found_enemy_data.display_name)
	else:
		enemies_resp += "You notice several enemies in this district, such as\n"
		for i in range(len(enemies_in_district) - 1):
			found_enemy_data = EwEnemy(id_enemy=enemies_in_district[i])

			if found_enemy_data.identifier != '':
				if not ewcfg.gvs_active:
					identifier_text = " {}".format(":regional_indicator_{}:".format(found_enemy_data.identifier.lower()))
				else:
					identifier_text = " {}, ({})".format(":regional_indicator_{}:".format(found_enemy_data.identifier.lower()), found_enemy_data.gvs_coord)
			else:
				identifier_text = ""

			if found_enemy_data.ai == ewcfg.enemy_ai_coward or found_enemy_data.ai == ewcfg.enemy_ai_sandbag or (
					found_enemy_data.ai == ewcfg.enemy_ai_defender and found_enemy_data.id_target != user_data.id_user):
				threat_emote = ewcfg.emote_slimeheart
			else:
				threat_emote = ewcfg.emote_slimeskull

			enemies_resp += ("{} **{}" + identifier_text + "**\n").format(threat_emote, found_enemy_data.display_name)
			
		final_enemy_data = EwEnemy(id_enemy=enemies_in_district[num_enemies - 1])

		if final_enemy_data.identifier != '':
			if not ewcfg.gvs_active:
				identifier_text = " {}".format(":regional_indicator_{}:".format(final_enemy_data.identifier.lower()))
			else:
				identifier_text = " {}, ({})".format( ":regional_indicator_{}:".format(final_enemy_data.identifier.lower()), final_enemy_data.gvs_coord)
		else:
			identifier_text = ""
			
		if final_enemy_data.ai == ewcfg.enemy_ai_coward or final_enemy_data.ai == ewcfg.enemy_ai_sandbag or (final_enemy_data.ai == ewcfg.enemy_ai_defender and final_enemy_data.id_target != user_data.id_user):
			threat_emote = ewcfg.emote_slimeheart
		else:
			threat_emote = ewcfg.emote_slimeskull

		enemies_resp += ("{} **{}" + identifier_text + "**").format(threat_emote, final_enemy_data.display_name)
	
	return enemies_resp

def get_slimeoids_resp(id_server, poi):
	slimeoids_resp = ""
	
	slimeoids_in_district = ewutils.get_slimeoids_in_poi(id_server=id_server, poi=poi.id_poi)

	for id_slimeoid in slimeoids_in_district:
		slimeoid_data = EwSlimeoid(id_slimeoid=id_slimeoid)
		if slimeoid_data.sltype == ewcfg.sltype_nega:
			slimeoids_resp += "\n{} is here.".format(slimeoid_data.name)
			
	return slimeoids_resp


"""
	Command that moves everyone from one district to another
"""
async def boot(cmd):
	author = cmd.message.author
	user_data = EwUser(member=cmd.message.author)

	if not author.guild_permissions.administrator and user_data.life_state != ewcfg.life_state_kingpin:
		response = "You do not have the power to move the masses from one location to another."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if len(cmd.tokens) != 3:
		response = 'Usage: !boot [location A] [location B]'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	destination_a = cmd.tokens[1]
	destination_b = cmd.tokens[2]

	old_poi = ewcfg.id_to_poi.get(destination_a)
	new_poi = ewcfg.id_to_poi.get(destination_b)
	

	if old_poi != None and new_poi != None:
	
		district_data = EwDistrict(district = old_poi.id_poi, id_server = user_data.id_server)
	
		users = district_data.get_players_in_district()
		
		for user in users:
			moved_user_data = EwUser(id_user=user, id_server=user_data.id_server)
			moved_user_data.poi = new_poi.id_poi
			moved_user_data.persist()
		response = "Everyone in {} has been moved to {}!".format(old_poi.id_poi, new_poi.id_poi)

	if destination_a == "all" and new_poi != None:
		for district in ewcfg.poi_list:
			district_data = EwDistrict(district = district.id_poi, id_server = user_data.id_server)

			users = district_data.get_players_in_district()

			for user in users:
				moved_user_data = EwUser(id_user = user, id_server = user_data.id_server)
				moved_user_data.poi = new_poi.id_poi
				moved_user_data.persist()
				
				
		response = "@everyone has been moved to {}".format(new_poi.id_poi)

	else:
		response = '**DEBUG:** Invalid POIs'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

# SWILLDERMUK
def get_random_prank_item(user_data, district_data):
	response = ""

	items_in_poi = ewutils.execute_sql_query(
		"SELECT {id_item} FROM items WHERE {id_owner} = %s AND {id_server} = %s".format(
			id_item=ewcfg.col_id_item,
			id_owner=ewcfg.col_id_user,
			id_server=ewcfg.col_id_server
		), (
			user_data.poi,
			district_data.id_server
		))

	prank_items = []
	
	for item in items_in_poi:
		id_item = item[0]
		possible_prank_item = EwItem(id_item=id_item)
		
		context = possible_prank_item.item_props.get('context')
		food_item_id = possible_prank_item.item_props.get('id_food')
		
		if (context == ewcfg.context_prankitem or food_item_id == "defectivecreampie"):
			prank_items.append(id_item)

	if len(prank_items) > 0:
		id_item = random.choice(prank_items)
		
		prank_item = EwItem(id_item=id_item)
		
		item_name = prank_item.item_props.get('item_name')
		if item_name == None:
			item_name = prank_item.item_props.get('food_name')
		
		response = "\n\nYou think you can spot a {} lying on the ground somewhere...".format(item_name)
	
	return response

"""
	Get information about all the pois in the poi list
"""
async def print_map_data(cmd):
	
	if not cmd.message.author.guild_permissions.administrator:
		return
	
	districts_count = 0
	subzones_count = 0
	apartments_count = 0
	outskirts_count = 0
	streets_count = 0
	transports_count = 0
	
	for poi in ewcfg.poi_list:
		
		if poi.is_district:
			districts_count += 1
			
			#print(poi.major_role)
			#print(poi.minor_role)
			
		if poi.is_subzone:
			subzones_count += 1
		if poi.is_apartment:
			apartments_count += 1
		if poi.is_outskirts:
			outskirts_count += 1
		if poi.is_street:
			streets_count += 1
			
			#print(poi.minor_role)
			
		if poi.is_transport:
			transports_count += 1
		
		neighbor_count = 0
		
		#print('\n\nNeighbors for {}\n====================='.format(poi.str_name))
		for neighbor_poi in ewcfg.poi_list:
			
			if neighbor_poi.id_poi in poi.neighbors.keys() and poi.id_poi not in neighbor_poi.neighbors.keys():
				print('\n========================\nsevered connection for POIs {} and {}'.format(poi.str_name, neighbor_poi.str_name))
			elif poi.id_poi in neighbor_poi.neighbors.keys() and neighbor_poi.id_poi not in poi.neighbors.keys():
				print('\n========================\nsevered connection for POIs {} and {}'.format(poi.str_name, neighbor_poi.str_name))
				
		if poi.is_subzone:
			for neighbor in poi.neighbors.keys():
				if neighbor not in poi.mother_districts:
					print('subzone {} has invalid mother district(s)'.format(poi.str_name))
			
			#if neighbor_poi.id_poi in poi.neighbors.keys():
			#if poi.id_poi in neighbor_poi.neighbors.keys():
				#neighbor_count += 1
				#print(neighbor_poi.str_name)
		
		#if poi.is_outskirts:
			#print('found {} neighbors for {}'.format(neighbor_count, poi.id_poi))
			
	# client = ewutils.get_client()
	# server = client.get_server(cmd.guild.id)
	# 		
	# rolenames = []
	# for role in server.roles:
	# 	rolenames.append(role.name)
	# 	
	# rolenames.sort()
	# for name in rolenames:
	# 	print(name)
	
	print("\n\nPOI LIST STATISTICS:\n{} districts\n{} subzones\n{} apartments\n{} outskirts\n{} streets\n{} transports\n\n".format(districts_count, subzones_count, apartments_count, outskirts_count, streets_count, transports_count))
	
	
def get_void_connections_resp(poi, id_server):
	response = ""
	void_connections = get_void_connection_pois(id_server)
	if poi == ewcfg.poi_id_thevoid:
		connected_poi_names = [ewcfg.id_to_poi.get(poi_id).str_name for poi_id in void_connections]
		response = "\nThe street sign in the intersection points to {}, and {}".format(", ".join(connected_poi_names), ewcfg.id_to_poi.get(ewcfg.poi_id_thesewers).str_name)
	elif poi in void_connections:
		response = "There's also a well lit staircase leading underground, but it looks too clean to be an entrance to the subway."
	return response