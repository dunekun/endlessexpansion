import asyncio
import time

import ewrolemgr
import ewutils
import ewcfg
import ewcmd
from ew import EwUser

"""
	Commands for raid bosses only.
"""


async def writhe(cmd):
	resp = await ewcmd.start(cmd = cmd)
	response = ""
	user_data = EwUser(member = cmd.message.author)

	if user_data.life_state != ewcfg.life_state_grandfoe:
		response = "Only the NEGASLIME {} can do that.".format(ewcfg.emote_negaslime)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		# play animation
		he = ewcfg.emote_he
		s_ = ewcfg.emote_s_
		ve = ewcfg.emote_ve
		vt = ewcfg.emote_vt
		v_ = ewcfg.emote_v_
		h_ = ewcfg.emote_h_
		va = ewcfg.emote_va
		ht = ewcfg.emote_ht
		hs = ewcfg.emote_hs
		blank = ewcfg.emote_blank
		
		writhing1 = he
		writhing2 = s_ + he + "\n" + ve
		writhing3 = s_ + h_ + he + "\n" + vt + he
		writhing4 = s_ + h_ + ht + "\n" + vt + he + ve
		writhing5 = s_ + h_ + ht + "\n" + va + he + vt + he + "\n" + ve
		writhing6 = s_ + h_ + ht + "\n" + va + ht + va + ht + "\n" + v_ + ve + ve + ve + "\n" + ve
		writhing7 = s_ + h_ + ht + "\n" + va + ht + va + hs + he + "\n" + v_ + ve + v_ + vt + he + "\n" + ve + blank + ve
		writhing8 = s_ + h_ + ht + "\n" + va + ht + va + hs + he + "\n" + v_ + ve + v_ + vt + h_ + he + "\n" + vt + he + vt + he
		writhing9 = s_ + h_ + ht + "\n" + va + ht + va + hs + h_ + he + "\n" + v_ + ve + v_ + vt + h_ + ht + "\n" + vt + ht + vt + ht + blank + ve + "\n" + blank + ve + blank + ve
		writhing10 = s_ + h_ + ht + "\n" + va + ht + va + hs + h_ + he + "\n" + v_ + ve + v_ + vt + h_ + ht + "\n" + vt + ht + vt + ht + blank + vt + he + "\n" + blank + ve + blank + vt + he

		writhings = [writhing1,  writhing2, writhing3, writhing4, writhing5, writhing6, writhing7, writhing8, writhing9, writhing10]

		for writhing in writhings:
			cur_time = time.time()
			await ewutils.edit_message(cmd.client, resp, writhing)
			elapsed = time.time() - cur_time
			await asyncio.sleep(2.0 - elapsed)

		id_server = cmd.guild.id
		targets = []

		# search for players in the negaslime's location in database and put them in a list
		if id_server != None:
			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND poi = '{}' AND life_state IN (1, 2);".format(
					user_data.poi
				), (
					id_server,
				))

				# convert pulled IDs into member objects
				target_ids = cursor.fetchall()
				for target_id in target_ids:
					target = cmd.guild.get_member(target_id[0])
					targets.append(target)

				conn.commit()
			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

		victim_list = []

		# kill everyone in the negaslime's poi and remember their names
		for target in targets:
			if target != None:
				user_data_target = EwUser(member = target)

				user_data_target.id_killer = cmd.message.author.id
				user_data_target.die(cause = ewcfg.cause_grandfoe)
				user_data_target.persist()
				await ewrolemgr.updateRoles(client = cmd.client, member = target)
				sewerchannel = ewutils.get_channel(cmd.guild, ewcfg.channel_sewers)
				await ewutils.send_message(cmd.client, sewerchannel, "{} ".format(ewcfg.emote_slimeskull) + ewutils.formatMessage(target, "You have been crushed by tendrils. {}".format(ewcfg.emote_slimeskull)))

				victim_list.append(target)

		# display result of the writhing
		if len(victim_list) > 0:
			victims_string = ewutils.userListToNameString(victim_list)
			response = "Your tendrils have successfully killed {}.".format(victims_string)
		else:
			response = "Your tendrils didn't kill anyone :("

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
