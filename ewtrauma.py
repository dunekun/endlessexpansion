import asyncio
import math
import time
import random

import discord


class EwTrauma:

	# The trauma's name
	id_trauma = ""

	# String used to describe the trauma when you !data yourself
	str_trauma_self = ""

	# String used to describe the trauma when you !data another player
	str_trauma = ""

	# the trauma's effect
	trauma_class = ""

	def __init__(self,
		id_trauma = "",
		str_trauma_self = "",
		str_trauma = "",
		trauma_class = "",
	):

		self.id_trauma = id_trauma

		if str_trauma_self == "":
			str_trauma_self = "You have the {} trauma.".format(self.id_trauma)
		self.str_trauma_self = str_trauma_self

		if str_trauma == "":
			str_trauma = "They have the {} trauma.".format(self.id_trauma)
		self.str_trauma = str_trauma

		self.trauma_class = trauma_class

class EwHitzone:
	

	name = ""

	aliases = []

	id_injury = ""

	def __init__(self,
		name = "",
		aliases = [],
		id_injury = "",
	):
		self.name = name
		self.aliases = aliases
		self.id_injury = id_injury


