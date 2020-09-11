import asyncio

import random
import time

import ewcmd
import ewutils
from ewplayer import EwPlayer
import ewcfg
import ewmap
import ewrolemgr
import ewmarket
import ewitem
import ewfarm
import ewsmelting
import ewcosmeticitem
from ew import EwUser
import ewslimeoid
import ewhunting
import ewwep
import ewquadrants
import ewdistrict

from ewitem import EwItem
from ewdistrict import EwDistrict

class EwApartment:
	id_user = -1
	id_server = -1

	name = "a city apartment."
	description = "It's drafty in here! You briefly consider moving out, but your SlimeCoin is desperate to leave your pocket."
	poi = "downtown"
	rent = 200000
	apt_class = "c"
	num_keys = 0
	key_1 = 0
	key_2 = 0

	def __init__(
			self,
			id_user=None,
			id_server=None
	):
		if (id_user != None and id_server != None):
			self.id_user = id_user
			self.id_server = id_server

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object
				cursor.execute("SELECT {}, {}, {}, {}, {}, {}, {}, {} FROM apartment WHERE id_user = %s and id_server = %s".format(
					ewcfg.col_apt_name,
					ewcfg.col_apt_description,
					ewcfg.col_poi,
					ewcfg.col_rent,
					ewcfg.col_apt_class,
					ewcfg.col_num_keys,
					ewcfg.col_key_1,
					ewcfg.col_key_2

				), (self.id_user,
					self.id_server))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.name = result[0]
					self.description = result[1]
					self.poi = result[2]
					self.rent = result[3]
					self.apt_class = result[4]
					self.num_keys = result[5]
					self.key_1 = result[6]
					self.key_2 = result[7]
				elif id_server != None:
					# Create a new database entry if the object is missing.
					cursor.execute("REPLACE INTO apartment({}, {}) VALUES(%s, %s)".format(
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

	def persist(self):
		ewutils.execute_sql_query(
			"REPLACE INTO apartment ({col_id_server}, {col_id_user}, {col_apt_name}, {col_apt_description}, {col_poi}, {col_rent}, {col_apt_class}, {col_num_keys}, {col_key_1}, {col_key_2}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
				col_id_server=ewcfg.col_id_server,
				col_id_user=ewcfg.col_id_user,
				col_apt_name=ewcfg.col_apt_name,
				col_apt_description=ewcfg.col_apt_description,
				col_poi=ewcfg.col_poi,
				col_rent=ewcfg.col_rent,
				col_apt_class=ewcfg.col_apt_class,
				col_num_keys = ewcfg.col_num_keys,
				col_key_1 = ewcfg.col_key_1,
				col_key_2 = ewcfg.col_key_2,

			), (
				self.id_server,
				self.id_user,
				self.name,
				self.description,
				self.poi,
				self.rent,
				self.apt_class,
				self.num_keys,
				self.key_1,
				self.key_2

			))
class EwFurniture:
	item_type = "furniture"

	# The proper name of the furniture item
	id_furniture = ""

	# The string name of the furniture item
	str_name = ""

	# The text displayed when you look at it
	str_desc = ""

	# How rare the item is, can be "Plebeian", "Patrician", or "Princeps"
	rarity = ""

	# Cost in SlimeCoin to buy this item. (slime now, but hopefully we make an exception for furniture)
	price = 0

	# Names of the vendors selling this item. (yo munchy/ben, i kind of want to add a furniture mart)
	vendors = []

	#Text when placing the item
	furniture_place_desc = ""

	#Text when the generic "look" is used
	furniture_look_desc = ""

	#How you received this item
	acquisition = ""

	#the set that the furniture belongs to
	furn_set = ""

	#furniture color
	hue = ""



	def __init__(
		self,
		id_furniture = "",
		str_name = "",
		str_desc = "",
		rarity = "",
		acquisition = "",
		price = 0,
		vendors = [],
		furniture_place_desc = "",
		furniture_look_desc = "",
		furn_set = "",
		hue="",
		num_keys = 0

	):
		self.item_type = ewcfg.it_furniture
		self.id_furniture = id_furniture
		self.str_name = str_name
		self.str_desc = str_desc
		self.rarity = rarity
		self.acquisition = acquisition
		self.price = price
		self.vendors = vendors
		self.furniture_place_desc = furniture_place_desc
		self.furniture_look_desc = furniture_look_desc
		self.furn_set = furn_set
		self.hue = hue
		self.num_keys = num_keys

async def consult(cmd):
	target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
	#to check the descriptions, look for consult_responses in ewcfg

	if target_name == None or len(target_name) == 0:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "What region would you like to look at?"))

	user_data = EwUser(member=cmd.message.author)
	response = ""

	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.poi != ewcfg.poi_id_realestate:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You have to !consult at Slimecorp Real Estate in Old New Yonkers."))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(target_name)

	if poi == None:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "That place doesn't exist. The stupidity of the question drives the realtor to down another bottle."))

	elif poi.id_poi in ewcfg.transports:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "As much as the realtor would like to charge you for being homeless, you can't pay rent for sleeping on public transport."))

	elif poi.id_poi == ewcfg.poi_id_rowdyroughhouse or poi.id_poi == ewcfg.poi_id_copkilltown or poi.id_poi == ewcfg.poi_id_juviesrow:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "\"We don't have apartments in such...urban places,\" your consultant mutters under his breath."))


	elif poi.is_subzone:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You don't find it on the list of properties. Try something that isn't a subzone."))

	elif poi.id_poi == ewcfg.poi_id_assaultflatsbeach or poi.id_poi == ewcfg.poi_id_dreadford: #check for DT and other S districts separately, otherwise rank by class
		multiplier = ewcfg.apartment_s_multiplier

	elif poi.id_poi == ewcfg.poi_id_downtown:
		multiplier = ewcfg.apartment_dt_multiplier

	elif poi.property_class == ewcfg.property_class_c:
		multiplier = 1

	elif poi.property_class == ewcfg.property_class_b:
		multiplier = ewcfg.apartment_b_multiplier

	elif poi.property_class == ewcfg.property_class_a:
		multiplier = ewcfg.apartment_a_multiplier

	else:
		response = "Not for sale."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	if ewcfg.consult_responses[poi.id_poi]:
		response = "You ask the realtor what he thinks of {}.\n\n\"".format(poi.str_name) + ewcfg.consult_responses[poi.id_poi] + "\"\n\n"
		response += "The cost per month is {:,} SC. \n\n The down payment is four times that, {:,} SC.".format(multiplier * getPriceBase(cmd=cmd), multiplier * 4 * getPriceBase(cmd=cmd))
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def signlease(cmd):
	target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
	if target_name == None or len(target_name) == 0:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "What region would you like to rent?"))

	user_data = EwUser(member=cmd.message.author)

	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.poi != ewcfg.poi_id_realestate:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You have to !signlease at Slimecorp Real Estate in Old New Yonkers."))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(target_name)

	if poi == None:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "That place doesn't exist. The consultant behind the counter is aroused by your stupidity."))

	elif poi == ewcfg.poi_id_rowdyroughhouse or poi == ewcfg.poi_id_copkilltown or poi == ewcfg.poi_id_juviesrow:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "\"We don't have apartments in such...urban places,\" your consultant mutters under his breath."))

	elif poi.id_poi in ewcfg.transports:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "As much as the realtor would like to charge you for being homeless, you can't pay rent for sleeping on public transport."))

	elif poi.is_subzone:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You don't find it on the list of properties. Try something that isn't a subzone."))
	#these prices are based on prices in the design doc.
	elif poi.id_poi == ewcfg.poi_id_assaultflatsbeach or poi.id_poi == ewcfg.poi_id_dreadford:
		base_cost = ewcfg.apartment_s_multiplier * getPriceBase(cmd=cmd)

	elif poi.id_poi == ewcfg.poi_id_downtown:
		base_cost = ewcfg.apartment_dt_multiplier * getPriceBase(cmd=cmd)

	elif poi.property_class == ewcfg.property_class_c:
		base_cost = getPriceBase(cmd=cmd)

	elif poi.property_class == ewcfg.property_class_b:
		base_cost = ewcfg.apartment_b_multiplier * getPriceBase(cmd=cmd)

	elif poi.property_class == ewcfg.property_class_a:
		base_cost = ewcfg.apartment_a_multiplier * getPriceBase(cmd=cmd)

	else:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,"Not for sale."))



	if(user_data.slimecoin < base_cost*4):
		return await ewutils.send_message(cmd.client, cmd.message.channel,ewutils.formatMessage(cmd.message.author, "You can't afford it."))

	response = "The receptionist slides you a contract. It reads:\n\n THE TENANT, {},  WILL HERETO SUBMIT {:,} SLIMECOIN EACH MONTH UNTIL THEY INEVITABLY HIT ROCK BOTTOM. THEY MUST ALSO PROVIDE A DOWN PAYMENT OF {:,} TO INSURE THE PROPERTY FROM THEIR GREASY JUVENILE HANDS. SLIMECORP IS NOT RESPONSIBLE FOR ANY INJURY OR PROPERTY DAMAGE THAT MAY OCCUR ON THE PREMISES. THEY'RE ALSO NOT RESPONSIBLE IN GENERAL. YOU ARE. BITCH. \n\nDo you !sign the document, or do you !rip it into a million pieces?".format(cmd.message.author.display_name, base_cost, base_cost*4)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	try:
		message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and 
														message.content.lower() in [ewcfg.cmd_sign, ewcfg.cmd_rip])

		if message != None:
			if message.content.lower() == ewcfg.cmd_sign:
				accepted = True
			if message.content.lower() == ewcfg.cmd_rip:
				accepted = False

	except Exception as e:
		print(e)
		accepted = False

	if not accepted:
		response = "You dirty the agency's floor with your wanton ripping of contracts. Ah. How satisfying."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	else:

		user_data = EwUser(member=cmd.message.author)
		user_apt = EwApartment(id_user=user_data.id_user, id_server=user_data.id_server)

		if (user_data.apt_zone != ewcfg.location_id_empty):
			had_old_place = True
		else:
			had_old_place = False

		user_data.change_slimecoin(n=-base_cost*4, coinsource=ewcfg.coinsource_spending)
		user_data.apt_zone = poi.id_poi
		user_data.persist()


		if user_apt.key_1 != 0:
			ewitem.item_delete(user_apt.key_1)
			user_apt.key_1 = 0
			user_apt.rent = user_apt.rent/1.5
		if user_apt.key_2 != 0:
			ewitem.item_delete(user_apt.key_2)
			user_apt.key_2 = 0
			user_apt.rent = user_apt.rent / 1.5
		user_apt.num_keys = 0

		user_apt.name = "Slimecorp Apartment"
		user_apt.apt_class = poi.property_class
		user_apt.description = "You're on {}'s property.".format(cmd.message.author.display_name)
		user_apt.poi = poi.id_poi
		user_apt.rent = base_cost
		user_apt.persist()

		response = "You signed the lease for an apartment in {} for {:,} SlimeCoin a month.".format(poi.str_name, base_cost)

		if had_old_place:
			response += " The receptionist calls up a moving crew, who quickly move your stuff to your new place. "

		await toss_squatters(user_data.id_user, user_data.id_server)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def retire(cmd):
	user_data = EwUser(member=cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)
	poi_dest = ewcfg.id_to_poi.get(ewcfg.poi_id_apt + user_data.apt_zone) #there isn't an easy way to change this, apologies for being a little hacky


	owner_user = None
	if cmd.mentions_count == 0 and cmd.tokens_count > 1:
		server = cmd.guild
		member_object = server.get_member(ewutils.getIntToken(cmd.tokens))
		owner_user = EwUser(member = member_object)
	elif cmd.mentions_count == 1:
		owner_user = EwUser(member = cmd.mentions[0])

	if owner_user:
		return await usekey(cmd, owner_user)
	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))
	elif ewutils.active_restrictions.get(user_data.id_user) != None and ewutils.active_restrictions.get(user_data.id_user) > 0:
		response = "You can't do that right now."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif user_data.apt_zone != poi.id_poi:
		response = "You don't own an apartment here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		ewmap.move_counter += 1
		move_current = ewutils.moves_active[cmd.message.author.id] = ewmap.move_counter
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You start walking toward your apartment."))
		await asyncio.sleep(20)

		if move_current == ewutils.moves_active[cmd.message.author.id]:
			user_data = EwUser(member=cmd.message.author)
			user_data.poi = poi_dest.id_poi
			user_data.persist()
			await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
			response = "You're in your apartment."

			try:
				await ewutils.send_message(cmd.client, cmd.message.author, response)
			except:
				await ewutils.send_message(cmd.client, ewutils.get_channel(cmd.guild, poi_dest.channel), ewutils.formatMessage(cmd.message.author, response))



async def depart(cmd=None, isGoto = False, movecurrent=None):
	player = EwPlayer(id_user = cmd.message.author.id)
	user_data = EwUser(id_user = player.id_user, id_server = player.id_server)
	poi_source = ewcfg.id_to_poi.get(user_data.poi)
	poi_dest = ewcfg.id_to_poi.get(poi_source.mother_districts[0])

	#isgoto checks if this is part of a goto command.

	client = ewutils.get_client()
	server = ewcfg.server_list[user_data.id_server]
	member_object = server.get_member(user_data.id_user)

	if not poi_source.is_apartment:
		response = "You're not in an apartment."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	else:
		if isGoto:
			move_current = movecurrent
		else:
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You exit the apartment."))
			ewmap.move_counter += 1
			move_current = ewutils.moves_active[cmd.message.author.id] = ewmap.move_counter
		await asyncio.sleep(20)
		if move_current == ewutils.moves_active[cmd.message.author.id]:
			user_data = EwUser(id_user=player.id_user, id_server=player.id_server)
			user_data.poi = poi_dest.id_poi
			user_data.visiting = ewcfg.location_id_empty
			user_data.time_lastenter = int(time.time())
			ewutils.active_target_map[user_data.id_user] = ""
			user_data.persist()

			ewutils.end_trade(user_data.id_user)
			await user_data.move_inhabitants(id_poi = poi_dest.id_poi)	

			await ewrolemgr.updateRoles(client=client, member=member_object)

			if isGoto:
				response = "You arrive in {}.".format(poi_dest.str_name)

			else:
				response = "Here we are. The outside world."

			await ewutils.send_message(cmd.client, ewutils.get_channel(server, poi_dest.channel), ewutils.formatMessage(cmd.message.author, response))

			# SWILLDERMUK
			await ewutils.activate_trap_items(poi_dest.id_poi, user_data.id_server, user_data.id_user)
			
			return


def getPriceBase(cmd):
	#based on stock success
	user_data = EwUser(member=cmd.message.author) #market rates average to 1000. This fomula calculates prices to specification based on that amount.
	kfc = ewmarket.EwStock(stock='kfc', id_server = user_data.id_server)
	tcb = ewmarket.EwStock(stock='tacobell', id_server=user_data.id_server)
	hut = ewmarket.EwStock(stock='pizzahut', id_server=user_data.id_server)
	if abs(kfc.market_rate - 1000) > abs(tcb.market_rate - 1000) and abs(kfc.market_rate - 1000) > abs(hut.market_rate - 1000):
		return kfc.market_rate * 201
	elif abs(tcb.market_rate - 1000) > abs(hut.market_rate - 1000):
		return tcb.market_rate * 201
	else:
		return hut.market_rate * 201
 #returns a price based on the stock with the biggest change

async def rent_time(id_server = None):

	try:
		conn_info = ewutils.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()
		client = ewutils.get_client()
		if id_server != None:
			#get all players with apartments. If a player is evicted, thir rent is 0, so this will not affect any bystanders.
			cursor.execute("SELECT apartment.rent, users.id_user FROM users INNER JOIN apartment ON users.id_user=apartment.id_user WHERE users.id_server = %s AND apartment.id_server = %s AND apartment.rent > 0".format(

			), (
				id_server,
				id_server,
			))

			landowners = cursor.fetchall()

			for landowner in landowners:
				owner_id_user = int(landowner[1])
				owner_rent_price = landowner[0]

				user_data = EwUser(id_user=owner_id_user, id_server=id_server)
				user_poi = ewcfg.id_to_poi.get(user_data.poi)
				poi = ewcfg.id_to_poi.get(user_data.apt_zone)

				if owner_rent_price > user_data.slimecoin:

					if(user_poi.is_apartment and user_data.visiting == ewcfg.location_id_empty):
						user_data.poi = user_data.apt_zone #toss out player
						user_data.persist()
						server = ewcfg.server_list[user_data.id_server]
						member_object = server.get_member(owner_id_user)

						await ewrolemgr.updateRoles(client = client, member=member_object)
						player = EwPlayer(id_user = owner_id_user)
						response = "{} just got evicted. Point and laugh, everyone.".format(player.display_name)
						await ewutils.send_message(client, ewutils.get_channel(server, poi.channel), response)


					user_data = EwUser(id_user=owner_id_user, id_server=id_server)
					user_apt = EwApartment(id_user=owner_id_user, id_server=id_server)
					poi = ewcfg.id_to_poi.get(user_data.apt_zone)

					toss_items(id_user=str(user_data.id_user) + 'closet', id_server=user_data.id_server, poi = poi)
					toss_items(id_user=str(user_data.id_user) + 'fridge', id_server=user_data.id_server, poi = poi)
					toss_items(id_user=str(user_data.id_user) + 'decorate', id_server=user_data.id_server, poi = poi)

					user_data.apt_zone = ewcfg.location_id_empty
					user_data.persist()
					user_apt.rent = 0
					user_apt.poi = " "
					user_apt.persist()

					await toss_squatters(user_id=user_data.id_user, server_id=id_server)

				else:
					user_data.change_slimecoin(n=-owner_rent_price, coinsource=ewcfg.coinsource_spending)
					user_data.persist()
	finally:
		cursor.close()
		ewutils.databaseClose(conn_info)


#async def rent_cycle(cmd):
 #   user_data = EwUser(member = cmd.message.author)
 #   await rent_time(id_server = user_data.id_server)


async def apt_look(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)
	apt_model = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	poi = ewcfg.id_to_poi.get(apt_model.poi)
	lookObject = str(cmd.message.author.id)
	isVisiting = False
	resp_cont = ewutils.EwResponseContainer(id_server=playermodel.id_server)

	if usermodel.visiting != ewcfg.location_id_empty:
		apt_model = EwApartment(id_user=usermodel.visiting, id_server=playermodel.id_server)
		poi = ewcfg.id_to_poi.get(apt_model.poi)
		lookObject = str(usermodel.visiting)
		isVisiting = True

	response = "You stand in {}, your flat in {}.\n\n{}\n\n".format(apt_model.name, poi.str_name, apt_model.description)

	if isVisiting:
		response = response.replace("your", "a")

	resp_cont.add_channel_response(cmd.message.channel, response)

	furns = ewitem.inventory(id_user= lookObject+ewcfg.compartment_id_decorate, id_server= playermodel.id_server, item_type_filter=ewcfg.it_furniture)

	has_hat_stand = False

	furniture_id_list = []
	furn_response = ""
	for furn in furns:
		i = ewitem.EwItem(furn.get('id_item'))

		furn_response += "{} ".format(i.item_props['furniture_look_desc'])

		furniture_id_list.append(i.item_props['id_furniture'])
		if i.item_props.get('id_furniture') == "hatstand":
			has_hat_stand = True


		hue = ewcfg.hue_map.get(i.item_props.get('hue'))
		if hue != None and i.item_props.get('id_furniture') not in ewcfg.furniture_specialhue:
			furn_response += " It's {}. ".format(hue.str_name)
		elif i.item_props.get('id_furniture') in ewcfg.furniture_specialhue:
			if hue != None:
				furn_response = furn_response.replace("-*HUE*-", hue.str_name)
			else:
				furn_response = furn_response.replace("-*HUE*-", "white")

	furn_response += "\n\n"

	if all(elem in furniture_id_list for elem in ewcfg.furniture_lgbt):
		furn_response += "This is the most homosexual room you could possibly imagine. Everything is painted rainbow. A sign on your bedroom door reads \"FORNICATION ZONE\". There's so much love in the air that some dust mites set up a gay bar in your closet. It's amazing.\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_haunted):
		furn_response += "One day, on a whim, you decided to say \"Levy Jevy\" 3 times into the mirror. Big mistake. Not only did it summon several staydeads, but they're so enamored with your decoration that they've been squatting here ever since.\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_highclass):
		furn_response += "This place is loaded. Marble fountains, fully stocked champagne fridges, complementary expensive meats made of bizarre unethical ingredients, it's a treat for the senses. You wonder if there's any higher this place can go. Kind of depressing, really.\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_leather):
		furn_response += "34 innocent lives. 34 lives were taken to build the feng shui in this one room. Are you remorseful about that? Obsessed? Nobody has the base antipathy needed to peer into your mind and pick at your decisions. The leather finish admittedly does look fantastic, however. Nice work.\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_church):
		furn_response += random.choice(ewcfg.bible_verses) + "\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_pony):
		furn_response += "When the Mane 6 combine their powers, kindness, generosity, loyalty, honesty, magic, and the other one, they combine to form the most powerful force known to creation: friendship. Except for slime. That's still stronger.\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_blackvelvet):
		furn_response += "Looking around just makes you want to loosen your tie a bit and pull out an expensive cigar. Nobody in this city of drowned rats and slimeless rubes can stop you now. You commit homicide...in style. Dark, velvety smooth style.\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_seventies):
		furn_response += "Look at all this vintage furniture. Didn't the counterculture that created all this shit advocate for 'peace and love'? Yuck. I hope you didn't theme your bachelor pad around that kind of shit and just bought everything for its retro aesthetic.\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_shitty):
		furn_response += "You're never gonna make it. Look at all this furniture you messed up, do you think someday you can escape this? You're never gonna have sculptures like Stradivarius, or paintings as good as that one German guy. You're deluded and sitting on splinters. Grow up. \n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_instrument):
		furn_response += "You assembled the instruments. Now all you have to do is form a soopa groop and play loudly over other people acts next Slimechella. It's high time the garage bands of this city take over, with fresh homemade shredding and murders most foul. The world's your oyster. As soon as you can trust them with all this expensive equipment.\n\n"
	if all(elem in furniture_id_list for elem in ewcfg.furniture_slimecorp):
		furn_response = "SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP.\n\n"


	clock_data = ewcmd.weather_txt(id_server=playermodel.id_server)
	clock_data = clock_data[16:20]
	furn_response = furn_response.format(time = clock_data)
	resp_cont.add_channel_response(cmd.message.channel, furn_response)

	response = ""
	iterate = 0
	frids = ewitem.inventory(id_user=lookObject + ewcfg.compartment_id_fridge, id_server=playermodel.id_server)

	if(len(frids) > 0):
		response += "\n\nThe fridge contains: "
		fridge_pile = []
		for frid in frids:
			fridge_pile.append(frid.get('name'))
		response += ewutils.formatNiceList(fridge_pile)
		response = response + '.'
	closets = ewitem.inventory(id_user=lookObject + ewcfg.compartment_id_closet, id_server=playermodel.id_server)

	resp_cont.add_channel_response(cmd.message.channel, response)
	response = ""

	if (len(closets) > 0):
		closet_pile = []
		hatstand_pile = []
		for closet in closets:
			closet_obj = ewitem.EwItem(id_item=closet.get('id_item'))
			map_obj = ewcfg.cosmetic_map.get(closet_obj.item_props.get('id_cosmetic'))
			if has_hat_stand and map_obj and map_obj.is_hat == True:
				hatstand_pile.append(closet.get('name'))
			else:
				closet_pile.append(closet.get('name'))
		if len(closet_pile) > 0:
			response += "\n\nThe closet contains: "
			response += ewutils.formatNiceList(closet_pile)
			response = response + '.'
			resp_cont.add_channel_response(cmd.message.channel, response)

		if len(hatstand_pile) > 0:
			response = "\n\nThe hat stand holds: "
			response += ewutils.formatNiceList(hatstand_pile)
			response = response + '.'
			resp_cont.add_channel_response(cmd.message.channel, response)



	shelves = ewitem.inventory(id_user=lookObject + ewcfg.compartment_id_bookshelf, id_server=playermodel.id_server)

	response = ""
	if (len(shelves) > 0):
		response += "\n\nThe bookshelf holds: "
		shelf_pile = []
		for shelf in shelves:
			shelf_pile.append(shelf.get('name'))
		response += ewutils.formatNiceList(shelf_pile)
		response = response + '.'

	resp_cont.add_channel_response(cmd.message.channel, response)

	freezeList = ewslimeoid.get_slimeoid_look_string(user_id=lookObject+'freeze', server_id = playermodel.id_server)

	resp_cont.add_channel_response(cmd.message.channel, freezeList)
	return await resp_cont.post(channel=cmd.message.channel)
	#return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def store_item(cmd, dest):
	destination = dest #used to separate the compartment keyword from the string displayed to the user.
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	apt_model = EwApartment(id_server=playermodel.id_server, id_user=cmd.message.author.id)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)


	if usermodel.visiting != ewcfg.location_id_empty:
		recipient = str(usermodel.visiting)
		apt_model = EwApartment(id_server=playermodel.id_server, id_user=usermodel.visiting)

	else:
		recipient = str(cmd.message.author.id)

	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		if item_sought.get('soulbound'):
			response = "You can't just put away soulbound items. You have to keep them in your pants at least until the Rapture hits."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif item_sought.get('item_type') == ewcfg.it_furniture and (dest != ewcfg.compartment_id_decorate and dest != "store"):
			response = "The fridge and closet don't have huge spaces for furniture storage. Try !decorate or !stow instead."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif item_sought.get('item_type') != ewcfg.it_furniture and (dest == ewcfg.compartment_id_decorate):
			response = "Are you going to just drop items on the ground like a ruffian? Store them in your fridge or closet instead."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		if destination == "store":
			if item_sought.get('item_type') == ewcfg.it_food:
				destination = ewcfg.compartment_id_fridge

			elif item_sought.get('item_type') == ewcfg.it_furniture:
				destination = ewcfg.compartment_id_decorate

			elif item_sought.get('item_type') == ewcfg.it_book:
				destination = ewcfg.compartment_id_bookshelf

			else:
				destination = ewcfg.compartment_id_closet

		storage_limit_base = 4
		if apt_model.apt_class == ewcfg.property_class_b:
			storage_limit_base *= 2

		elif apt_model.apt_class == ewcfg.property_class_a:
			storage_limit_base *= 4

		elif apt_model.apt_class == ewcfg.property_class_s:
			storage_limit_base *= 8


		name_string = item_sought.get('name')

		items_stored = ewitem.inventory(id_user=recipient+destination, id_server=playermodel.id_server)

		if len(items_stored) >= storage_limit_base * 2 and destination == ewcfg.compartment_id_closet:
			response = "The closet is bursting at the seams. Fearing the consequences of opening the door, you decide to hold on to the {}.".format(name_string)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif len(items_stored) >= storage_limit_base and destination == ewcfg.compartment_id_fridge:
			response = "The fridge is so full it's half open, leaking 80's era CFCs into the flat. You decide to hold on to the {}.".format(name_string)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif len(items_stored) >= int(storage_limit_base*1.5) and destination == ewcfg.compartment_id_decorate:
			response = "You have a lot of furniture here already. Hoarding is unladylike, so you decide to hold on to the {}.".format(name_string)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif len(items_stored) >= int(storage_limit_base*3) and destination == ewcfg.compartment_id_bookshelf:
			response = "Quite frankly, you doubt you wield the physical ability to cram another zine onto your bookshelf, so you decided to hold on to the {}.".format(name_string)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


		if item.item_type == ewcfg.it_food and destination == ewcfg.compartment_id_fridge :
			item.item_props["time_fridged"] = time.time()
			item.persist()

		elif item.item_type == ewcfg.it_weapon:
			if usermodel.weapon == item.id_item:
				if usermodel.weaponmarried:
					response = "If only it were that easy. But you can't just shove your lover in a {}.".format(destination)
					return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				usermodel.weapon = -1
				usermodel.persist()
			elif usermodel.sidearm == item.id_item:
				usermodel.sidearm = -1
				usermodel.persist()

		elif item.item_type == ewcfg.it_cosmetic:
			item.item_props["adorned"] = 'false'
			item.item_props["slimeoid"] = 'false'
			item.persist()

		ewitem.give_item(id_item=item.id_item, id_server=playermodel.id_server, id_user=recipient + destination)

		if(destination == ewcfg.compartment_id_decorate):
			response = item.item_props['furniture_place_desc']

		else:
			response = "You store the {} in the {}.".format(name_string, destination)
			hatrack = ewitem.find_item(id_server=playermodel.id_server, id_user=str(playermodel.id_user)+"decorate", item_search="hatstand")
			if destination == "closet" and item_sought.get('item_type') == ewcfg.it_cosmetic:
				map_obj = ewcfg.cosmetic_map.get(item.item_props.get('id_cosmetic'))
				if map_obj != None:
					if map_obj.is_hat == True and hatrack:
						response = "You hang the {} on the rack.".format(name_string)

	else:
		response = "Are you sure you have that item?"

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def remove_item(cmd, dest):
	destination = dest #used to separate the compartment keyword from the string displayed to the user.

	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if usermodel.visiting != ewcfg.location_id_empty:
		recipient = str(usermodel.visiting)

	else:
		recipient = str(cmd.message.author.id)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

	aptmodel = EwApartment(id_user=recipient, id_server=playermodel.id_server)
	key_1 = EwItem(id_item=aptmodel.key_1)
	key_2 = EwItem(id_item=aptmodel.key_2)

	if key_1.id_owner != str(usermodel.id_user) and key_2.id_owner != str(usermodel.id_user) and usermodel.visiting != ewcfg.location_id_empty:
		response = "Burglary takes finesse. You are but a lowly gangster, who takes money the old fashioned way."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	#if the command is "take", we need to determine where the item might be
	if dest == "apartment":
		item_sought = ewitem.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_bookshelf, id_server=playermodel.id_server)
		if not item_sought:
			item_sought = ewitem.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_fridge, id_server=playermodel.id_server)
			if not item_sought:
				item_sought = ewitem.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_closet, id_server=playermodel.id_server)
				if not item_sought:
					item_sought = ewitem.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_decorate, id_server=playermodel.id_server)
				else:
					destination = ewcfg.compartment_id_closet
			else:
				destination = ewcfg.compartment_id_fridge
		else:
			destination = ewcfg.compartment_id_bookshelf

	elif dest == ewcfg.compartment_id_fridge:
		item_sought = ewitem.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_fridge, id_server=playermodel.id_server)

	elif dest == ewcfg.compartment_id_closet:
		item_sought = ewitem.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_closet, id_server=playermodel.id_server)

	elif dest == ewcfg.compartment_id_decorate:
		item_sought = ewitem.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_decorate, id_server=playermodel.id_server)
		destination = "apartment"

	elif dest == ewcfg.compartment_id_bookshelf:
		item_sought = ewitem.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_bookshelf, id_server=playermodel.id_server)

	if item_sought:
		name_string = item_sought.get('name')
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))

		if item_sought.get('item_type') == ewcfg.it_food:
			food_items = ewitem.inventory(
				id_user=cmd.message.author.id,
				id_server=playermodel.id_server,
				item_type_filter=ewcfg.it_food
			)
			if len(food_items) >= usermodel.get_food_capacity():
				response = "You can't carry any more food."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif item_sought.get('item_type') == ewcfg.it_weapon:
			wep_items = ewitem.inventory(
				id_user=cmd.message.author.id,
				id_server=playermodel.id_server,
				item_type_filter=ewcfg.it_weapon
			)
			if len(wep_items) >= usermodel.get_weapon_capacity():
				response = "You can't carry any more weapons."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		if item_sought.get('item_type') == ewcfg.it_food and destination == ewcfg.compartment_id_fridge:
			#the formula is: expire time = expire time + current time - time frozen
			item.item_props['time_expir'] = str(int(float(item.item_props.get('time_expir'))) + (int(time.time()) - int(float(item.item_props.get('time_fridged')))))
			item.time_expir = int(float(item.item_props.get('time_expir')))
			item.item_props['time_fridged'] = '0'
			item.persist()

		ewitem.give_item(id_item=item.id_item, id_server=playermodel.id_server, id_user=cmd.message.author.id)

		response = "You take the {} from the {}.".format(name_string, destination)

		hatrack = ewitem.find_item(id_server=playermodel.id_server, id_user=str(playermodel.id_user) + "decorate", item_search="hatstand")
		if destination == "closet" and item_sought.get('item_type') == ewcfg.it_cosmetic:
			map_obj = ewcfg.cosmetic_map.get(item.item_props.get('id_cosmetic'))
			if map_obj != None:
				if map_obj.is_hat == True and hatrack:
					response = "You take the {} off the rack.".format(name_string)


		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	else:
		response = "Are you sure you have that item?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def upgrade(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	apt_model = EwApartment(id_server=playermodel.id_server, id_user=cmd.message.author.id)

	if usermodel.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if usermodel.apt_zone == ewcfg.location_id_empty:
		response = "You don't have an apartment."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	elif usermodel.poi != ewcfg.poi_id_realestate:
		response = "Upgrade your home at the apartment agency."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	elif(apt_model.apt_class == ewcfg.property_class_s):
		response = "Fucking hell, man. You're loaded, and we're not upgrading you."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	elif(usermodel.slimecoin < apt_model.rent * 8):
		response = "You can't even afford the down payment. We're not entrusting an upgrade to a 99%er like you."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	else:
		poi = ewcfg.id_to_poi.get(usermodel.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = usermodel.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		response = "Are you sure? The upgrade cost is {:,} SC, and rent goes up to {:,} SC per month. To you !accept the deal, or do you !refuse it?".format(apt_model.rent*8, apt_model.rent*2)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		accepted = False

		try:
			message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and 
															message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

			if message != None:
				if message.content.lower() == ewcfg.cmd_accept:
					accepted = True
				if message.content.lower() == ewcfg.cmd_refuse:
					accepted = False
		except:
			accepted = False

		if not accepted:
			response = "Eh. Your loss."
			return await ewutils.send_message(cmd.client, cmd.message.channel,ewutils.formatMessage(cmd.message.author, response))

		else:
			usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
			apt_model = EwApartment(id_server=playermodel.id_server, id_user=cmd.message.author.id)

			usermodel.change_slimecoin(n=apt_model.rent * -8, coinsource= ewcfg.coinsource_spending)

			apt_model.rent *= 2
			apt_model.apt_class = letter_up(letter=apt_model.apt_class)

			usermodel.persist()
			apt_model.persist()
			response = "The deed is done. Back at your apartment, a Slimecorp builder nearly has a stroke trying to speed-renovate. You're now rank {}.".format(apt_model.apt_class)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def watch(cmd):
	player_model = EwPlayer(id_user=cmd.message.author.id)
	user_model = EwUser(id_user=cmd.message.author.id, id_server=player_model.id_server)
	poi = user_model.poi

	if user_model.visiting != ewcfg.location_id_empty:
		user_id = user_model.visiting
	else:
		user_id = cmd.message.author.id
	apartment_model = EwApartment(id_server=cmd.guild.id, id_user=user_id)
	apartment_model.persist()

	poi_object = ewcfg.id_to_poi.get(poi)
	item_sought = ewitem.find_item(id_user=str(user_id) + ewcfg.compartment_id_decorate, id_server=player_model.id_server, item_search="television")
	if item_sought:
		item_obj = ewitem.EwItem(id_item=item_sought.get('id_item'))
	else:
		item_obj = None

	if not poi_object.is_apartment:
		response = "Watching TV in public sounds like a good idea on paper, but when you're 3 hours in, braindead and drooling your fucking tonsils out your yapper you won't want the masses taking pictures."
	elif not item_sought:
		response = "There's no TV here. Give it up and go back to killing people."
	elif item_obj and "television" not in item_obj.item_props.get('id_furniture'):
		response = "Get your counterfeit TVs out of here before you start watching the real deal."
	else:
		user_model.persist()
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You begin watching TV."))
		for x in range (0, 62):
			await asyncio.sleep(300)
			#await asyncio.sleep(1)
			user_model = EwUser(id_user=cmd.message.author.id, id_server=player_model.id_server)
			item_sought = ewitem.find_item(id_user=str(user_id) + ewcfg.compartment_id_decorate, id_server=player_model.id_server, item_search="television")
			if user_model.poi == poi and user_model.time_last_action > (int(time.time()) - ewcfg.time_kickout) and item_sought:
				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, random.choice(ewcfg.tv_lines)))
			else:
				if user_model.time_last_action <= (int(time.time()) - ewcfg.time_kickout):
					return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You fell asleep watching TV."))
				else:
					return
		#await asyncio.sleep(1)
		await asyncio.sleep(300)
		for lyric in ewcfg.the_slime_lyrics:
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, lyric))
			await asyncio.sleep(8)


		poi = ewcfg.id_to_poi.get(user_model.poi)
		
		await ewhunting.spawn_enemy(id_server=cmd.message.guild.id, pre_chosen_type=ewcfg.enemy_type_megaslime, pre_chosen_poi=poi.mother_districts[0], pre_chosen_slimes=ewcfg.tv_set_slime, pre_chosen_level=ewcfg.tv_set_level, pre_chosen_displayname="The Slime")
		response = ""

	user_model = EwUser(id_user=cmd.message.author.id, id_server=player_model.id_server)
	ewutils.active_target_map[user_model.id_user] = ""
	user_model.persist()
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def add_key(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	apartment_data = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if user_data.poi != ewcfg.poi_id_realestate:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You need to request a housekey at the Real Estate Agency."))
	elif user_data.apt_zone == ewcfg.location_id_empty:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You don't have an apartment."))
	elif apartment_data.apt_class == ewcfg.property_class_c:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're practically homeless yourself with that slumhouse you've leased out. Upgrade your house to get a roommate!"))
	elif (apartment_data.apt_class == ewcfg.property_class_b or apartment_data.apt_class == ewcfg.property_class_a) and apartment_data.num_keys >=1:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You already have a roommate. If we let you guys create hippie communes like you're tyring we'd go out of business."))
	elif apartment_data.apt_class == ewcfg.property_class_s and apartment_data.num_keys >= 2:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "2 roommates is enough. You upgraded the apartment, and we upgraded its fragile load bearing capcity. But not by much."))
	elif user_data.slimecoin < apartment_data.rent:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You need to pay base rent in order to receive a new housekey. It sadly appears as though you can't even afford a new friend."))
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		response = "Adding a key will change your rent to {:,} SlimeCoin. It will cost {:,}, as a down payment. Do you !accept or !refuse?".format(int(apartment_data.rent*1.5), apartment_data.rent)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		try:
			accepted = False
			message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and 
															message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

			if message != None:
				if message.content.lower() == ewcfg.cmd_accept:
					accepted = True
				if message.content.lower() == ewcfg.cmd_refuse:
					accepted = False
		except:
			accepted = False
		if not accepted:
			response = "Ok, sure. Live alone forever. See if I care."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		else:
			user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
			user_data.change_slimecoin(n= -apartment_data.rent, coinsource=ewcfg.coinsource_spending)
			user_data.persist()


			new_item_id = ewitem.item_create(
				id_user=cmd.message.author.id,
				id_server=cmd.guild.id,
				item_type=ewcfg.it_item,
				item_props={
					'item_name': "key to {}'s house".format(playermodel.display_name),
					'id_item': "housekey",
					'item_desc': "A key to {}'s house. They must trust you a lot.".format(playermodel.display_name),
					'rarity': ewcfg.rarity_plebeian,
					'houseID': "{}".format(cmd.message.author.id),
					'context': "housekey"
				}
			)
			new_item = EwItem(id_item=new_item_id)
			new_item.soulbound = True
			new_item.persist()

			apartment_data.num_keys += 1
			apartment_data.rent = apartment_data.rent * 1.5
			if apartment_data.key_1 == 0:
				apartment_data.key_1 = new_item_id
			else:
				apartment_data.key_2 = new_item_id
			apartment_data.persist()
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "The realtor examines your profile for a bit before opening his filing cabinet and pulling out a key from the massive pile. 'You two lovebirds enjoy yourselves', he sleepily remarks before tossing it onto the desk. Sweet, new key!"))


async def usekey(cmd, owner_user):
	user_data = EwUser(member=cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)
	poi_dest = ewcfg.id_to_poi.get(ewcfg.poi_id_apt + owner_user.apt_zone)  # there isn't an easy way to change this, apologies for being a little hacky
	inv = ewitem.inventory(id_user=cmd.message.author.id, id_server=cmd.guild.id)
	key = None
	for item_inv in inv:
		if "key to" in item_inv.get('name'):
			item_key_check = EwItem(id_item=item_inv.get('id_item'))
			if item_key_check.item_props.get("houseID") == str(owner_user.id_user):
				key = item_key_check

	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must enter an apartment in a zone's channel.".format(cmd.tokens[0])))
	elif key == None:
		response = "You don't have a key for their apartment."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif owner_user.apt_zone != poi.id_poi:
		response = "Your key doesn't match an apartment here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,  response))
	else:
		ewmap.move_counter += 1
		move_current = ewutils.moves_active[cmd.message.author.id] = ewmap.move_counter
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You start walking toward the apartment."))

		await asyncio.sleep(20)


		if move_current == ewutils.moves_active[cmd.message.author.id]:
			user_data = EwUser(member=cmd.message.author)
			user_data.poi = poi_dest.id_poi
			user_data.visiting = owner_user.id_user
			user_data.persist()
			await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
			response = "You're in the apartment."

			try:
				await ewutils.send_message(cmd.client, cmd.message.author, response)
			except:
				await ewutils.send_message(cmd.client, ewutils.get_channel(cmd.guild, poi_dest.channel), ewutils.formatMessage(cmd.message.author, response))

async def manual_changelocks(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	apartment_data = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if user_data.poi != ewcfg.poi_id_realestate:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You need to request a housekey at the Real Estate Agency."))
	elif user_data.apt_zone == ewcfg.location_id_empty:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You don't have an apartment."))
	elif apartment_data.num_keys <=0:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You don't have any roommates. You live alone."))
	elif user_data.slimecoin < apartment_data.rent * 0.5:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You need to pay half of base rent in order to change the locks around. Whatever scourge you set loose on your property, you'll just have to live with them."))
	else:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		response = "Changing the locks will revert your rent back to before you added keys. It will cost {:,}, though. Do you !accept or !refuse?".format(apartment_data.rent/2)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		try:
			accepted = False
			message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and 
															message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

			if message != None:
				if message.content.lower() == ewcfg.cmd_accept:
					accepted = True
				if message.content.lower() == ewcfg.cmd_refuse:
					accepted = False
		except:
			accepted = False
		if not accepted:
			response = "Ahahaha. Of course you don't."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		else:
			user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
			user_data.change_slimecoin(n=-(apartment_data.rent/2), coinsource=ewcfg.coinsource_spending)
			user_data.persist()

			apartment_data = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)
			if apartment_data.key_1 != 0:
				ewitem.item_delete(apartment_data.key_1)
				apartment_data.key_1 = 0
				apartment_data.rent = apartment_data.rent/1.5
			if apartment_data.key_2 != 0:
				ewitem.item_delete(apartment_data.key_2)
				apartment_data.key_2 = 0
				apartment_data.rent = apartment_data.rent / 1.5
			apartment_data.num_keys = 0
			apartment_data.persist()


			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,  "The realtor makes a couple of shady sounding phone calls and informs you the keys have been permanently destroyed."))

def check(str):
	if str.content == ewcfg.cmd_sign or str.content == ewcfg.cmd_rip:
		return True


	#async def bazaar_update(cmd): ##DEBUG COMMAND. DO NOT RELEASE WITH THIS.
	#   playermodel = EwPlayer(id_user=cmd.message.author.id)
	#  market_data = EwMarket(playermodel.id_server)
	#   market_data.bazaar_wares.clear()

	#  bazaar_foods = []
	#  bazaar_cosmetics = []
	#  bazaar_general_items = []
	#  bazaar_furniture = []

	# for item in ewcfg.vendor_inv.get(ewcfg.vendor_bazaar):
	#	 if item in ewcfg.item_names:
	#		bazaar_general_items.append(item)
	#
	#	   elif item in ewcfg.food_names:
	#		  bazaar_foods.append(item)
	#	 elif item in ewcfg.cosmetic_names:
	#		  bazaar_cosmetics.append(item)
	#
	#	   elif item in ewcfg.furniture_names:
	#		  bazaar_furniture.append(item)
	#
	#   market_data.bazaar_wares['generalitem'] = random.choice(bazaar_general_items)

	#   market_data.bazaar_wares['food1'] = random.choice(bazaar_foods)
	# Don't add repeated foods
	#  while market_data.bazaar_wares.get('food2') is None or market_data.bazaar_wares.get('food2') == \
	#		 market_data.bazaar_wares['food1']:
	#	market_data.bazaar_wares['food2'] = random.choice(bazaar_foods)

	# market_data.bazaar_wares['cosmetic1'] = random.choice(bazaar_cosmetics)
	# Don't add repeated cosmetics
	# while market_data.bazaar_wares.get('cosmetic2') is None or market_data.bazaar_wares.get('cosmetic2') == \
	#		market_data.bazaar_wares['cosmetic1']:
	#   market_data.bazaar_wares['cosmetic2'] = random.choice(bazaar_cosmetics)

	#while market_data.bazaar_wares.get('cosmetic3') is None or market_data.bazaar_wares.get('cosmetic3') == \
	#	   market_data.bazaar_wares['cosmetic1'] or market_data.bazaar_wares.get('cosmetic3') == \
	#	  market_data.bazaar_wares['cosmetic2']:
	# market_data.bazaar_wares['cosmetic3'] = random.choice(bazaar_cosmetics)

	#market_data.bazaar_wares['furniture1'] = random.choice(bazaar_furniture)


	#market_data.persist()


async def freeze(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_server= playermodel.id_server, id_user=cmd.message.author.id)
	ew_slime_model = ewslimeoid.EwSlimeoid(id_user=cmd.message.author.id, id_server=playermodel.id_server)

	if usermodel.visiting != ewcfg.location_id_empty and ew_slime_model.name != "":
		response = "Your slimeoid, sensing you're trying to abandon them in someone else's freezer, begins to pout. Dammit, you can't refuse a face like that."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	elif usermodel.visiting != ewcfg.location_id_empty:
		response = "You don't have a slimeoid on you."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if ew_slime_model.name != "":
		ew_slime_model.id_user += "freeze"
		ew_slime_model.life_state = ewcfg.slimeoid_state_stored
		ew_slime_model.persist()
		usermodel.active_slimeoid = -1
		usermodel.persist()
		response = "You pick up your slimeoid. {} wonders what is going on, but trusts you implicitly. You open the freezer. {} begins to panic. However, you overpower them, shove them in the icebox, and quickly close the door. Whew. You wonder if this is ethical.".format(ew_slime_model.name, ew_slime_model.name)

	else:
		response = "You don't have a slimeoid for that."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	#slimeoid storage works just like regular item storage. Just add "freeze" to the owner's name to store it.

async def unfreeze(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)
	firstCheck = True
	slimeoid_search = ""

	for token in cmd.tokens: #check for first occurrence in comma separated list
		if firstCheck:
			firstCheck = False

		else:
			slimeoid_search += token + " "

	slimeoid_search = slimeoid_search[:-1]
	id_slimeoid = ewslimeoid.find_slimeoid(id_user=str(cmd.message.author.id) + "freeze", id_server=playermodel.id_server, slimeoid_search=slimeoid_search)
	if id_slimeoid != None:
		ew_slime_model = ewslimeoid.EwSlimeoid(id_user=str(cmd.message.author.id) + "freeze", id_slimeoid=id_slimeoid , id_server=playermodel.id_server)
	else:
		ew_slime_model = ewslimeoid.EwSlimeoid(id_user=str(cmd.message.author.id) + "freeze", slimeoid_name=slimeoid_search, id_server=playermodel.id_server)
	yourslimeoid = ewslimeoid.EwSlimeoid(id_user=cmd.message.author.id, id_server=playermodel.id_server)

	if usermodel.visiting != ewcfg.location_id_empty:
		response = "The freezer's stuck! Well you're a guest, anyhow. You probably shouldn't steal any slimeoids."

	elif yourslimeoid.name != "":
		response = "You already have a slimeoid on you. !freeze it first."

	elif slimeoid_search == None or len(slimeoid_search) == 0:
		response = "You need to specify your slimeoid's name."

	elif ew_slime_model.name == None or len(ew_slime_model.name) == 0:
		response = "You don't have anyone like that in the fridge."

	else:
		ew_slime_model.id_user = cmd.message.author.id
		ew_slime_model.life_state = ewcfg.slimeoid_state_active
		ew_slime_model.persist()
		usermodel.active_slimeoid = ew_slime_model.id_slimeoid
		usermodel.persist()
		response = "You open the freezer. Your slimeoid stumbles out, desperately gasping for air. {} isn't sure what it did to deserve cryostasis, but it gives you an apologetic yap in order to earn your forgiveness. \n\n {} is now your slimeoid.".format(ew_slime_model.name, ew_slime_model.name, ew_slime_model.name)

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def apartment (cmd):
	usermodel = EwUser(member=cmd.message.author)
	apartmentmodel = EwApartment(id_user=usermodel.id_user, id_server=usermodel.id_server)
	if usermodel.apt_zone == ewcfg.location_id_empty:
		response = "You don't have an apartment."

	else:
		poi = ewcfg.id_to_poi.get(usermodel.apt_zone)
		response = "Your apartment is in {}. This {} rank apartment costs {:,} SlimeCoin a month.".format(poi.str_name, apartmentmodel.apt_class.upper(), apartmentmodel.rent)

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def apt_help(cmd):
	response = "This is your apartment, your home away from home. You can store items here, but if you can't pay rent they will be ejected to the curb. You can store slimeoids here, too, but eviction sends them back to the real estate agency. You can only access them once you rent another apartment. Rent is charged every two IRL days, and if you can't afford the charge, you are evicted. \n\nHere's a command list. \n!depart: Leave your apartment. !goto commands work also.\n!look: look at your apartment, including all its items.\n!inspect <item>: Examine an item in the room or in your inventory.\n!stow <item>: Place an item in the room.\n!fridge/!closet/!decorate <item>: Place an item in a specific spot.\n!snag <item>: Take an item from storage.\n!unfridge/!uncloset/!undecorate <item>: Take an item from a specific spot.\n!freeze/!unfreeze <slimeoid name>: Deposit and withdraw your slimeoids. You can have 3 created at a time.\n!aptname <new name>:Change the apartment's name.\n!aptdesc <new name>: Change the apartment's base description."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def customize(cmd = None, isDesc = False):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	apt_model = EwApartment(id_server=playermodel.id_server, id_user=cmd.message.author.id)

	#dual function for changing apt info

	if not isDesc: #check for description function or name function
		property_type = "name"
		namechange = cmd.message.content[(len(ewcfg.cmd_aptname)):].strip()
	else:
		property_type = "description"
		namechange = cmd.message.content[(len(ewcfg.cmd_aptdesc)):].strip()

	if usermodel.visiting != ewcfg.location_id_empty:
		response = "This apartment isn't yours."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if property_type == "name":
		apt_model.name = namechange

	elif property_type == "description":
		apt_model.description = namechange

	response = "You changed the {}.".format(property_type)

	if len(namechange) < 2:
		response = "You didn't enter a proper {}.".format(property_type)

	else:
		apt_model.persist()

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def knock(cmd = None):
	user_data = EwUser(member=cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	target_data = None
	if cmd.mentions_count == 0 and cmd.tokens_count > 1:
		server = ewcfg.server_list[user_data.id_server]
		target = server.get_member(cmd.tokens[1])
		target_data = EwUser(member = target)
	elif cmd.mentions_count == 1:
		target = cmd.mentions[0]
		target_data = EwUser(member = cmd.mentions[0])

	if target_data:
		target_poi = ewcfg.id_to_poi.get(target_data.poi)
		if poi.is_apartment:
			response = "You're already in an apartment."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif target_data.apt_zone != user_data.poi:
			response = "You're not anywhere near their apartment."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif (not target_poi.is_apartment) or target_data.visiting != ewcfg.location_id_empty:
			response = "You knock, but nobody's home."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		else:
			response = "{} is knocking at your door. Do you !accept their arrival, or !refuse entry?".format(cmd.message.author.display_name)
			try:
				await ewutils.send_message(cmd.client, target, ewutils.formatMessage(target, response))
			except:
				response = "They aren't taking in any visitors right now."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

			try:
				accepted = False
				if ewutils.active_target_map.get(user_data.id_user) == target_data.apt_zone:
					return #returns if the user is spam knocking. However, the person in the apt still gets each of the DMs above.
				else:
					user_data = EwUser(member=cmd.message.author)
					ewutils.active_target_map[user_data.id_user] = target_data.apt_zone
					message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == target and 
														message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

					if message != None:
						if message.content.lower() == ewcfg.cmd_accept:
							accepted = True
						if message.content.lower() == ewcfg.cmd_refuse:
							accepted = False

							user_data = EwUser(member=cmd.message.author)
							
							# Flag the person knocking to discourage spam
							enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
							user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_knock, enlisted)
							user_data.persist()
							await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
							await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "They don't want your company, and have tipped off the authorities."))
					else:
						pass
						#user_data = EwUser(member=cmd.message.author)
						#if ewutils.active_target_map.get(user_data.id_user) != "": #checks if a user is knocking, records the recipient and removes it when done
						#	user_data.persist()
			except:
				accepted = False
			user_data = EwUser(member=cmd.message.author)
			if accepted:
				user_data.poi = target_poi.id_poi
				user_data.visiting = target_data.id_user
				ewutils.active_target_map[user_data.id_user] = ""
				user_data.persist()
				await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
				response = "You arrive in the abode of {}.".format(target.display_name)
				await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
				response = "{} enters your home.".format(cmd.message.author.display_name)
				return await ewutils.send_message(cmd.client, target, ewutils.formatMessage(target, response))
			else:
				if ewutils.active_target_map.get(user_data.id_user) != "":
					ewutils.active_target_map[user_data.id_user] = ""
	elif cmd.mentions_count == 0:
		response = "Whose door are you knocking?"
		return await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
	else:
		response = "One door at a time, please."
		return await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))

async def bootall(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

	await toss_squatters(user_id=usermodel.id_user, server_id=usermodel.id_server, keepKeys=True)

	response = "You throw a furious tantrum and shoo all the undesirables out. It's only you and your roommates now."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def trickortreat(cmd = None):
	user_data = EwUser(member=cmd.message.author)

	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		response = "There will be neither trick nor treat found in these parts."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "The undead are too wicked and impure for such acts. Seems you can't have your cake and !haunt it too on Double Halloween."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.hunger >= ewutils.hunger_max_bylevel(user_data.slimelevel):
		response = "You're too hungry to trick-or-treat right now."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	reject = False

	items = ewitem.inventory(
		id_user=cmd.message.author.id,
		id_server=cmd.guild.id,
		item_type_filter=ewcfg.it_cosmetic
	)

	costumes = 0
	for it in items:
		i = EwItem(it.get('id_item'))
		context = i.item_props.get('context')
		adorned = i.item_props.get('adorned')
		if context == 'costume' and adorned == 'true':
			costumes += 1

	if costumes == 0 and cmd.mentions_count >= 1:
		response = "How are you gonna go trick-or-treating without a costume on?"
		return await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
	elif costumes == 0 and cmd.mentions_count == 0:
		response = "How are you gonna go trick-or-treating without a costume on?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.mentions_count == 1:
		target = cmd.mentions[0]
		target_data = EwUser(member=target)
		target_poi = ewcfg.id_to_poi.get(target_data.poi)
		if poi.is_apartment:
			response = "You're already in an apartment."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif target_data.apt_zone != user_data.poi:
			response = "You're not anywhere near their apartment."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif (not target_poi.is_apartment) or target_data.visiting != ewcfg.location_id_empty:
			response = "You knock, but nobody's home."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		else:
			response = "{} is all dressed up for Double Halloween, waiting at your doorstep. Do you pull a !trick on them, or !treat them to a piece of candy?".format(cmd.message.author.display_name)

			try:
				await ewutils.send_message(cmd.client, target, ewutils.formatMessage(target, response))
			except:
				response = "They aren't taking in any visitors right now."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

			try:
				treat = False
				if ewutils.active_target_map.get(user_data.id_user) == target_data.apt_zone:
					# For Double Halloween spam knocking isn't really an issue. Just clear up their slot in the active target map for now.
					#print('DEBUG: Spam knock in trickortreat command.')
					ewutils.active_target_map[user_data.id_user] = ""
					return #returns if the user is spam knocking. However, the person in the apt still gets each of the DMs above.
				else:
					user_data = EwUser(member=cmd.message.author)
					ewutils.active_target_map[user_data.id_user] = target_data.apt_zone
					message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == target and 
														message.content.lower() in [ewcfg.cmd_trick, ewcfg.cmd_treat])

					if message != None:
						if message.content.lower() == ewcfg.cmd_treat:
							treat = True
						if message.content.lower() == ewcfg.cmd_trick:
							treat = False
					else:
						reject = True
						#user_data = EwUser(member=cmd.message.author)
						#if ewutils.active_target_map.get(user_data.id_user) != "": #checks if a user is knocking, records the recipient and removes it when done
						#	user_data.persist()
			except:
				reject = True
			user_data = EwUser(member=cmd.message.author)

			if reject:
				response = "No response. Maybe they're busy?"
				await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
				response = "You just sort of wait in your apartment until they go away."
				return await ewutils.send_message(cmd.client, target, ewutils.formatMessage(target, response))

			hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
			user_data.hunger += ewcfg.hunger_pertrickortreat * int(hunger_cost_mod)
			user_data.persist()

			if treat:
				ewutils.active_target_map[user_data.id_user] = ""
				
				item = random.choice(ewcfg.trickortreat_results)
				item_props = ewitem.gen_item_props(item)
				if item is not None:
					ewitem.item_create(
						item_type=item.item_type,
						id_user=cmd.message.author.id,
						id_server=cmd.guild.id,
						item_props=item_props
					)
				item_name = item_props.get('food_name')

				response = "{} gives you a {}. You thank them, and go about your business.".format(target.display_name, item_name)
				await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
				response = "You give {} a {}. Happy Double Halloween, you knucklehead!".format(cmd.message.author.display_name, item_name)
				return await ewutils.send_message(cmd.client, target, ewutils.formatMessage(target, response))
			else:
				slime_loss = random.randrange(10000) + 1

				if slime_loss <= 10:
					trick_index = 0
				elif slime_loss <= 100:
					trick_index = 1
				elif slime_loss <= 1000:
					trick_index = 2
				else:
					trick_index = 3
					
				if ewutils.active_target_map.get(user_data.id_user) != None and ewutils.active_target_map.get(user_data.id_user) != "":
					ewutils.active_target_map[user_data.id_user] = ""
				user_data.change_slimes(n = -slime_loss, source=ewcfg.source_damage)
				if user_data.slimes <= 0:
					client = ewutils.get_client()
					server = client.get_guild(user_data.id_server)
					user_poi = ewcfg.id_to_poi.get(user_data.poi)

					resp_cont = ewutils.EwResponseContainer(id_server=user_data.id_server)
					player_data = EwPlayer(id_user=user_data.id_user, id_server=user_data.id_server)

					user_data.trauma = ewcfg.trauma_id_environment
					user_data.die(cause=ewcfg.cause_killing)
					deathreport = "{skull} *{uname}*: You were tricked to death. {skull}".format(skull=ewcfg.emote_slimeskull, uname=player_data.display_name)

					resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)
					resp_cont.add_channel_response(user_poi.channel, deathreport)

					await resp_cont.post()
					await ewrolemgr.updateRoles(client=client, member=server.get_member(user_data.id_user))

				user_data.persist()
				response = ewcfg.halloween_tricks_trickee[trick_index].format(target.display_name, slime_loss)
				await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
				response = ewcfg.halloween_tricks_tricker[trick_index].format(cmd.message.author.display_name, slime_loss)
				return await ewutils.send_message(cmd.client, target, ewutils.formatMessage(target, response))


	elif cmd.mentions_count == 0:
		user_poi = ewcfg.id_to_poi.get(user_data.poi)

		if user_poi.is_capturable:
			hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
			user_data.hunger += ewcfg.hunger_pertrickortreat * int(hunger_cost_mod)
			user_data.persist()

			trick_chance = 10

			lowtrick = 10
			mediumtrick = 7
			hightrick = 4
			extremetrick = 3

			property_class = user_poi.property_class

			if property_class == ewcfg.property_class_c:
				trick_chance = lowtrick
			elif property_class == ewcfg.property_class_b:
				trick_chance = mediumtrick
			elif property_class == ewcfg.property_class_a:
				trick_chance = hightrick
			elif property_class == ewcfg.property_class_s:
				trick_chance = extremetrick

			class_based_treats = []
			for treat in ewcfg.trickortreat_results:
				if trick_chance == lowtrick and treat.price == 100:
					class_based_treats.append(treat)
				elif trick_chance == mediumtrick and treat.price == 1000:
					class_based_treats.append(treat)
				elif trick_chance == hightrick and treat.price == 10000:
					class_based_treats.append(treat)
				elif trick_chance == extremetrick and treat.price == 100000:
					class_based_treats.append(treat)


			response = "You try and go trick-or-treating around various houses in {}.\n".format(user_poi.str_name)

			if random.randrange(trick_chance) == 0:
				treat = False
			else:
				treat = True

			if treat:
				item = random.choice(class_based_treats)
				item_props = ewitem.gen_item_props(item)
				if item is not None:
					ewitem.item_create(
						item_type=item.item_type,
						id_user=cmd.message.author.id,
						id_server=cmd.guild.id,
						item_props=item_props
					)
				item_name = item_props.get('food_name')

				response += "A kind resident gives you a {}. You thank them, and go about your business.".format(item_name)
			else:
				slime_loss = random.randrange(10000) + 1

				if slime_loss <= 10:
					trick_index = 0
				elif slime_loss <= 100:
					trick_index = 1
				elif slime_loss <= 1000:
					trick_index = 2
				else:
					trick_index = 3

				user_data.change_slimes(n=-slime_loss, source=ewcfg.source_damage)
				if user_data.slimes <= 0:
					client = ewutils.get_client()
					server = client.get_guild(user_data.id_server)
					user_poi = ewcfg.id_to_poi.get(user_data.poi)

					resp_cont = ewutils.EwResponseContainer(id_server=user_data.id_server)
					player_data = EwPlayer(id_user=user_data.id_user, id_server=user_data.id_server)

					user_data.trauma = ewcfg.trauma_id_environment
					user_data.die(cause=ewcfg.cause_killing)
					deathreport = "{skull} *{uname}*: You were tricked to death. {skull}".format(skull=ewcfg.emote_slimeskull, uname=player_data.display_name)

					resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)
					resp_cont.add_channel_response(user_poi.channel, deathreport)

					await resp_cont.post()
					await ewrolemgr.updateRoles(client=client, member=server.get_member(user_data.id_user))
				user_data.persist()
				response += ewcfg.halloween_tricks_trickee[trick_index].format("A pranksterous resident", slime_loss)


			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		else:
			response = "Whose door are you knocking?"
			return await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))

	else:
		response = "One door at a time, please."
		return await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))


async def cancel(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)
	aptmodel = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)

	if usermodel.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if usermodel.poi != ewcfg.poi_id_realestate:
		response = "You can only null your lease at the Real Estate Agency."
	elif usermodel.apt_zone == ewcfg.location_id_empty:
		response = "You don't have an apartment."
	elif aptmodel.rent * 4 > usermodel.slimecoin:
		response = "You can't afford the lease separation. Time to take your eviction like a champ."
	else:
		poi = ewcfg.id_to_poi.get(usermodel.poi)
		district_data = EwDistrict(district = poi.id_poi, id_server = usermodel.id_server)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		poi = ewcfg.id_to_poi.get(usermodel.apt_zone)
		response = "The separation will cost {:,} SlimeCoin. Do you !accept the termination, or !refuse it?".format(aptmodel.rent * 4)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		try:
			accepted = False
			message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and 
															message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

			if message != None:
				if message.content.lower() == ewcfg.cmd_accept:
					accepted = True
				if message.content.lower() == ewcfg.cmd_refuse:
					accepted = False
		except:
			accepted = False
		if not accepted:
			response = "Ahahaha. Of course you don't."
			return await ewutils.send_message(cmd.client, cmd.message.channel,ewutils.formatMessage(cmd.message.author, response))

		else:
			usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)
			aptmodel = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)

			response = "You cancel your {} apartment for {:,} SlimeCoin.".format(poi.str_name , aptmodel.rent * 4)
			inv_toss_closet = ewitem.inventory(id_user=str(usermodel.id_user) + ewcfg.compartment_id_closet, id_server=playermodel.id_server)

			toss_items(id_user=str(usermodel.id_user) + ewcfg.compartment_id_closet, id_server=playermodel.id_server, poi=poi)
			toss_items(id_user=str(usermodel.id_user) + ewcfg.compartment_id_fridge, id_server=playermodel.id_server, poi=poi)
			toss_items(id_user=str(usermodel.id_user) + ewcfg.compartment_id_decorate, id_server=playermodel.id_server, poi=poi)

			usermodel.apt_zone = ewcfg.location_id_empty
			usermodel.change_slimecoin(n=aptmodel.rent * -4, coinsource=ewcfg.coinsource_spending)
			aptmodel.rent = 0
			aptmodel.poi = ""
			aptmodel.apt_class = ewcfg.property_class_c
			usermodel.persist()
			aptmodel.persist()

			await toss_squatters(cmd.message.author.id, cmd.guild.id)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def toss_squatters(user_id = None, server_id = None, keepKeys = False):
	player_info = EwPlayer(id_user=user_id)
	apt_info = EwApartment(id_user=user_id, id_server= server_id)

	client = ewutils.get_client()
	server = client.get_guild(server_id)
	
	member_data = server.get_member(player_info.id_user)
	
	if player_info.id_server != None and member_data != None:
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();
			client = ewutils.get_client()

			# get all players visiting an evicted apartment and kick them out
			cursor.execute(
				"SELECT {} FROM users WHERE {} = %s AND {} = %s".format(
					ewcfg.col_id_user,
					ewcfg.col_visiting,
					ewcfg.col_id_server,
				), (
					member_data.id,
					server_id,
				))

			squatters = cursor.fetchall()
			key_1 = EwItem(id_item=apt_info.key_1).id_owner
			key_2 = EwItem(id_item=apt_info.key_2).id_owner
			for squatter in squatters:
				sqt_data = EwUser(id_user=squatter[0], id_server=player_info.id_server)
				if keepKeys and (sqt_data.id_user == key_1 or sqt_data.id_user == key_2):
					pass
				else:
					server = ewcfg.server_list[sqt_data.id_server]
					member_object = server.get_member(squatter[0])
					sqt_data.poi = sqt_data.poi[3:]
					sqt_data.visiting = ewcfg.location_id_empty
					sqt_data.persist()
					await ewrolemgr.updateRoles(client=client, member=member_object)
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

async def lobbywarning(cmd):
	user_data = EwUser(member = cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)
	if poi.is_apartment:
		response = "Try that in a DM to ENDLESS WAR."
	else:
		response = "You're not in an apartment."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def aquarium(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)

	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		if item.item_props.get('acquisition') == ewcfg.acquisition_fishing:

			if float(item.item_props.get('time_expir')) < time.time():
				response = "Uh oh. This thing's been rotting for awhile. You give the fish mouth to mouth in order to revive it. Somehow this works, and a few minutes later it's swimming happily in a tank."
			else:
				response = "You gently pull the flailing, sopping fish from your back pocket, dropping it into an aquarium. It looks a little less than alive after being deprived of oxygen for so long, so you squirt a bit of your slime in the tank to pep it up."


			fname = "{}'s aquarium".format(item.item_props.get('food_name'))
			fdesc = "You look into the tank to admire your {}. {}".format(item.item_props.get('food_name'), item.item_props.get('food_desc'))
			lookdesc = "A {} tank sits on a shelf.".format(item.item_props.get('food_name'))
			placedesc = "You carefully place the aquarium on your shelf. The {} inside silently heckles you each time your clumsy ass nearly drops it.".format(item.item_props.get('food_name'))
			ewitem.item_create(
				id_user=cmd.message.author.id,
				id_server=cmd.guild.id,
				item_type=ewcfg.it_furniture,
				item_props={
					'furniture_name': fname,
					'id_furniture': "aquarium",
					'furniture_desc': fdesc,
					'rarity': ewcfg.rarity_plebeian,
					'acquisition': "{}".format(item_sought.get('id_item')),
					'furniture_place_desc': placedesc,
					'furniture_look_desc': lookdesc
				}
			)

			ewitem.give_item(id_item=item_sought.get('id_item'), id_user=str(cmd.message.author.id) + "aqu", id_server=cmd.guild.id)
			#ewitem.item_delete(id_item=item_sought.get('id_item'))

		else:
			response = "That's not a fish. You're not going to find a fancy tank with filters and all that just to drop a damn {} in it.".format(item_sought.get('name'))
	else:
		if item_search == "" or item_search == None:
			response = "Specify a fish. You're not allowed to put yourself into an aquarium."
		else:
			response = "Are you sure you have that item?"
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def propstand(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)

	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		if item.item_type == ewcfg.it_furniture:
			if item.item_props.get('id_furniture') == "propstand":
				response = "It's already on a prop stand."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		if item.soulbound:
			response = "Cool idea, but no. If you tried to mount a soulbound item above the fireplace you'd be stuck there too."
		else:
			if item.item_type == ewcfg.it_weapon and usermodel.weapon >= 0 and item.id_item == usermodel.weapon:
				if usermodel.weaponmarried:
					weapon = ewcfg.weapon_map.get(item.item_props.get("weapon_type"))
					response = "Your dearly beloved? Put on a propstand? At least have the decency to get a divorce at the dojo first, you cretin.".format(weapon.str_weapon)
					return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				else:
					usermodel.weapon = -1
					usermodel.persist()
			elif item.item_type == ewcfg.it_cosmetic:
				item.item_props["adorned"] = "false"
				item.item_props["slimeoid"] = 'false'
				item.persist()

			fname = "{} stand".format(item_sought.get('name'))
			response = "You affix the {} to a wooden mount. You know this priceless trophy will last thousands of years, so you spray it down with formaldehyde to preserve it forever. Or at least until you decide to remove it.".format(item_sought.get('name'))
			lookdesc = "A {} is mounted on the wall.".format(item_sought.get('name'))
			placedesc = "You mount the {} on the wall. God damn magnificent.".format(item_sought.get('name'))
			fdesc = item_sought.get('item_def').str_desc
			if fdesc.find('{') >= 0:
				fdesc = fdesc.format_map(item.item_props)

				if fdesc.find('{') >= 0:
					fdesc = fdesc.format_map(item.item_props)
			fdesc += " It's preserved on a mount."

			ewitem.item_create(
				id_user=cmd.message.author.id,
				id_server=cmd.guild.id,
				item_type=ewcfg.it_furniture,
				item_props={
					'furniture_name': fname,
					'id_furniture': "propstand",
					'furniture_desc': fdesc,
					'rarity': ewcfg.rarity_plebeian,
					'acquisition': "{}".format(item_sought.get('id_item')),
					'furniture_place_desc': placedesc,
					'furniture_look_desc': lookdesc
				}
			)
			ewitem.give_item(id_item=item_sought.get('id_item'), id_user=str(cmd.message.author.id) + "stand", id_server=cmd.guild.id)
			#ewitem.item_delete(id_item=item_sought.get('id_item'))

	else:
		if item_search == "" or item_search == None:
			response = "Specify the item you want to put on the stand."
		else:
			response = "Are you sure you have that item?"
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def flowerpot(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)

	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		vegetable = ewcfg.food_map.get(item.item_props.get('id_food'))
		if vegetable and ewcfg.vendor_farm in vegetable.vendors:

			if float(item.item_props.get('time_expir')) < time.time():
				response = "Whoops. The stink lines on these {} have developed sentience and are screaming in agony. Must've kept them in your pocket too long. Well, whatever. It'll air out with enough slime. You shove the {} into a pot.".format(item_sought.get('name'), item_sought.get('name'))
			else:
				response = "You remove the freshly picked {} from your inventory and shove them into some nearby earthenware. Ah, the circle of life. Maybe with enough time you'll be able to !harvest them after they fully grow. LOL, just kidding. We all know that doesn't work.".format(item_sought.get('name'))

			fname = "Pot of {}".format(item.item_props.get('food_name'))
			fdesc = "You gaze at your well-tended {}. {}".format(item.item_props.get('food_name'), item.item_props.get('food_desc'))
			lookdesc = "A pot of {} sits on a shelf.".format(item.item_props.get('food_name'))
			placedesc = "You take your flowerpot full of {} and place it on the windowsill.".format(item.item_props.get('food_name'))
			ewitem.item_create(
				id_user=cmd.message.author.id,
				id_server=cmd.guild.id,
				item_type=ewcfg.it_furniture,
				item_props={
					'furniture_name': fname,
					'id_furniture': "flowerpot",
					'furniture_desc': fdesc,
					'rarity': ewcfg.rarity_plebeian,
					'acquisition': "{}".format(item_sought.get('id_item')),
					'furniture_place_desc': placedesc,
					'furniture_look_desc': lookdesc
				}
			)

			ewitem.give_item(id_item=item_sought.get('id_item'), id_user=str(cmd.message.author.id) + "flo", id_server=cmd.guild.id)
			#ewitem.item_delete(id_item=item_sought.get('id_item'))

		else:
			response = "You put a {} in the flowerpot. You then senselessly break the pot, dropping it on the ground, because {} is not a real plant and you're a knuckledragging retard.".format(item_sought.get('name'), item_sought.get('name'))
	else:
		if item_search == "" or item_search == None:
			rand1 = random.randrange(100)
			rand2 = random.randrange(5)
			response = ""
			if rand1 > 80:
				response = "**"
			for x in range (rand2+1):
				response+="Y"
			for x in range (rand2+1):
				response+="E"
			for x in range (rand2+1):
				response+="A"
			for x in range (rand2+1):
				response+="H"
			response +=" BRO!"
			if rand1 > 80:
				response +="**"
		else:
			response = "Are you sure you have that item?"
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def releasefish(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

	if usermodel.poi != ewcfg.poi_id_bazaar:
		response = "You need to see a specialist at The Bazaar to do that."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(usermodel.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = usermodel.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		if item.item_type == ewcfg.it_furniture:
			if item.item_props.get('id_furniture') == "aquarium" and item.item_props.get('acquisition') != ewcfg.acquisition_smelting:
				ewitem.give_item(id_item=item.item_props.get('acquisition'), id_user = cmd.message.author.id, id_server = cmd.guild.id)
				response = "The mysterious individual running the fish luring stall helps you coax the fish out of its tank."
				ewitem.item_delete(id_item=item_sought.get('id_item'))
			elif item.item_props.get('acquisition') == ewcfg.acquisition_smelting:
				response = "Uh oh. This one's not coming out. "
			else:
				response = "Don't try to conjure a fish out of just anything. Find an aquarium."
		else:
			response = "Don't try to conjure a fish out of just anything. Find an aquarium."
	else:
		response = "Are you sure you have that fish?"
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def releaseprop(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

	if user_data.poi != ewcfg.poi_id_bazaar:
		response = "You need to see a specialist at The Bazaar to do that."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		if item.item_type == ewcfg.it_furniture:
			if item.item_props.get('id_furniture') == "propstand" and item.item_props.get('acquisition') != ewcfg.acquisition_smelting:
				ewitem.give_item(id_item=item.item_props.get('acquisition'), id_user = cmd.message.author.id, id_server = cmd.guild.id)
				response = "After a bit of tugging, you and the mysterious individual running the prop release stall pry the item of its stand."
				ewitem.item_delete(id_item=item_sought.get('id_item'))
			elif item.item_props.get('acquisition') == ewcfg.acquisition_smelting:
				response = "Uh oh. This one's not coming out. "
			else:
				response = "Don't try to unstand that which is not a stand."
		else:
			response = "Don't try to unstand that which is not a stand."
	else:
		response = "Are you sure you have that item?"
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def unpot(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		if item.item_type == ewcfg.it_furniture:
			if item.item_props.get('id_furniture') == "flowerpot" and item.item_props.get('acquisition') != ewcfg.acquisition_smelting:
				ewitem.give_item(id_item=item.item_props.get('acquisition'), id_user = cmd.message.author.id, id_server = cmd.guild.id)
				response = "You yank the foliage out of the pot."
				ewitem.item_delete(id_item=item_sought.get('id_item'))
			else:
				response = "Get the pot before you unpot it."
		else:
			response = "Get the pot before you unpot it."
	else:
		response = "Are you sure you have that plant?"
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def wash(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)
	slimeoid_search = ewslimeoid.find_slimeoid(slimeoid_search=item_search, id_server=playermodel.id_server, id_user=playermodel.id_user)
	slimeoid = ewslimeoid.EwSlimeoid(id_slimeoid=slimeoid_search, id_server=playermodel.id_server, id_user=playermodel.id_user)
	if usermodel.visiting != ewcfg.location_id_empty:
		usermodel = EwUser(id_user=usermodel.visiting, id_server=playermodel.id_server)

	if ewitem.find_item(item_search="washingmachine", id_user=str(usermodel.id_user) + ewcfg.compartment_id_decorate, id_server=playermodel.id_server, item_type_filter = ewcfg.it_furniture):
		if item_sought:
			item = ewitem.EwItem(id_item=item_sought.get('id_item'))
			if item.item_type == ewcfg.it_cosmetic:
				if item.item_props.get('hue') is None or item.item_props.get('hue') == "":
					response = "You jam your dirty laundry into the machine. It's so loud you can't hear the gunshots outside anymore, but you're sure the neighbors won't mind. Some time later, your {} pops out, freshly cleaned and full of static.".format(item.item_props.get('cosmetic_name'))
				else:
					item.item_props['hue'] = ""
					item.persist()
					response = "You toss the {} into the washing machine. The thing shakes and sputters like a juvie begging for its life, but after a few minutes your {} comes out undyed.".format(item.item_props.get('cosmetic_name'), item.item_props.get('cosmetic_name'))
				if item.item_props.get('adorned') == 'true':
					response += " You readorn the {}. Man, this feels comfy.".format(item.item_props.get('cosmetic_name'))
			else:
				response = "Don't put a {} in the washing machine. You'll break it. Christ, you spent like 1.6 mega on that fucking thing.".format(item_sought.get('name'))
		elif slimeoid_search and slimeoid.life_state == ewcfg.slimeoid_state_active:
			if (slimeoid.hue == "" or slimeoid.hue is None) and (slimeoid.coating == "" or slimeoid.coating is None):
				response = "You tell {} that there's a poudrin for it in the washer. D'aww. It's so trusting. The moment it enters, you close the lid and crank the spin cycle. You laugh for awhile, but quickly realize you don't know how to pause it and let {} out. Guess you'll have to wait the full 20 minutes. Time passes, and your slimeoid stumbles out, nearly unconscious. Sorry, little buddy.".format(slimeoid.name, slimeoid.name)
			else:
				response = "You toss your colored slimeoid in the washing machine and press start. Not only is {} now tumbling around and getting constantly scalded by the water, it's also suddenly insecure about how you wanted to rid it of its racial identity. After about 20 minutes {} steps out, demoralized, exhausted, and green as an ogre. Nice. Nice.".format(slimeoid.name, slimeoid.name)
				slimeoid.hue = ""
				slimeoid.coating = ""
				slimeoid.persist()
		elif item_search == "":
			response = "There's nothing to wash. You start the machine anyway, riding it like a fucking bucking bronco. This thing really was a great investment."
		elif item_search == "brain":
			response = "You learn the cult-like ideology that all washing machines share. Truly, this new philosophy will change the future of humanity, and you'll be the one it all starts with. You'll follow this washing machine through thick and thin, through cover-ups and mass suicide plots. The religion will be called: LAUNDRONISM. \n\nActually, you know what? This is fucking stupid. ENDLESS WAR is way better at brainwashing than this rusty old thing."
		else:
			response = "There's no item or slimeoid with that name. "
	else:
		response = "You don't have a washing machine."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def browse(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	if ewitem.find_item(item_search="laptopcomputer", id_user=str(usermodel.id_user) + ewcfg.compartment_id_decorate, id_server=playermodel.id_server):
		response = random.choice(ewcfg.browse_list)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		await apt_look(cmd=cmd)

async def frame(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

	namechange = cmd.message.content[(len(ewcfg.cmd_frame)):].strip()

	if ewitem.find_item(item_search="pictureframe", id_user=usermodel.id_user, id_server=playermodel.id_server, item_type_filter = ewcfg.it_furniture) and len(namechange) >= 3:
		item_sought = ewitem.find_item(item_search="pictureframe", id_user=usermodel.id_user, id_server=playermodel.id_server, item_type_filter = ewcfg.it_furniture)
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		item.item_props['furniture_desc'] = namechange
		item.persist()
		response = "You slip the photo into a frame."
	elif len(namechange) < 3:
		response = "You try to put the nothing you have into the frame, but then you realize that's fucking stupid. Put an image link in there"
	else:
		response = "You don't have a frame."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def dyefurniture(cmd):
	first_id = ewutils.flattenTokenListToString(cmd.tokens[1:2])
	second_id = ewutils.flattenTokenListToString(cmd.tokens[2:])

	try:
		first_id_int = int(first_id)
		second_id_int = int(second_id)
	except:
		first_id_int = None
		second_id_int = None

	if first_id != None and len(first_id) > 0 and second_id != None and len(second_id) > 0:
		response = "You don't have one."

		items = ewitem.inventory(
			id_user=cmd.message.author.id,
			id_server=cmd.guild.id,
		)

		furniture = None
		dye = None
		for item in items:
			if item.get('id_item') in [first_id_int, second_id_int] or first_id in ewutils.flattenTokenListToString(
					item.get('name')) or second_id in ewutils.flattenTokenListToString(item.get('name')):
				if item.get('item_type') == ewcfg.it_furniture and furniture is None:
					furniture = item

				if item.get('item_type') == ewcfg.it_item and item.get('name') in ewcfg.dye_map and dye is None:
					dye = item

				if furniture != None and dye != None:
					break

		if furniture != None:
			if dye != None:
				user_data = EwUser(member=cmd.message.author)

				furniture_item = ewitem.EwItem(id_item=furniture.get("id_item"))
				dye_item = ewitem.EwItem(id_item=dye.get("id_item"))

				hue = ewcfg.hue_map.get(dye_item.item_props.get('id_item'))

				response = "You dye your {} in {} paint!".format(furniture_item.item_props.get('furniture_name'), hue.str_name)
				furniture_item.item_props['hue'] = hue.id_hue

				furniture_item.persist()
				ewitem.item_delete(id_item=dye.get('id_item'))
			else:
				response = 'Use which dye? Check your **!inventory**.'
		else:
			response = 'Dye which furniture? Check your **!inventory**.'

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'You need to specify which furniture you want to paint and which dye you want to use! Check your **!inventory**.'))

async def set_alarm(cmd):
	player_data = EwPlayer(id_user = cmd.message.author.id)
	user_data = EwUser(id_user=cmd.message.author.id, id_server=player_data.id_server)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[2:])
	time_set = ewutils.flattenTokenListToString(cmd.tokens[1:2])

	if ((not time_set[:-2].isnumeric()) or not (time_set[-2:] == "am" or time_set[-2:] == "pm")) and time_set != "off":
		response = "You're setting it wrong, dumbass. See, I knew you were bad at this."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	item_sought = ewitem.find_item(item_search=item_search, id_user=user_data.id_user, id_server=player_data.id_server)
	if item_sought:
		item = EwItem(id_item=item_sought.get('id_item'))
		if "alarmclock" == item.item_props.get('id_furniture'):
			item.item_props['furniture_name'] = "alarm clock set to {}".format(time_set)
			item.persist()
			response = "You set the clock to {}.".format(time_set)
		else:
			response = "That's not an alarm clock. Be less delusional next time."
	else:
		response = "You don't have an item like that."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def setOffAlarms(id_server = None):
	
	ewutils.logMsg('Setting off alarms...')
	
	if id_server != None:
		client = ewutils.get_client()
		server = client.get_guild(id_server)
		time_current = ewmarket.EwMarket(id_server=id_server).clock
		if time_current <= 12:
			displaytime = str(time_current)
			ampm = 'am'
		if time_current > 12:
			displaytime = str(time_current - 12)
			ampm = 'pm'

		if time_current == 24:
			ampm = "am"
		elif time_current == 12:
			ampm = "pm"

		item_search = "alarm clock set to {}{}".format(displaytime, ampm)
		clockinv = ewitem.find_item_all(item_search="alarmclock", id_server=id_server, item_type_filter = ewcfg.it_furniture)

		for clock in clockinv:
			isFurnished = False
			clock_obj = EwItem(id_item=clock.get('id_item'))

			if clock_obj.item_props.get('furniture_name') == item_search:
				if "decorate" in clock_obj.id_owner:
					isFurnished = True
				clock_user = clock_obj.id_owner.replace("decorate", "")
				clock_member = server.get_member(user_id=clock_user)
				if clock_member != None:
					clock_player = EwUser(member=clock_member)
					if (isFurnished == False or ("apt" in clock_player.poi and clock_player.visiting == "empty")) and clock_member:
						try:
							await ewutils.send_message(client, clock_member, ewutils.formatMessage(clock_member, "BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP"))
						except:
							ewutils.logMsg("failed to send alarm to user {}".format(clock_member.id))

async def jam(cmd):
	#def leppard and pearl jam? meet def jam. this is what the refrance, fuck yeah.
	item_found = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_found, id_user=cmd.message.author.id, id_server=cmd.guild.id)

	if item_sought:
		item = EwItem(id_item=item_sought.get('id_item'))
		if item.item_props.get("id_furniture") in ewcfg.furniture_instrument or item.item_props.get("weapon_type") == ewcfg.weapon_id_bass:
			cycle = random.randrange(20)
			response = ""
			for x in range(1, cycle):
				response += random.choice([":musical_note:", ":notes:"])
		else:
			response = "You place your mouth on the {} but it makes no noise. Either that's not an instrument or you aren't good enough.".format(item_sought.get('name'))
	else:
		response = "Are you sure you have that item?"

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

#****************************************************************************
#ADD NEW FUNCTIONS HERE async above, non-async below
#****************************************************************************
def toss_items(id_user = None, id_server = None, poi = None):
	if id_user != None and id_server != None and poi != None:
		inv_toss = ewitem.inventory(id_user=id_user, id_server=id_server)
		for stuff in inv_toss:  # toss all items out
			stuffing = ewitem.EwItem(id_item=stuff.get('id_item'))
			stuffing.id_owner = poi.id_poi
			if stuff.get('item_type') == ewcfg.it_food and id_user[-6:] == ewcfg.compartment_id_fridge:
				stuffing.item_props['time_expir'] = str(int(float(stuffing.item_props.get('time_expir'))) + (int(time.time()) - int(float(stuffing.item_props.get('time_fridged')))))
				stuffing.time_expir = int(float(stuffing.item_props.get('time_expir')))
				stuffing.item_props['time_fridged'] = '0'
			stuffing.persist()


def letter_up(letter = None):
	if letter == ewcfg.property_class_a:
		return ewcfg.property_class_s
	elif letter == ewcfg.property_class_b:
		return ewcfg.property_class_a
	elif letter == ewcfg.property_class_c:
		return ewcfg.property_class_b


async def aptCommands(cmd):
	tokens_count = len(cmd.tokens)
	cmd_text = cmd.tokens[0].lower() if tokens_count >= 1 else ""
	player = EwPlayer(id_user=cmd.message.author.id)
	user_data = EwUser(id_user=cmd.message.author.id, id_server=player.id_server)
	server = ewcfg.server_list[user_data.id_server]
	member_object = server.get_member(user_data.id_user)

	if cmd_text == ewcfg.cmd_depart or cmd_text == ewcfg.cmd_retire:
		return await depart(cmd)
	elif cmd_text == ewcfg.cmd_fridge:
		return await store_item(cmd=cmd, dest=ewcfg.compartment_id_fridge)
	elif cmd_text == ewcfg.cmd_store:
		return await store_item(cmd=cmd, dest="store")
	elif cmd_text == ewcfg.cmd_closet:
		return await store_item(cmd=cmd, dest=ewcfg.compartment_id_closet)
	elif cmd_text == ewcfg.cmd_take:
		return await remove_item(cmd=cmd, dest="apartment")
	elif cmd_text == ewcfg.cmd_uncloset:
		return await remove_item(cmd=cmd, dest=ewcfg.compartment_id_closet)
	elif cmd_text == ewcfg.cmd_unfridge:
		return await remove_item(cmd=cmd, dest=ewcfg.compartment_id_fridge)
	elif cmd_text == ewcfg.cmd_decorate:
		return await store_item(cmd=cmd, dest=ewcfg.compartment_id_decorate)
	elif cmd_text == ewcfg.cmd_undecorate:
		return await remove_item(cmd=cmd, dest=ewcfg.compartment_id_decorate)
	elif cmd_text in [ewcfg.cmd_shelve, ewcfg.cmd_shelve_alt_1]:
		return await store_item(cmd=cmd, dest=ewcfg.compartment_id_bookshelf)
	elif cmd_text in [ewcfg.cmd_unshelve, ewcfg.cmd_unshelve_alt_1]:
		return await remove_item(cmd=cmd, dest=ewcfg.compartment_id_bookshelf)
	elif cmd_text == ewcfg.cmd_upgrade:
		return await upgrade(cmd = cmd)
	elif cmd_text == ewcfg.cmd_breaklease:
		return await cancel(cmd=cmd)
	elif cmd_text == ewcfg.cmd_look:
		return await apt_look(cmd)
	elif cmd_text == ewcfg.cmd_freeze:
		return await freeze(cmd=cmd)
	elif cmd_text == ewcfg.cmd_unfreeze:
		return await unfreeze(cmd=cmd)
	elif cmd_text == ewcfg.cmd_aptname:
		return await customize(cmd=cmd)
	elif cmd_text == ewcfg.cmd_aptdesc:
		return await customize(cmd=cmd, isDesc=True)
	elif cmd_text == ewcfg.cmd_move or cmd_text == ewcfg.cmd_move_alt1 or cmd_text == ewcfg.cmd_move_alt2 or cmd_text == ewcfg.cmd_move_alt3 or cmd_text == ewcfg.cmd_move_alt4 or cmd_text == ewcfg.cmd_move_alt5:
		return await ewmap.move(cmd=cmd, isApt = True)
	elif cmd_text == ewcfg.cmd_knock:
		return await knock(cmd=cmd)
	#elif cmd_text == ewcfg.cmd_trickortreat:
	#	return await trickortreat(cmd=cmd)
	elif cmd_text == ewcfg.cmd_wash:
		return await wash(cmd=cmd)
	elif cmd_text == ewcfg.cmd_browse:
		return await browse(cmd=cmd)
	# from here, all commands are prebuilt and just set to work in DMs
	cmd.message.author = member_object
	if cmd_text == ewcfg.cmd_use:
		return await ewitem.item_use(cmd=cmd)
	elif cmd_text == ewcfg.cmd_pot:
		return await flowerpot(cmd=cmd)
	elif cmd_text == ewcfg.cmd_unpot:
		return await unpot(cmd=cmd)
	elif cmd_text == ewcfg.cmd_extractsoul:
		return await ewitem.soulextract(cmd=cmd)
	elif cmd_text == ewcfg.cmd_returnsoul:
		return await ewitem.returnsoul(cmd=cmd)
	elif cmd_text == ewcfg.cmd_releaseprop:
		return await releaseprop(cmd=cmd)
	elif cmd_text == ewcfg.cmd_releasefish:
		return await releasefish(cmd=cmd)
	elif cmd_text == ewcfg.cmd_halt or cmd_text == ewcfg.cmd_halt_alt1:
		return await ewmap.halt(cmd=cmd)
	elif cmd_text == ewcfg.cmd_aquarium:
		return await aquarium(cmd=cmd)
	elif cmd_text == ewcfg.cmd_propstand:
		return await propstand(cmd=cmd)
	elif cmd_text == ewcfg.cmd_howl or cmd_text == ewcfg.cmd_howl_alt1:
		return await ewcmd.cmd_howl(cmd=cmd)
	elif cmd_text == ewcfg.cmd_moan:
		return await ewcmd.cmd_moan(cmd=cmd)
	elif cmd_text == ewcfg.cmd_data:
		return await ewcmd.data(cmd=cmd)
	elif cmd_text == ewcfg.cmd_hunger:
		return await ewcmd.hunger(cmd=cmd)
	elif cmd_text == ewcfg.cmd_slimecoin or cmd_text == ewcfg.cmd_slimecoin_alt1 or cmd_text == ewcfg.cmd_slimecoin_alt2 or cmd_text == ewcfg.cmd_slimecoin_alt3:
		return await ewmarket.slimecoin(cmd=cmd)
	elif cmd_text == ewcfg.cmd_score or cmd_text == ewcfg.cmd_score_alt1:
		return await ewcmd.score(cmd=cmd)
	elif cmd_text == ewcfg.cmd_slimeoid:
		return await ewslimeoid.slimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_adorn:
		return await ewcosmeticitem.adorn(cmd=cmd)
	elif cmd_text == ewcfg.cmd_smelt:
		return await ewsmelting.smelt(cmd=cmd)
	elif cmd_text == ewcfg.cmd_dress_slimeoid or cmd_text == ewcfg.cmd_dress_slimeoid_alt1:
		return await ewslimeoid.dress_slimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_annoint or cmd_text == ewcfg.cmd_annoint_alt1:
		return await ewwep.annoint(cmd=cmd)
	elif cmd_text == ewcfg.cmd_petslimeoid:
		return await ewslimeoid.petslimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_abuseslimeoid:
		return await ewslimeoid.abuseslimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_playfetch:
		return await ewslimeoid.playfetch(cmd=cmd)
	elif cmd_text == ewcfg.cmd_observeslimeoid:
		return await ewslimeoid.observeslimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_walkslimeoid:
		return await ewslimeoid.walkslimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_wiki:
		return await ewcmd.wiki(cmd=cmd)
	elif cmd_text == ewcfg.cmd_unsalute:
		return await ewcmd.unsalute(cmd=cmd)
	elif cmd_text == ewcfg.cmd_time or cmd_text == ewcfg.cmd_clock or cmd_text == ewcfg.cmd_weather:
		return await ewcmd.weather(cmd=cmd)
	elif cmd_text == ewcfg.cmd_add_quadrant:
		return await ewquadrants.add_quadrant(cmd=cmd)
	elif cmd_text == ewcfg.cmd_clear_quadrant:
		return await ewquadrants.clear_quadrant(cmd=cmd)
	elif cmd_text == ewcfg.cmd_apartment:
		return await apartment(cmd=cmd)
	elif cmd_text == ewcfg.cmd_booru:
		return await ewcmd.booru(cmd=cmd)
	elif cmd_text == ewcfg.cmd_dyecosmetic or ewcfg.cmd_dyecosmetic_alt1 == cmd_text or ewcfg.cmd_dyecosmetic_alt2 == cmd_text or ewcfg.cmd_dyecosmetic_alt3 == cmd_text:
		return await ewcosmeticitem.dye(cmd=cmd)
	elif cmd_text == ewcfg.cmd_equip == cmd_text:
		return await ewwep.equip(cmd=cmd)
	elif ewcfg.cmd_give == cmd_text:
		return await ewitem.give(cmd=cmd)
	elif ewcfg.cmd_hurl == cmd_text:
		return await ewcmd.hurl(cmd=cmd)
	elif ewcfg.cmd_map == cmd_text:
		return await ewcmd.map(cmd=cmd)
	elif ewcfg.cmd_news == cmd_text or ewcfg.cmd_patchnotes == cmd_text:
		return await ewcmd.patchnotes(cmd=cmd)
	elif ewcfg.cmd_petslimeoid == cmd_text:
		return await ewslimeoid.petslimeoid(cmd=cmd)
	elif ewcfg.cmd_quarterlyreport == cmd_text:
		return await ewmarket.quarterlyreport(cmd=cmd)
	elif ewcfg.cmd_salute == cmd_text:
		return await ewcmd.salute(cmd=cmd)
	elif ewcfg.cmd_get_ashen == cmd_text or ewcfg.cmd_get_ashen_alt1 == cmd_text:
		return await ewquadrants.get_ashen(cmd=cmd)
	elif ewcfg.cmd_get_caliginous == cmd_text or ewcfg.cmd_get_caliginous_alt1 == cmd_text:
		return await ewquadrants.get_caliginous(cmd=cmd)
	elif ewcfg.cmd_get_flushed == cmd_text or ewcfg.cmd_get_flushed_alt1 == cmd_text:
		return await ewquadrants.get_ashen(cmd=cmd)
	elif ewcfg.cmd_get_pale == cmd_text or ewcfg.cmd_get_pale_alt1 == cmd_text:
		return await ewquadrants.get_pale(cmd=cmd)
	elif ewcfg.cmd_get_quadrants == cmd_text:
		return await ewquadrants.get_quadrants(cmd=cmd)
	elif ewcfg.cmd_harvest == cmd_text:
		return await ewcmd.harvest(cmd=cmd)
	elif ewcfg.cmd_check_farm == cmd_text:
		return await ewfarm.check_farm(cmd=cmd)
	elif ewcfg.cmd_bottleslimeoid == cmd_text:
		return await ewslimeoid.bottleslimeoid(cmd=cmd)
	elif ewcfg.cmd_unbottleslimeoid == cmd_text:
		return await ewslimeoid.unbottleslimeoid(cmd = cmd)
	elif ewcfg.cmd_piss == cmd_text:
		return await ewcmd.piss(cmd=cmd)
	elif ewcfg.cmd_scout == cmd_text:
		return await ewmap.scout(cmd=cmd)
	elif ewcfg.cmd_smoke == cmd_text:
		return await ewcosmeticitem.smoke(cmd=cmd)
	elif ewcfg.cmd_squeeze == cmd_text:
		return await ewitem.squeeze(cmd=cmd)
	elif ewcfg.cmd_watch == cmd_text:
		return await watch(cmd=cmd)
	elif ewcfg.cmd_setalarm == cmd_text:
		return await set_alarm(cmd=cmd)
	elif ewcfg.cmd_bootall == cmd_text:
		return await bootall(cmd=cmd)
	#elif cmd_text == "~bazaarupdate":
	 #   return await bazaar_update(cmd)
	elif cmd_text == ewcfg.cmd_help or cmd_text == ewcfg.cmd_help_alt1 or cmd_text == ewcfg.cmd_help_alt2 or cmd_text == ewcfg.cmd_help_alt3:
		return await apt_help(cmd)
	elif cmd_text == ewcfg.cmd_accept or cmd_text == ewcfg.cmd_refuse:
		pass
	elif cmd_text == ewcfg.cmd_switch or cmd_text == ewcfg.cmd_switch_alt_1:
		return await ewwep.switch_weapon(cmd=cmd)
	elif cmd_text == ewcfg.cmd_changespray or cmd_text == ewcfg.cmd_changespray_alt1:
		return await ewdistrict.change_spray(cmd=cmd)
	elif cmd_text == ewcfg.cmd_tag:
		return await ewdistrict.tag(cmd=cmd)
	elif cmd_text == ewcfg.cmd_sidearm:
		return await ewwep.sidearm(cmd=cmd)
	#elif cmd_text == ewcfg.cmd_trick or cmd_text == ewcfg.cmd_treat:
	#	pass
	elif cmd_text[0]==ewcfg.cmd_prefix: #faliure text
		randint = random.randint(1, 3)
		msg_mistake = "ENDLESS WAR is growing frustrated."
		if randint == 2:
			msg_mistake = "ENDLESS WAR denies you his favor."
		elif randint == 3:
			msg_mistake = "ENDLESS WAR pays you no mind."

		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, msg_mistake), 2)

async def nothing(cmd):# for an accept, refuse, sign or rip
	return 0
