import ewutils
import ewcfg
import discord
import asyncio

# from ewmap import EwPoi
from ew import EwUser
from ewplayer import EwPlayer
# from ewitem import EwGeneralItem
# from ewitem import item_create
# from ewitem import EwItem
# from ewitem import find_item
# from ewitem import inventory
# from ewsmelting import EwSmeltingRecipe
# from ewslimeoid import EwSlimeoid

# Placeholders
theforbiddenoneoneone_desc = "The forbidden one."

forbiddenstuffedcrust_eat = "You eat the forbidden one."

forbiddenstuffedcrust_desc = "The forbidden stuffed crust."

# To circumvent import issues, some variables must be defined here, since they haven't been defined in ewcfg yet
ewcfg.it_item = 'item'
ewcfg.life_state_executive = 6

cmd_debug1 = "debug1"
cmd_debug2 = "debug2"
cmd_debug3 = "debug3"
cmd_debug4 = "verify"
cmd_debug6 = "debug6"
cmd_debug7 = "eavesdrop"
cmd_debug8 = "powerwalk"

poi_id_labs_elevator = "laboratory-elevator"
poi_id_labs_bf4 = "slimeoid-lab-bf4"
poi_id_labs_bf61 = "slimeoid-lab-bf61"
poi_id_labs_bf93 = "slimeoid-lab-bf93"
poi_id_labs_boardroom = "the-boardroom"

item_id_debug_shred_1 = "shred-1"
item_id_debug_shred_2 = "shred-2"
item_id_debug_shred_3 = "shred-3"
item_id_debug_shred_4 = "shred-4"
item_id_debug_shred_5 = "shred-5"
item_id_debug_shred_6 = "shred-6"
item_id_debug_shred_7 = "shred-7"
item_id_debug_shred_8 = "shred-8"
item_id_debug_shred_9 = "shred-9"
item_id_debug_shred_10 = "shred-10"
item_id_debug_shred_11 = "shred-11"
item_id_debug_shred_12 = "shred-12"
item_id_debug_shred_13 = "shred-13"

# Item descriptions
shred_desc = "It’s a shred of office paper. There’s definitely something written on it, but you can’t make out what it is because it’s just a single shred of paper. Maybe if you got a big enough pile of paper shreds you could smelt something legible."
invitation_desc = "It’s an invitation for some kind of a formal event hosted in BF93 of the SlimeCorp Labratory in Brawlden. There’s a barcode at the bottom of the page that is just begging to be scanned. You probably guessed that’s what it was already, though. You’re one smart cookie, y’know that pal? You’re one reeeaaalll smart cookie."

# An ID variable and a name for the elevator to keep things hidden in ewcfg and ewmap
debugroom = poi_id_labs_elevator
debugroom_short = "elevator"

# Same as above, this is used to keep things hidden from the player
debugroom_set = [
	poi_id_labs_bf4,
	poi_id_labs_bf61,
	poi_id_labs_bf93,
]

# All 12 districts that the paper shreds will spawn in. The 13th one will be fished up in freshwater piers.
debugdistricts = [
	"slimesend",
	"wreckington",
	"arsonbrookfarms",
	"downtown",
	"nlacakanmcinemas",
	"jaywalkerplain",
	"vagrantscornerport",
	"neomilwaukeestate",
	"westglocksbury",
	"smogsburgsubwaystation",
	"toxington",
	"cratersville",
]

# Piers where the 13th shred can be fished up from
debugpiers = [
	"slimesendpier",
	"assaultflatsbeachpier",
	"vagrantscornerpier",
	"ferry"
]

# Text and strings used for the ARG
id_debug_secret_invitation = "secretinvitation"
secret_invitation_str_name = "Secret Invitation"

passnum_elevator = "618024466110"
passnum_office = "4643"
passnum_gateway = "61234210"

msg_no = "no"
msg_yes = "yes"
sherman_answer_1 = "45"
sherman_answer_2 = "n8head"
verify_incorrect_response = "You enter in some random bullshit you just thought up to try and straight up hack into this bitch. You are responded to with a really, really loud error sound. Whatever, you’ll just keep trying this until it works."

# POIs for the gateway, elevator, and basement floors
# debugpois = [
# 	EwPoi( # laboratory gateway - only users with lifestate_executive can access this area.
# 		id_poi = "laboratory-gateway",
# 		alias = [
# 			"lgwAlias"
# 		],
# 		str_name = "SlimeCorp Slimeoid Laboratory Gateway",
# 		str_desc = "It's a long, long hallway, leading into the labs. Funny, you usually don't remember walking through here.",
# 		coord = (66, 6), #oooOOOoooOOOOoooo spooky
# 		channel = "slimeoid-lab-gateway",
# 		role = "Slimeoid Lab Gateway",
# 		pvp = False,
# 		is_subzone = True,
# 		mother_district = "brawlden"
# 	),
# 	EwPoi( # Laboratory Elevator - Connects to BF4, BF61, and BF93
# 		id_poi = "laboratory-elevator",
# 		alias = [
# 			"laboratoryelevator",
# 			"elevator",
# 			"lel"
# 		],
# 		str_name = "SlimeCorp Slimeoid Laboratory Elevator",
# 		str_desc = "You gaze upon the embarrassment of buttons laid out before you, labeled from F1 to BF99. Jesus Christ, what the hell could fill up all those floors? It looks like you’ll never find out, because only a few floors down in the far depths of the laboratory are currently accessible.\n\nSo, which floor will it be? *Available destinations are: BF4, BF61, and BF93.* ",
# 		coord = (62, 6),
# 		channel = "slimeoid-lab-elevator",
# 		role = "Slimeoid Lab Elevator",
# 		pvp = False,
# 		is_subzone = True,
# 		mother_district = "brawlden"
# 	),
# 	EwPoi( # Laboratory BF4
# 		id_poi = poi_id_labs_bf4,
# 		alias = [
# 			"bf4"
# 		],
# 		str_name = "BF4",
# 		str_desc = "It’s a simple, nondescript office space with rows of cubicles and at least one water cooler. Countless pieces of paper containing boring business bullshit are archived in the celadon **filing cabinets** that line the walls. There’s a few potted plants, whatever. Most of the cubicles are devoid of personality, aside from one flamboyantly decorated desk that catches your eye. It is topped by a **personal computer** that the user presumably forgot to turn off.\n\nAside from the cubicles, there are actual offices for the higher-ups in the company. They are all locked, of course, but that doesn’t stop you from peering inside from their large glass windows. Interestingly, there is one **office**, which actually seems to be currently inhabited. In the corner of the room is an inconspicuous **janitorial closet**.",
# 		coord = (62, 4),
# 		channel = "slimeoid-lab-bf4",
# 		role = "Slimeoid Lab BF4",
# 		pvp = False,
# 		is_subzone = True,
# 		mother_district = "brawlden"
# 	),
# 	EwPoi( # Laboratory BF61
# 		id_poi = poi_id_labs_bf61,
# 		alias = [
# 			"bf61"
# 		],
# 		str_name = "BF61",
# 		str_desc = "It is very cold and very dark. Almost everything you can see is constructed out of grey stainless steel, right down to the tiled metal floor. The only thing illuminating your surroundings is the faint glow of **vats** containing half-formed Slimeoids in various stages of incubation. There are a few **specimens** that have been fully spawned, but their uncanny disfigurements and containment behind thick, presumably blast resistance glass means they are probably for research only. Try to play fetch with them at your own risk. Among these imprisoned Slimeoids is a single **negaslimeoid**. \n\nPast this broad hallway is a room filled with all manner of scientific clutter, from test tubes containing colorful liquids to piles of yellow **folders** filled with eclectic research results. Across two long desks lay about a dozen computers, all deactivated for the night. In the corner of this messy room is a locked door with a modest **plaque**.",
# 		coord = (60, 6),
# 		channel = "slimeoid-lab-bf61",
# 		role = "Slimeoid Lab BF61",
# 		pvp = False,
# 		is_subzone = True,
# 		mother_district = "brawlden"
# 	),
# 	EwPoi( # Laboratory BF93 
# 		id_poi = poi_id_labs_bf93,
# 		alias = [
# 			"bf93"
# 		],
# 		str_name = "BF93",
# 		str_desc = "It is a dimly lit, long hallway. Locked doors appear on both sides about every ten feet, with potted plants and paintings decorating the spaces between them.\n\nAt the end of the hallway, bright light escapes from a door barely creaked open. On the other side of it is a small white room with no discernible features besides a large, stainless steel **gateway** that blocks your further exploration.",
# 		coord = (62, 8),
# 		channel = "slimeoid-lab-bf93",
# 		role = "Slimeoid Lab BF93",
# 		pvp = False,
# 		is_subzone = True,
# 		mother_district = "brawlden"
# 	),
# 	EwPoi( # The boardroom. Connects to BF93
# 		id_poi = poi_id_labs_boardroom,
# 		alias = [
# 			"boardroom"
# 		],
# 		str_name = "The Boardroom",
# 		str_desc = "A place where meetings are held. Obviously.",
# 		coord = (62, 10),
# 		channel = "the-boardroom",
# 		role = "The Boardroom",
# 		pvp = False,
# 		is_subzone = True,
# 		mother_district = "brawlden"
# 	),
# ]

# The 13 shreds and the invitation
# debugitem_set = [
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_1,
# 		alias = [
# 			"shred1"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_2,
# 		alias = [
# 			"shred2"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_3,
# 		alias = [
# 			"shred3"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_4,
# 		alias = [
# 			"shred4"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_5,
# 		alias = [
# 			"shred5"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_6,
# 		alias = [
# 			"shred6"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_7,
# 		alias = [
# 			"shred7"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_8,
# 		alias=[
# 			"shred8"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_9,
# 		alias = [
# 			"shred9"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_10,
# 		alias = [
# 			"shred10"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_11,
# 		alias=[
# 			"shred11"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_12,
# 		alias = [
# 			"shred12"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = item_id_debug_shred_13,
# 		alias = [
# 			"shred13"
# 		],
# 		str_name = "Singular shred of suspicious looking paper",
# 		str_desc = shred_desc,
# 	),
# 	EwGeneralItem(
# 		id_item = id_debug_secret_invitation,
# 		str_name = secret_invitation_str_name,
# 		str_desc = invitation_desc,
# 		acquisition = "smelting"
# 	),
# ]

# Paper shred 13 variables used in ewcfg and ewfish
#debugitem = debugitem_set[12]
debugfish_response = "\n\nHuh, that's funny. On top of that fish you just caught, you also reel in a small shred of paper."
debugfish_goal = 20

# The recipe for the secret invitation
# debugrecipes = [
# 	EwSmeltingRecipe(
# 		id_recipe = id_debug_secret_invitation,
# 		str_name = "Secret Invitation",
# 		alias = [
# 			"paper",
# 		],
# 		ingredients = {
# 			item_id_debug_shred_1 : 1,
# 			item_id_debug_shred_2: 1,
# 			item_id_debug_shred_3: 1,
# 			item_id_debug_shred_4: 1,
# 			item_id_debug_shred_5: 1,
# 			item_id_debug_shred_6: 1,
# 			item_id_debug_shred_7: 1,
# 			item_id_debug_shred_8: 1,
# 			item_id_debug_shred_9: 1,
# 			item_id_debug_shred_10: 1,
# 			item_id_debug_shred_11: 1,
# 			item_id_debug_shred_12: 1,
# 			item_id_debug_shred_13: 1
# 		},
# 		products = [id_debug_secret_invitation]
# 	),
# ]

# Objects in the laboratory that the player can !scrutinize
debug_objects_1 = {
	"filingcabinets": "You rummage through some random filing cabinets and find a bunch of bullshit. Among this bullshit is a national treasure. https://i.imgur.com/18PmTR0.png",
	"personalcomputer": "At first you thought this was N8’s desk, but then you realized who the handsome photo was addressed to. What a truly shameful display. Somehow, deep down, you always knew this is how he would decorate his office space. To get in and rummage through his files you’ll need his password… or, you’ll have to solve his password recovery security questions. Yeah, let’s just do that. \n\n*Do you want to try and solve Sherman’s security questions? Reply YES or NO.* https://i.imgur.com/3otydYl.png",
	"office": "You try peeking into the window, trying to look past the venetian blinds that were annoyingly performing the exact task they were designed for. You can make out the sound of multiple computers whirring inside. To enter, a number pad on the door requires a four digit PIN. \n\n*Enter the PIN? Reply YES or NO.* https://i.imgur.com/GLdLgG6.png",
	"janitorialcloset": "You open up the closet to reveal a disturbing display. A pudgy middle-aged man lies in the corner of the room, his rumpled white shirt and ripped red tie smeared in blood and slime residue. He is bound up with SLIMECORP-brand high-tension cords, with duct tape over his mouth. He looks blearily at you as you approach, blinking as if coming out of a deep stupor.\n\n*Do you release him from his bondage? Reply YES or NO.*"
}

debug_objects_2 = {
	"vats": "Goddamn, look at all these lil’ freaks. Even normal Slimeoid incubation kind of grosses you out, but these things are on another level. What even are some of those body parts? You’ve memorized the spreadsheet, and you don’t remember dislocated jaw beak being an option. Maybe there’s going to be a Slimeoid update soon, or something. https://i.imgur.com/f6djMqe.png",
	"specimens": "Yeah, okay. Here are some of those gross-looking Slimeoids that actually got made, you guess. Should you even call them Slimeoids? They look so strange and aggressive, like they’re ready to pounce on the first guy they can sink their gelatinous claws into and rip him limb from limb. You hardly feel any urge to pet and/or howl with them at all! You resist the urge to tap on the glass. https://i.imgur.com/BOR3VCJ.png",
	"negaslimeoid": "Oh shit, there’s a negaslimeoid in here! Luckily, no cold shiver runs down your spine. They must be keeping him in a pressurized cabin or something. You know, you’ve never actually stopped and looked at one of these things up close before. All of your exposure to them has been overwhelmingly short and negative. They really are quite spooky, with that scratchy, abstract blackness that vaguely implies a hole of some variety they’ve got for a face. Wait, how long has it been looking at you? Uhhh… let’s hurry up and scrutinize something else. https://i.imgur.com/akhAua2.png",
	"folders": "You open up a random folder and a few photos and notes spill out. Hey, wait a second, all this looks very familiar… \n\noops, one fell out! https://i.imgur.com/TQlAya4.png\nhttps://ew.krakissi.net/img/sc/ancient-war.bmp",
	"plaque": "Well, then. Looks like this is it. You stand just outside of the office you’ve seen so many times in transmissions. You have no idea what to expect on the other side of this door. You’d be lying if you said you weren’t a little bit scared. https://i.imgur.com/VI0sFjB.png"
}

debug_objects_3 = {
	"gateway": "You gaze upon the gateway. That’s definitely not what you should be calling this thing, but you aren’t exactly sure what the proper name for “sci-fi door” is and calling it a gateway sounds cool. To enter, a large console next to the door requires an eight digit password.\n\n*Enter the password? Reply YES or NO.* https://i.imgur.com/kISrWVq.png",
}

# Two placeholder commands
def debug1():
	print("DEBUG1")

# Lock a district, preventing users without the executive lifestate from accessing it.
# async def debug3(cmd):
# 	locked_district = None
# 	all_locks_list = []
# 	response = ""
# 
# 	author = cmd.message.author
# 	user_data = EwUser(member=cmd.message.author)
# 
# 	if not author.guild_permissions.administrator:
# 		return
# 
# 	if len(cmd.tokens) > 1:
# 		locked_district = cmd.tokens[1]
# 
# 		all_locks = ewutils.execute_sql_query(
# 			"SELECT {district} FROM global_locks WHERE id_server = %s AND {locked_status} = %s".format(
# 				district=ewcfg.col_district,
# 				locked_status=ewcfg.col_locked_status
# 			), (
# 				user_data.id_server,
# 				'true'
# 			))
# 
# 		for lock in all_locks:
# 			all_locks_list.append(lock[0])
# 
# 		if locked_district in all_locks_list:
# 			response = "District **{}** is now unlocked.".format(locked_district)
# 
# 			try:
# 				ewutils.execute_sql_query(
# 					"UPDATE global_locks SET {locked_status} = %s WHERE id_server = %s AND {district} = %s".format(
# 						locked_status=ewcfg.col_locked_status,
# 						district=ewcfg.col_district,
# 					), (
# 						'false',
# 						user_data.id_server,
# 						locked_district
# 					))
# 			except:
# 				ewutils.logMsg('Failed to unlock district with id {}'.format(locked_district))
# 				response = "Failed to unlock district."
# 
# 		else:
# 			# Try making a new lock for that district
# 			response = "District **{}** is now locked.".format(locked_district)
# 
# 			try:
# 				ewutils.execute_sql_query(
# 					"INSERT INTO global_locks ({id_server}, {district}, {locked_status}) VALUES(%s, %s, %s)".format(
# 						id_server=ewcfg.col_id_server,
# 						district=ewcfg.col_district,
# 						locked_status=ewcfg.col_locked_status
# 					), (
# 						user_data.id_server,
# 						locked_district,
# 						'true'
# 					))
# 			# A duplicate entry exists, update the existing lock to true instead
# 			except:
# 				try:
# 					ewutils.execute_sql_query(
# 						"UPDATE global_locks SET {locked_status} = %s WHERE id_server = %s AND {district} = %s".format(
# 							locked_status=ewcfg.col_locked_status,
# 							district=ewcfg.col_district,
# 						), (
# 							'true',
# 							user_data.id_server,
# 							locked_district
# 						))
# 				except:
# 					ewutils.logMsg('Failed to lock district with id {}'.format(locked_district))
# 					response = "Failed to lock district."
# 
# 	else:
# 		response = "Lock which district?"
# 
# 	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# # Enter in a password to unlock the labs elevator
# async def debug4(cmd):
# 	user_data = EwUser(member=cmd.message.author)
# 	response = ""
# 	
# 	if user_data.poi != ewcfg.poi_id_slimeoidlab or (len(cmd.tokens) < 2):
# 		response = "Verify *what*, exactly?"
# 	else:
# 		if cmd.tokens[1] != passnum_elevator:
# 			response = verify_incorrect_response
# 		else:
# 			response = "You enter the number you found on the barcode of N6’s ID. You wait for a few moments with bated breath before a delightful jingle of approval rings through your waxy, teenage ears. You are now able to use the elevator.\n\n*Use the !descend command followed by the floor number you want to go to.*"
# 			try:
# 				ewutils.execute_sql_query("UPDATE global_locks SET {locked_status} = %s WHERE id_server = %s AND {district} = %s".format(
# 					locked_status=ewcfg.col_locked_status,
# 					district=ewcfg.col_district,
# 				), (
# 					'false',
# 					user_data.id_server,
# 					poi_id_labs_elevator
# 				))
# 			except:
# 				ewutils.logMsg('Failed to unlock elevator.')
# 				response = "ACESS DENIED."
# 			
# 	if response != "":
# 		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 	
# # Grant users access to 'the-boardroom' text channel. They can read but not send messages.
# async def debug5(client, cmd, id_server):
# 	
# 	member = cmd.message.author
# 	
# 	if not member.guild_permissions.administrator:
# 		return
# 	
# 	server = client.get_server(id_server)
# 	
# 	channel = ewutils.get_channel(server = server, channel_name = 'the-boardroom')
# 
# 	overwrite = channel.overwrites_for(member) or discord.PermissionOverwrite()
# 	overwrite.read_messages=True
# 	overwrite.send_messages=False
# 	
# 	#permissions = channel.permissions_for(member)
# 	#permissions.update(read_messages=True)
# 	#permissions.update(send_messages=False)
# 	
# 	await client.edit_channel_permissions(channel, member, overwrite)
# 	
# 	response = "You enter the door. around the corner, you can hear speaking. You peer over to listen in..."
# 	
# 	return response

# # Puts 12 paper shreds in 12 districts.
# async def debug6(cmd):
# 	client = cmd.client
# 	message = cmd.message
# 	author = cmd.message.author
# 	response = ""
# 	counter = 0
# 	
# 	# Used for debugging
# 	#user_data = EwUser(member=author)
# 	
# 	if not author.guild_permissions.administrator:
# 		return
# 	
# 	for item in debugitem_set:
# 
# 		#Skip over the invitation and the fished up shred, they don't get generated here
# 		if counter == 12:
# 			continue
# 		
# 		item_create(
# 			item_type=ewcfg.it_item,
# 			id_user=debugdistricts[counter],
# 			id_server=message.guild.id,
# 			item_props={
# 				'id_item': item.id_item,
# 				'context': item.context,
# 				'item_name': item.str_name,
# 				'item_desc': item.str_desc,
# 			}
# 		),
# 		ewutils.logMsg('Created item: {}'.format(item.id_item))
# 		item = EwItem(id_item=item.id_item)
# 		item.persist()
# 		
# 		counter += 1
# 		
# 	response = "Invitation created. Pieces scattered to...\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
# 		debugdistricts[0],
# 		debugdistricts[1],
# 		debugdistricts[2],
# 		debugdistricts[3],
# 		debugdistricts[4],
# 		debugdistricts[5],
# 		debugdistricts[6],
# 		debugdistricts[7],
# 		debugdistricts[8],
# 		debugdistricts[9],
# 		debugdistricts[10],
# 		debugdistricts[11],
# 	)
# 	
# 	response += "\nAdditionally, one piece was scattered into the sea. It will take 20 fish to fetch it."
# 
# 	await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
# 
# # Used in bf93 to gain access to the N's conversation. Only works if the player has the invitation in their inventory.
# async def debug7(cmd):
# 	user_data = EwUser(member=cmd.message.author)
# 	
# 	if user_data.poi != poi_id_labs_bf93:
# 		response = "Eavesdrop on *what*, exactly?"
# 		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 	item_search = id_debug_secret_invitation
# 	item_sought = find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.message.guild.id if cmd.message.guild is not None else None)
# 
# 	if item_sought:
# 		response = await ewcfg.debug5(client=cmd.client, cmd=cmd, id_server=user_data.id_server)
# 	else:
# 		response = "Eavesdrop on *what*, exactly?"
# 
# 	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

# Used by N10 to 'powerwalk' to the speakeasy while in the boardroom meeting. Teleports you to the ez after 60 seconds
# async def debug8(cmd):
# 	user_data = EwUser(member=cmd.message.author)
# 	author = cmd.message.author
# 	
# 	if user_data.life_state == ewcfg.life_state_executive or author.guild_permissions.administrator:
# 		response = "You begin powerwalking to The King's Wife's Son Speakeasy. It's 1 minute away."
# 		
# 		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 		await asyncio.sleep(60)
# 		
# 		user_data.poi = "thekingswifessonspeakeasy"
# 		user_data.persist()
# 	
# 	else:
# 		
# 		response = "**POWERWALK IS NOT A COMMAND YOU FUCKING IDIOT**"
# 		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	

# The scrutinize command doesn't have to be here forever, it just has to stay in ewdebug for the time being, since an import error will occur otherwise
"""
	Get information about an object in a district
"""
# async def scrutinize(cmd):
# 	user_data = EwUser(member=cmd.message.author)
# 	response = ""
# 	member = cmd.message.author
# 	found_object = False
# 	pass_is_correct = False
# 	has_3d_glasses = False
# 	searched_object = ewutils.flattenTokenListToString(cmd.tokens[1:])
# 	
# 	if len(cmd.tokens) < 2:
# 		response = "Scrutinize *what*, exactly?"
# 		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 	if user_data.poi not in debugroom_set:
# 		response = "You squint your eyes real hard at your surroundings, but nothing seems to be of interest."
# 	else:
# 		if user_data.poi == poi_id_labs_bf4 and searched_object in debug_objects_1:
# 			found_object = True
# 			response = debug_objects_1[searched_object]
# 		if user_data.poi == poi_id_labs_bf61 and searched_object in debug_objects_2:
# 			found_object = True
# 			response = debug_objects_2[searched_object]
# 		if user_data.poi == poi_id_labs_bf93 and searched_object in debug_objects_3:
# 			found_object = True
# 			response = debug_objects_3[searched_object]
# 			
# 		# Special cases where the responses need to be split up in order for images to be embedded correctly.
# 		if searched_object == "specimens" and found_object == True:
# 			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 			response = "Next to the containment cell, there is a clipboard storage unit performing its intended function. You take a look at the contents... \n\n“Again, you’re hesitating. We aren’t trying to provide target practice for gangsters, these creatures should be able to take on a horde of those degenerates with ease. They should be feared, not sought out for free slime. More fangs, more talons. I want to see monsters. Remember N6, we are only giving the people a comprehensible face for their abstract oppression. Some may speak of cruelty, or even hypocrisy, but this is not so. The deaths we will cause will only serve to scare, and then save the people from the thousands of deaths that he causes on a daily basis. Showing mercy at this critical stage will only serve to confuse the public, and make them resistant to our solution. And if they are resistant to us, then all is lost. Sacrifice a few today, save everyone tomorrow. Remember that.”"
# 		
# 		if searched_object == "negaslimeoid" and found_object == True:
# 			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 			response = "Next to the containment cell, there is a clipboard storage unit performing its intended function. You take a look at the contents... \n\n“What a vile, repugnant creature. It is truly remarkable how similar the molecular structure of it is to the Negaslime. They really are of the same cloth. Let’s not keep it here for any longer than necessary, no matter how fascinating it might be for you to study. We’re already quite capable of dealing with a potential second descension, thank you very much. Keeping that here is just… too scary. I don’t like it. Oh God, I think it just looked at me.”"
# 		
# 		# Special cases that require further input from user.
# 		if searched_object == "personalcomputer" and found_object == True:
# 			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 			try:
# 				msg = await cmd.client.wait_for(timeout=30, author=member)
# 
# 				if msg != None:
# 					if msg.content.lower() == msg_yes:
# 						response = "*Reply with your answer.* https://i.imgur.com/7F6E3IX.png"
# 						await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 						
# 						try:
# 							msg = await cmd.client.wait_for(timeout=30, author=member)
# 
# 							if msg != None:
# 								if msg.content.lower() == sherman_answer_1:
# 									response = "*Reply with your answer.* https://i.imgur.com/lVdLmzp.png"
# 									await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 	
# 									try:
# 										msg = await cmd.client.wait_for(timeout=30, author=member)
# 	
# 										if msg != None:
# 											if msg.content.lower() == sherman_answer_2:
# 												response = "Jackpot!! You’re in. Oh God, it’s even worse than you predicted. Look at that unholy, writhing mass of files underneath the porn windows. You suddenly lose all appetite to explore the computer’s depths, but that list of locations might come in handy. https://i.imgur.com/gBkCxIj.png"
# 											else:
# 												response = verify_incorrect_response
# 									
# 									except:
# 										response = "You decide you’ll come back after you explore a bit more."
# 
# 							else:
# 								response = verify_incorrect_response
# 
# 						except:
# 							response = "You decide you’ll come back after you explore a bit more."
# 							
# 					else:
# 						response = "You decide you’ll come back after you explore a bit more."
# 
# 			except:
# 				response = "You decide you’ll come back after you explore a bit more."
# 
# 		if searched_object == "office" and found_object == True:
# 			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 			# Wait for an answer
# 			try:
# 				msg = await cmd.client.wait_for(timeout=30, author=member)
# 
# 				if msg != None:
# 					if msg.content.lower() == msg_yes:
# 						response = "*Reply with your answer.*"
# 						await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 						try:
# 							msg = await cmd.client.wait_for(timeout=30, author=member)
# 
# 							if msg != None:
# 							
# 								if msg.content == passnum_office:
# 									response = "It’s a room completely full of computers, just fucking absolutely smothered in them. They all seem to be running the exact same peculiar program… https://i.imgur.com/vw1ELfT.png"
# 								else:
# 									response = verify_incorrect_response
# 						
# 						except:
# 							response = "You decide you’ll come back after you explore a bit more."
# 
# 					else:
# 						response = "You decide you’ll come back after you explore a bit more."
# 			
# 			except:
# 				response = "You decide you’ll come back after you explore a bit more."
# 				
# 		if searched_object == "janitorialcloset" and found_object == True:
# 			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 			weapon_item = EwItem(id_item=user_data.weapon)
# 			weapon = weapon_item.item_props.get("weapon_type")
# 
# 			try:
# 				msg = await cmd.client.wait_for(timeout=30, author=member)
# 
# 				if msg != None:
# 					if msg.content.lower() == msg_yes:
# 						if weapon != "katana":
# 							response = "Alas, you have nothing to cut open the highly durable SLIMECORP-brand high-tension cords! Maybe if you had some sort of sick ass slab of premium Japanese steel, folded over a thousand times, you could break his chains…"
# 						else:
# 							response = "“Oh, thank god... I've been tied up here for weeks… My stamina... need food... please... pizza... just a drop of sauce... a crumb of taco shell… *cough cough* **HAAACKK**\nSLIMECORP... it was a slaughter... they Zuckerberged our whole marketing team... and Human Resources... they were all burned for fuel… *whimper*\nAnd the SlimeCoin...  somehow they knew... that the Board of Directors kept our precious crypto on our proprietary Rectal Hard Drives… one by one... they went down the line, one by one... bent us over the board room table... and took it all… *sob*\nThat SlimeCoin is the legacy of Yum! Brands... it's all that's left of our great company… Please... the USB drive they stored it on must be around here somewhere. If you untie me I can get that SlimeCoin, and maybe... just maybe... Yum! Brands can be rebuilt!”\n\nThis guy seems like bad news. You figure this is a trap and if you help him he'll just turn out to be a SLIMECORP repli-droid, or a mischievous elf, or something. You drive the tip of your katana into his weak skull and frisk him for any valuables. In his wallet you find a few pictures of the man, not with any family but with a big friendly-looking Slimeoid. Damn. Gang war makes another orphan. But them's the breaks in Slime City."
# 					elif msg.content.lower() == msg_no:
# 						response = "You conclude he’s probably doing this of his own accord and decide it’s best to leave him be."
# 					else:
# 						response = "You decide you’ll come back after you explore a bit more."
# 			except:
# 				response = "You decide you’ll come back after you explore a bit more."
# 				
# 		if searched_object == "plaque" and found_object == True:
# 			slimeoid_match = False
# 			player_slimeoid = EwSlimeoid(member = member)
# 
# 			if (player_slimeoid.life_state == ewcfg.slimeoid_state_active) and (user_data.life_state != ewcfg.life_state_corpse):
# 				pass
# 			else:
# 				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 				response = "Predictably, it’s locked. Unpredictably, you can’t find a keyhole or number pad with which to unlock it. That is, until you shuffle a little bit to the right. You’re suddenly caught off guard by a ray of red light tracing up your body before stopping at your knees and providing a harsh, disapproving noise. Looks like that thing is a scanner, but what it wants to scan you have no idea."
# 				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 			cosmetics = inventory(
# 				id_user=user_data.id_user,
# 				id_server=cmd.message.guild.id,
# 				item_type_filter=ewcfg.it_cosmetic
# 			)
# 
# 			# get the cosmetics worn by the slimeoid
# 			adorned_cosmetics = []
# 			for item in cosmetics:
# 				cos = EwItem(id_item=item.get('id_item'))
# 				if cos.item_props.get('slimeoid') == 'true':
# 					hue = ewcfg.hue_map.get(cos.item_props.get('hue'))
# 					adorned_cosmetics.append(
# 						(hue.str_name + " colored " if hue != None else "") + cos.item_props.get('cosmetic_name'))
# 
# 			if len(adorned_cosmetics) > 0:
# 				if "pair of 3D glasses" in adorned_cosmetics:
# 					has_3d_glasses = True
# 			
# 			# Check if user has a slimeoid that matches the executive's
# 			if player_slimeoid.body == "teardrop" \
# 			and player_slimeoid.head == "eye" \
# 			and player_slimeoid.legs == "legs" \
# 			and player_slimeoid.armor == "scales" \
# 			and player_slimeoid.weapon == "blades" \
# 			and player_slimeoid.special == "spit" \
# 			and player_slimeoid.ai == "a" \
# 			and player_slimeoid.level == 6 \
# 			and has_3d_glasses:
# 				slimeoid_match = True
# 			else:
# 				slimeoid_match = False
# 			
# 			if slimeoid_match:
# 				response = "Once again, you find yourself outside the office of N6, SlimeCorp’s Head of Research and Development. You aren’t sure if you’re totally ready. You turn the handle as the plagiarized Slimeoid next to you is analyzed by the scanner. Somewhat predictably, given the fact that you’re reading this new flavor text, you’ve solved the puzzle correctly. The door unlocks and you press onward, into… https://i.imgur.com/fCjiPxk.png"
# 				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 				response = "An empty office. Well, that’s anticlimactic. There’s not even really anything to rummage through, that is, besides a stupid, girly-looking journal. Aw man, you were all geared up for a fight."
# 				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 				response = "Still, you crack open the book.\nhttps://i.imgur.com/BHDOK4b.png\nhttps://i.imgur.com/0vRCDcN.png\nhttps://i.imgur.com/02amAGt.png\nhttps://i.imgur.com/DJpst1a.png\nhttps://i.imgur.com/gFraS1q.png"
# 			else:
# 				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 				response = "Predictably, it’s locked. Unpredictably, you can’t find a keyhole or number pad with which to unlock it. That is, until you shuffle a little bit to the right. You’re suddenly caught off guard by a ray of red light tracing up your body before stopping at your knees and providing a harsh, disapproving noise. Looks like that thing is a scanner, but what it wants to scan you have no idea."			
# 		
# 
# 		if searched_object == "gateway" and found_object == True:
# 			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 			try:
# 				msg = await cmd.client.wait_for(timeout=30, author=member)
# 
# 				if msg != None:
# 					if msg.content.lower() == msg_yes:
# 						response = "*Reply with your answer.*"
# 						await ewutils.send_message(cmd.client, cmd.message.channel,
# 												   ewutils.formatMessage(cmd.message.author, response))
# 
# 						try:
# 							msg = await cmd.client.wait_for(timeout=30, author=member)
# 
# 							if msg != None:
# 
# 								if msg.content == passnum_gateway:
# 									response = "You enter the password into the console, and you hear the shifting of gears and decompression of air from within the walls. After a few moments, the gateway unlocks, and slides to the right. You enter a second room, which is decorated just as spartanly as the first. Inside, a far more casual yet still locked door awaits you. There is a barcode scanner next to it. https://i.imgur.com/yg4qC54.png"
# 									await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 									response = "You try waving your hand under it just to see what happens, and you are startled by a recording of a female voice. “Greetings and salutations, my fellow executives. Thank you for attending our meeting tonight. As you know, security is our top priority. Scan the invitation you were given, and then hand it to Sherman. He will shred it and scatter the pieces across the city, so it may never be reused by another party. Your brothers and sisters await you inside.”"
# 									await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 
# 									item_search = id_debug_secret_invitation
# 									item_sought = find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.message.guild.id if cmd.message.guild is not None else None)
# 
# 									if item_sought:
# 										response = "You place the suspicious invitation under the barcode scanner. You hear the simple unlocking of a door. You enter into a short hallway, with yet another door at the end of it. You approach it, ready to solve yet another bullshit puzzle, when your slime runs cold. You can hear voices, and very clearly at that.\n\nNow would be a perfect time to !eavesdrop."
# 									else:
# 										response = "You have no idea what the voice is referring to. After a few minutes of trying to scan every item in your inventory, you figure you must need to solve another puzzle and exit the second room. The gateway closes behind you."
# 									
# 								else:
# 									response = verify_incorrect_response
# 
# 						except:
# 							response = "You decide you’ll come back after you explore a bit more."
# 
# 					else:
# 						response = "You decide you’ll come back after you explore a bit more."
# 
# 			except:
# 				response = "You decide you’ll come back after you explore a bit more."
# 		
# 		if found_object == False:
# 			response = "You couldn't find what you were looking for."
# 
# 	if response != "":
# 		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

# It's over.
async def begin_cataclysm(user_data):
	
	player_data = EwPlayer(user_data.id_user)
	player_name = player_data.display_name
	
	client = ewutils.get_client()
	server = client.get_guild(user_data.id_server)
	auditorium_channel = ewutils.get_channel(server, 'auditorium')

	responses = [
		"@everyone",
		"You point the sword towards the heavens, making your prescense known. ENDLESS WAR begins to shudder as he witnesses what's about to happen...",
		"Dark clouds begin to assemble in the skies above. Buildings around you begin to lose their color. The ground begins to shake, and a sense of dread envelops you as you grip the handle of the cold metal sword.",
		"All of the wicked things you've ever done have come back to haunt you. But you've made your bed, and now you have to lie in it.",
		"All of the sins and hatred you've brought forth will be spun into form. But you knew that, and you lept toward the darkness anyways.",
		"With blade in hand, you unleash an unparalleled wave of anguish and dread over the city of Neo Los Angeles City AKA Neo Milw-",
		"**The sword snaps in two.**",
		"Wow. Just wow. No seriously, what the fuck did you think was gonna happen? I swear, people get so hopped up when they hear about shit like the Negaslime, like the Endless Rock, that they delude themselves into thinking that everything in this game has to be some kind of history-altering cataclysm. Not this time, dumbass. You've endured countless acts of BDSM Sadomasochism, and for what? Well, I'll tell you plain and simple: It was all for fucking **NOTHING**.",
		"Yeah yeah, you've been taken for a fool, everyone laugh at the dummy, and then we can all go home and pretend like this whole 'Swilldermuk' thing never happened, right? No, fuck you. You are gonna sit here and listen to me ramble off about how much of a fucking retard you are. I swear to god, the nerve that some people have, to think that they can play this race to the bottom and intentionally let themselves get pranked, it's just absolutely *disgusting*. Tell me, {}, you've been pranked so much... Who exactly is it that you've pranked? Can you name even one person? I thought not.".format(player_name),
		"This whole event, it was all about NOT getting pranked, about one-upping your bros and seeing the stupid ass retarded look on their face when you blew a goddamn airhorn right in their eardrums. But you? You're just a pathetic whipping boy who turned this whole thing upside down. You probably think I'm being a bit mean here don't you? But let's be real, I'm just stating the God's honest truth when I say this: You enjoy pain. You enjoy being whipped and beaten. The way you get your rocks off is when someone deliberately humiliates you, all for their own personal gain. Consider all of this a wake up call.",
		"You thought that you could just get away with being a disgusting sexfiend in public. You thought that when all of this was over, you'd get a nice item for your uh, what were your efforts again? Oh that's right, standing around waiting for credence to build up and then opening your body to unspeakable acts of debauchery. No strategy. No brains. No soul. You're just as bad, if not worse than the people who cowardly stood inside their apartments, waiting for all this to blow over. And so here we are, at the end of the road, pontificating over how badly you fucked everything up. Where do we go from here?",
		"How are you gonna reconcile with the fact that all your scars were for naught? 'How am I supposed to COPE', you might be thinking? Well, for starters, stop being such a reprehensible freak. I'm dead serious. All those times you let people further and further drain your credence, it was just abysmal and agonizing to watch. You don't have to apologize to anyone, you don't have to be put in a cage or any of that shit, because God knows how much you'd fucking *enjoy it*. Just remember this. On this day, April 7th, in the year of our lord, two thousand and twenty, you, {}, were fucking cringey, embarassing, and above all retarded. Commit it to memory. Tell your grandkids about it one day, even. It'll be a story for the ages.".format(player_name),
		"Now, as for everyone else reading this: Do your part, do your DUTY, even, and !pointandlaugh at {}, while you still can. It's what they fucking deserve.".format(player_name),
	]
	
	for i in range(len(responses)):
		response = responses[i]


		if response == responses[1]:
			await ewutils.send_message(client, auditorium_channel, ewutils.formatMessage(player_data, response))
		else:
			await ewutils.send_message(client, auditorium_channel, response)
			
		if i >= 7:
			await asyncio.sleep(20)
		else:
			await asyncio.sleep(10)

last_words = "Hahaha, fucking pranked, **idiot**."