import asyncio
import time
import random
import math

import ewcfg
import ewcaptcha
import ewutils
import ewitem
import ewmap
import ewrolemgr
import ewstats
import ewstatuseffects
import ewhunting

from ew import EwUser
from ewitem import EwItem
from ewmarket import EwMarket
from ewslimeoid import EwSlimeoid
from ewdistrict import EwDistrict
from ewplayer import EwPlayer
from ewhunting import EwEnemy
from ewstatuseffects import EwStatusEffect
from ewstatuseffects import EwEnemyStatusEffect

""" A weapon object which adds flavor text to kill/shoot. """
class EwWeapon:

	item_type = "weapon"

	# A unique name for the weapon. This is used in the database and typed by
	# users, so it should be one word, all lowercase letters.
	id_weapon = ""

	# An array of names that might be used to identify this weapon by the player.
	alias = None#[]

	# Displayed when !equip-ping this weapon
	str_equip = ""

	# Displayed when this weapon is used for a !kill
	str_kill = ""

	# Displayed to the dead victim in the sewers. Brief phrase such as "gunned down" etc.
	str_killdescriptor = ""

	# Displayed when viewing the !trauma of another player.
	str_trauma = ""

	# Displayed when viewing the !trauma of yourself.
	str_trauma_self = ""
	
	# like str_weapon but without the article
	str_name = ""

	# Displayed when viewing the !weapon of another player.
	str_weapon = ""

	# Displayed when viewing the !weapon of yourself.
	str_weapon_self = ""

	# Same as weapon and weapon_self, but used when the player's weapon skill is max.
	str_weaponmaster = ""
	str_weaponmaster_self = ""

	# Displayed when a non-lethal hit occurs.
	str_damage = ""

	# Displayed when a weapon backfires
	str_backfire = ""

	# Displayed when a weapon jams
	str_jammed = ""

	# Displayed when two players wielding the same weapon !spar with each other.
	str_duel = ""

	# Function that applies the special effect for this weapon.
	fn_effect = None#[]

	# Displayed when a weapon effect causes a critical hit.
	str_crit = ""

	# Displayed when a weapon effect causes a miss.
	str_miss = ""

	# Displayed when !inspect-ing
	str_description = ""

	# Displayed when reloading
	str_reload = ""

	# Displayed when the weapon used it's last ammo
	str_reload_warning = ""

	# Displayed when the weapon is unjammed
	str_unjam = ""
	
	# Displayed in a scalp's description.
	str_scalp = ""

	# Clip size
	clip_size = 0

	# Cost
	price = 0

	# Hard Cooldown 
	cooldown = 0

	# Vendor
	vendors = None#[]

	# Classes the weapon belongs to
	classes = None#[]

	acquisition = "dojo"

	# Statistics metric
	stat = ""
	
	# sap needed to fire
	sap_cost = 0

	# length of captcha you need to solve to fire
	captcha_length = 0

	#whether the weapon is a tool
	is_tool = 0

	#an array for storing extra string data for different tools
	tool_props = {}

	def __init__(
		self,
		id_weapon = "",
		alias =   [],
		str_equip = "",
		str_kill = "",
		str_killdescriptor = "",
		str_trauma = "",
		str_trauma_self = "",
		str_name = "",
		str_weapon = "",
		str_weapon_self = "",
		str_damage = "",
		str_backfire = "",
		str_duel = "",
		str_weaponmaster = "",
		str_weaponmaster_self = "",
		fn_effect = None,
		str_crit = "",
		str_miss = "",
		str_jammed = "",
		str_description = "",
		str_reload = "",
		str_reload_warning = "",
		str_unjam = "",
		str_scalp = "",
		clip_size = 0,
		price = 0,
		cooldown = 0,
		vendors = [],
		classes = [],
		acquisition = "dojo",
		stat = "",
		sap_cost = 0,
		captcha_length = 0,
		is_tool = 0,
		tool_props = None
	):
		self.item_type = ewcfg.it_weapon

		self.id_weapon = id_weapon
		self.alias = alias
		self.str_equip = str_equip
		self.str_kill = str_kill
		self.str_killdescriptor = str_killdescriptor
		self.str_trauma = str_trauma
		self.str_trauma_self = str_trauma_self
		self.str_name = str_name
		self.str_weapon = str_weapon
		self.str_weapon_self = str_weapon_self
		self.str_damage = str_damage
		self.str_backfire = str_backfire
		self.str_duel = str_duel
		self.str_weaponmaster = str_weaponmaster
		self.str_weaponmaster_self = str_weaponmaster_self
		self.fn_effect = fn_effect
		self.str_crit = str_crit
		self.str_miss = str_miss
		self.str_jammed = str_jammed
		self.str_description = str_description
		self.str_reload = str_reload
		self.str_reload_warning = str_reload_warning
		self.str_unjam = str_unjam
		self.str_scalp = str_scalp
		self.clip_size = clip_size
		self.price = price
		self.cooldown = cooldown
		self.vendors = vendors
		self.classes = classes
		self.acquisition = acquisition
		self.stat = stat
		self.sap_cost = sap_cost
		self.captcha_length = captcha_length
		self.is_tool = is_tool
		self.tool_props = tool_props,
		#self.str_name = self.str_weapon,



""" A data-moving class which holds references to objects we want to modify with weapon effects. """
class EwEffectContainer:
	miss = False
	crit = False
	backfire = False
	backfire_damage = 0
	jammed = False
	strikes = 0
	slimes_damage = 0
	slimes_spent = 0
	user_data = None
	shootee_data = None
	weapon_item = None
	time_now = 0
	bystander_damage = 0
	miss_mod = 0
	crit_mod = 0
	sap_damage = 0
	sap_ignored = 0

	# Debug method to dump out the members of this object.
	def dump(self):
		print("effect:\nmiss: {miss}\nbackfire: {backfire}\ncrit: {crit}\nstrikes: {strikes}\nslimes_damage: {slimes_damage}\nslimes_spent: {slimes_spent}\nexplosion_dmg: {bystander_damage}".format(
			miss = self.miss,
			backfire = self.backfire,
			crit = self.crit,
			strikes = self.strikes,
			slimes_damage = self.slimes_damage,
			slimes_spent = self.slimes_spent,
			bystander_damage = self.bystander_damage
		))

	def __init__(
		self,
		miss = False,
		crit = False,
		backfire = False,
		jammed = False,
		strikes = 0,
		slimes_damage = 0,
		slimes_spent = 0,
		user_data = None,
		shootee_data = None,
		weapon_item = None,
		time_now = 0,
		bystander_damage = 0,
		miss_mod = 0,
		crit_mod = 0,
		sap_damage = 0,
		sap_ignored = 0,
		backfire_damage = 0
	):
		self.miss = miss
		self.crit = crit
		self.backfire = backfire
		self.jammes = jammed
		self.strikes = strikes
		self.slimes_damage = slimes_damage
		self.slimes_spent = slimes_spent
		self.user_data = user_data
		self.shootee_data = shootee_data
		self.weapon_item = weapon_item
		self.time_now = time_now
		self.bystander_damage = bystander_damage
		self.miss_mod = miss_mod
		self.crit_mod = crit_mod
		self.sap_damage = sap_damage
		self.sap_ignored = sap_ignored
		self.backfire_damage = backfire_damage

def canAttack(cmd):
	response = ""
	time_now_float = time.time()
	time_now = int(time_now_float)
	user_data = EwUser(member = cmd.message.author)
	district_data = EwDistrict(id_server=user_data.id_server, district=user_data.poi)
	weapon_item = None
	weapon = None
	captcha = None

	tokens_lower = []
	for token in cmd.tokens:
		tokens_lower.append(token.lower())

	if user_data.weapon >= 0:
		weapon_item = EwItem(id_item = user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
		captcha = weapon_item.item_props.get('captcha')

	channel_poi = ewcfg.chname_to_poi.get(cmd.message.channel.name)
	#if user_data.life_state == ewcfg.life_state_enlisted or user_data.life_state == ewcfg.life_state_corpse:
	#	if user_data.life_state == ewcfg.life_state_enlisted:
	#		response = "Not so fast, you scrooge! Only Juveniles can attack during Slimernalia."
	#	else:
	#		response = "You lack the moral fiber necessary for violence."

	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		response = "You can't commit violence from here."
	elif ewmap.poi_is_pvp(user_data.poi) == False and cmd.mentions_count >= 1:
		response = "You must go elsewhere to commit gang violence."
	elif channel_poi.id_poi != user_data.poi and user_data.poi not in channel_poi.mother_districts:
		#Only way to do this right now is by using the gellphone
		response = "Alas, you still can't shoot people through your phone."
	elif cmd.mentions_count > 1:
		response = "One shot at a time!"
	elif user_data.hunger >= ewutils.hunger_max_bylevel(user_data.slimelevel):
		response = "You are too exhausted for gang violence right now. Go get some grub!"
	elif weapon != None and user_data.sap < weapon.sap_cost:
		response = "You don't have enough sap to attack. ({}/{})".format(user_data.sap, weapon.sap_cost)
	elif weapon != None and ewcfg.weapon_class_ammo in weapon.classes and int(weapon_item.item_props.get('ammo')) == 0:
		response = "You've run out of ammo and need to {}!".format(ewcfg.cmd_reload)
	elif weapon != None and ewcfg.weapon_class_thrown in weapon.classes and weapon_item.stack_size == 0:
		response = "You're out of {}! Go buy more at the {}".format(weapon.str_weapon, ewutils.formatNiceList(names = weapon.vendors, conjunction="or" ))
	elif weapon != None and weapon.cooldown + (float(weapon_item.item_props.get("time_lastattack")) if weapon_item.item_props.get("time_lastattack") != None else 0) > time_now_float:
		response = "Your {weapon_name} isn't ready for another attack yet!".format(weapon_name = weapon.id_weapon)
	elif weapon != None and weapon_item.item_props.get("jammed") == "True":
		response = "Your {weapon_name} is jammed, you will need to {unjam} it before shooting again.\nSecurity Code: **{captcha}**".format(weapon_name = weapon.id_weapon, unjam = ewcfg.cmd_unjam, captcha = ewutils.text_to_regional_indicator(captcha))
	elif weapon != None and ewcfg.weapon_class_captcha in weapon.classes and captcha not in [None, ""] and captcha.lower() not in tokens_lower:
		response = "ERROR: Invalid security code.\nEnter **{}** to proceed.".format(ewutils.text_to_regional_indicator(captcha))

	elif user_data.weapon == -1 and user_data.life_state != ewcfg.life_state_shambler:
		response = "How do you expect to engage in gang violence if you don't even have a weapon yet? Head to the Dojo in South Sleezeborough to pick one up!"
	elif cmd.mentions_count <= 0:
		# user is going after enemies rather than players

		# Get target's info.
		# converts ['THE', 'Lost', 'juvie'] into 'the lost juvie'
		huntedenemy = " ".join(cmd.tokens[1:]).lower()

		enemy_data = ewhunting.find_enemy(huntedenemy, user_data)

		user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_milkers
		user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_boober
		user_isslimecorp = user_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
		user_isshambler = user_data.life_state == ewcfg.life_state_shambler

		if (time_now - user_data.time_lastkill) < ewcfg.cd_kill:
			# disallow kill if the player has killed recently
			response = "Take a moment to appreciate your last slaughter."

		elif user_iskillers == False and user_isrowdys == False and user_isslimecorp == False and user_isshambler == False:
			# Only killers, rowdys, the cop killer, and rowdy fucker can shoot people.
			if user_data.life_state == ewcfg.life_state_juvenile:
				response = "Juveniles lack the moral fiber necessary for violence."
			else:
				response = "You lack the moral fiber necessary for violence."

		elif enemy_data != None:
			# enemy found, redirect variables to code in ewhunting
			response = ewcfg.enemy_targeted_string

		else:
			# no enemy is found within that district
			response = "Your bloodlust is appreciated, but ENDLESS WAR couldn't find what you were trying to kill."

	elif cmd.mentions_count == 1:
		# Get target's info.
		member = cmd.mentions[0]
		shootee_data = EwUser(member = member)

		user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_milkers
		user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_boober
		user_isslimecorp = user_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
		user_isshambler = user_data.life_state == ewcfg.life_state_shambler
  
		weapon_possession_data = user_data.get_weapon_possession()

		if shootee_data.life_state == ewcfg.life_state_kingpin:
			# Disallow killing generals.
			response = "He is hiding in his ivory tower and playing video games like a retard."

		elif (time_now - user_data.time_lastkill) < ewcfg.cd_kill:
			# disallow kill if the player has killed recently
			response = "Take a moment to appreciate your last slaughter."

		elif shootee_data.poi != user_data.poi:
			response = "You can't reach them from where you are."

		elif ewmap.poi_is_pvp(shootee_data.poi) == False:
			response = "{} is not mired in the ENDLESS WAR right now.".format(member.display_name)
			
		elif user_isshambler == True and len(district_data.get_enemies_in_district(classes = [ewcfg.enemy_class_gaiaslimeoid])) > 0:
			response = "You can't attack them, they're protected by Gaiaslimeoids!"
			
		# elif shootee_data.life_state == ewcfg.life_state_shambler and (user_iskillers == True or user_isrowdys == True or user_isslimecorp == True) and len(district_data.get_enemies_in_district(classes = [ewcfg.enemy_class_shambler])) > 0:
		# 	response = "You can't attack them, they're protected by a horde of enemy Shamblers!"

		elif user_iskillers == False and user_isrowdys == False and user_isslimecorp == False and user_isshambler == False:
			# Only killers, rowdys, the cop killer, and rowdy fucker can shoot people.
			if user_data.life_state == ewcfg.life_state_juvenile:
				response = "Juveniles lack the moral fiber necessary for violence."
			else:
				response = "You lack the moral fiber necessary for violence."

		elif (time_now - shootee_data.time_lastrevive) < ewcfg.invuln_onrevive:
			# User is currently invulnerable.
			response = "{} has died too recently and is immune.".format(member.display_name)

		elif shootee_data.life_state == ewcfg.life_state_corpse and shootee_data.busted == True:
			# Target is already dead and not a ghost.
			response = "{} is already dead.".format(member.display_name)
		
		elif shootee_data.life_state == ewcfg.life_state_corpse and ewcfg.status_ghostbust_id not in user_data.getStatusEffects():
			# Target is a ghost but user is not able to bust 
			response = "You don't know how to fight a ghost."

		elif shootee_data.life_state == ewcfg.life_state_corpse and shootee_data.poi == ewcfg.poi_id_thevoid:
			# Can't bust ghosts in their realm
			response = "{} is empowered by the void, and deflects your attacks without breaking a sweat.".format(member.display_name)

		elif weapon_possession_data and (shootee_data.id_user == weapon_possession_data[0]):
			# Target is possessing user's weapon
			response = "{}'s contract forbids you from harming them. You should've read the fine print.".format(member.display_name)

		elif time_now > shootee_data.time_expirpvp and not (shootee_data.life_state == ewcfg.life_state_shambler or shootee_data.get_inhabitee() == user_data.id_user or user_isshambler):
			# Target is neither flagged for PvP, nor a shambler, nor a ghost inhabiting the player. Player is not a shambler.
			response = "{} is not mired in the ENDLESS WAR right now.".format(member.display_name)

		# Identify if the shooter and the shootee are on the same team.
		#same_faction = False
		#if user_iskillers and shootee_data.faction == ewcfg.faction_milkers:
		#	same_faction = True
		#if user_isrowdys and shootee_data.faction == ewcfg.faction_boober:
		#	same_faction = True

	return response


def canCap(cmd):
	response = ""
	time_now_float = time.time()
	time_now = int(time_now_float)
	user_data = EwUser(member=cmd.message.author)
	sidearm_item = None
	sidearm = None
	captcha = None
	sidearm_viable = 0
	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = cmd.guild.id)

	tokens_lower = []
	for token in cmd.tokens:
		tokens_lower.append(token.lower())
	#alternate sidearm model that i'm saving just in case
	#if user_data.sidearm >= 0:
	#	sidearm_item = EwItem(id_item=user_data.sidearm)
	#	sidearm = ewcfg.weapon_map.get(sidearm_item.item_props.get("weapon_type"))
	#	captcha = sidearm_item.item_props.get('captcha')
	#	if ewcfg.weapon_class_paint in sidearm.classes:
	#		sidearm_viable = 1

	if user_data.weapon >= 0: #and sidearm_viable == 0
		sidearm_item = EwItem(id_item=user_data.weapon)
		sidearm = ewcfg.weapon_map.get(sidearm_item.item_props.get("weapon_type"))
		captcha = sidearm_item.item_props.get('captcha')
		if ewcfg.weapon_class_paint in sidearm.classes:
			sidearm_viable = 1


	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		response = "You can't spray graffiti from here."
	elif user_data.poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown]:
		response = "There’s no point, the rest of your gang has already covered this place in spraypaint. Focus on exporting your graffiti instead."
	elif user_data.poi == ewcfg.poi_id_juviesrow:
			response = "Nah, the Rowdys and Killers have both agreed this is neutral ground. You don’t want to start a diplomatic crisis, " \
					   "just stick to spraying down sick graffiti and splattering your rival gang across the pavement in the other districts."
	elif district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
	elif not user_data.poi in ewcfg.capturable_districts:
		response = "This zone cannot be captured."
		if poi.is_district == True:
			response += " To take this district, you need to enter into the streets."
	elif sidearm != None and ewcfg.weapon_class_thrown in sidearm.classes and sidearm_item.stack_size == 0:
		response = "You're out of {}! Go buy more at the {}".format(sidearm.str_weapon, ewutils.formatNiceList(names=sidearm.vendors,  conjunction="or"))
	elif sidearm != None and sidearm.cooldown + (float(sidearm_item.item_props.get("time_lastattack")) if sidearm_item.item_props.get("time_lastattack") != None else 0) > time_now_float:
		response = "Your {weapon_name} isn't ready for another spray yet!".format(weapon_name=sidearm.id_weapon)
	elif sidearm != None and ewcfg.weapon_class_captcha in sidearm.classes and captcha not in [None, ""] and captcha.lower() not in tokens_lower:
		response = "ERROR: Invalid security code. Enter **{}** to proceed.".format(ewutils.text_to_regional_indicator(captcha))
	elif user_data.life_state != ewcfg.life_state_enlisted:
		response = "Juveniles are too cowardly and/or centrist to be vandalizing anything."
	elif sidearm != None and ewcfg.weapon_class_ammo in sidearm.classes and int(sidearm_item.item_props.get('ammo')) <= 0:
		response = "You've run out of ammo and need to {}!".format(ewcfg.cmd_reload)
	elif sidearm_viable == 0:
		response = "With what, your piss? Get some paint from Based Hardware and stop fucking around."

	return response

""" Player deals damage to another player. """



async def attack(cmd):

	time_now_float = time.time()
	time_now = int(time_now_float)
	response = ""
	deathreport = ""
	levelup_response = ""
	shambler_resp = ""
	coinbounty = 0
	resp_cont = ewutils.EwResponseContainer(id_server = cmd.guild.id)
	market_data = EwMarket(id_server = cmd.guild.id)

	user_data = EwUser(member = cmd.message.author, data_level = 1)
	slimeoid = EwSlimeoid(member = cmd.message.author)
	weapon = None
	weapon_item = None
	if user_data.weapon >= 0:
		weapon_item = EwItem(id_item = user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))

	response = canAttack(cmd)

	if response == "":
		# Get shooting player's info
		if user_data.slimelevel <= 0: 
			user_data.slimelevel = 1
			user_data.persist()

		# Get target's info.
		member = cmd.mentions[0]
		if member.id == cmd.message.author.id:
			response = "Try {}.".format(ewcfg.cmd_suicide)
			resp_cont.add_channel_response(cmd.message.channel.name, response)
			return await resp_cont.post()
		else:
			shootee_data = EwUser(member = member, data_level = 1)
		shootee_slimeoid = EwSlimeoid(member = member)
		shootee_name = member.display_name


		shootee_weapon = None
		shootee_weapon_item = None
		if shootee_data.weapon >= 0:
			shootee_weapon_item = EwItem(id_item = shootee_data.weapon)
			shootee_weapon = ewcfg.weapon_map.get(shootee_weapon_item.item_props.get("weapon_type"))

		user_mutations = user_data.get_mutations()
		shootee_mutations = shootee_data.get_mutations()

		district_data = EwDistrict(district = user_data.poi, id_server = cmd.guild.id)

		miss = False
		crit = False
		backfire = False
		backfire_damage = 0
		jammed = False
		strikes = 0
		bystander_damage = 0
		miss_mod = 0
		crit_mod = 0
		dmg_mod = 0
		sap_damage = 0
		sap_ignored = 0

		# Weaponized flavor text.
		hitzone = get_hitzone()
		randombodypart = hitzone.name
		if random.random() < 0.5:
			randombodypart = random.choice(hitzone.aliases)
		
		shooter_status_mods = get_shooter_status_mods(user_data, shootee_data, hitzone)
		shootee_status_mods = get_shootee_status_mods(shootee_data, user_data, hitzone)

		miss_mod += round(shooter_status_mods['miss'] + shootee_status_mods['miss'], 2)
		crit_mod += round(shooter_status_mods['crit'] + shootee_status_mods['crit'], 2)
		dmg_mod += round(shooter_status_mods['dmg'] + shootee_status_mods['dmg'], 2)

		if shootee_weapon != None:
			if ewcfg.weapon_class_heavy in shootee_weapon.classes:
				miss_mod -= 0.1
				crit_mod += 0.05

		slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 60)
		slimes_damage = int((slimes_spent * (10 + user_data.attack)) * (100 + (user_data.weaponskill * 5)) / 100.0)

		if user_data.weaponskill < 5:
			miss_mod += (5 - user_data.weaponskill) / 10

		if weapon is None:
			slimes_damage /= 2  # penalty for not using a weapon, otherwise fists would be on par with other weapons
		slimes_dropped = shootee_data.totaldamage + shootee_data.slimes

		slimes_damage += int(slimes_damage * dmg_mod)

		user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_milkers

		if shootee_data.life_state == ewcfg.life_state_corpse:
			# Attack a ghostly target
			coinbounty = int(shootee_data.bounty / ewcfg.slimecoin_exchangerate)
			user_data.change_slimecoin(n = coinbounty, coinsource = ewcfg.coinsource_bounty)

			ewstats.track_maximum(user = user_data, metric = ewcfg.stat_biggest_bust_level, value = shootee_data.slimelevel)

			# Steal items
			#ewitem.item_loot(member = member, id_user_target = cmd.message.author.id)

			shootee_data.id_killer = user_data.id_user
			die_resp = shootee_data.die(cause = ewcfg.cause_busted)

			response = "{name_target}\'s ghost has been **BUSTED**!!".format(name_target = member.display_name)

			if coinbounty > 0:
				response += "\n\n SlimeCorp transfers {:,} SlimeCoin to {}\'s account.".format(coinbounty, cmd.message.author.display_name)

			# adjust busts
			ewstats.increment_stat(user = user_data, metric = ewcfg.stat_ghostbusts)

			# pay sap cost
			if weapon != None:
				user_data.sap -= weapon.sap_cost
				user_data.limit_fix()

			# Persist every users' data.
			user_data.persist()
			shootee_data.persist()
			if die_resp != resp_cont:
				resp_cont.add_response_container(die_resp)
			resp_cont.add_channel_response(cmd.message.channel.name, response)
			
			resp_cont.add_member_to_update(member)

		else:
			#hunger drain
			user_data.hunger += ewcfg.hunger_pershot * ewutils.hunger_cost_mod(user_data.slimelevel)

			#randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]

			# Weapon-specific adjustments
			if weapon != None and weapon.fn_effect != None:

				# Build effect container
				ctn = EwEffectContainer(
					miss = miss,
					backfire=backfire,
					crit = crit,
					jammed=jammed,
					slimes_damage = slimes_damage,
					slimes_spent = slimes_spent,
					user_data = user_data,
					weapon_item = weapon_item,
					shootee_data = shootee_data,
					time_now = time_now_float,
					bystander_damage = bystander_damage,
					miss_mod = miss_mod,
					crit_mod = crit_mod,
					sap_damage = sap_damage,
					sap_ignored = sap_ignored,
					backfire_damage = backfire_damage
				)

				# Make adjustments
				weapon.fn_effect(ctn)

				# Apply effects for non-reference values
				miss = ctn.miss
				backfire = ctn.backfire
				crit = ctn.crit
				jammed = ctn.jammed
				slimes_damage = ctn.slimes_damage
				slimes_spent = ctn.slimes_spent
				strikes = ctn.strikes
				bystander_damage = ctn.bystander_damage
				sap_damage = ctn.sap_damage
				sap_ignored = ctn.sap_ignored
				backfire_damage = ctn.backfire_damage
				# user_data and shootee_data should be passed by reference, so there's no need to assign them back from the effect container.

				if (slimes_spent > user_data.slimes):
					# Not enough slime to shoot.
					response = "You don't have enough slime to attack. ({:,}/{:,})".format(user_data.slimes, slimes_spent)
					return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

				weapon_item.item_props['time_lastattack'] = time_now_float
				weapon_item.persist()
				
				# Spend slimes, to a minimum of zero
				user_data.change_slimes(n = (-user_data.slimes if slimes_spent >= user_data.slimes else -slimes_spent), source = ewcfg.source_spending)

				user_data.sap -= weapon.sap_cost
				user_data.limit_fix()
				user_data.persist()

				if weapon.id_weapon == ewcfg.weapon_id_garrote:
					shootee_data.persist()
					response = "You wrap your wire around {}'s neck...".format(member.display_name)
					resp_cont.add_channel_response(cmd.message.channel.name, response)
					resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)
					await resp_cont.post()
					msg = await cmd.client.wait_for('message', timeout = 5, check = lambda message: message.author == member)

					user_data = EwUser(member = cmd.message.author, data_level = 1)
					shootee_data = EwUser(member = member, data_level = 1)

					# One of the players died in the meantime
					if user_data.life_state == ewcfg.life_state_corpse or shootee_data.life_state == ewcfg.life_state_corpse:
						return
					# A user left the district or strangling was broken
					elif msg != None or user_data.poi != shootee_data.poi:
						return
					else:
						shootee_data.clear_status(ewcfg.status_strangled_id)
						#shootee_data.persist()
					
				# Remove a bullet from the weapon
				if ewcfg.weapon_class_ammo in weapon.classes:
					weapon_item.item_props['ammo'] = int(weapon_item.item_props.get("ammo")) - 1

				# Remove one item from stack
				if ewcfg.weapon_class_thrown in weapon.classes:
					weapon_item.stack_size -= 1

				life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_shambler]
				factions = ["", user_data.faction if backfire else shootee_data.faction]

				# Burn players in district
				if ewcfg.weapon_class_burning in weapon.classes:
					if not miss:
						resp = burn_bystanders(user_data=user_data, burn_dmg=bystander_damage, life_states=life_states, factions=factions, district_data=district_data)
						resp_cont.add_response_container(resp)

				if ewcfg.weapon_class_exploding in weapon.classes:
					if not miss:
						resp = weapon_explosion(user_data=user_data, shootee_data=shootee_data, district_data=district_data, market_data = market_data, life_states=life_states, factions=factions, slimes_damage=bystander_damage, backfire=backfire, time_now=time_now, target_enemy=False, sap_damage = 2)
						resp_cont.add_response_container(resp)

			# can't hit lucky lucy
			if shootee_data.life_state == ewcfg.life_state_lucky:
				miss = True

			if miss or backfire or jammed:
				slimes_damage = 0
				sap_damage = 0
				weapon_item.item_props["consecutive_hits"] = 0
				crit = False

			if crit:
				sap_damage += 1

			if user_data.life_state == ewcfg.life_state_shambler:
				sap_damage += 1	

			# Remove !revive invulnerability.
			user_data.time_lastrevive = 0

			# apply attacker damage mods
			slimes_damage *= damage_mod_attack(
				user_data = user_data,
				user_mutations = user_mutations,
				market_data = market_data,
				district_data = district_data
			)

			# apply defender damage mods
			slimes_damage *= damage_mod_defend(
				shootee_data = shootee_data,
				shootee_mutations = shootee_mutations,
				market_data = market_data,
				shootee_weapon = shootee_weapon
			)
			
			if shootee_weapon != None:
				if sap_damage > 0 and ewcfg.weapon_class_defensive in shootee_weapon.classes:
					sap_damage -= 1

			sap_armor = get_sap_armor(shootee_data = shootee_data, sap_ignored = sap_ignored)
			slimes_damage *= sap_armor
			slimes_damage = int(max(slimes_damage, 0))

			sap_damage = min(sap_damage, shootee_data.hardened_sap)

			injury_severity = get_injury_severity(shootee_data, slimes_damage, crit)

			# Damage stats
			ewstats.track_maximum(user = user_data, metric = ewcfg.stat_max_hitdealt, value = slimes_damage)
			ewstats.change_stat(user = user_data, metric = ewcfg.stat_lifetime_damagedealt, n = slimes_damage)

			# Slimes from this shot might be awarded to the boss.
			role_boss = (ewcfg.role_copkiller if user_iskillers else ewcfg.role_rowdyfucker)
			boss_slimes = 0
			user_inital_level = user_data.slimelevel

			was_juvenile = False
			was_shambler = False
			was_killed = False
			was_shot = False

			if shootee_data.life_state in [ewcfg.life_state_shambler, ewcfg.life_state_enlisted, ewcfg.life_state_juvenile, ewcfg.life_state_lucky, ewcfg.life_state_executive]:
				# User can be shot.
				if shootee_data.life_state == ewcfg.life_state_juvenile:
					was_juvenile = True

				if shootee_data.life_state == ewcfg.life_state_shambler:
					was_shambler = True
				was_shot = True

			if was_shot:
				# Flag the user for PvP

				user_poi = ewcfg.id_to_poi.get(user_data.poi)
				user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_attack, True)

				resp_cont.add_member_to_update(cmd.message.author)

				if slimes_damage >= shootee_data.slimes - shootee_data.bleed_storage:
					was_killed = True
					if ewcfg.mutation_id_thickerthanblood in user_mutations:
						slimes_damage = 0
					else:
						slimes_damage = max(shootee_data.slimes - shootee_data.bleed_storage, 0)

				sewer_data = EwDistrict(district = ewcfg.poi_id_thesewers, id_server = cmd.guild.id)
				# move around slime as a result of the shot
				if was_shambler or was_juvenile or user_data.faction == shootee_data.faction:
					slimes_drained = int(3 * slimes_damage / 4) # 3/4
					slimes_toboss = 0
				else:
					slimes_drained = 0
					slimes_toboss = int(slimes_damage / 2)

				damage = slimes_damage

				slimes_tobleed = int((slimes_damage - slimes_toboss - slimes_drained) / 2)
				if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
					slimes_tobleed = 0
				if ewcfg.mutation_id_bleedingheart in shootee_mutations:
					slimes_tobleed *= 2

				slimes_directdamage = slimes_damage - slimes_tobleed
				slimes_splatter = slimes_damage - slimes_toboss - slimes_tobleed - slimes_drained

				# Damage victim's wardrobe (heh, WARdrobe... get it??)
				victim_cosmetics = ewitem.inventory(
					id_user = member.id,
					id_server = cmd.guild.id,
					item_type_filter = ewcfg.it_cosmetic
				)

				onbreak_responses = []

				for cosmetic in victim_cosmetics:
					if not int(cosmetic.get('soulbound')) == 1:
					
						c = EwItem(cosmetic.get('id_item'))
	
						# Damage it if the cosmetic is adorned and it has a durability limit
						if c.item_props.get("adorned") == 'true' and c.item_props['durability'] is not None:
	
							#print("{} current durability: {}:".format(c.item_props.get("cosmetic_name"), c.item_props['durability']))
	
							durability_afterhit = int(c.item_props['durability']) - slimes_damage
	
							#print("{} durability after next hit: {}:".format(c.item_props.get("cosmetic_name"), durability_afterhit))
	
							if durability_afterhit <= 0: # If it breaks
								c.item_props['durability'] = durability_afterhit
								c.persist()
	
	
								shootee_data.persist()
	
								onbreak_responses.append(str(c.item_props['str_onbreak']).format(c.item_props['cosmetic_name']))
	
								ewitem.item_delete(id_item = c.id_item)
	
							else:
								c.item_props['durability'] = durability_afterhit
								c.persist()
	
						else:
							pass

				market_data.splattered_slimes += slimes_damage
				market_data.persist()
				user_data.splattered_slimes += slimes_damage
				user_data.persist()
				boss_slimes += slimes_toboss
				district_data.change_slimes(n = slimes_splatter, source = ewcfg.source_killing)
				shootee_data.bleed_storage += slimes_tobleed
				shootee_data.change_slimes(n = - slimes_directdamage, source = ewcfg.source_damage)
				shootee_data.hardened_sap -= sap_damage
				sewer_data.change_slimes(n = slimes_drained)
				sewer_data.persist()

				if was_killed:
					#adjust statistics
					ewstats.increment_stat(user = user_data, metric = ewcfg.stat_kills)
					ewstats.track_maximum(user = user_data, metric = ewcfg.stat_biggest_kill, value = int(slimes_dropped))
					if user_data.slimelevel > shootee_data.slimelevel:
						ewstats.increment_stat(user = user_data, metric = ewcfg.stat_lifetime_ganks)
					elif user_data.slimelevel < shootee_data.slimelevel:
						ewstats.increment_stat(user = user_data, metric = ewcfg.stat_lifetime_takedowns)

					if shootee_data.life_state == ewcfg.life_state_shambler:
						ewstats.increment_stat(user = user_data, metric = ewcfg.stat_shamblers_killed)

					if weapon != None:
						weapon_item.item_props["kills"] = (int(weapon_item.item_props.get("kills")) if weapon_item.item_props.get("kills") != None else 0) + 1
						weapon_item.item_props["totalkills"] = (int(weapon_item.item_props.get("totalkills"))  if weapon_item.item_props.get("totalkills") != None else 0) + 1
						ewstats.increment_stat(user = user_data, metric = weapon.stat)
						
						# Give a bonus to the player's weapon skill for killing a stronger player.
						if shootee_data.slimelevel >= user_data.slimelevel and shootee_data.slimelevel >= user_data.weaponskill:
							user_data.add_weaponskill(n = 1, weapon_type = weapon.id_weapon)

					# Collect bounty
					coinbounty = int(shootee_data.bounty / ewcfg.slimecoin_exchangerate)  # 100 slime per coin
					
					if shootee_data.slimes >= 0:
						user_data.change_slimecoin(n = coinbounty, coinsource = ewcfg.coinsource_bounty)

					# Steal items
					#ewitem.item_loot(member = member, id_user_target = cmd.message.author.id)

					#add bounty
					user_data.add_bounty(n = (shootee_data.bounty / 2) + (slimes_dropped / 4))
					
					# Scalp text
					if weapon != None:
						scalp_text = weapon.str_scalp
					else:
						scalp_text = ""
					
					if shootee_data.life_state != ewcfg.life_state_shambler:
						# Drop shootee scalp
						ewitem.item_create(
							item_type = ewcfg.it_cosmetic,
							id_user = cmd.message.author.id,
							id_server = cmd.guild.id,
							item_props = {
								'id_cosmetic': 'scalp',
								'cosmetic_name': "{}'s scalp".format(shootee_name),
								'cosmetic_desc': "A scalp.{}".format(scalp_text),
								'str_onadorn': ewcfg.str_generic_onadorn,
								'str_unadorn': ewcfg.str_generic_unadorn,
								'str_onbreak': ewcfg.str_generic_onbreak,
								'rarity': ewcfg.rarity_patrician,
								'attack': 1,
								'defense': 0,
								'speed': 0,
								'ability': None,
								'durability': int(ewutils.slime_bylevel(shootee_data.slimelevel) / 4),
								'original_durability': int(ewutils.slime_bylevel(shootee_data.slimelevel) / 4),
								'size': 1,
								'fashion_style': ewcfg.style_cool,
								'freshness': 10,
								'adorned': 'false'
							}
						)
					elif ewcfg.status_modelovaccine_id in user_data.getStatusEffects():
						shootee_data.degradation = 0
						shambler_resp = "Your purified slime seeps into and emulsifies in their mangled corpse, healing their degraded body. When they revive, they’ll be a normal slimeboi like the rest of us. A pure, homogenous race of ENDLESS WAR fearing juveniles. It brings a tear to your eye."

					# release bleed storage
					if ewcfg.mutation_id_thickerthanblood in user_mutations:
						slimes_todistrict = 0
						slimes_tokiller = shootee_data.slimes
					else:
						slimes_todistrict = shootee_data.slimes / 2
						slimes_tokiller = shootee_data.slimes / 2
					district_data.change_slimes(n = slimes_todistrict, source = ewcfg.source_killing)
					levelup_response = user_data.change_slimes(n = slimes_tokiller, source = ewcfg.source_killing)
					if ewcfg.mutation_id_fungalfeaster in user_mutations:
						user_data.hunger = 0

					# if shootee_data.life_state != ewcfg.life_state_shambler:
					# 	user_data.degradation -= int(shootee_data.slimelevel / 10)

					user_data.persist()
					district_data.persist()
					# Player was killed.
					shootee_data.id_killer = user_data.id_user
					die_resp = shootee_data.die(cause = ewcfg.cause_killing)
					#shootee_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)

					user_data = EwUser(member = cmd.message.author, data_level = 1)
					district_data = EwDistrict(district = district_data.name, id_server = district_data.id_server)

					kill_descriptor = "beaten to death"
					if weapon != None:
						response = weapon.str_damage.format(
							name_player = cmd.message.author.display_name,
							name_target = member.display_name,
							hitzone = randombodypart,
							strikes = strikes
						)
						kill_descriptor = weapon.str_killdescriptor
						if crit:
							response += " {}".format(weapon.str_crit.format(
								name_player = cmd.message.author.display_name,
								name_target = member.display_name,
								hitzone = randombodypart,
							))

						response = ""

						if len(onbreak_responses) != 0:
							for onbreak_response in onbreak_responses:
								response += "\n\n" + onbreak_response

						response += "\n\n{}".format(weapon.str_kill.format(
							name_player = cmd.message.author.display_name,
							name_target = member.display_name,
							emote_skull = ewcfg.emote_slimeskull
						))

						if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
							response += "\n" + weapon.str_reload_warning.format(name_player = cmd.message.author.display_name)

						if ewcfg.weapon_class_captcha in weapon.classes:
							new_captcha = ewutils.generate_captcha(length = weapon.captcha_length)
							response += "\nNew security code: **{}**".format(ewutils.text_to_regional_indicator(new_captcha))
							weapon_item.item_props['captcha'] = new_captcha
							weapon_item.persist()

						shootee_data.trauma = weapon.id_weapon

					else:
						response = ""

						if len(onbreak_responses) != 0:
							for onbreak_response in onbreak_responses:
								response = onbreak_response + "\n\n"

						response += "{name_target} is hit!!\n\n{name_target} has died.".format(name_target = member.display_name)

						shootee_data.trauma = ewcfg.trauma_id_environment

					if shootee_data.faction != "" and shootee_data.faction == user_data.faction:
						shootee_data.trauma = ewcfg.trauma_id_betrayal

					if slimeoid.life_state == ewcfg.slimeoid_state_active:
						brain = ewcfg.brain_map.get(slimeoid.ai)
						response += "\n\n" + brain.str_kill.format(slimeoid_name = slimeoid.name)

					if shootee_slimeoid.life_state == ewcfg.slimeoid_state_active:
						brain = ewcfg.brain_map.get(shootee_slimeoid.ai)
						response += "\n\n" + brain.str_death.format(slimeoid_name = shootee_slimeoid.name)
					
					if coinbounty > 0:
						response += "\n\n SlimeCorp transfers {:,} SlimeCoin to {}\'s account.".format(coinbounty, cmd.message.author.display_name)
      
					weapon_possession = user_data.get_weapon_possession()
					if weapon_possession:
						response += fulfill_ghost_weapon_contract(weapon_possession, market_data, user_data, cmd.message.author.display_name)

					if shambler_resp != "":
						response += "\n\n" + shambler_resp

					shootee_data.persist()
					resp_cont.add_response_container(die_resp)
					resp_cont.add_channel_response(cmd.message.channel.name, response)
				else:
					# A non-lethal blow!
					
					# apply injury
					if injury_severity > 0:
						shootee_data.apply_injury(hitzone.id_injury, injury_severity, user_data.id_user)

					if weapon != None:
						if miss:
							response = "{}".format(weapon.str_miss.format(
								name_player = cmd.message.author.display_name,
								name_target = member.display_name
							))
						elif backfire:
							response = "{}".format(weapon.str_backfire.format(
								name_player = cmd.message.author.display_name,
								name_target = member.display_name
							))

							if user_data.slimes - user_data.bleed_storage <= backfire_damage:
								district_data.change_slimes(n = user_data.slimes)
								district_data.persist()
								shootee_data.persist()
								user_data.trauma = ewcfg.trauma_id_environment
								die_resp = user_data.die(cause = ewcfg.cause_backfire)
								district_data = EwDistrict(district = district_data.name, id_server = district_data.id_server)
								shootee_data = EwUser(member = member, data_level = 1)
								resp_cont.add_member_to_update(cmd.message.author)
								resp_cont.add_response_container(die_resp)
							else:
								district_data.change_slimes(n = backfire_damage / 2)
								user_data.change_slimes(n = -backfire_damage / 2,  source = ewcfg.source_self_damage)
								user_data.bleed_storage += int(backfire_damage / 2)

						elif jammed:
							response = "{}".format(weapon.str_jammed.format(
								name_player = cmd.message.author.display_name,
								name_target = member.display_name
							))
						else:
							response = weapon.str_damage.format(
								name_player = cmd.message.author.display_name,
								name_target = member.display_name,
								hitzone = randombodypart,
								strikes = strikes
							)
							if crit:
								response += " {}".format(weapon.str_crit.format(
									name_player = cmd.message.author.display_name,
									name_target = member.display_name,
									hitzone = randombodypart,
								))

							sap_response = ""
							if sap_damage > 0:
								sap_response = " and {sap_damage} hardened sap".format(sap_damage = sap_damage)

							response += " {target_name} loses {damage:,} slime{sap_response}!".format(
								target_name = member.display_name,
								damage = damage,
								sap_response = sap_response
							)

							if len(onbreak_responses) != 0:
								for onbreak_response in onbreak_responses:
									response += "\n\n" + onbreak_response
						
						if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
							response += "\nn"+weapon.str_reload_warning.format(name_player = cmd.message.author.display_name)

						if ewcfg.weapon_class_captcha in weapon.classes or jammed:
							new_captcha = ewutils.generate_captcha(length = weapon.captcha_length)
							response += "\nNew security code: **{}**".format(ewutils.text_to_regional_indicator(new_captcha))
							weapon_item.item_props['captcha'] = new_captcha
							weapon_item.persist()
					else:
						if miss:
							response = "{target_name} dodges your strike.".format(target_name = member.display_name)
						else:
							response = "{target_name} is hit!! {target_name} loses {damage:,} slime!".format(
								target_name = member.display_name,
								damage = damage
							)

							if len(onbreak_responses) != 0:
								for onbreak_response in onbreak_responses:
									response += "\n\n" + onbreak_response

					resp_cont.add_channel_response(cmd.message.channel.name, response)
			else:
				response = 'You are unable to attack {}.'.format(member.display_name)
				resp_cont.add_channel_response(cmd.message.channel.name, response)

			# Add level up text to response if appropriate
			if user_inital_level < user_data.slimelevel:
				resp_cont.add_channel_response(cmd.message.channel.name, "\n" + levelup_response)
			# Team kills don't award slime to the kingpin.
			if user_data.faction != shootee_data.faction and user_data.life_state != ewcfg.life_state_shambler:
				# Give slimes to the boss if possible.
				kingpin = ewutils.find_kingpin(id_server = cmd.guild.id, kingpin_role = role_boss)

				if kingpin:
					
					kingpin.change_slimes(n = boss_slimes)
					kingpin.persist()

			# Persist every users' data.
			user_data.persist()
			if user_data.weapon > 0:
				weapon_item.persist()

			shootee_data.persist()
			if shootee_weapon_item != None:
				shootee_weapon_item = EwItem(id_item = shootee_weapon_item.id_item)
				shootee_weapon_item.item_props["consecutive_hits"] = 0
				shootee_weapon_item.persist()

			district_data.persist()

			# Assign the corpse role to the newly dead player.
			if was_killed:
				resp_cont.add_member_to_update(member)
				# announce death in kill feed channel
				#killfeed_channel = ewutils.get_channel(cmd.guild, ewcfg.channel_killfeed)
				killfeed_resp = resp_cont.channel_responses[cmd.message.channel.name]
				for r in killfeed_resp:
					resp_cont.add_channel_response(ewcfg.channel_killfeed, r)
				resp_cont.format_channel_response(ewcfg.channel_killfeed, cmd.message.author)
				resp_cont.add_channel_response(ewcfg.channel_killfeed, "`-------------------------`")

				# Flag the user for PvP

				user_poi = ewcfg.id_to_poi.get(user_data.poi)
				user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_kill, True)

				user_data.persist()
				resp_cont.add_member_to_update(cmd.message.author)

			#await ewutils.send_message(cmd.client, killfeed_channel, ewutils.formatMessage(cmd.message.author, killfeed_resp))

			# Send the response to the player.
			resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)

		await resp_cont.post()
		
	elif response == ewcfg.enemy_targeted_string:
		#TODO - Move this to it's own function in ewhunting or merge it into the previous code block somehow
		
		# Enemy has been targeted rather than a player
		await attackEnemy(cmd, user_data, weapon, resp_cont, weapon_item, slimeoid, market_data, time_now_float)
		
	else:
		resp_cont.add_channel_response(cmd.message.channel.name, response)
		resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)
		
		await resp_cont.post()

""" player kills themself """
async def suicide(cmd):
	response = ""

	resp_cont = ewutils.EwResponseContainer(id_server = cmd.guild.id)

	# Only allowed in the combat zone.
	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		response = "You must go into the city to commit {}.".format(cmd.tokens[0][1:])
	else:
		# Get the user data.
		user_data = EwUser(member = cmd.message.author)
		if user_data.life_state == ewcfg.life_state_shambler:
			response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


		user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_milkers
		user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_boober
		user_isgeneral = user_data.life_state == ewcfg.life_state_kingpin
		user_isjuvenile = user_data.life_state == ewcfg.life_state_juvenile
		user_isdead = user_data.life_state == ewcfg.life_state_corpse
		user_isexecutive = user_data.life_state == ewcfg.life_state_executive
		user_islucky = user_data.life_state == ewcfg.life_state_lucky

		if user_isdead:
			response = "Too late for that."
		elif user_isjuvenile:
			response = "Juveniles are too cowardly for suicide."
		elif user_isgeneral:
			response = "\*click* Alas, your gun has jammed."
		elif user_iskillers or user_isrowdys or user_isexecutive or user_islucky or user_isjuvenile:
			if ewutils.active_restrictions.get(user_data.id_user) != None and ewutils.active_restrictions.get(user_data.id_user) > 0:
				response = "You can't do that right now."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response)) 

			slimes_total = user_data.slimes
			slimes_drained = int(slimes_total * 0.1)
			slimes_todistrict = slimes_total - slimes_drained
				
			sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=user_data.id_server)
			sewer_data.change_slimes(n = slimes_drained)
			#print(sewer_data.degradation)
			sewer_data.persist()

			district_data = EwDistrict(district = user_data.poi, id_server = cmd.guild.id)
			district_data.change_slimes(n = slimes_todistrict, source = ewcfg.source_killing)
			district_data.persist()

			# Set the id_killer to the player himself, remove his slime and slime poudrins.
			user_data.id_killer = cmd.message.author.id
			user_data.trauma = ewcfg.trauma_id_suicide
			user_data.visiting = ewcfg.location_id_empty
			die_resp = user_data.die(cause = ewcfg.cause_suicide)
			resp_cont.add_response_container(die_resp)
			user_data.persist()

			# Assign the corpse role to the player. He dead.
			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

			if user_data.has_soul == 1:
				response = '{} has willingly returned to the slime. {}'.format(cmd.message.author.display_name, ewcfg.emote_slimeskull)
			else:
				response = "Ahh. As it should be. {}".format(ewcfg.emote_slimeskull)

		else:
			# This should never happen. We handled all the role cases. Just in case.
			response = "\*click* Alas, your gun has jammed."

	# Send the response to the player.
	resp_cont.add_channel_response(cmd.message.channel.name, ewutils.formatMessage(cmd.message.author, response))
	await resp_cont.post()

""" Damage all players in a district; Exploding weapon's effect """
def weapon_explosion(user_data = None, shootee_data = None, district_data = None, market_data = None, life_states = None, factions = None, slimes_damage = 0, backfire = None, time_now = 0, target_enemy = None, sap_damage = 0, sap_ignored = 0):
	
	enemy_data = None
	if user_data != None and shootee_data != None and district_data != None:
		user_player = EwPlayer(id_user=user_data.id_user, id_server=user_data.id_server)
		if target_enemy == False:
			shootee_player = EwPlayer(id_user=shootee_data.id_user, id_server=shootee_data.id_server)
		else:
			enemy_data = shootee_data
			
			# This makes it so that a display name can still be accessed regardless if a player or enemy is the target of the attack
			shootee_player = shootee_data

		weapon_item = EwItem(id_item = user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))

		client = ewutils.get_client()
		server = client.get_guild(user_data.id_server)
		
		channel = ewcfg.id_to_poi.get(user_data.poi).channel

		resp_cont = ewutils.EwResponseContainer(id_server=user_data.id_server)

		bystander_users = district_data.get_players_in_district(life_states=life_states, factions=factions, pvp_only=True)
		bystander_enemies = district_data.get_enemies_in_district()

		for bystander in bystander_users:
			# Don't damage the shooter or the shootee a second time
			
			# If an enemy is being targeted, check id_enemy instead of id_user when going through bystander_users
			checked_id = None
			if target_enemy:
				checked_id = shootee_data.id_enemy
			else:
				checked_id = shootee_data.id_user
			
			if bystander != user_data.id_user and bystander != checked_id:
				response = ""

				target_data = EwUser(id_user=bystander, id_server=user_data.id_server, data_level = 1)
				target_player = EwPlayer(id_user=bystander, id_server=user_data.id_server)

				target_iskillers = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_milkers
				target_isrowdys = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_boober
				target_isjuvenile = target_data.life_state == ewcfg.life_state_juvenile	
				target_isshambler = target_data.life_state == ewcfg.life_state_shambler

				role_boss = (ewcfg.role_copkiller if user_data.faction == ewcfg.faction_milkers else ewcfg.role_rowdyfucker)
				boss_slimes = 0

				target_weapon = None
				if target_data.weapon >= 0:
					target_weapon_item = EwItem(id_item = target_data.weapon)
					target_weapon = ewcfg.weapon_map.get(target_weapon_item.item_props.get("weapon_type"))


				# apply defensive mods
				slimes_damage_target = slimes_damage * damage_mod_defend(
					shootee_data = target_data,
					shootee_mutations = target_data.get_mutations(),
					shootee_weapon = target_weapon,
					market_data = market_data,
				)

				# apply sap armor
				sap_armor = get_sap_armor(shootee_data = target_data, sap_ignored = sap_ignored)
				slimes_damage_target *= sap_armor
				slimes_damage_target = int(max(0, slimes_damage_target))

				slimes_dropped = target_data.totaldamage + target_data.slimes

				was_killed = False

				if slimes_damage_target >= target_data.slimes - target_data.bleed_storage:
					was_killed = True
					slimes_damage_target = max(target_data.slimes - target_data.bleed_storage, 0)
					
				sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=user_data.id_server)

				# move around slime as a result of the shot
				if target_isshambler or target_isjuvenile or user_data.faction == target_data.faction:
					slimes_drained = int(3 * slimes_damage_target / 4) # 3/4
					slimes_toboss = 0
				else:
					slimes_drained = 0
					slimes_toboss = int(slimes_damage_target / 2)

				damage = slimes_damage_target
				

				slimes_tobleed = int((slimes_damage_target - slimes_toboss - slimes_drained) / 2)

				slimes_directdamage = slimes_damage_target - slimes_tobleed
				slimes_splatter = slimes_damage_target - slimes_toboss - slimes_tobleed - slimes_drained

				boss_slimes += slimes_toboss
				district_data.change_slimes(n = slimes_splatter, source = ewcfg.source_killing)
				target_data.bleed_storage += slimes_tobleed
				target_data.change_slimes(n = - slimes_directdamage, source = ewcfg.source_damage)
				sewer_data.change_slimes(n = slimes_drained)
				sewer_data.persist()

				sap_damage_target = min(sap_damage, target_data.hardened_sap)
				target_data.hardened_sap -= sap_damage_target

				if was_killed:
					#adjust statistics
					ewstats.increment_stat(user = user_data, metric = ewcfg.stat_kills)
					ewstats.track_maximum(user = user_data, metric = ewcfg.stat_biggest_kill, value = int(slimes_dropped))
					if user_data.slimelevel > target_data.slimelevel:
						ewstats.increment_stat(user = user_data, metric = ewcfg.stat_lifetime_ganks)
					elif user_data.slimelevel < target_data.slimelevel:
						ewstats.increment_stat(user = user_data, metric = ewcfg.stat_lifetime_takedowns)

					# Collect bounty
					coinbounty = int(target_data.bounty / ewcfg.slimecoin_exchangerate)

					#add bounty
					user_data.add_bounty(n = (target_data.bounty / 2) + (slimes_dropped / 4))

					user_data.change_slimecoin(n = coinbounty, coinsource = ewcfg.coinsource_bounty)

					# Give a bonus to the player's weapon skill for killing a stronger player.
					if target_data.slimelevel >= user_data.slimelevel:
						user_data.add_weaponskill(n = 1, weapon_type = weapon.id_weapon)

					district_data.change_slimes(n = target_data.slimes/2, source = ewcfg.source_killing)
					levelup_resp = user_data.change_slimes(n = target_data.slimes/2, source = ewcfg.source_killing)

					target_data.id_killer = user_data.id_user

					target_data.trauma = ewcfg.trauma_id_environment
					target_data.die(cause = ewcfg.cause_killing)
					#target_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
					target_data.persist()

					response += "{} was killed by an explosion during your fight with {}!".format(target_player.display_name, shootee_player.display_name)
					if coinbounty > 0:
						response += "\n\n SlimeCorp transfers {:,} SlimeCoin to {}\'s account.".format(coinbounty, user_player.display_name)

					resp_cont.add_channel_response(channel, response)

					resp_cont.add_member_to_update(server.get_member(target_data.id_user))
				#Survived the explosion
				else:
					sap_response = ""
					if sap_damage_target > 0:
						sap_response = " and {} hardened sap".format(sap_damage_target)

					response += "{} was caught in an explosion during your fight with {} and lost {:,} slime{}".format(target_player.display_name, shootee_player.display_name, damage, sap_response)
					resp_cont.add_channel_response(channel, response)
					target_data.persist()

				if user_data.faction != target_data.faction:
					# Give slimes to the boss if possible.
					kingpin = ewutils.find_kingpin(id_server = server.id, kingpin_role = role_boss)

					if kingpin:
						
						kingpin.change_slimes(n = boss_slimes)
						kingpin.persist()

		for bystander in bystander_enemies:
			# Don't damage the shooter or the enemy a second time
			
			if enemy_data != None:
				id_enemy_used = enemy_data.id_enemy
			else:
				id_enemy_used = None
			
			if bystander != user_data.id_user and bystander != id_enemy_used:
				response = ""

				slimes_damage_target = slimes_damage
				target_enemy_data = EwEnemy(id_enemy=bystander, id_server=user_data.id_server)

				# apply sap armor
				sap_armor = get_sap_armor(shootee_data = target_enemy_data, sap_ignored = sap_ignored)
				slimes_damage_target *= sap_armor
				slimes_damage_target = int(max(0, slimes_damage_target))

				slimes_dropped = target_enemy_data.totaldamage + target_enemy_data.slimes

				was_killed = False

				if slimes_damage >= target_enemy_data.slimes - target_enemy_data.bleed_storage:
					was_killed = True

				sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=user_data.id_server)

				# move around slime as a result of the shot
				slimes_drained = int(3 * slimes_damage / 4)  # 3/4

				damage = slimes_damage

				slimes_tobleed = int((slimes_damage - slimes_drained) / 2)

				slimes_directdamage = slimes_damage - slimes_tobleed
				slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained

				district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
				target_enemy_data.bleed_storage += slimes_tobleed
				target_enemy_data.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
				sewer_data.change_slimes(n=slimes_drained)
				sewer_data.persist()

				sap_damage_target = min(sap_damage, target_enemy_data.hardened_sap)
				target_enemy_data.hardened_sap -= sap_damage_target

				if was_killed:
					# adjust statistics
					ewstats.increment_stat(user=user_data, metric=ewcfg.stat_kills)
					ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))
					if user_data.slimelevel > target_enemy_data.level:
						ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_ganks)
					elif user_data.slimelevel < target_enemy_data.level:
						ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_takedowns)


					# Give a bonus to the player's weapon skill for killing a stronger player.
					if target_enemy_data.level >= user_data.slimelevel:
						user_data.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

					district_data.change_slimes(n=target_enemy_data.slimes / 2, source=ewcfg.source_killing)
					levelup_resp = user_data.change_slimes(n=target_enemy_data.slimes / 2, source=ewcfg.source_killing)

					ewhunting.delete_enemy(target_enemy_data)

					response += "{} was killed by an explosion during your fight with {}!".format(target_enemy_data.display_name, shootee_player.display_name)
					resp_cont.add_response_container(ewhunting.drop_enemy_loot(target_enemy_data, district_data))
					resp_cont.add_channel_response(channel, response)

				# Survived the explosion
				else:
					sap_response = ""
					if sap_damage_target > 0:
						sap_response = " and {} hardened sap".format(sap_damage_target)
					response += "{} was caught in an explosion during your fight with {} and lost {:,} slime{}".format(target_enemy_data.display_name, shootee_player.display_name, damage, sap_response)
					resp_cont.add_channel_response(channel, response)
					target_enemy_data.persist()

		return resp_cont

def burn_bystanders(user_data = None, burn_dmg = 0, life_states = None, factions = None, district_data = None):
	if life_states != None and factions != None and district_data != None:
		bystander_users = district_data.get_players_in_district(life_states=life_states, factions=factions, pvp_only=True)
		resp_cont = ewutils.EwResponseContainer(id_server=user_data.id_server)
		channel = ewcfg.id_to_poi.get(district_data.name).channel

		for bystander in bystander_users:
			bystander_user_data = EwUser(id_user = bystander, id_server = user_data.id_server)
			bystander_player_data = EwPlayer(id_user = bystander, id_server = user_data.id_server)
			resp = bystander_user_data.applyStatus(id_status=ewcfg.status_burning_id, value=burn_dmg, source=user_data.id_user).format(name_player = bystander_player_data.display_name)
			resp_cont.add_channel_response(channel, resp)

		bystander_enemies = district_data.get_enemies_in_district()

		for bystander in bystander_enemies:
			bystander_enemy_data = EwEnemy(id_enemy=bystander, id_server=user_data.id_server)
			resp = bystander_enemy_data.applyStatus(id_status=ewcfg.status_burning_id, value=burn_dmg, source=user_data.id_user).format(name_player = bystander_enemy_data.display_name)
			resp_cont.add_channel_response(channel, resp)
		
		return resp_cont

""" Player spars with a friendly player to gain slime. """
async def spar(cmd):
	time_now = int(time.time())
	response = ""

	if cmd.message.channel.name != ewcfg.channel_dojo:
		response = "You must go to the dojo to spar."

	elif cmd.mentions_count > 1:
		response = "One sparring partner at a time!"
		
	elif cmd.mentions_count == 1:
		member = cmd.mentions[0]

		if(member.id == cmd.message.author.id):
			response = "How do you expect to spar with yourself?"
		else:
			# Get killing player's info.
			user_data = EwUser(member = cmd.message.author)
			if user_data.life_state == ewcfg.life_state_shambler:
				response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

			weapon_item = EwItem(id_item = user_data.weapon)

			# Get target's info.
			sparred_data = EwUser(member = member)
			sparred_weapon_item = EwItem(id_item = sparred_data.weapon)

			user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_milkers
			user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_boober
			user_isslimecorp = user_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
			user_isdead = user_data.life_state == ewcfg.life_state_corpse

			if user_data.hunger >= ewutils.hunger_max_bylevel(user_data.slimelevel):
				response = "You are too exhausted to train right now. Go get some grub!"
			elif user_data.poi != ewcfg.poi_id_dojo or sparred_data.poi != ewcfg.poi_id_dojo:
				response = "Both players need to be in the dojo to spar."
			elif sparred_data.hunger >= ewutils.hunger_max_bylevel(sparred_data.slimelevel):
				response = "{} is too exhausted to train right now. They need a snack!".format(member.display_name)
			elif user_isdead == True:
				response = "The dead think they're too cool for conventional combat. Pricks."
			elif (user_iskillers == False and user_isrowdys == False and user_isslimecorp == False) or user_data.life_state == ewcfg.life_state_corpse:
				# Only killers, rowdys, the cop killer, and the rowdy fucker can spar
				response = "Juveniles lack the backbone necessary for combat."
			else:
				was_juvenile = False
				was_sparred = False
				was_dead = False
				was_player_tired = False
				was_target_tired = False
				was_enemy = False
				duel = False

				#Determine if the !spar is a duel:
				weapon = None
				if user_data.weapon >= 0 and sparred_data.weapon >= 0 and weapon_item.item_props.get("weapon_type") == sparred_weapon_item.item_props.get("weapon_type"):
					weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
					duel = True

				if sparred_data.life_state == ewcfg.life_state_corpse:
					# Target is already dead.
					was_dead = True
				elif (user_data.time_lastspar + ewcfg.cd_spar) > time_now:
					# player sparred too recently
					was_player_tired = True
					timeuntil_player_spar = ewcfg.cd_spar - (time_now - user_data.time_lastspar)
				elif (sparred_data.time_lastspar + ewcfg.cd_spar) > time_now:
					# taret sparred too recently
					was_target_tired = True
					timeuntil_target_spar = ewcfg.cd_spar - (time_now - sparred_data.time_lastspar)
				elif sparred_data.life_state == ewcfg.life_state_juvenile:
					# Target is a juvenile.
					was_juvenile = True

				elif (user_iskillers and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction == ewcfg.faction_milkers)) or (user_isrowdys and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction == ewcfg.faction_boober)):
					# User can be sparred.
					was_sparred = True
				elif (user_iskillers and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction == ewcfg.faction_boober)) or (user_isrowdys and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction == ewcfg.faction_milkers)):
					# Target is a member of the opposing faction.
					was_enemy = True


				#if the duel is successful
				if was_sparred:
					weaker_player = sparred_data if sparred_data.slimes < user_data.slimes else user_data
					stronger_player = sparred_data if user_data is weaker_player else user_data

					# Weaker player gains slime based on the slime of the stronger player.
					possiblegain = int(ewcfg.slimes_perspar_base * (2.2 ** weaker_player.slimelevel))
					slimegain = min(possiblegain, stronger_player.slimes / 20)
					weaker_player.change_slimes(n = slimegain)
					
					#hunger drain for both players
					user_data.hunger += ewcfg.hunger_perspar * ewutils.hunger_cost_mod(user_data.slimelevel)
					sparred_data.hunger += ewcfg.hunger_perspar * ewutils.hunger_cost_mod(sparred_data.slimelevel)

					# Bonus 50% slime to both players in a duel.
					if duel:
						weaker_player.change_slimes(n = slimegain / 2)
						stronger_player.change_slimes(n = slimegain / 2)

						if weaker_player.weaponskill < 5 or (weaker_player.weaponskill + 1) < stronger_player.weaponskill:
							weaker_player.add_weaponskill(n = 1, weapon_type = weapon.id_weapon)

						if stronger_player.weaponskill < 5 or (stronger_player.weaponskill + 1) < weaker_player.weaponskill:
							stronger_player.add_weaponskill(n = 1, weapon_type = weapon.id_weapon)

					weaker_player.time_lastspar = time_now

					# Flag the user for PvP
					# user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_spar, True)

					user_data.persist()
					sparred_data.persist()
					# await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)


					# player was sparred with
					if duel and weapon != None:
						response = weapon.str_duel.format(name_player = cmd.message.author.display_name, name_target = member.display_name)
					else:
						response = '{} parries the attack. :knife: {}'.format(member.display_name, ewcfg.emote_slime5)

					#Notify if max skill is reached	
					if weapon != None:
						if user_data.weaponskill >= 5:
							response += ' {} is a master of the {}.'.format(cmd.message.author.display_name, weapon.id_weapon)
						if sparred_data.weaponskill >= 5:
							response += ' {} is a master of the {}.'.format(member.display_name, weapon.id_weapon)

				else:
					if was_dead:
						# target is already dead
						response = '{} is already dead.'.format(member.display_name)
					elif was_target_tired:
						# target has sparred too recently
						response = '{} is too tired to spar right now. They\'ll be ready in {} seconds.'.format(member.display_name, int(timeuntil_target_spar))
					elif was_player_tired:
						# player has sparred too recently
						response = 'You are too tired to spar right now. Try again in {} seconds'.format(int(timeuntil_player_spar))
					elif was_enemy:
						# target and player are different factions
						response = "You cannot spar with your enemies."
					else:
						#otherwise unkillable
						response = '{} cannot spar now.'.format(member.display_name)
	else:
		response = 'Your fighting spirit is appreciated, but ENDLESS WAR didn\'t understand that name.'

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

""" equip a weapon """
async def equip(cmd):
	user_data = EwUser(member = cmd.message.author)

	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	time_now = int(time.time())

	if user_data.time_lastenlist > time_now:
		response = "You've enlisted way too recently! You can't equip any weapons just yet."

	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

	item_sought = ewitem.find_item(item_search = item_search, id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None)

	if item_sought:
		item = EwItem(id_item = item_sought.get("id_item"))

		if item.item_type == ewcfg.it_weapon:
			weapon = ewcfg.weapon_map.get(item.item_props.get("weapon_type"))
			#if weapon.is_tool == 1 and (user_data.sidearm < 0 or user_data.weapon >= 0):
			#	return await sidearm(cmd =cmd)
			response = user_data.equip(item)
			user_data.persist()
			item.persist()
		else:
			response = "Not a weapon, you ignorant juvenile."
	else:
		response = "You don't have one."

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

""" name a weapon using a slime poudrin """
async def annoint(cmd):
	response = ""

	if cmd.tokens_count < 2:
		response = "Specify a name for your weapon!"
	else:
		annoint_name = cmd.message.content[(len(ewcfg.cmd_annoint)):].strip()

		if len(annoint_name) > 32:
			response = "That name is too long. ({:,}/32)".format(len(annoint_name))
		else:
			user_data = EwUser(member = cmd.message.author)
			if user_data.life_state == ewcfg.life_state_shambler:
				response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


			poudrin = ewitem.find_item(item_search = "slimepoudrin", id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None, item_type_filter = ewcfg.it_item)

			all_weapons = ewitem.inventory(
				id_server = cmd.guild.id,
				item_type_filter = ewcfg.it_weapon
			)
			for weapon in all_weapons:
				if weapon.get("name") == annoint_name and weapon.get("id_item") != user_data.weapon:
					response = "**ORIGINAL WEAPON NAME DO NOT STEAL.**"
					return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


			if poudrin is None:
				response = "You need a slime poudrin."
			elif user_data.slimes < 100:
				response = "You need more slime."
			elif user_data.weapon < 0:
				response = "Equip a weapon first."
			else:
				# Perform the ceremony.
				user_data.change_slimes(n = -100, source = ewcfg.source_spending)
				weapon_item = EwItem(id_item = user_data.weapon)
				weapon_item.item_props["weapon_name"] = annoint_name
				weapon_item.persist()

				if user_data.weaponskill < 10:
					user_data.add_weaponskill(n = 1, weapon_type = weapon_item.item_props.get("weapon_type"))

				# delete a slime poudrin from the player's inventory
				ewitem.item_delete(id_item = poudrin.get('id_item'))

				user_data.persist()

				response = "You place your weapon atop the poudrin and annoint it with slime. It is now known as {}!\n\nThe name draws you closer to your weapon. The poudrin was destroyed in the process.".format(annoint_name)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def marry(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	weapon_item = EwItem(id_item = user_data.weapon)
	weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
	display_name = cmd.message.author.display_name
	if weapon != None:
		weapon_name = weapon_item.item_props.get("weapon_name") if len(weapon_item.item_props.get("weapon_name")) > 0 else weapon.str_weapon

	#Checks to make sure you're in the dojo.
	if user_data.poi != ewcfg.poi_id_dojo:
		response = "Do you really expect to just get married on the side of the street in this war torn concrete jungle? No way, you need to see a specialist for this type of thing, someone who can empathize with a man’s love for his arsenal. Maybe someone in the Dojo can help, *hint hint*."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	#Informs you that you cannot be a fucking faggot.
	elif cmd.mentions_count > 0:
		response = "Ewww, gross! You can’t marry another juvenile! That’s just degeneracy, pure and simple. What happened to the old days, where you could put a bullet in someone’s brain for receiving a hug? You people have gone soft on me, I tells ya."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	#Makes sure you have a weapon to marry.
	elif weapon is None:
		response = "How do you plan to get married to your weapon if you aren’t holding any weapon? Goddamn, think these things through, I have to spell out everything for you."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	#Makes sure you have a displayed rank 4 or higher weapon.
	elif user_data.weaponskill < 8:
		response = "Slow down, Casanova. You do not nearly have a close enough bond with your {} to engage in holy matrimony with it. You’ll need to reach rank 4 mastery or higher to get married.".format(weapon_name)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	#Makes sure you aren't trying to farm the extra weapon mastery ranks by marrying over and over again.
	elif user_data.weaponmarried == True:
		response = "Ah, to recapture the magic of the first nights together… Sadly, those days are far behind you now. You’ve already had your special day, now it’s time to have the same boring days forever. Aren’t you glad you got married??"
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		#Preform the ceremony 2: literally this time
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"You decide it’s finally time to take your relationship with your {} to the next level. You approach the Dojo Master with your plight, requesting his help to circumvent the legal issues of marrying your weapon. He takes a moment to unfurl his brow before letting out a raspy chuckle. He hasn’t been asked to do something like this for a long time, or so he says. You scroll up to the last instance of this flavor text and conclude he must have Alzheimer's or something. Regardless, he agrees.".format(weapon.str_weapon)
		))
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"Departing from the main floor of the Dojo, he rounds a corner and disappears for a few minutes before returning with illegally doctor marriage paperwork and cartoonish blotches of ink on his face and hands to visually communicate the hard work he’s put into the forgeries. You see, this is a form of visual shorthand that artists utilize so they don’t have to explain every beat of their narrative explicitly, but I digress."
		))
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"You express your desire to get things done as soon as possible so that you can stop reading this boring wall of text and return to your busy agenda of murder, and so he prepares to officiate immediately. You stand next to your darling {}, the only object of your affection in this godforsaken city. You shiver with anticipation for the most anticipated in-game event of your ENDLESS WAR career. A crowd of enemy and allied gangsters alike forms around you three as the Dojo Master begins the ceremony...".format(weapon_name)
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"”We are gathered here today to witness the combined union of {} and {}.".format(display_name, weapon_name)
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"Two of the greatest threats in the current metagame. No greater partners, no worse adversaries."
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"Through thick and thin, these two have stood together, fought together, and gained experience points--otherwise known as “EXP”--together."
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"It was not through hours mining or stock exchanges that this union was forged, but through iron and slime."
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"Without the weapon, the wielder would be defenseless, and without the wielder, the weapon would have no purpose."
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"It is this union that we are here today to officially-illegally affirm.”"
		))
		await asyncio.sleep(6)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"He takes a pregnant pause to increase the drama, and allow for onlookers to press 1 in preparation."
		))
		await asyncio.sleep(6)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"“I now pronounce you juvenile and armament!! You may anoint the {}”".format(weapon.str_weapon)
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"You begin to tear up, fondly regarding your last kill with your {} that you love so much. You lean down and kiss your new spouse on the handle, anointing an extra two mastery ranks with pure love. It remains completely motionless, because it is an inanimate object. The Dojo Master does a karate chop midair to bookend the entire experience. Sick, you’re married now!".format(weapon_name)
		))

		#Sets their weaponmarried table to true, so that "you are married to" appears instead of "you are wielding" intheir !data, you get an extra two mastery levels, and you can't change your weapon.
		user_data = EwUser(member = cmd.message.author)
		user_data.weaponmarried = True
		user_data.add_weaponskill(n = 2, weapon_type = weapon.id_weapon)
		user_data.persist()
		weapon_item.item_props["married"] = user_data.id_user
		weapon_item.persist()
		return


async def divorce(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	weapon_item = EwItem(id_item = user_data.weapon)
	weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
	if weapon != None:
		weapon_name = weapon_item.item_props.get("weapon_name") if len(weapon_item.item_props.get("weapon_name")) > 0 else weapon.str_weapon

	#Makes sure you have a partner to divorce.
	if user_data.weaponmarried == False:
		response = "I appreciate your forward thinking attitude, but how do you expect to get a divorce when you haven’t even gotten married yet? Throw your life away first, then we can talk."
	# Checks to make sure you're in the dojo.
	elif user_data.poi != ewcfg.poi_id_dojo:
		response = "As much as it would be satisfying to just chuck your {} down an alley and be done with it, here in civilization we deal with things *maturely.* You’ll have to speak to the guy that got you into this mess in the first place, or at least the guy that allowed you to make the retarded decision in the first place. Luckily for you, they’re the same person, and he’s at the Dojo.".format(weapon.str_weapon)
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		#Unpreform the ceremony
		response = "You decide it’s finally time to end the frankly obviously retarded farce that is your marriage with your {}. Things were good at first, you both wanted the same things out of life. But, that was then and this is now. You reflect briefly on your myriad of woes; the constant bickering, the mundanity of your everyday routine, the total lack of communication. You’re a slave. But, a slave you will be no longer! You know what you must do." \
				"\nYou approach the Dojo Master yet again, and explain to him your troubles. He solemnly nods along to every beat of your explanation. Luckily, he has a quick solution. He rips apart the marriage paperwork he forged last flavor text, and just like that you’re divorced from {}. It receives half of your SlimeCoin in the settlement, a small price to pay for your freedom. You hand over what used to be your most beloved possession and partner to the old man, probably to be pawned off to whatever bumfuck juvie waddles into the Dojo next. You don’t care, you just don’t want it in your data. " \
				"So, yeah. You’re divorced. Damn, that sucks.".format(weapon.str_weapon, weapon_name)

		#You divorce your weapon, discard it, lose it's rank, and loose half your SlimeCoin in the aftermath.
		user_data.weaponmarried = False
		user_data.weapon = -1
		ewutils.weaponskills_set(member = cmd.message.author, weapon = weapon_item.item_props.get("weapon_type"), weaponskill = 0)

		fee = (user_data.slimecoin / 2)
		user_data.change_slimecoin(n = -fee, coinsource = ewcfg.coinsource_revival)

		user_data.persist()

		#delete weapon item
		ewitem.item_delete(id_item = weapon_item.id_item)
	
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def reload(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	response = ""
	reload_mismatch = True

	if user_data.weapon > 0:
		weapon_item = EwItem(id_item = user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))

		if ewcfg.weapon_class_ammo in weapon.classes:
			weapon_item.item_props["ammo"] = weapon.clip_size
			weapon_item.persist()
			response = weapon.str_reload
			reload_mismatch = False

	if user_data.sidearm > 0:
		sidearm_item = EwItem(id_item=user_data.sidearm)
		sidearm = ewcfg.weapon_map.get(sidearm_item.item_props.get("weapon_type"))

		if ewcfg.weapon_class_ammo in sidearm.classes:
			sidearm_item.item_props["ammo"] = sidearm.clip_size
			sidearm_item.persist()
			if response != "":
				response += "\n"
			response += sidearm.str_reload
			reload_mismatch = False

	if user_data.weapon == -1 and user_data.sidearm == -1:
		response = "What are you expecting to reload, dumbass? {} a weapon first!".format(ewcfg.cmd_equip)
	elif reload_mismatch:
		response = "What do you think you're going to be reloading with that?"

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def unjam(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	if user_data.weapon > 0:
		weapon_item = EwItem(id_item = user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
		if ewcfg.weapon_class_jammable in weapon.classes:
			if weapon_item.item_props.get("jammed") == "True":
				captcha = weapon_item.item_props.get("captcha").lower()
				tokens_lower = []
				for token in cmd.tokens[1:]:
					tokens_lower.append(token.lower())

				if captcha in tokens_lower:
					weapon_item.item_props["jammed"] = "False"
					weapon_item.persist()
					response = weapon.str_unjam.format(name_player = cmd.message.author.display_name)
				else:
					response = "ERROR: Invalid security code.\nEnter **{}** to proceed.".format(ewutils.text_to_regional_indicator(captcha))
			else:
				response = "Let’s not get ahead of ourselves, there’s nothing clogging with your {weapon} (yet)!!".format(weapon = weapon.id_weapon)
		else:
			response = "What are you trying to do, exactly? Your weapon can’t jam!!"
	else:
		response = "What are you expecting to do, dumbass? {} a weapon first!".format(ewcfg.cmd_equip)
	
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

# Returns the total modifier of all statuses of a certain type and target of a given player
def get_shooter_status_mods(user_data = None, shootee_data = None, hitzone = None):

	mods = {
		'dmg': 0,
		'crit': 0,
		'miss': 0
	}

	user_statuses = user_data.getStatusEffects()
	for status in user_statuses:
		status_flavor = ewcfg.status_effects_def_map.get(status)

		# check target for targeted status effects
		if status in [ewcfg.status_taunted_id, ewcfg.status_aiming_id, ewcfg.status_evasive_id]:
			if user_data.combatant_type == "player":
				status_data = EwStatusEffect(id_status = status, user_data = user_data)
			else:
				status_data = EwEnemyStatusEffect(id_status = status, enemy_data = user_data)

			if status_data.id_target != -1:
				if status == ewcfg.status_taunted_id:
					if shootee_data.combatant_type == ewcfg.combatant_type_player and shootee_data.id_user == status_data.id_target:
						continue
					elif shootee_data.combatant_type == ewcfg.combatant_type_enemy and shootee_data.id_enemy == status_data.id_target:
						continue
				elif status == ewcfg.status_aiming_id:
					if shootee_data.combatant_type == ewcfg.combatant_type_player and shootee_data.id_user != status_data.id_target:
						continue
					elif shootee_data.combatant_type == ewcfg.combatant_type_enemy and shootee_data.id_enemy != status_data.id_target:
						continue

		if status_flavor is not None:
			mods['miss'] += status_flavor.miss_mod_self
			mods['crit'] += status_flavor.crit_mod_self
			mods['dmg'] += status_flavor.dmg_mod_self

		# apply hitzone damage and crit mod
		if hitzone != None and status == hitzone.id_injury:
			status_data = EwStatusEffect(id_status = status, user_data = user_data)
			try:
				value_int = int(status_data.value)
				
				mods['crit'] += 0.5 * value_int / 10
				mods['dmg'] += 1 * value_int / 10

			except:
				ewutils.logMsg("error with int conversion")

	#apply trauma mods
	if user_data.combatant_type == 'player':
		trauma = ewcfg.trauma_map.get(user_data.trauma)

		if trauma != None:
			if trauma.trauma_class == ewcfg.trauma_class_movespeed:
				mods['miss'] += 0.3 * user_data.degradation / 100
			elif trauma.trauma_class == ewcfg.trauma_class_damage:
				mods['dmg'] -= 0.9 * user_data.degradation / 100


	return mods

# Returns the total modifier of all statuses of a certain type and target of a given player
def get_shootee_status_mods(user_data = None, shooter_data = None, hitzone = None):

	mods = {
		'dmg': 0,
		'crit': 0,
		'miss': 0
	}

	user_statuses = user_data.getStatusEffects()
	for status in user_statuses:
		status_flavor = ewcfg.status_effects_def_map.get(status)

		# check target for targeted status effects
		if status in [ewcfg.status_evasive_id]:
			if user_data.combatant_type == "player":
				status_data = EwStatusEffect(id_status = status, user_data = user_data)
			else:
				status_data = EwEnemyStatusEffect(id_status = status, enemy_data = user_data)

			if status_data.id_target != -1:
				if shooter_data.id_user != status_data.id_target:
					continue

		if status_flavor is not None:
			mods['miss'] += status_flavor.miss_mod
			mods['crit'] += status_flavor.crit_mod
			mods['dmg'] += status_flavor.dmg_mod

	#apply trauma mods
	if user_data.combatant_type == 'player':
		trauma = ewcfg.trauma_map.get(user_data.trauma)

		if trauma != None and trauma.trauma_class == ewcfg.trauma_class_accuracy:
			mods['miss'] -= 0.2 * user_data.degradation / 100

	return mods

async def attackEnemy(cmd, user_data, weapon, resp_cont, weapon_item, slimeoid, market_data, time_now_float):
	time_now = int(time_now_float)
	# Get shooting player's info
	if user_data.slimelevel <= 0:
		user_data.slimelevel = 1
		user_data.persist()

	# Get target's info.
	huntedenemy = " ".join(cmd.tokens[1:]).lower()
	enemy_data = ewhunting.find_enemy(huntedenemy, user_data)
	
	sandbag_mode = False
	if enemy_data.enemytype == ewcfg.enemy_type_sandbag:
		sandbag_mode = True
	
	if (enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state in [ewcfg.life_state_executive, ewcfg.life_state_enlisted]) or (enemy_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler):
		response = "Hey ASSHOLE! They're on your side!!"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif (enemy_data.enemyclass == ewcfg.enemy_class_shambler and enemy_data.gvs_coord not in ewcfg.gvs_coords_end):
		response = "It's best not to interfere with whatever those Juveniles are up to. If it gets close, that's your time to strike."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	# elif (enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and ewutils.gvs_check_gaia_protected(enemy_data)):
	# 	response = "It's no use, there's another gaiaslimeoid in front that's protecting them!"
	# 	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response)) 
	elif user_data.life_state == ewcfg.life_state_shambler and enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid:
		response = "It's not worth going near those... *things*. You'd get torn to shreds, it's better to send out lackeys to do your job for you."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		# if (time_now - user_data.time_lasthaunt) < ewcfg.cd_shambler_attack:
		# 	response = "Your shitty zombie jaw is too tired to chew on that {}. Try again in {} seconds.".format(enemy_data.display_name, int(ewcfg.cd_shambler_attack-(time_now-user_data.time_lasthaunt)))
		# 	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		# else:
		# 	user_data.time_lasthaunt = time_now
		# 	user_data.persist()
			


	user_mutations = user_data.get_mutations()

	district_data = EwDistrict(district=user_data.poi, id_server=cmd.guild.id)

	miss = False
	crit = False
	backfire = False
	backfire_damage = 0
	jammed = False
	strikes = 0
	bystander_damage = 0
	miss_mod = 0
	crit_mod = 0
	dmg_mod = 0
	sap_damage = 0
	sap_ignored = 0

	# Weaponized flavor text.
	hitzone = get_hitzone()
	randombodypart = hitzone.name
	if random.random() < 0.5:
		randombodypart = random.choice(hitzone.aliases)

	shooter_status_mods = get_shooter_status_mods(user_data, enemy_data, hitzone)
	shootee_status_mods = get_shootee_status_mods(enemy_data, user_data, hitzone)

	miss_mod += round(shooter_status_mods['miss'] + shootee_status_mods['miss'], 2)
	crit_mod += round(shooter_status_mods['crit'] + shootee_status_mods['crit'], 2)
	dmg_mod += round(shooter_status_mods['dmg'] + shootee_status_mods['dmg'], 2)

	slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 60)
	slimes_damage = int((slimes_spent * (10 + user_data.attack)) * (100 + (user_data.weaponskill * 5)) / 100.0)
	
	if user_data.weaponskill < 5:
		miss_mod += (5 - user_data.weaponskill) / 10

	# If the player is using a repel, remove the repel, and make the first hit do 99.9% less damage, rounded up.
	statuses = user_data.getStatusEffects()
	if ewcfg.status_repelled_id in statuses:
		user_data.clear_status(ewcfg.status_repelled_id)
		after_effects_response = user_data.applyStatus(ewcfg.status_repelaftereffects_id)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, after_effects_response))
		slimes_damage /= 1000
		slimes_damage = math.ceil(slimes_damage)
		
	# If the player has cancelled a repel by attacking an enemy, make all their hits do 99% less damage for two seconds, rounded up.
	if ewcfg.status_repelaftereffects_id in statuses:
		slimes_damage /= 100
		slimes_damage = math.ceil(slimes_damage)

	if weapon is None:
		slimes_damage /= 2  # penalty for not using a weapon, otherwise fists would be on par with other weapons
	slimes_dropped = enemy_data.totaldamage + enemy_data.slimes

	slimes_damage += int(slimes_damage * dmg_mod)

	user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_milkers
	user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_boober
	user_isslimecorp = user_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]

	# hunger drain
	if not sandbag_mode:
		user_data.hunger += ewcfg.hunger_pershot * ewutils.hunger_cost_mod(user_data.slimelevel)
		
	#randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]

	# Weapon-specific adjustments
	if weapon != None and weapon.fn_effect != None:
		# Build effect container
		ctn = EwEffectContainer(
			miss=miss,
			backfire=backfire,
			crit=crit,
			jammed=jammed,
			slimes_damage=slimes_damage,
			slimes_spent=slimes_spent,
			user_data=user_data,
			weapon_item=weapon_item,
			shootee_data=enemy_data,
			time_now=time_now_float,
			bystander_damage=bystander_damage,
			miss_mod=miss_mod,
			crit_mod=crit_mod,
			sap_damage=sap_damage,
			sap_ignored=sap_ignored,
			backfire_damage=backfire_damage
		)

		# Make adjustments
		if weapon.id_weapon != ewcfg.weapon_id_garrote:
			weapon.fn_effect(ctn)

		# Apply effects for non-reference values
		miss = ctn.miss
		backfire = ctn.backfire
		crit = ctn.crit
		jammed = ctn.jammed
		slimes_damage = ctn.slimes_damage
		slimes_spent = ctn.slimes_spent
		strikes = ctn.strikes
		bystander_damage = ctn.bystander_damage
		sap_damage = ctn.sap_damage
		sap_ignored = ctn.sap_ignored
		backfire_damage = ctn.backfire_damage
		# user_data and enemy_data should be passed by reference, so there's no need to assign them back from the effect container.
		
		if sandbag_mode:
			slimes_spent_sandbag = slimes_spent
			slimes_spent = 0
			slimes_dropped = 0
		
		if (slimes_spent > user_data.slimes):
			# Not enough slime to shoot.
			response = "You don't have enough slime to attack. ({:,}/{:,})".format(user_data.slimes, slimes_spent)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


		if sandbag_mode and backfire:
			backfire = False
			miss = True

		weapon_item.item_props['time_lastattack'] = time_now_float
		weapon_item.persist()

		# print(user_data.slimes)
		# print(slimes_spent)

		# Spend slimes, to a minimum of zero
		user_data.change_slimes(n=(-user_data.slimes if slimes_spent >= user_data.slimes else -slimes_spent), source=ewcfg.source_spending)
		user_data.persist()

		# Spend sap
		user_data.sap -= weapon.sap_cost
		user_data.limit_fix()
		user_data.persist()

		if weapon.id_weapon == ewcfg.weapon_id_garrote:
			enemy_data.persist()
			response = "You wrap your wire around {}'s neck...\n**...to no avail! {} breaks free with ease!**".format(
				enemy_data.display_name, enemy_data.display_name)
			resp_cont.add_channel_response(cmd.message.channel.name, response)
			resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)
			await resp_cont.post()

			user_data = EwUser(member=cmd.message.author)

			# TODO - Make enemies able to be strangled
			# One of the players/enemies died in the meantime
			if user_data.life_state == ewcfg.life_state_corpse or enemy_data.life_state == ewcfg.enemy_lifestate_dead:
				return
			else:
				return
			
		# else:
		# pass
		# enemy_data.persist()

		# Remove a bullet from the weapon
		if ewcfg.weapon_class_ammo in weapon.classes:
			weapon_item.item_props['ammo'] = int(weapon_item.item_props.get("ammo")) - 1

		# Remove one item from stack
		if ewcfg.weapon_class_thrown in weapon.classes:
			weapon_item.stack_size -= 1
		
		if not sandbag_mode:
			life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_shambler]
			bystander_faction = ""
			if user_data.faction == "rowdys":
				bystander_faction = "killers"
			elif user_data.faction == "killers":
				bystander_faction = "rowdys"

			factions = ["", user_data.faction if backfire else bystander_faction]

			# Burn players in district
			if ewcfg.weapon_class_burning in weapon.classes:
				if enemy_data.enemyclass in [ewcfg.enemy_class_gaiaslimeoid, ewcfg.enemy_class_shambler]:
					miss = True
				
				if not miss:
					resp = burn_bystanders(user_data=user_data, burn_dmg=bystander_damage, life_states=life_states, factions=factions, district_data=district_data)
					resp_cont.add_response_container(resp)

			if ewcfg.weapon_class_exploding in weapon.classes:
				if enemy_data.enemyclass in [ewcfg.enemy_class_gaiaslimeoid, ewcfg.enemy_class_shambler]:
					miss = True
				
				user_data.persist()
				enemy_data.persist()

				if not miss:
					# Damage players/enemies in district
					resp = weapon_explosion(user_data=user_data, shootee_data=enemy_data, district_data=district_data, market_data = market_data, life_states=life_states, factions=factions, slimes_damage=bystander_damage, backfire=backfire, time_now=time_now, target_enemy=True)
					resp_cont.add_response_container(resp)

			user_data = EwUser(member=cmd.message.author)

	if miss or backfire or jammed:
		slimes_damage = 0
		sap_damage = 0
		weapon_item.item_props["consecutive_hits"] = 0
		crit = False

	if crit:
		sap_damage += 1

	if user_data.life_state == ewcfg.life_state_shambler:
		sap_damage += 1

	# Remove !revive invulnerability.
	user_data.time_lastrevive = 0

	# apply attacker damage mods
	slimes_damage *= damage_mod_attack(
		user_data = user_data,
		user_mutations = user_mutations,
		market_data = market_data,
		district_data = district_data
	)

			
	# Defender enemies take less damage
	if enemy_data.ai == ewcfg.enemy_ai_defender:
		slimes_damage *= 0.5
		
	# Bicarbonate enemies take more damage
	if enemy_data.weathertype == ewcfg.enemy_weathertype_rainresist:
		slimes_damage *= 1.5
		
	# # Shamblers deal less damage to gaiaslimeoids
	# if enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state == ewcfg.life_state_shambler:
	# 	slimes_damage *= 0.25

	if not sandbag_mode:
		# apply hardened sap armor
		sap_armor = get_sap_armor(shootee_data = enemy_data, sap_ignored = sap_ignored)
		slimes_damage *= sap_armor
		slimes_damage = int(max(slimes_damage, 0))

	sap_damage = min(sap_damage, enemy_data.hardened_sap)

	# Damage stats
	ewstats.track_maximum(user=user_data, metric=ewcfg.stat_max_hitdealt, value=slimes_damage)
	ewstats.change_stat(user=user_data, metric=ewcfg.stat_lifetime_damagedealt, n=slimes_damage)

	user_inital_level = user_data.slimelevel

	was_killed = False

	if slimes_damage >= enemy_data.slimes - enemy_data.bleed_storage:
		was_killed = True
		if ewcfg.mutation_id_thickerthanblood in user_mutations:
			slimes_damage = 0
		else:
			slimes_damage = max(enemy_data.slimes - enemy_data.bleed_storage, 0)

	sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=cmd.guild.id)
	# move around slime as a result of the shot
	slimes_drained = int(3 * slimes_damage / 4)  # 3/4

	damage = slimes_damage

	slimes_tobleed = int((slimes_damage - slimes_drained) / 2)
	if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
		slimes_tobleed = 0

	slimes_directdamage = slimes_damage - slimes_tobleed
	slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained
	
	if sandbag_mode:
		slimes_drained = 0
		slimes_tobleed = 0
		#slimes_directdamage = 0
		slimes_splatter = 0

	district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
	enemy_data.bleed_storage += slimes_tobleed
	enemy_data.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
	enemy_data.hardened_sap -= sap_damage
	enemy_data.persist()
	sewer_data.change_slimes(n=slimes_drained)
	sewer_data.persist()

	if was_killed:
		# adjust statistics
		ewstats.increment_stat(user=user_data, metric=ewcfg.stat_pve_kills)
		ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))
		if user_data.slimelevel > enemy_data.level:
			ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_pve_ganks)
		elif user_data.slimelevel < enemy_data.level:
			ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_pve_takedowns)

		if weapon != None:
			weapon_item.item_props["kills"] = (int(weapon_item.item_props.get("kills")) if weapon_item.item_props.get("kills") != None else 0) + 1
			weapon_item.item_props["totalkills"] = (int(weapon_item.item_props.get("totalkills")) if weapon_item.item_props.get("totalkills") != None else 0) + 1
			ewstats.increment_stat(user=user_data, metric=weapon.stat)

		# Give a bonus to the player's weapon skill for killing a stronger enemy.
		if enemy_data.enemytype != ewcfg.enemy_type_sandbag and enemy_data.level >= user_data.slimelevel and weapon is not None:
			user_data.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

		# release bleed storage
		if ewcfg.mutation_id_thickerthanblood in user_mutations:
			slimes_todistrict = enemy_data.slimes * 0.25
			slimes_tokiller = enemy_data.slimes * 0.75
		else:
			slimes_todistrict = enemy_data.slimes / 2
			slimes_tokiller = enemy_data.slimes / 2
			
		if sandbag_mode:
			slimes_todistrict = 0
			slimes_tokiller = 0
			
		district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)
		levelup_response = user_data.change_slimes(n=slimes_tokiller, source=ewcfg.source_killing)
		if ewcfg.mutation_id_fungalfeaster in user_mutations:
			user_data.hunger = 0

		# Enemy was killed.
		ewhunting.delete_enemy(enemy_data)

		kill_descriptor = "beaten to death"
		if weapon != None:
			response = weapon.str_damage.format(
				name_player=cmd.message.author.display_name,
				name_target=enemy_data.display_name,
				hitzone=randombodypart,
				strikes=strikes
			)
			kill_descriptor = weapon.str_killdescriptor
			if crit:
				response += " {}".format(weapon.str_crit.format(
					name_player=cmd.message.author.display_name,
					name_target=enemy_data.display_name,
					hitzone = randombodypart,
				))

			response += "\n\n{}".format(weapon.str_kill.format(
				name_player=cmd.message.author.display_name,
				name_target=enemy_data.display_name,
				emote_skull=ewcfg.emote_slimeskull
			))

			if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
				response += "\n" + weapon.str_reload_warning.format(
					name_player=cmd.message.author.display_name)

			if ewcfg.weapon_class_captcha in weapon.classes:
				new_captcha = ewutils.generate_captcha(length = weapon.captcha_length)
				response += "\nNew security code: **{}**".format(ewutils.text_to_regional_indicator(new_captcha))
				weapon_item.item_props['captcha'] = new_captcha
				weapon_item.persist()
		else:
			response = "{name_target} is hit!!\n\n{name_target} has died.".format(
				name_target=enemy_data.display_name)

		weapon_possession = user_data.get_weapon_possession()
		if weapon_possession:
			response += fulfill_ghost_weapon_contract(weapon_possession, market_data, user_data, cmd.message.author.display_name)

		# When a raid boss dies, use this response instead so its drops aren't shown in the killfeed
		old_response = response

		# give player item for defeating an enemy
		resp_cont.add_response_container(ewhunting.drop_enemy_loot(enemy_data, district_data))

		if slimeoid.life_state == ewcfg.slimeoid_state_active:
			brain = ewcfg.brain_map.get(slimeoid.ai)
			response += "\n" + brain.str_kill.format(slimeoid_name=slimeoid.name)

		user_data.persist()
		resp_cont.add_channel_response(cmd.message.channel.name, response)
		user_data = EwUser(member=cmd.message.author)
	else:
		# A non-lethal blow!
		if weapon != None:
			if miss:
				response = "{}".format(weapon.str_miss.format(
					name_player=cmd.message.author.display_name,
					name_target=enemy_data.display_name
				))
			elif backfire:
				response = "{}".format(weapon.str_backfire.format(
					name_player=cmd.message.author.display_name,
					name_target=enemy_data.display_name
				))

				if user_data.slimes - user_data.bleed_storage <= backfire_damage:
					district_data.change_slimes(n = user_data.slimes)
					district_data.persist()
					user_data.trauma = ewcfg.trauma_id_environment
					die_resp = user_data.die(cause = ewcfg.cause_backfire)
					district_data = EwDistrict(district = district_data.name, id_server = district_data.id_server)
					resp_cont.add_member_to_update(cmd.message.author)
					resp_cont.add_response_container(die_resp)
				else:
					district_data.change_slimes(n = backfire_damage / 2)
					user_data.change_slimes(n = -backfire_damage / 2,  source = ewcfg.source_self_damage)
					user_data.bleed_storage += int(backfire_damage / 2)

			elif jammed:
				response = "{}".format(weapon.str_jammed.format(
					name_player=cmd.message.author.display_name,
					name_target=enemy_data.display_name
				))
			else:
				response = weapon.str_damage.format(
					name_player=cmd.message.author.display_name,
					name_target=enemy_data.display_name,
					hitzone=randombodypart,
					strikes=strikes
				)
				if crit:
					response += " {}".format(weapon.str_crit.format(
						name_player=cmd.message.author.display_name,
						name_target=enemy_data.display_name,
						hitzone = randombodypart,
					))

				sap_response = ""
				if sap_damage > 0:
					sap_response = " and {sap_damage} hardened sap".format(sap_damage = sap_damage)

				response += " {target_name} loses {damage:,} slime{sap_response}!".format(
					target_name=enemy_data.display_name,
					damage=damage,
					sap_response=sap_response
				)

				if enemy_data.ai == ewcfg.enemy_ai_coward:
					response += random.choice(ewcfg.coward_responses_hurt).format(enemy_data.display_name)
				elif enemy_data.ai == ewcfg.enemy_ai_defender:
					enemy_data.id_target = user_data.id_user
					enemy_data.persist()

			if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
				response += "\n" + weapon.str_reload_warning.format(
					name_player=cmd.message.author.display_name)
	
			if ewcfg.weapon_class_captcha in weapon.classes or jammed:
				new_captcha = ewutils.generate_captcha(length = weapon.captcha_length)
				response += "\nNew security code: **{}**".format(ewutils.text_to_regional_indicator(new_captcha))
				weapon_item.item_props['captcha'] = new_captcha
				weapon_item.persist()
		else:
			if miss:
				response = "{target_name} dodges your strike.".format(target_name=enemy_data.display_name)
			else:
				response = "{target_name} is hit!! {target_name} loses {damage:,} slime!".format(
					target_name=enemy_data.display_name,
					damage=damage
				)

				if enemy_data.ai == ewcfg.enemy_ai_coward:
					response += random.choice(ewcfg.coward_responses_hurt).format(enemy_data.display_name)
				elif enemy_data.ai == ewcfg.enemy_ai_defender:
					enemy_data.id_target = user_data.id_user
					enemy_data.persist()
					
		if sandbag_mode:
			response += '\n*The dojo master cries out from afar:*\n"If this were a real fight, you would have spent **{}** slime on that attack!"'.format(slimes_spent_sandbag)

		resp_cont.add_channel_response(cmd.message.channel.name, response)

	# Add level up text to response if appropriate
	if user_inital_level < user_data.slimelevel:
		resp_cont.add_channel_response(cmd.message.channel.name, "\n" + levelup_response)
	# Enemy kills don't award slime to the kingpin.

	# Persist user data.
	# Flag the user for PvP
	if not sandbag_mode:

		user_poi = ewcfg.id_to_poi.get(user_data.poi)
		user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_attack, True)

	resp_cont.add_member_to_update(cmd.message.author)
	user_data.persist()
	if user_data.weapon > 0:
		weapon_item.persist()

	district_data.persist()

	# If an enemy is a raidboss, announce that kill in the killfeed
	if was_killed and (enemy_data.enemytype in ewcfg.raid_bosses):
		# announce raid boss kill in kill feed channel

		killfeed_resp = "*{}*: {}".format(cmd.message.author.display_name, old_response)
		killfeed_resp += "\n`-------------------------`{}".format(ewcfg.emote_megaslime)

		killfeed_resp_cont = ewutils.EwResponseContainer(id_server=cmd.guild.id)
		killfeed_resp_cont.add_channel_response(ewcfg.channel_killfeed, killfeed_resp)
		await killfeed_resp_cont.post()

		# Send the response to the player.
		resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)
		await resp_cont.post()

	else:
		resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)
	
		await resp_cont.post()

async def harden_sap(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	statuses = user_data.getStatusEffects()
	response = ""

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "You're dead, bitch."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	sap_to_harden = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)
	
	if sap_to_harden == None:
		sap_to_harden = 1
	
	if sap_to_harden <= 0:
		sap_to_harden = user_data.sap

	if sap_to_harden > user_data.sap:
		response = "You don't have that much sap to harden."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	harden_mod = 1
	if ewcfg.status_injury_torso_id in statuses:
		status_data = EwStatusEffect(id_status = ewcfg.status_injury_torso_id, user_data = user_data)
		harden_mod -= 0.5 * int(status_data.value) / 10

	harden_real = max(0, int(sap_to_harden * harden_mod))

	user_data.hardened_sap += harden_real
	user_data.sap -= sap_to_harden

	user_data.persist()

	response = "You harden {} sap.".format(harden_real)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def liquefy_sap(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	response = ""

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "You're dead, bitch."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	sap_to_liquefy = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)
	
	if sap_to_liquefy == None:
		sap_to_liquefy = 1
	
	if sap_to_liquefy <= 0:
		sap_to_liquefy = user_data.hardened_sap

	if sap_to_liquefy > user_data.hardened_sap:
		response = "You don't have that much hardened sap."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	user_data.sap += sap_to_liquefy
	user_data.hardened_sap -= sap_to_liquefy

	user_data.persist()

	response = "You liquefy {} sap.".format(sap_to_liquefy)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def dodge(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	response = ""

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "A bit late for that, don't you think?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	sap_cost = 3
	
	if sap_cost > user_data.sap:
		response = "You don't have enough sap to {}. ({}/{})".format(cmd.tokens[0], user_data.sap, sap_cost)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	#if cmd.mentions_count < 1:
	#	response = "Whose attacks do you want to {}?".format(cmd.tokens[0])
	#	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	if cmd.mentions_count > 1:
		response = "You can only focus on dodging one person at a time.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	if cmd.mentions_count == 1:
		target = cmd.mentions[0]
		target_data = EwUser(member = target)
	else:
		huntedenemy = " ".join(cmd.tokens[1:]).lower()
		target_data = target = ewhunting.find_enemy(enemy_search=huntedenemy, user_data=user_data)

	if target_data == None:
		response = "ENDLESS WAR didn't understand that name.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		try:
			if (target_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state in [ewcfg.life_state_executive, ewcfg.life_state_enlisted]) or (target_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler):
				response = "Hey ASSHOLE! They're on your side!!"
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			elif (target_data.enemyclass == ewcfg.enemy_class_shambler and target_data.gvs_coord not in ewcfg.gvs_coords_end):
				response = "It's no use, they're too far away!"
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		except:
			pass

	if target_data.poi != user_data.poi:
		response = "You can't {} someone, who's not even here.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	id_status = ewcfg.status_evasive_id

	user_data.clear_status(id_status = id_status)

	user_data.applyStatus(id_status = id_status, source = cmd.message.author.id, id_target = (target.id if target_data.combatant_type == "player" else target_data.id_enemy))

	user_data.sap -= sap_cost

	user_poi = ewcfg.id_to_poi.get(user_data.poi)
	user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_attack, True)

	user_data.persist()

	response = "You spend {} sap to focus on dodging {}'s attacks.".format(sap_cost, target.display_name)
	await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def taunt(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	response = ""

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "A bit late for that, don't you think?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	sap_cost = 5
	
	if sap_cost > user_data.sap:
		response = "You don't have enough sap to {}. ({}/{})".format(cmd.tokens[0], user_data.sap, sap_cost)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	#if cmd.mentions_count < 1:
	#	response = "Who do you want to {}?".format(cmd.tokens[0])
	#	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	if cmd.mentions_count > 1:
		response = "You can only focus on taunting one person at a time.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	if cmd.mentions_count == 1:
		target = cmd.mentions[0]
		target_data = EwUser(member = target)
	else:
		huntedenemy = " ".join(cmd.tokens[1:]).lower()
		target_data = target = ewhunting.find_enemy(enemy_search=huntedenemy, user_data=user_data)

	if target_data == None:
		response = "ENDLESS WAR didn't understand that name.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		try:
			if (target_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state in [ewcfg.life_state_executive, ewcfg.life_state_enlisted]) or (target_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler):
				response = "Hey ASSHOLE! They're on your side!!"
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			elif (target_data.enemyclass == ewcfg.enemy_class_shambler and target_data.gvs_coord not in ewcfg.gvs_coords_end):
				response = "It's no use, they're too far away!"
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		except:
			pass

	if target_data.poi != user_data.poi:
		response = "You can't {} someone, who's not even here.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	id_status = ewcfg.status_taunted_id

	target_statuses = target_data.getStatusEffects()

	if id_status in target_statuses:
		response = "{} has already been taunted.".format(target.display_name)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	target_data.applyStatus(id_status = id_status, source = cmd.message.author.id, id_target = cmd.message.author.id)

	user_data.sap -= sap_cost

	user_poi = ewcfg.id_to_poi.get(user_data.poi)
	user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_attack, True)
	user_data.persist()

	response = "You spend {} sap to taunt {} into attacking you.".format(sap_cost, target.display_name)
	await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def aim(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	response = ""

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "A bit late for that, don't you think?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	sap_cost = 2
	
	if sap_cost > user_data.sap:
		response = "You don't have enough sap to {}. ({}/{})".format(cmd.tokens[0], user_data.sap, sap_cost)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	#if cmd.mentions_count < 1:
	#	response = "Who do you want to {} at?".format(cmd.tokens[0])
	#	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	if cmd.mentions_count > 1:
		response = "You can only focus on aiming at one person at a time.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	if cmd.mentions_count == 1:
		target = cmd.mentions[0]
		target_data = EwUser(member = target)
	else:
		huntedenemy = " ".join(cmd.tokens[1:]).lower()
		target_data = target = ewhunting.find_enemy(enemy_search=huntedenemy, user_data=user_data)

	if target_data == None:
		response = "ENDLESS WAR didn't understand that name.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		try:
			if (target_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state in [ewcfg.life_state_executive, ewcfg.life_state_enlisted]) or (target_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler):
				response = "Hey ASSHOLE! They're on your side!!"
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			elif (target_data.enemyclass == ewcfg.enemy_class_shambler and target_data.gvs_coord not in ewcfg.gvs_coords_end):
				response = "It's no use, they're too far away!"
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		except:
			pass

	if target_data.poi != user_data.poi:
		response = "You can't {} at someone, who's not even here.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	id_status = ewcfg.status_aiming_id

	user_data.clear_status(id_status = id_status)

	user_data.applyStatus(id_status = id_status, source = cmd.message.author.id, id_target = (target.id if target_data.combatant_type == "player" else target_data.id_enemy))

	user_data.sap -= sap_cost

	user_poi = ewcfg.id_to_poi.get(user_data.poi)
	user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_attack, True)
	user_data.persist()

	response = "You spend {} sap to aim at {}'s weak spot.".format(sap_cost, target.display_name)
	await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

def damage_mod_attack(user_data, market_data, user_mutations, district_data):
	damage_mod = 1

	# Weapon possession
	if user_data.get_weapon_possession():
		damage_mod *= 1.2

	# Lone wolf
	if ewcfg.mutation_id_lonewolf in user_mutations:
		allies_in_district = district_data.get_players_in_district(
			min_level = math.ceil((1/10) ** 0.25 * user_data.slimelevel),
			life_states = [ewcfg.life_state_enlisted],
			factions = [user_data.faction]
		)
		if user_data.id_user in allies_in_district:
			allies_in_district.remove(user_data.id_user)

		if len(allies_in_district) == 0:
			damage_mod *= 1.5
			
	# Organic fursuit
	if ewcfg.mutation_id_organicfursuit in user_mutations and (
		ewutils.check_fursuit_active(user_data.id_server)
	):
		damage_mod *= 2

	# Social animal
	if ewcfg.mutation_id_socialanimal in user_mutations:
		allies_in_district = district_data.get_players_in_district(
			min_level = math.ceil((1/10) ** 0.25 * user_data.slimelevel),
			life_states = [ewcfg.life_state_enlisted],
			factions = [user_data.faction]
		)
		if user_data.id_user in allies_in_district:
			allies_in_district.remove(user_data.id_user)

		damage_mod *= 1 + 0.1 * len(allies_in_district)
				
	# Dressed to kill
	if ewcfg.mutation_id_dressedtokill in user_mutations:
		if user_data.freshness >= 250:
			damage_mod *= 1.5

	if ewcfg.mutation_id_2ndamendment in user_mutations:
		if user_data.weapon != -1 and user_data.sidearm != -1:
			weapon_item = EwItem(id_item=user_data.weapon)
			weapon_c = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
			sidearm_item = EwItem(id_item=user_data.sidearm)
			sidearm_c = ewcfg.weapon_map.get(sidearm_item.item_props.get("weapon_type"))
			if weapon_c.is_tool == 0 and sidearm_c.is_tool == 0:
				damage_mod *= 1.25

	return damage_mod

def damage_mod_defend(shootee_data, shootee_mutations, market_data, shootee_weapon):

	damage_mod = 1
	if ewcfg.mutation_id_organicfursuit in shootee_mutations and (
		ewutils.check_fursuit_active(shootee_data.id_server)
	):
		damage_mod *= 0.1

	# Fat chance
	if ewcfg.mutation_id_fatchance in shootee_mutations and shootee_data.hunger / shootee_data.get_hunger_max() > 0.5:
		damage_mod *= 0.75
			

	# defensive weapon
	if shootee_weapon != None:
		if ewcfg.weapon_class_defensive in shootee_weapon.classes:
			damage_mod *= 0.75

	return damage_mod

def get_sap_armor(shootee_data, sap_ignored):
	# apply hardened sap armor
	try:
		effective_hardened_sap = shootee_data.hardened_sap - sap_ignored + shootee_data.defense
	except: # If shootee_data doesn't have defense, aka it's a monster
		effective_hardened_sap = shootee_data.hardened_sap - sap_ignored
	level = 0

	if hasattr(shootee_data, "slimelevel"):
		level = shootee_data.slimelevel
	elif hasattr(shootee_data, "level"):
		level = shootee_data.level

	if effective_hardened_sap >= 0:
		sap_armor = 10 / (10 + effective_hardened_sap)
	else:
		sap_armor = (10 + abs(effective_hardened_sap)) / 10
	return sap_armor



async def spray(cmd):
	#Get user data, then flag for PVP
	user_data = EwUser(id_user=cmd.message.author.id, id_server=cmd.guild.id)

	market_data = EwMarket(id_server=cmd.guild.id)
	time_current = market_data.clock

	time_now_float = time.time()
	time_now = int(time_now_float)

	#was_pvp = user_data.time_expirpvp > time_now
	#user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_annex, enlisted=True)

	user_data.persist()
	# if not was_pvp:
	# 	await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
	# 	user_data = EwUser(id_user=cmd.message.author.id, id_server=cmd.guild.id)

	# Get shooting player's info

	weapon = None
	weapon_item = None
	sidearm_viable = 0
	user_mutations = user_data.get_mutations()


	#if user_data.sidearm >= 0:
	#	weapon_item = EwItem(id_item=user_data.sidearm)
	#	weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
	#	captcha = weapon_item.item_props.get('captcha')
	#	if ewcfg.weapon_class_paint in weapon.classes:
	#		sidearm_viable = 1

	if user_data.weapon >= 0 and sidearm_viable == 0:
		weapon_item = EwItem(id_item=user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
		captcha = weapon_item.item_props.get('captcha')

	response = canCap(cmd)
	if response == "":
		if user_data.slimelevel <= 0:
			user_data.slimelevel = 1
			user_data.persist()

		#Get district data
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(id_server=cmd.guild.id, district=poi.id_poi)

		gangsters_in_district = district_data.get_players_in_district(min_slimes=ewcfg.min_slime_to_cap, life_states=[ewcfg.life_state_enlisted], ignore_offline=True)


		miss = False
		crit = False
		backfire = False

		jammed = False
		strikes = 0
		bystander_damage = 0
		miss_mod = 0
		crit_mod = 0
		dmg_mod = 0
		sap_damage = 0
		sap_ignored = 0

		weapon.fn_effect = ewcfg.weapon_type_convert.get(weapon.id_weapon)

		shooter_status_mods = get_shooter_status_mods(user_data, None, None)

		miss_mod += round(shooter_status_mods['miss'], 2)
		crit_mod += round(shooter_status_mods['crit'], 2)
		dmg_mod += round(shooter_status_mods['dmg'], 2)
		
		slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 300)
		slimes_damage = int((50000 + slimes_spent * 10) * (100 + (user_data.weaponskill * 5)) / 100.0)
		slimes_spent = round(slimes_spent * .1125)
		statuses = user_data.getStatusEffects()

		backfire_damage = int(ewutils.slime_bylevel(user_data.slimelevel) / 20)

		if weapon is None:
			slimes_damage /= 2  # penalty for not using a weapon, otherwise fists would be on par with other weapons

		slimes_damage += int(slimes_damage * dmg_mod)
		#user_data.hunger += ewcfg.hunger_pershot * ewutils.hunger_cost_mod(user_data.slimelevel)

		if weapon != None and weapon.fn_effect != None:
			# Build effect container
			ctn = EwEffectContainer(
				miss=miss,
				backfire=backfire,
				crit=crit,
				jammed=jammed,
				slimes_damage=slimes_damage,
				slimes_spent=slimes_spent,
				user_data=user_data,
				weapon_item=weapon_item,
				shootee_data=None,
				time_now=time_now,
				bystander_damage=bystander_damage,
				miss_mod=miss_mod,
				crit_mod=crit_mod,
				sap_damage=sap_damage,
				sap_ignored=sap_ignored,
				backfire_damage=backfire_damage
			)

			# Make adjustments


			weapon.fn_effect(ctn)

			# Apply effects for non-reference values
			resp_cont = ewutils.EwResponseContainer(id_server=cmd.guild.id)
			miss = ctn.miss
			backfire = ctn.backfire
			crit = ctn.crit
			jammed = ctn.jammed
			slimes_damage = ctn.slimes_damage
			slimes_spent = ctn.slimes_spent
			sap_damage = ctn.sap_damage
			backfire_damage = ctn.backfire_damage

			if backfire is True and random.randint(0, 1) == 0:
				miss = False

			if district_data.all_neighbors_friendly() and user_data.faction != district_data.controlling_faction:
				backfire = True

			if miss is True and random.randint(0, 1) == 0:
				miss = False

			if (slimes_spent > user_data.slimes):
				# Not enough slime to shoot.
				response = "You don't have enough slime to cap. ({:,}/{:,})".format(user_data.slimes, slimes_spent)
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

			weapon_item.item_props['time_lastattack'] = time_now_float
			weapon_item.persist()
			user_data.change_slimes(n=(-user_data.slimes if slimes_spent >= user_data.slimes else -slimes_spent), source=ewcfg.source_spending)
			user_data.persist()


			# Remove a bullet from the weapon
			if ewcfg.weapon_class_ammo in weapon.classes:
				weapon_item.item_props['ammo'] = int(weapon_item.item_props.get("ammo")) - 1

			# Remove one item from stack
			if ewcfg.weapon_class_thrown in weapon.classes:
				weapon_item.stack_size -= 1
			if miss or backfire or jammed:
				slimes_damage = 0

				weapon_item.item_props["consecutive_hits"] = 0
				crit = False
			weapon_item.persist()
			# Remove !revive invulnerability.
			user_data.time_lastrevive = 0
			market_data = EwMarket(id_server=cmd.guild.id)
			# apply attacker damage mods
			slimes_damage *= damage_mod_attack(
				user_data=user_data,
				user_mutations=user_mutations,
				market_data=market_data,
				district_data=district_data
			)
			if weapon.id_weapon == ewcfg.weapon_id_watercolors:
				if not (miss or backfire or jammed):
					slimes_damage = ewcfg.min_garotte

			elif weapon.id_weapon == ewcfg.weapon_id_thinnerbomb:
				if user_data.faction == district_data.controlling_faction:
					slimes_damage = round(slimes_damage * .2)
				else:
					slimes_damage *= 3
					backfire_damage *= 3

			if ewcfg.mutation_id_patriot in user_mutations:
				slimes_damage *= 1.25
			if len(gangsters_in_district) == 1 and ewcfg.mutation_id_lonewolf in user_mutations:
				slimes_damage *= 1.25

			if 3 <= time_current <= 10:
				slimes_damage *= (4/3)

			#if (user_data.faction != district_data.controlling_faction and (user_data.faction is None or user_data.faction == '')) and district_data.capture_points > ewcfg.limit_influence[district_data.property_class]:
			#	slimes_damage = round(slimes_damage / 5)
			#	pass
			if weapon != None:
				if miss:
					response = weapon.tool_props[0].get('miss_spray')
				elif backfire:
					response = "You're in a dangerous place, and it's having an effect on your nerves...\n" + weapon.str_backfire.format(name_player = cmd.message.author.display_name) + "\nNext time, don't cap this deep in enemy territory.\n {} loses {} slime!".format(cmd.message.author.display_name, backfire_damage)

					if user_data.slimes - user_data.bleed_storage <= backfire_damage:
						district_data.change_slimes(n=user_data.slimes)
						district_data.persist()
						die_resp = user_data.die(cause=ewcfg.cause_backfire)
						district_data = EwDistrict(district=district_data.name, id_server=district_data.id_server)
						resp_cont.add_member_to_update(cmd.message.author)
						resp_cont.add_response_container(die_resp)
					else:
						district_data.change_slimes(n=backfire_damage / 2)
						user_data.change_slimes(n=-backfire_damage / 2, source=ewcfg.source_self_damage)
						user_data.bleed_storage += int(backfire_damage / 2)

				elif jammed:
					response = "Your spray can gets clogged with some stray sludge! Better unjam that!"
				else:

					response = weapon.tool_props[0].get('reg_spray').format(gang = user_data.faction[:-1].capitalize(), curse = random.choice(list(ewcfg.curse_words.keys())))
					response += " You got {:,} influence for the {}!".format(int(abs(slimes_damage)), user_data.faction.capitalize())


					if (user_data.faction != district_data.cap_side and district_data.cap_side != "") and (user_data.faction is not None or user_data.faction != ''):
						slimes_damage = round(slimes_damage * -.8)
					#district_data.change_capture_points()


					district_data.change_capture_points(progress=slimes_damage, actor=user_data.faction)

					if crit and weapon.id_weapon == ewcfg.weapon_id_watercolors:
						district_data.change_capture_points(progress=-district_data.capture_points, actor=user_data.faction)

					district_data.persist()

					district_data = EwDistrict(district=district_data.name, id_server=district_data.id_server)
					#district_data.capture_points += slimes_damage
					#if district_data.capture_points < 0:
					#	district_data.controlling_faction = user_data.faction
					#	district_data.capture_points *= -1
					#district_data.persist()
					#response = weapon.str_damage.format(
					#	name_player=cmd.message.author.display_name,
					#	name_target=enemy_data.display_name,
					#	hitzone=randombodypart,
					#	strikes=strikes
					#)

					if crit:
						if user_data.faction == ewcfg.faction_boober:
							color = "pink"
						elif user_data.faction == "slimecorp":
							color = "Slimecorp propaganda"
						else:
							color = "purple"
						response = user_data.spray + "\n\n"
						response += weapon.tool_props[0].get('crit_spray').format(color = color)
						response += " It gets you {:,} influence!".format(abs(slimes_damage))
						#response += " {}".format(weapon.str_crit.format(
						#	name_player=cmd.message.author.display_name,
						#	name_target=enemy_data.display_name,
						#	hitzone=randombodypart,
						#))


				if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
					response += "\n" + weapon.str_reload_warning.format(
						name_player=cmd.message.author.display_name)

				if ewcfg.weapon_class_captcha in weapon.classes or jammed:
					if weapon.id_weapon != ewcfg.weapon_id_paintgun:
						new_captcha_low = ewutils.generate_captcha(length = weapon.captcha_length)
						new_captcha = ewutils.text_to_regional_indicator(new_captcha_low)
						#new_loc = new_loc.replace(new_captcha_low, new_captcha)
						response += "\nNew captcha is {}.".format(new_captcha)
						weapon_item.item_props['captcha'] = new_captcha_low
						#new_captcha = ewutils.generate_captcha(length = weapon.captcha_length)
					else:
						riflearray = ewcaptcha.riflecap
						direction = str(random.choice(riflearray))
						weapon_item.item_props['captcha'] = direction
						new_captcha_gun = ewutils.text_to_regional_indicator(direction)
						response += "\nNext target is {}.".format(new_captcha_gun)
					weapon_item.persist()
				father_district_poi = ewcfg.id_to_poi.get(poi.father_district)
				number_streets = len(ewutils.get_street_list(father_district_poi.id_poi))
				if district_data.controlling_faction == user_data.faction and abs(district_data.capture_points) > ewcfg.limit_influence[father_district_poi.property_class]/number_streets:
					if user_data.faction == ewcfg.faction_boober:
						color = "pink"
					elif user_data.faction == "slimecorp":
						color = "Slimecorp propaganda"
					else:
						color = "purple"
					response += "\nThe street is awash in a sea of {}. It's hard to imagine where else you could spray down.".format(color)
				elif district_data.controlling_faction == user_data.faction and abs(district_data.capture_points) > (ewcfg.min_influence[father_district_poi.property_class] + ewcfg.limit_influence[father_district_poi.property_class])/(2 * number_streets):
					pass
					response += "\nThe {} have developed a decent grip on this district.".format(user_data.faction)
				elif district_data.controlling_faction == user_data.faction and abs(district_data.capture_points) > ewcfg.min_influence[father_district_poi.property_class]/number_streets:
					pass
					response += "\nThe {} have developed a loose grip on this district.".format(user_data.faction)

		else:
			if miss:
					response = "You spray something so obscure nobody notices."
			else:
				response = "Nice vandalism! You get {damage} influence out of it!".format(
					damage=abs(slimes_damage)
				)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))




def get_hitzone(injury_map = None):
	if injury_map == None:
		injury_map = ewcfg.injury_weights

	injury = ewutils.weightedChoice(injury_map)

	hitzone = ewcfg.hitzone_map.get(injury)

	return hitzone

def get_injury_severity(shootee_data, slimes_damage, crit):

	severity = 0
	if shootee_data.slimes > 0:
		severity += slimes_damage / shootee_data.slimes
	severity *= 10

	if crit:
		severity += 2

	severity += random.randrange(-2, 3)
	severity = max(0, round(severity))

	return severity


async def sidearm(cmd):
	user_data = EwUser(member=cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to equip a {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	time_now = int(time.time())

	if user_data.time_lastenlist > time_now:
		response = "You've enlisted way too recently! You can't sidearm any weapons just yet."

	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None)

	if item_sought:
		item = EwItem(id_item=item_sought.get("id_item"))

		if item.item_type == ewcfg.it_weapon:

			response = user_data.equip_sidearm(sidearm_item = item)
			user_data.persist()
			item.persist()

		else:
			response = "Not a tool, you ignorant juvenile."
	else:
		response = "You don't have one."

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def switch_weapon(cmd):
	user_data = EwUser(member = cmd.message.author)
	weapon_holder = user_data.weapon
	user_data.weapon = user_data.sidearm
	user_data.sidearm = weapon_holder
	user_data.persist()

	if user_data.weapon == -1 and user_data.sidearm == -1:
		response = "You switch your nothing for nothing. What a notable exchange."
	elif user_data.weapon == -1 and user_data.sidearm:
		response = "You put your weapon away."
	elif user_data.weapon >= 0:
		weapon_item = EwItem(id_item=user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
		response = "**FWIP-CLICK!** You whip out your {}.".format(weapon_item.item_props.get("weapon_name") if weapon_item.item_props.get("weapon_name") != "" else weapon.str_name)
		if ewcfg.weapon_class_captcha in weapon.classes:
			newcaptcha = ewutils.text_to_regional_indicator(weapon_item.item_props.get('captcha'))
			response += " New captcha is {}.".format(newcaptcha)
	else:
		response = ""
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
""" name a weapon using a slime poudrin """

def fulfill_ghost_weapon_contract(possession_data, market_data, user_data, user_name):
	ghost_id = possession_data[0]
	ghost_data = EwUser(id_user = ghost_id, id_server = user_data.id_server)
	
	# shooter 20%, which ghost gains as negative slime up to a cap of 300k
	slime_sacrificed = int(user_data.slimes * 0.2)
	user_data.change_slimes(n = -slime_sacrificed, source = ewcfg.source_ghost_contract)
	negaslime_gained = min(300000, slime_sacrificed)
	ghost_data.change_slimes(n = -negaslime_gained, source = ewcfg.source_ghost_contract)
	ghost_data.persist()
	market_data.negaslime -= -negaslime_gained
	market_data.persist()

	# cancel possession
	ewutils.execute_sql_query(
		"UPDATE inhabitations SET {empowered} = %s WHERE {id_fleshling} = %s AND {id_server} = %s".format(
			empowered = ewcfg.col_empowered,
			id_fleshling = ewcfg.col_id_fleshling,
			id_server = ewcfg.col_id_server,
		),(
			False,
			user_data.id_user,
			user_data.id_server,
		)
	)

	server = ewutils.get_client().get_guild(user_data.id_server)
	ghost_name = server.get_member(ghost_id).display_name
	return "\n\n {} winces in pain as their slime is corrupted into negaslime. {}'s contract has been fulfilled.".format(user_name, ghost_name)

