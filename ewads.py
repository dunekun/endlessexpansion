import time

import ewcfg
import ewutils

from ew import EwUser
from ewplayer import EwPlayer
from ewdistrict import EwDistrict

class EwAd:

	id_ad = -1

	id_server = -1
	id_sponsor = ""

	content = ""
	time_expir = 0

	def __init__(
		self,
		id_ad = None
	):
		if id_ad != None:
			self.id_ad = id_ad
			data = ewutils.execute_sql_query("SELECT {id_server}, {id_sponsor}, {content}, {time_expir} FROM ads WHERE {id_ad} = %s".format(
				id_server = ewcfg.col_id_server,
				id_sponsor = ewcfg.col_id_sponsor,
				content = ewcfg.col_ad_content,
				time_expir = ewcfg.col_time_expir,
				id_ad = ewcfg.col_id_ad,
			),(
				self.id_ad,
			))

			if len(data) > 0:
				result = data[0]
				
				self.id_server = result[0]
				self.id_sponsor = result[1]
				self.content = result[2]
				self.time_expir = result[3]
			else:
				self.id_ad = -1

	def persist(self):
		ewutils.execute_sql_query("REPLACE INTO ads ({}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s)".format(
			ewcfg.col_id_ad,
			ewcfg.col_id_server,
			ewcfg.col_id_sponsor,
			ewcfg.col_ad_content,
			ewcfg.col_time_expir,
		),(
			self.id_ad,
			self.id_server,
			self.id_sponsor,
			self.content,
			self.time_expir
		))
	

def create_ad(id_server, id_sponsor, content, time_expir):
	ewutils.execute_sql_query("INSERT INTO ads ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)".format(
		ewcfg.col_id_server,
		ewcfg.col_id_sponsor,
		ewcfg.col_ad_content,
		ewcfg.col_time_expir,
	),(
		id_server,
		id_sponsor,
		content,
		time_expir,
	))

def get_ads(id_server):
	time_now = int(time.time())
	ad_ids = []
	data = ewutils.execute_sql_query("SELECT {id_ad} FROM ads WHERE {id_server} = %s AND {time_expir} > %s ORDER BY {time_expir} ASC".format(
		id_ad = ewcfg.col_id_ad,
		id_server = ewcfg.col_id_server,
		time_expir = ewcfg.col_time_expir,
	),(
		id_server,
		time_now
	))

	for result in data:
		ad_ids.append(result[0])
 
	return ad_ids

def delete_expired_ads(id_server):
	time_now = int(time.time())
	data = ewutils.execute_sql_query("DELETE FROM ads WHERE {id_server} = %s AND {time_expir} < %s".format(
		id_server = ewcfg.col_id_server,
		time_expir = ewcfg.col_time_expir,
	),(
		id_server,
		time_now
	))
	

def format_ad_response(ad_data):
	
	sponsor_player = EwPlayer(id_user = ad_data.id_sponsor)
	sponsor_disclaimer = "Paid for by {}".format(sponsor_player.display_name)
	ad_response = "A billboard catches your eye:\n\n{}\n\n*{}*".format(ad_data.content, sponsor_disclaimer)

	return ad_response

async def advertise(cmd):

	time_now = int(time.time())
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	if user_data.poi != ewcfg.poi_id_slimecorphq:
		response = "To buy ad space, you'll need to go SlimeCorp HQ."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		

	cost = ewcfg.slimecoin_toadvertise

	if user_data.slimecoin < cost:
		response = "Your don't have enough slimecoin to advertise. ({:,}/{:,})".format(user_data.slimecoin, cost)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	ads = get_ads(cmd.guild.id)

	if len(ads) >= ewcfg.max_concurrent_ads:
		first_ad = EwAd(id_ad = ads[0])
		first_expire = first_ad.time_expir

		secs_to_expire = int(first_expire - time_now)
		mins_to_expire = int(secs_to_expire / 60)
		hours_to_expire = int(mins_to_expire / 60)
		days_to_expire = int(hours_to_expire / 24)

		expire_list = []
		if hours_to_expire > 0:
			expire_list.append("{} days".format(days_to_expire))
		if hours_to_expire > 0:
			expire_list.append("{} hours".format(hours_to_expire % 24))
		if mins_to_expire > 0:
			expire_list.append("{} minutes".format(mins_to_expire % 60))
		else:
			expire_list.append("{} seconds".format(secs_to_expire % 60))

		time_to_expire = ewutils.formatNiceList(names = expire_list, conjunction = "and")

		response = "Sorry, but all of our ad space is currently in use. The next vacancy will be in {}.".format(time_to_expire)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.tokens_count < 2:
		response = "Please specify the content of your ad."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	content = cmd.message.content[len(cmd.tokens[0]):].strip()

	if len(content) > ewcfg.max_length_ads:
		response = "Your ad is too long, we can't fit that on a billboard. ({:,}/{:,})".format(len(content), ewcfg.max_length_ads)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	sponsor_disclaimer = "Paid for by {}".format(cmd.message.author.display_name)

	response = "This is what your ad is going to look like."
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = "{}\n\n*{}*".format(content, sponsor_disclaimer)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = "It will cost {:,} slimecoin to stay up for 4 weeks. Is this fine? {} or {}".format(cost, ewcfg.cmd_confirm, ewcfg.cmd_cancel)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	accepted = False
	try:
		msg = await cmd.client.wait_for('message', timeout = 30, check=lambda message: message.author == cmd.message.author and 
															message.content.lower() in [ewcfg.cmd_confirm, ewcfg.cmd_cancel])

		if msg != None:
			if msg.content.lower() == ewcfg.cmd_confirm:
				accepted = True
	except:
		accepted = False

	if accepted:
		create_ad(
			id_server = cmd.guild.id,
			id_sponsor = cmd.message.author.id,
			content = content,
			time_expir = time_now + ewcfg.uptime_ads,
		)
			
		user_data.change_slimecoin(n = -cost, coinsource = ewcfg.coinsource_spending)

		user_data.persist()


		response = "Your ad will be put up immediately. Thank you for your business."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		response = "Good luck raising awareness by word of mouth."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def ads_look(cmd):
	user_data = EwUser(member = cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	response = "You look around for ads. God, you love being advertised to...\n"

	ads = get_ads(id_server = cmd.guild.id)


	if poi.has_ads and len(ads) > 0:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		for id_ad in ads:
			ad_data = EwAd(id_ad = id_ad)
			ad_resp = format_ad_response(ad_data)
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, ad_resp))

	else:
		response += "\nBut you couldn't find any. Bummer."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
