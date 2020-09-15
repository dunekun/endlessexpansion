#!/usr/bin/python3
#
# endless-war
# mperron (2018)
#
# a chat bot for the RFCK discord server

import discord
import asyncio
import random
import sys
import time
import json
import subprocess
import traceback
import re
import os
import shlex

import ewutils
import ewcfg
import ewfarm
import ewcmd
import ewcasino
import ewfood
import ewwep
import ewjuviecmd
import ewmarket
import ewspooky
import ewkingpin
import ewplayer
import ewserver
import ewitem
import ewmap
import ewrolemgr
import ewraidboss
import ewleaderboard
import ewcosmeticitem
import ewslimeoid
import ewdistrict
import ewmutation
import ewquadrants
import ewtransport
import ewstatuseffects
import ewsmelting
import ewhunting
import ewfish
import ewfaction
import ewapt
import ewweather
import ewworldevent
import ewdungeons
import ewads
import ewbook
import ewsports
import ewrace
import ewdebug

from ewitem import EwItem
from ew import EwUser
from ewplayer import EwPlayer
from ewmarket import EwMarket
from ewmarket import EwStock
from ewdistrict import EwDistrict
from ewstatuseffects import EwStatusEffect


ewutils.logMsg('Starting up...')
init_complete = False

client = discord.Client()


# A map containing user IDs and the last time in UTC seconds since we sent them
# the help doc via DM. This is to prevent spamming.
last_helped_times = {}

# Map of server ID to a map of active users on that server.
active_users_map = {}

# Map of all command words in the game to their implementing function.
cmd_map = {
	## NEW COMMANDS FOR ENDLESS EXPANSION
	ewcfg.cmd_kiss: ewcmd.kiss,
	ewcfg.cmd_smother: ewcmd.smother,
	ewcfg.cmd_milk: ewcmd.milk,
	ewcfg.cmd_compliment: ewcmd.compliment,
	ewcfg.cmd_fondle: ewcmd.fondle,
	ewcfg.cmd_fondle_alt1: ewcmd.fondle,
	ewcfg.cmd_fondle_alt2: ewcmd.fondle,
	ewcfg.cmd_flatten: ewcmd.flatten,
	ewcfg.cmd_hug: ewcmd.hug,
	ewcfg.cmd_grill: ewcmd.grill,

	#ewcfg.cmd_fondle: ewcmd.fondle,

	# Attack another player
	ewcfg.cmd_kill: ewwep.attack,
	ewcfg.cmd_shoot: ewwep.attack,
	ewcfg.cmd_shoot_alt1: ewwep.attack,
	ewcfg.cmd_shoot_alt2: ewwep.attack,
	ewcfg.cmd_shoot_alt3: ewwep.attack,
	ewcfg.cmd_shoot_alt4: ewwep.attack,
	ewcfg.cmd_shoot_alt5: ewwep.attack,
	ewcfg.cmd_shoot_alt6: ewwep.attack,
	ewcfg.cmd_attack: ewwep.attack,

	# Reload
	ewcfg.cmd_reload: ewwep.reload,
	ewcfg.cmd_reload_alt1: ewwep.reload,
	
	# Fix your jammed gun
	ewcfg.cmd_unjam: ewwep.unjam,

	# Choose your weapon
	ewcfg.cmd_equip: ewwep.equip,
	ewcfg.cmd_arm: ewwep.equip,
	ewcfg.cmd_arsenalize: ewwep.equip,
	ewcfg.cmd_sidearm: ewwep.sidearm,
	
	# Kill yourself
	ewcfg.cmd_suicide: ewwep.suicide,
	ewcfg.cmd_suicide_alt1: ewwep.suicide,
	ewcfg.cmd_suicide_alt2: ewwep.suicide,

	# Spar with an ally
	ewcfg.cmd_spar: ewwep.spar,

	# Name your current weapon.
	ewcfg.cmd_annoint: ewwep.annoint,
	ewcfg.cmd_annoint_alt1: ewwep.annoint,

	# Marry and divorce your current weapon.
	ewcfg.cmd_marry: ewwep.marry,
	ewcfg.cmd_divorce: ewwep.divorce,
	
	# Crush a poudrin to get some slime.
	ewcfg.cmd_crush: ewjuviecmd.crush,
	ewcfg.cmd_crush_alt1: ewjuviecmd.crush,

	# move from juvenile to one of the armies (rowdys or killers)
	ewcfg.cmd_enlist: ewjuviecmd.enlist,
	ewcfg.cmd_renounce: ewjuviecmd.renounce,
	ewcfg.cmd_vouch: ewfaction.vouch,

	# gives slime to the miner (message.author)
	ewcfg.cmd_mine: ewjuviecmd.mine,

	# flags a vein as dangerous
	ewcfg.cmd_flag: ewjuviecmd.flag,

	# Show the current slime score of a player.
	ewcfg.cmd_score: ewcmd.score,
	ewcfg.cmd_score_alt1: ewcmd.score,

	# Show a player's combat data.
	ewcfg.cmd_data: ewcmd.data,

	# Show a player's mutations.
	ewcfg.cmd_mutations: ewcmd.mutations,
	ewcfg.cmd_mutations_alt_1: ewcmd.mutations,

	# sap system
	ewcfg.cmd_view_sap: ewcmd.view_sap,
	ewcfg.cmd_harden_sap: ewwep.harden_sap,
	ewcfg.cmd_harden_sap_alt1: ewwep.harden_sap,
	ewcfg.cmd_liquefy_sap: ewwep.liquefy_sap,

	
	# combat sap commands
	ewcfg.cmd_taunt: ewwep.taunt,
	ewcfg.cmd_aim: ewwep.aim,
	ewcfg.cmd_dodge: ewwep.dodge,
	ewcfg.cmd_dodge_alt1: ewwep.dodge,
	ewcfg.cmd_dodge_alt2: ewwep.dodge,

	# Check how hungry you are.
	ewcfg.cmd_hunger: ewcmd.hunger,

	#check what time it is, and the weather
	ewcfg.cmd_time: ewcmd.weather,
	ewcfg.cmd_clock: ewcmd.weather,
	ewcfg.cmd_weather: ewcmd.weather,

	# Rowdys thrash and Killers dab.
	ewcfg.cmd_thrash: ewcmd.thrash,
	ewcfg.cmd_dab: ewcmd.dab,
	#foremly cmd_dab
	# Ghosts can BOO 
	ewcfg.cmd_boo: ewcmd.boo,
	#ewcfg.cmd_spook: ewcmd.spook,
	
	# Juvies can dance
	ewcfg.cmd_dance: ewcmd.dance,
	
	# Terezi Gang can flip coins
	ewcfg.cmd_coinflip: ewcmd.coinflip,
    
	# Make a costume for Double Halloween
	#ewcfg.cmd_makecostume: ewitem.makecostume,

	# Show the total of negative slime in the market.
	ewcfg.cmd_negapool: ewspooky.negapool,
	
	# Show the total of negative slime in the world.
	ewcfg.cmd_negaslime: ewspooky.negaslime,
	
	# Show the total of positive slime in the world.
	ewcfg.cmd_endlesswar: ewcmd.endlesswar,
	
	# Show the number of swears in the global swear jar.
	ewcfg.cmd_swear_jar: ewcmd.swearjar,

	# Display the progress towards the current Quarterly Goal.
	ewcfg.cmd_quarterlyreport: ewmarket.quarterlyreport,


	ewcfg.cmd_retire: ewapt.retire,
	ewcfg.cmd_depart: ewapt.depart,
	ewcfg.cmd_consult: ewapt.consult,
	#ewcfg.cmd_rent_cycle: ewapt.rent_cycle,
	ewcfg.cmd_sign_lease: ewapt.signlease,
	ewcfg.cmd_apartment: ewapt.apartment,
	ewcfg.cmd_rip: ewapt.nothing,
	ewcfg.cmd_sign: ewapt.nothing,
	ewcfg.cmd_upgrade: ewapt.upgrade,
	ewcfg.cmd_knock: ewapt.knock,
	#ewcfg.cmd_trickortreat: ewapt.trickortreat,
	ewcfg.cmd_breaklease: ewapt.cancel,


	ewcfg.cmd_pot: ewapt.flowerpot,

	ewcfg.cmd_aquarium: ewapt.lobbywarning,
	ewcfg.cmd_propstand: ewapt.lobbywarning,

	ewcfg.cmd_releaseprop: ewapt.releaseprop,
	ewcfg.cmd_releasefish: ewapt.releasefish,
	ewcfg.cmd_unpot: ewapt.unpot,
	ewcfg.cmd_smoke: ewcosmeticitem.smoke,

	ewcfg.cmd_frame: ewapt.frame,
	ewcfg.cmd_extractsoul: ewitem.soulextract,
	ewcfg.cmd_returnsoul: ewitem.returnsoul,
	ewcfg.cmd_betsoul: ewcasino.betsoul,
	ewcfg.cmd_buysoul: ewcasino.buysoul,
	ewcfg.cmd_squeeze: ewitem.squeeze,

	ewcfg.cmd_toss: ewcmd.toss_off_cliff,
	ewcfg.cmd_jump: ewcmd.jump,
	ewcfg.cmd_push: ewcmd.push,
	ewcfg.cmd_push_alt_1: ewcmd.push,


	ewcfg.cmd_dyefurniture: ewapt.dyefurniture,

	ewcfg.cmd_purify: ewcmd.purify,

	ewcfg.cmd_store: ewcmd.store_item,
	ewcfg.cmd_take: ewcmd.remove_item,

	ewcfg.cmd_fridge: ewapt.lobbywarning,
	ewcfg.cmd_closet: ewapt.lobbywarning,
	ewcfg.cmd_decorate: ewapt.lobbywarning,
	ewcfg.cmd_shelve: ewapt.lobbywarning,
	ewcfg.cmd_shelve_alt_1: ewapt.lobbywarning,
	ewcfg.cmd_unfridge: ewapt.lobbywarning,
	ewcfg.cmd_uncloset: ewapt.lobbywarning,
	ewcfg.cmd_undecorate: ewapt.lobbywarning,
	ewcfg.cmd_unshelve: ewapt.lobbywarning,
	ewcfg.cmd_unshelve_alt_1: ewapt.lobbywarning,
	ewcfg.cmd_freeze: ewapt.lobbywarning,
	ewcfg.cmd_aptname: ewapt.lobbywarning,
	ewcfg.cmd_aptdesc: ewapt.lobbywarning,
	ewcfg.cmd_addkey: ewapt.add_key,
	ewcfg.cmd_changelocks: ewapt.manual_changelocks,
	ewcfg.cmd_setalarm: ewapt.set_alarm,
	ewcfg.cmd_jam: ewapt.jam,


	# revive yourself as a juvenile after having been killed.
	ewcfg.cmd_revive: ewspooky.revive,

	# Ghosts can haunt enlisted players to reduce their slime score.
	ewcfg.cmd_haunt: ewspooky.haunt,

	# how ghosts leave the sewers
	ewcfg.cmd_manifest: ewspooky.manifest,

	# ghosts can inhabit players to follow them around
	ewcfg.cmd_inhabit: ewspooky.inhabit,

	# remove inhabitted status
	ewcfg.cmd_letgo: ewspooky.let_go,

	# ghosts can empower the weapon of the player they're inhabiting
	ewcfg.cmd_possess_weapon: ewspooky.possess_weapon,

	# ghosts can turn their negaslime into negapoudrins
	ewcfg.cmd_crystalize_negapoudrin: ewspooky.crystalize_negapoudrin,
	
	# Play slime pachinko!
	ewcfg.cmd_slimepachinko: ewcasino.pachinko,

	# Toss the dice at slime craps!
	ewcfg.cmd_slimecraps: ewcasino.craps,

	# Pull the lever on a slot machine!
	ewcfg.cmd_slimeslots: ewcasino.slots,

	# Play slime roulette!
	ewcfg.cmd_slimeroulette: ewcasino.roulette,

	# Play slime baccarat!
	ewcfg.cmd_slimebaccarat: ewcasino.baccarat,

	# Play slime skat!
	ewcfg.cmd_slimeskat: ewcasino.skat,
	ewcfg.cmd_slimeskat_join: ewcasino.skat_join,
	ewcfg.cmd_slimeskat_decline: ewcasino.skat_decline,
	ewcfg.cmd_slimeskat_bid: ewcasino.skat_bid,
	ewcfg.cmd_slimeskat_call: ewcasino.skat_call,
	ewcfg.cmd_slimeskat_pass: ewcasino.skat_pass,
	ewcfg.cmd_slimeskat_play: ewcasino.skat_play,
	ewcfg.cmd_slimeskat_hearts: ewcasino.skat_hearts,
	ewcfg.cmd_slimeskat_slugs: ewcasino.skat_slugs,
	ewcfg.cmd_slimeskat_hats: ewcasino.skat_hats,
	ewcfg.cmd_slimeskat_shields: ewcasino.skat_shields,
	ewcfg.cmd_slimeskat_grand: ewcasino.skat_grand,
	ewcfg.cmd_slimeskat_null: ewcasino.skat_null,
	ewcfg.cmd_slimeskat_take: ewcasino.skat_take,
	ewcfg.cmd_slimeskat_hand: ewcasino.skat_hand,
	ewcfg.cmd_slimeskat_choose: ewcasino.skat_choose,


	# Russian Roulette
	ewcfg.cmd_russian: ewcasino.russian_roulette,
	ewcfg.cmd_accept: ewcmd.accept,
	ewcfg.cmd_refuse: ewcmd.refuse,
	
	# Dueling
	ewcfg.cmd_duel: ewcasino.duel,


	# See what's for sale in the Food Court.
	ewcfg.cmd_menu: ewfood.menu,
	ewcfg.cmd_menu_alt1: ewfood.menu,
	ewcfg.cmd_menu_alt2: ewfood.menu,

	# Order refreshing food and drinks!
	ewcfg.cmd_order: ewfood.order,
	ewcfg.cmd_buy: ewfood.order,

	# Transfer slime between players. Shares a cooldown with investments.
	ewcfg.cmd_transfer: ewmarket.xfer,
	ewcfg.cmd_transfer_alt1: ewmarket.xfer,

	# Show the player's slime coin.
	ewcfg.cmd_slimecoin: ewmarket.slimecoin,
	ewcfg.cmd_slimecoin_alt1: ewmarket.slimecoin,
	ewcfg.cmd_slimecoin_alt2: ewmarket.slimecoin,
	ewcfg.cmd_slimecoin_alt3: ewmarket.slimecoin,

	# Donate your slime to SlimeCorp in exchange for SlimeCoin.
	ewcfg.cmd_donate: ewmarket.donate,

	# Invest slimecoin into a stock
	ewcfg.cmd_invest: ewmarket.invest,

	# Withdraw slimecoin from your shares
	ewcfg.cmd_withdraw: ewmarket.withdraw,

	# show the exchange rate of a given stock
	ewcfg.cmd_exchangerate: ewmarket.rate,
	ewcfg.cmd_exchangerate_alt1: ewmarket.rate,
	ewcfg.cmd_exchangerate_alt2: ewmarket.rate,
	ewcfg.cmd_exchangerate_alt3: ewmarket.rate,
	ewcfg.cmd_exchangerate_alt4: ewmarket.rate,

	# show player's current shares in a compant
	ewcfg.cmd_shares: ewmarket.shares,

	# check available stocks
	ewcfg.cmd_stocks: ewmarket.stocks,

	# ads
	ewcfg.cmd_advertise: ewads.advertise,
	ewcfg.cmd_ads: ewads.ads_look,
	ewcfg.cmd_confirm: ewcmd.confirm,
	ewcfg.cmd_cancel: ewcmd.cancel,

	# show player inventory
	ewcfg.cmd_inventory: ewitem.inventory_print,
	ewcfg.cmd_inventory_alt1: ewitem.inventory_print,
	ewcfg.cmd_inventory_alt2: ewitem.inventory_print,
	ewcfg.cmd_inventory_alt3: ewitem.inventory_print,
	ewcfg.cmd_communitychest: ewitem.inventory_print,

	# get an item's description
	ewcfg.cmd_inspect: ewitem.item_look,
	ewcfg.cmd_inspect_alt1: ewitem.item_look,

	# use an item
	ewcfg.cmd_use: ewitem.item_use,


	# Remove a megaslime (1 mil slime) from a general.
	ewcfg.cmd_deadmega: ewkingpin.deadmega,

	# Release a player from their faction.
	ewcfg.cmd_pardon: ewkingpin.pardon,
	ewcfg.cmd_banish: ewkingpin.banish,


	# Navigate the world map.
	ewcfg.cmd_move: ewmap.move,
	ewcfg.cmd_move_alt1: ewmap.move,
	ewcfg.cmd_move_alt2: ewmap.move,
	ewcfg.cmd_move_alt3: ewmap.move,
	ewcfg.cmd_move_alt4: ewmap.move,
	ewcfg.cmd_move_alt5: ewmap.move,

	# go down
	ewcfg.cmd_descend: ewmap.descend,

	# Cancel all moves in progress.
	ewcfg.cmd_halt: ewmap.halt,
	ewcfg.cmd_halt_alt1: ewmap.halt,

	# public transportation
	ewcfg.cmd_embark: ewtransport.embark,
	ewcfg.cmd_embark_alt1: ewtransport.embark,
	ewcfg.cmd_disembark: ewtransport.disembark,
	ewcfg.cmd_disembark_alt1: ewtransport.disembark,
	ewcfg.cmd_checkschedule: ewtransport.check_schedule,

	# Look around the POI you find yourself in.
	ewcfg.cmd_look: ewmap.look,
	
	# Look around the POI, but do not obtain the district's description (reduces clutter and response time).
	ewcfg.cmd_survey: ewmap.survey,
	
	# Inspect objects in a POI
	# ewcfg.cmd_scrutinize: ewdebug.scrutinize,

	# Look around an adjacent POI
	ewcfg.cmd_scout: ewmap.scout,
	ewcfg.cmd_scout_alt1: ewmap.scout,

	# Check your current POI capture progress
	ewcfg.cmd_capture_progress: ewdistrict.capture_progress,

	# Change your current POI capture progress

	#ewcfg.cmd_annex: ewdistrict.annex,
	ewcfg.cmd_spray: ewwep.spray,
	#ewcfg.cmd_annex_alt1: ewdistrict.annex,
	ewcfg.cmd_spray_alt1: ewwep.spray,
	ewcfg.cmd_changespray:ewdistrict.change_spray,
	ewcfg.cmd_changespray:ewdistrict.change_spray,
	ewcfg.cmd_tag:ewdistrict.tag,

	# link to the world map
	ewcfg.cmd_map: ewcmd.map,
	ewcfg.cmd_transportmap: ewcmd.transportmap,

	#farming
	ewcfg.cmd_sow: ewfarm.sow,
	ewcfg.cmd_reap: ewfarm.reap,
	ewcfg.cmd_reap_alt: ewfarm.reap,
	ewcfg.cmd_check_farm: ewfarm.check_farm,
	ewcfg.cmd_irrigate: ewfarm.cultivate,
	ewcfg.cmd_weed: ewfarm.cultivate,
	ewcfg.cmd_fertilize: ewfarm.cultivate,
	ewcfg.cmd_pesticide: ewfarm.cultivate,
	ewcfg.cmd_mill: ewfarm.mill,

	# Fishing
	ewcfg.cmd_cast: ewfish.cast,
	ewcfg.cmd_reel: ewfish.reel,
	ewcfg.cmd_appraise: ewfish.appraise,
	ewcfg.cmd_barter: ewfish.barter,
	ewcfg.cmd_embiggen: ewfish.embiggen,

	#scavenging
	ewcfg.cmd_scavenge: ewjuviecmd.scavenge,
	ewcfg.cmd_scavenge_alt1: ewjuviecmd.scavenge,

	#cosmetics
	ewcfg.cmd_adorn: ewcosmeticitem.adorn,
	ewcfg.cmd_dedorn: ewcosmeticitem.dedorn,
	ewcfg.cmd_dedorn_alt1: ewcosmeticitem.dedorn,
	ewcfg.cmd_sew: ewcosmeticitem.sew,
	ewcfg.cmd_retrofit: ewcosmeticitem.retrofit,
	ewcfg.cmd_fashion: ewcmd.fashion,

	ewcfg.cmd_create: ewkingpin.create,
	ewcfg.cmd_forgemasterpoudrin: ewcmd.forge_master_poudrin,
	ewcfg.cmd_createitem: ewcmd.create_item,
	ewcfg.cmd_manualsoulbind: ewcmd.manual_soulbind,
	ewcfg.cmd_editprops: ewitem.manually_edit_item_properties,
	ewcfg.cmd_setslime: ewcmd.set_slime,
	ewcfg.cmd_checkstats: ewcmd.check_stats,
	# ewcfg.cmd_exalt: ewkingpin.exalt,
	ewcfg.cmd_dyecosmetic: ewcosmeticitem.dye,
	ewcfg.cmd_dyecosmetic_alt1: ewcosmeticitem.dye,
	ewcfg.cmd_dyecosmetic_alt2: ewcosmeticitem.dye,
	ewcfg.cmd_dyecosmetic_alt3: ewcosmeticitem.dye,

	#smelting
	ewcfg.cmd_smelt: ewsmelting.smelt,

	#give an item to another player
	ewcfg.cmd_give: ewitem.give,

	# drop item into your current district
	ewcfg.cmd_discard: ewitem.discard,
	ewcfg.cmd_discard_alt1: ewitem.discard,
	
	# delete a food item from your inventory
	ewcfg.cmd_trash: ewitem.trash,

	# recycle your trash at the slimecorp recycling plant
	ewcfg.cmd_recycle: ewcmd.recycle,
	ewcfg.cmd_recycle_alt1: ewcmd.recycle,

	# kill all players in your district; could be re-used for a future raid boss
	#ewcfg.cmd_writhe: ewraidboss.writhe,

	# Link to the guide.
	ewcfg.cmd_help: ewcmd.help,
	ewcfg.cmd_help_alt1: ewcmd.help,
	ewcfg.cmd_help_alt2: ewcmd.help,
	ewcfg.cmd_help_alt3: ewcmd.help,

	# Misc
	ewcfg.cmd_howl: ewcmd.cmd_howl,
	ewcfg.cmd_howl_alt1: ewcmd.cmd_howl,
	ewcfg.cmd_moan: ewcmd.cmd_moan,
	ewcfg.cmd_harvest: ewcmd.harvest,
	ewcfg.cmd_salute: ewcmd.salute,
	ewcfg.cmd_unsalute: ewcmd.unsalute,
	ewcfg.cmd_hurl: ewcmd.hurl,
	ewcfg.cmd_news: ewcmd.patchnotes,
	ewcfg.cmd_patchnotes: ewcmd.patchnotes,
	ewcfg.cmd_wiki: ewcmd.wiki,
	ewcfg.cmd_booru: ewcmd.booru,
	ewcfg.cmd_leaderboard: ewcmd.leaderboard,
	ewcfg.cmd_leaderboard_alt1: ewcmd.leaderboard,


	# Slimeoids

	ewcfg.cmd_incubateslimeoid: ewslimeoid.incubateslimeoid,
	ewcfg.cmd_growbody: ewslimeoid.growbody,
	ewcfg.cmd_growhead: ewslimeoid.growhead,
	ewcfg.cmd_growlegs: ewslimeoid.growlegs,
	ewcfg.cmd_growweapon: ewslimeoid.growweapon,
	ewcfg.cmd_growarmor: ewslimeoid.growarmor,
	ewcfg.cmd_growspecial: ewslimeoid.growspecial,
	ewcfg.cmd_growbrain: ewslimeoid.growbrain,
	ewcfg.cmd_nameslimeoid: ewslimeoid.nameslimeoid,
	ewcfg.cmd_raisemoxie: ewslimeoid.raisemoxie,
	ewcfg.cmd_lowermoxie: ewslimeoid.lowermoxie,
	ewcfg.cmd_raisegrit: ewslimeoid.raisegrit,
	ewcfg.cmd_lowergrit: ewslimeoid.lowergrit,
	ewcfg.cmd_raisechutzpah: ewslimeoid.raisechutzpah,
	ewcfg.cmd_lowerchutzpah: ewslimeoid.lowerchutzpah,
	ewcfg.cmd_spawnslimeoid: ewslimeoid.spawnslimeoid,
	ewcfg.cmd_dissolveslimeoid: ewslimeoid.dissolveslimeoid,
	ewcfg.cmd_slimeoid: ewslimeoid.slimeoid,
	ewcfg.cmd_instructions: ewslimeoid.instructions,
	ewcfg.cmd_playfetch: ewslimeoid.playfetch,
	ewcfg.cmd_petslimeoid: ewslimeoid.petslimeoid,
	ewcfg.cmd_abuseslimeoid: ewslimeoid.abuseslimeoid,
	ewcfg.cmd_walkslimeoid: ewslimeoid.walkslimeoid,
	ewcfg.cmd_observeslimeoid: ewslimeoid.observeslimeoid,
	ewcfg.cmd_slimeoidbattle: ewslimeoid.slimeoidbattle,
	ewcfg.cmd_saturateslimeoid: ewslimeoid.saturateslimeoid,
	ewcfg.cmd_restoreslimeoid: ewslimeoid.restoreslimeoid,
	ewcfg.cmd_bottleslimeoid: ewslimeoid.bottleslimeoid,
	ewcfg.cmd_unbottleslimeoid: ewslimeoid.unbottleslimeoid,
	ewcfg.cmd_feedslimeoid: ewslimeoid.feedslimeoid,
	ewcfg.cmd_dress_slimeoid: ewslimeoid.dress_slimeoid,
	ewcfg.cmd_dress_slimeoid_alt1: ewslimeoid.dress_slimeoid,
	ewcfg.cmd_undress_slimeoid: ewslimeoid.undress_slimeoid,
	ewcfg.cmd_undress_slimeoid_alt1: ewslimeoid.undress_slimeoid,

	# Negaslimeoids

	ewcfg.cmd_negaslimeoid: ewslimeoid.negaslimeoid,
	ewcfg.cmd_summonnegaslimeoid: ewspooky.summon_negaslimeoid,
	ewcfg.cmd_summonnegaslimeoid_alt1: ewspooky.summon_negaslimeoid,
	ewcfg.cmd_summonnegaslimeoid_alt2: ewspooky.summon_negaslimeoid,
	ewcfg.cmd_battlenegaslimeoid: ewslimeoid.negaslimeoidbattle,
	ewcfg.cmd_battlenegaslimeoid_alt1: ewslimeoid.negaslimeoidbattle,

	# Enemies
	ewcfg.cmd_summonenemy: ewhunting.summonenemy,
	ewcfg.cmd_deleteallenemies: ewhunting.delete_all_enemies,
	ewcfg.cmd_summongvsenemy: ewhunting.summongvsenemy,

	# troll romance
	ewcfg.cmd_add_quadrant: ewquadrants.add_quadrant,
	ewcfg.cmd_clear_quadrant: ewquadrants.clear_quadrant,
	ewcfg.cmd_get_quadrants: ewquadrants.get_quadrants,
	ewcfg.cmd_get_flushed: ewquadrants.get_flushed,
	ewcfg.cmd_get_flushed_alt1: ewquadrants.get_flushed,
	ewcfg.cmd_get_pale: ewquadrants.get_pale,
	ewcfg.cmd_get_pale_alt1: ewquadrants.get_pale,
	ewcfg.cmd_get_caliginous: ewquadrants.get_caliginous,
	ewcfg.cmd_get_caliginous_alt1: ewquadrants.get_caliginous,
	ewcfg.cmd_get_ashen: ewquadrants.get_ashen,
	ewcfg.cmd_get_ashen_alt1: ewquadrants.get_ashen,

	# mutations
	ewcfg.cmd_reroll_mutation: ewmutation.reroll_last_mutation,
	ewcfg.cmd_clear_mutations: ewmutation.clear_mutations,

	ewcfg.cmd_teleport: ewmap.teleport,
	ewcfg.cmd_teleport_alt1: ewmap.teleport,
	ewcfg.cmd_teleport_player: ewmap.teleport_player,
	ewcfg.cmd_print_map_data: ewmap.print_map_data,
	ewcfg.cmd_ping_me: ewcmd.ping_me,
	ewcfg.cmd_boot: ewmap.boot,
	ewcfg.cmd_bootall:ewapt.lobbywarning,

	ewcfg.cmd_piss: ewcmd.piss,
	ewcfg.cmd_fursuit: ewcmd.fursuit,

	# BOOK COMMANDS OH YEAH
	ewcfg.cmd_beginmanuscript: ewbook.begin_manuscript,
	ewcfg.cmd_beginmanuscript_alt_1: ewbook.begin_manuscript,
	ewcfg.cmd_beginmanuscript_alt_2: ewbook.begin_manuscript,
	ewcfg.cmd_setpenname: ewbook.set_pen_name,
	ewcfg.cmd_setpenname_alt_1: ewbook.set_pen_name,
	ewcfg.cmd_settitle: ewbook.set_title,
	ewcfg.cmd_settitle_alt_1: ewbook.set_title,
	ewcfg.cmd_setgenre: ewbook.set_genre,
	ewcfg.cmd_editpage: ewbook.edit_page,
	ewcfg.cmd_viewpage: ewbook.view_page,
	ewcfg.cmd_checkmanuscript: ewbook.check_manuscript,
	ewcfg.cmd_publishmanuscript: ewbook.publish_manuscript,
	ewcfg.cmd_readbook: ewbook.read_book,
	ewcfg.cmd_nextpage: ewbook.next_page,
	ewcfg.cmd_nextpage_alt_1: ewbook.next_page,
	ewcfg.cmd_previouspage: ewbook.previous_page,
	ewcfg.cmd_previouspage_alt_1: ewbook.previous_page,
	ewcfg.cmd_previouspage_alt_2: ewbook.previous_page,
	ewcfg.cmd_browsezines: ewbook.browse_zines,
	ewcfg.cmd_buyzine: ewbook.order_zine,
	ewcfg.cmd_buyzine_alt_1: ewbook.order_zine,
	ewcfg.cmd_rate: ewbook.rate_zine,
	ewcfg.cmd_rate_alt_1: ewbook.rate_zine,
	ewcfg.cmd_rate_alt_2: ewbook.rate_zine,
	ewcfg.cmd_setpages: ewbook.set_length,
	ewcfg.cmd_setpages_alt_1: ewbook.set_length,
	ewcfg.cmd_setpages_alt_2: ewbook.set_length,
	ewcfg.cmd_takedown: ewbook.take_down_zine,
	ewcfg.cmd_takedown_alt_1: ewbook.take_down_zine,
	ewcfg.cmd_takedown_alt_2: ewbook.take_down_zine,
	ewcfg.cmd_untakedown: ewbook.untake_down_zine,
	ewcfg.cmd_untakedown_alt_1: ewbook.untake_down_zine,
	ewcfg.cmd_untakedown_alt_2: ewbook.untake_down_zine,

	# LOL
	ewcfg.cmd_lol: ewcmd.lol,

	# restores poi roles to their proper names, only usable by admins
	ewcfg.cmd_restoreroles: ewrolemgr.restoreRoleNames,
	
	# hides all poi role names, only usable by admins
	ewcfg.cmd_hiderolenames: ewrolemgr.hideRoleNames,
	
	# recreates all hidden poi roles in the server in case restoreRoleNames doesnt work, only usable by admins
	ewcfg.cmd_recreateroles: ewrolemgr.recreateRoles,
	
	# deletes all roles in the server of a particular type
	ewcfg.cmd_deleteroles: ewrolemgr.deleteRoles,
		
	# removes all user overwrites in the server's poi channels
	ewcfg.cmd_removeuseroverwrites: ewrolemgr.remove_user_overwrites,
	
	# Collects all channel topics.
	ewcfg.cmd_collectopics: ewutils.collect_topics,
	
	# Changes those channel topics according to what's in their EwPoi definition
	ewcfg.cmd_synctopics: ewutils.sync_topics,
	
	# Shuts down the bot with sys.exit()
	ewcfg.cmd_shutdownbot: ewutils.shut_down_bot,
	
	# Checks the status of ewutils.TERMINATE
	ewcfg.cmd_checkbot: ewutils.check_bot,
	
	# Sets degradation values for GvS
	ewcfg.cmd_degradedistricts: ewutils.degrade_districts,

	# debug commands
	# ewcfg.cmd_debug1: ewdebug.debug1,
	# ewcfg.cmd_debug2: ewdebug.debug2,
	# ewcfg.cmd_debug3: ewdebug.debug3,
	# ewcfg.cmd_debug4: ewdebug.debug4,
	# ewcfg.debug5: ewdebug.debug5,
	# ewcfg.cmd_debug6: ewdebug.debug6,
	# ewcfg.cmd_debug7: ewdebug.debug7,
	# ewcfg.cmd_debug8: ewdebug.debug8,

	# ban a player from using commands
	ewcfg.cmd_arrest: ewcmd.arrest,
	ewcfg.cmd_release: ewcmd.release,
	ewcfg.cmd_release_alt1: ewcmd.release,
	ewcfg.cmd_balance_cosmetics: ewcmd.balance_cosmetics,

	# grant slimecorp executive status
	ewcfg.cmd_promote: ewcmd.promote,

	# trading
	ewcfg.cmd_trade: ewmarket.trade,
	ewcfg.cmd_offer: ewmarket.offer_item,
	ewcfg.cmd_remove_offer: ewmarket.remove_offer,
	ewcfg.cmd_completetrade: ewmarket.complete_trade,
	ewcfg.cmd_canceltrade: ewmarket.cancel_trade,

	# Praying at the base of ENDLESS WAR.
	ewcfg.cmd_pray: ewcmd.pray,

	# Gankers Vs. Shamblers gang swapping
	ewcfg.cmd_shamble: ewdistrict.shamble,
	ewcfg.cmd_rejuvenate: ewdistrict.rejuvenate,
	
	# slimeball
	ewcfg.cmd_slimeball: ewsports.slimeball,
	ewcfg.cmd_slimeballgo: ewsports.slimeballgo,
	ewcfg.cmd_slimeballstop: ewsports.slimeballstop,
	ewcfg.cmd_slimeballleave: ewsports.slimeballleave,

	# flush items and slime from subzones into their mother district
	ewcfg.cmd_flushsubzones: ewcmd.flush_subzones,

	#swap weapons
	ewcfg.cmd_switch: ewwep.switch_weapon,
	ewcfg.cmd_switch_alt_1: ewwep.switch_weapon,
	# Slimernalia
	# Check your current festivity
	#ewcfg.cmd_festivity: ewcmd.festivity,
	# Wrap a gift
	#ewcfg.cmd_wrap: ewcmd.wrap,
	# Unwrap a gift
	ewcfg.cmd_unwrap: ewcmd.unwrap,
	# Yo, Slimernalia
	#ewcfg.cmd_yoslimernalia: ewcmd.yoslimernalia
	
	# Swilldermuk
	# ewcfg.cmd_gambit: ewcmd.gambit,
	# ewcfg.cmd_credence: ewcmd.credence, #debug
	# ewcfg.cmd_get_credence: ewcmd.get_credence, #debug
	# ewcfg.cmd_reset_prank_stats: ewcmd.reset_prank_stats, #debug
	# ewcfg.cmd_set_gambit: ewcmd.set_gambit, #debug
	#ewcfg.cmd_pointandlaugh: ewcmd.point_and_laugh,
	ewcfg.cmd_prank: ewcmd.prank,
	
	# Gankers Vs. Shamblers
	ewcfg.cmd_gvs_printgrid: ewcmd.gvs_print_grid,
	ewcfg.cmd_gvs_printgrid_alt1: ewcmd.gvs_print_grid,
	ewcfg.cmd_gvs_printlane: ewcmd.gvs_print_lane,
	ewcfg.cmd_gvs_incubategaiaslimeoid: ewcmd.gvs_incubate_gaiaslimeoid,
	ewcfg.cmd_gvs_fabricatetombstone: ewcmd.gvs_fabricate_tombstone,
	ewcfg.cmd_gvs_joinoperation: ewcmd.gvs_join_operation,
	# ewcfg.cmd_gvs_leaveoperation: ewcmd.gvs_leave_operation,
	ewcfg.cmd_gvs_checkoperation: ewcmd.gvs_check_operations,
	ewcfg.cmd_gvs_plantgaiaslimeoid: ewcmd.gvs_plant_gaiaslimeoid,
	ewcfg.cmd_gvs_almanac: ewcmd.almanac,
	ewcfg.cmd_gvs_searchforbrainz: ewcmd.gvs_searchforbrainz,
	ewcfg.cmd_gvs_grabbrainz: ewcmd.gvs_grabbrainz,
	ewcfg.cmd_gvs_dive: ewcmd.gvs_dive,
	ewcfg.cmd_gvs_resurface: ewcmd.gvs_resurface,
	ewcfg.cmd_gvs_sellgaiaslimeoid: ewcmd.gvs_sell_gaiaslimeoid,
	ewcfg.cmd_gvs_sellgaiaslimeoid_alt: ewcmd.gvs_sell_gaiaslimeoid,
	ewcfg.cmd_gvs_dig: ewcmd.dig,
	ewcfg.cmd_gvs_progress: ewcmd.gvs_progress,
	ewcfg.cmd_gvs_gaiaslime: ewcmd.gvs_gaiaslime,
	ewcfg.cmd_gvs_gaiaslime_alt1: ewcmd.gvs_gaiaslime,
	ewcfg.cmd_gvs_brainz: ewcmd.gvs_brainz,

	# race
	ewcfg.cmd_set_race: ewrace.set_race,
	ewcfg.cmd_set_race_alt1: ewrace.set_race,
	ewcfg.cmd_exist: ewrace.exist,
	ewcfg.cmd_ree: ewrace.ree,
	ewcfg.cmd_autocannibalize: ewrace.autocannibalize,
	ewcfg.cmd_rattle: ewrace.rattle,
	ewcfg.cmd_beep: ewrace.beep,
	ewcfg.cmd_yiff: ewrace.yiff,
	ewcfg.cmd_hiss: ewrace.hiss,
	ewcfg.cmd_jiggle: ewrace.jiggle,
	ewcfg.cmd_flutter: ewrace.flutter,
	ewcfg.cmd_request_petting: ewrace.request_petting,
	ewcfg.cmd_rampage: ewrace.rampage,
	ewcfg.cmd_confuse: ewrace.confuse,
}

debug = False
db_prefix = '--db='
while sys.argv:
	arg_lower = sys.argv[0].lower()
	if arg_lower == '--debug':
		debug = True
	elif arg_lower.startswith(db_prefix):
		ewcfg.database = arg_lower[len(db_prefix):]

	sys.argv = sys.argv[1:]

# When debug is enabled, additional commands are turned on.
if debug == True:
	ewutils.DEBUG = True
	ewutils.logMsg('Debug mode enabled.')

ewutils.logMsg('Using database: {}'.format(ewcfg.database))

@client.event
async def on_member_remove(member):
	# Kill players who leave the server.
	try:
		user_data = EwUser(member = member)

		# don't kill players who haven't cleared the tutorial yet
		if user_data.poi in ewcfg.tutorial_pois:
			return

		user_data.trauma = ewcfg.trauma_id_suicide
		user_data.die(cause = ewcfg.cause_leftserver)
		user_data.persist()

		ewutils.logMsg('Player killed for leaving the server.')
	except:
		ewutils.logMsg('Failed to kill member who left the server.')

@client.event
async def on_member_update(before, after):
	# update last offline time if they went from offline to online
	try:
		if before.status == discord.Status.offline and after.status != discord.Status.offline:

			user_data = EwUser(member = after)
			user_data.time_lastoffline = int(time.time())
			user_data.persist()
	except:
		ewutils.logMsg('Failed to update member\'s last offline time.')

@client.event
async def on_ready():
	global init_complete
	if init_complete:
		return
	init_complete = True
	ewcfg.set_client(client)
	ewutils.logMsg('Logged in as {} ({}).'.format(client.user.name, client.user.id))

	ewutils.logMsg("Loaded NLACakaNM world map. ({}x{})".format(ewmap.map_width, ewmap.map_height))
	ewmap.map_draw()

	# Flatten role names to all lowercase, no spaces.
	fake_observer = EwUser()
	fake_observer.life_state = ewcfg.life_state_observer
	for poi in ewcfg.poi_list:
		if poi.role != None:
			poi.role = ewutils.mapRoleName(poi.role)
		if poi.major_role != None:
			poi.major_role = ewutils.mapRoleName(poi.major_role)
		if poi.minor_role != None:
			poi.minor_role = ewutils.mapRoleName(poi.minor_role)

		neighbors = []
		neighbor_ids = []
		#if poi.coord != None:
		if len(poi.neighbors.keys()) > 0:
			neighbors = ewmap.path_to(poi_start = poi.id_poi, user_data = fake_observer)
		#elif poi.id_poi == ewcfg.poi_id_thesewers:
		#	neighbors = ewcfg.poi_list

		if neighbors != None:
			
			for neighbor in neighbors:
				neighbor_ids.append(neighbor.id_poi)

		ewcfg.poi_neighbors[poi.id_poi] = set(neighbor_ids)
		ewutils.logMsg("Found neighbors for poi {}: {}".format(poi.id_poi, ewcfg.poi_neighbors[poi.id_poi]))


	for id_poi in ewcfg.landmark_pois:
		ewutils.logMsg("beginning landmark precomputation for " + id_poi)
		ewmap.landmarks[id_poi] = ewmap.score_map_from(
			poi_start = id_poi,
			user_data = fake_observer,
			landmark_mode = True
		)

	ewcosmeticitem.update_hues()

	ewutils.logMsg("finished landmark precomputation")

	try:
		await client.change_presence(activity = discord.Game(name = "EE " + ewcfg.version))
	except:
		ewutils.logMsg("Failed to change_presence!")

	# Look for a Twitch client_id on disk.
	# FIXME debug - temporarily disable Twitch integration
	if False:
		twitch_client_id = ewutils.getTwitchClientId()

	# If no twitch client ID is available, twitch integration will be disabled.
	# FIXME debug - temporarily disable Twitch integration.
	if True:
		twitch_client_id = None
		ewutils.logMsg('Twitch integration disabled.')
	elif twitch_client_id == None or len(twitch_client_id) == 0:
		ewutils.logMsg('No twitch_client_id file found. Twitch integration disabled.')
	else:
		ewutils.logMsg("Enabled Twitch integration.")

	# Channels in the connected discord servers to announce to.
	channels_announcement = []

	# Channels in the connected discord servers to send stock market updates to. Map of server ID to channel.
	channels_stockmarket = {}

	for server in client.guilds:
		# Update server data in the database
		ewserver.server_update(server = server)

		# store the list of channels in an ewutils field
		ewcfg.update_server_list(server = server)

		# find roles and add them tom the database
		ewrolemgr.setupRoles(client = client, id_server = server.id)
		
		# Refresh the permissions of all users
		# await ewrolemgr.refresh_user_perms(client = client, id_server = server.id, startup = True)

		# Grep around for channels
		ewutils.logMsg("connected to server: {}".format(server.name))
		for channel in server.channels:
			if(channel.type == discord.ChannelType.text):
				if(channel.name == ewcfg.channel_twitch_announcement):
					channels_announcement.append(channel)
					ewutils.logMsg("• found channel for announcements: {}".format(channel.name))

				elif(channel.name == ewcfg.channel_stockexchange):
					channels_stockmarket[server.id] = channel
					ewutils.logMsg("• found channel for stock exchange: {}".format(channel.name))

		# create all the districts in the database
		for poi_object in ewcfg.poi_list:
			poi = poi_object.id_poi
			# call the constructor to create an entry if it doesnt exist yet
			dist = EwDistrict(id_server = server.id, district = poi)
			# change the ownership to the faction that's already in control to initialize topic names
			try:
				# initialize gang bases
				if poi == ewcfg.poi_id_rowdyroughhouse:
					dist.controlling_faction = ewcfg.faction_boober
				elif poi == ewcfg.poi_id_copkilltown:
					dist.controlling_faction = ewcfg.faction_milkers

				resp_cont = dist.change_ownership(new_owner = dist.controlling_faction, actor = "init", client = client)
				dist.persist()
				await resp_cont.post()

			except:
				ewutils.logMsg('Could not change ownership for {} to "{}".'.format(poi, dist.controlling_faction))

		# kill people who left the server while the bot was offline
		#ewutils.kill_quitters(server.id) #FIXME function get_member doesn't find users reliably

		asyncio.ensure_future(ewdistrict.capture_tick_loop(id_server = server.id))
		asyncio.ensure_future(ewutils.bleed_tick_loop(id_server = server.id))
		asyncio.ensure_future(ewutils.enemy_action_tick_loop(id_server=server.id))
		asyncio.ensure_future(ewutils.burn_tick_loop(id_server = server.id))
		asyncio.ensure_future(ewutils.remove_status_loop(id_server = server.id))
		asyncio.ensure_future(ewworldevent.event_tick_loop(id_server = server.id))
		asyncio.ensure_future(ewutils.sap_tick_loop(id_server = server.id))
		# SWILLDERMUK
		# asyncio.ensure_future(ewutils.spawn_prank_items_tick_loop(id_server = server.id))
		# asyncio.ensure_future(ewutils.generate_credence_tick_loop(id_server = server.id))
		
		if ewcfg.gvs_active:
			asyncio.ensure_future(ewutils.gvs_gamestate_tick_loop(id_server=server.id))
		else:
			# Enemies do not spawn randomly during Gankers Vs. Shamblers
			asyncio.ensure_future(ewutils.spawn_enemies_tick_loop(id_server=server.id))

		if not debug:
			#await ewtransport.init_transports(id_server = server.id)
			asyncio.ensure_future(ewweather.weather_tick_loop(id_server = server.id))
		asyncio.ensure_future(ewslimeoid.slimeoid_tick_loop(id_server = server.id))
		asyncio.ensure_future(ewfarm.farm_tick_loop(id_server = server.id))
		asyncio.ensure_future(ewsports.slimeball_tick_loop(id_server = server.id))
		
		print('\nNUMBER OF CHANNELS IN SERVER: {}\n'.format(len(server.channels)))

	try:
		ewutils.logMsg('Creating message queue directory.')
		os.mkdir(ewcfg.dir_msgqueue)
	except FileExistsError:
		ewutils.logMsg('Message queue directory already exists.')

	ewutils.logMsg('Ready.')

	"""
		Set up for infinite loop to perform periodic tasks.
	"""
	time_now = int(time.time())
	time_last_pvp = time_now

	time_last_twitch = time_now
	time_twitch_downed = 0

	# Every three hours we log a message saying the periodic task hook is still active. On startup, we want this to happen within about 60 seconds, and then on the normal 3 hour interval.
	time_last_logged = time_now - ewcfg.update_hookstillactive + 60

	stream_live = None

	ewutils.logMsg('Beginning periodic hook loop.')
	while not ewutils.TERMINATE:
		time_now = int(time.time())

		# Periodic message to log that this stuff is still running.
		if (time_now - time_last_logged) >= ewcfg.update_hookstillactive:
			time_last_logged = time_now

			ewutils.logMsg("Periodic hook still active.")

		# Check to see if a stream is live via the Twitch API.
		# FIXME disabled
		if False:
		#if twitch_client_id != None and (time_now - time_last_twitch) >= ewcfg.update_twitch:
			time_last_twitch = time_now

			try:
				# Twitch API call to see if there are any active streams.
				json_string = ""
				p = subprocess.Popen(
					"curl -H 'Client-ID: {}' -X GET 'https://api.twitch.tv/helix/streams?user_login = rowdyfrickerscopkillers' 2>/dev/null".format(twitch_client_id),
					shell = True,
					stdout = subprocess.PIPE
				)

				for line in p.stdout.readlines():
					json_string += line.decode('utf-8')

				json_parsed = json.loads(json_string)

				# When a stream is up, data is an array of stream information objects.
				data = json_parsed.get('data')
				if data != None:
					data_count = len(data)
					stream_was_live = stream_live
					stream_live = True if data_count > 0 else False

					if stream_was_live == True and stream_live == False:
						time_twitch_downed = time_now

					if stream_was_live == False and stream_live == True and (time_now - time_twitch_downed) > 600:
						ewutils.logMsg("The stream is now live.")

						# The stream has transitioned from offline to online. Make an announcement!
						for channel in channels_announcement:
							await ewutils.send_message(
								client,
								channel,
								"ATTENTION CITIZENS. THE **ROWDY FUCKER** AND THE **COP KILLER** ARE **STREAMING**. BEWARE OF INCREASED KILLER AND ROWDY ACTIVITY.\n\n@everyone\n{}".format(
									"https://www.twitch.tv/rowdyfrickerscopkillers"
								)
							)
			except:
				ewutils.logMsg('Twitch handler hit an exception (continuing): {}'.format(json_string))
				traceback.print_exc(file = sys.stdout)

		# Flag all users in dangerous areas for PvP
		for server in client.guilds:
			await ewutils.flag_vulnerable_districts(id_server = server.id)

		# Clear PvP roles from players who are no longer flagged.
		if (time_now - time_last_pvp) >= ewcfg.update_pvp:
			time_last_pvp = time_now

			try:
				for server in client.guilds:
					# fetch all pvp roles
					pvp_roles = []
					for pvp_role in ewcfg.role_to_pvp_role.values():
						role = ewrolemgr.EwRole(id_server = server.id, name = pvp_role)
						pvp_roles.append(server.get_role(role.id_role))

					members = []
					for role in pvp_roles:
						if role is not None:
							members.extend(role.members)

					# Monitor all user roles and update if a user is no longer flagged for PvP.
					for member in members:
						await ewrolemgr.updateRoles(client = client, member = member, remove_or_apply_flag = 'remove')

			except:
				ewutils.logMsg('An error occurred in the scheduled role update task:')
				traceback.print_exc(file=sys.stdout)

		# Adjust the exchange rate of slime for the market.
		try:
			for server in client.guilds:

				# Load market data from the database.
				market_data = EwMarket(id_server = server.id)

				if market_data.time_lasttick + ewcfg.update_market <= time_now:

					market_response = ""
					exchange_data = EwDistrict(district = ewcfg.poi_id_stockexchange, id_server = server.id)

					for stock in ewcfg.stocks:
						s = EwStock(server.id, stock)
						# we don't update stocks when they were just added
						# or when shamblers have degraded it
						if s.timestamp != 0 and not exchange_data.is_degraded():
							s.timestamp = time_now
							market_response = ewmarket.market_tick(s, server.id)
							await ewutils.send_message(client, channels_stockmarket.get(server.id), market_response)

					market_data = EwMarket(id_server = server.id)
					market_data.time_lasttick = time_now

					# Advance the time and potentially change weather.
					market_data.clock += 1

					if market_data.clock >= 24 or market_data.clock < 0:
						market_data.clock = 0
						market_data.day += 1

					if market_data.clock == 6:
						# Update the list of available bazaar items by clearing the current list and adding the new items
						market_data.bazaar_wares.clear()

						bazaar_foods = []
						bazaar_cosmetics = []
						bazaar_general_items = []
						bazaar_furniture = []

						for item in ewcfg.vendor_inv.get(ewcfg.vendor_bazaar):
							if item in ewcfg.item_names:
								bazaar_general_items.append(item)

							elif item in ewcfg.food_names:
								bazaar_foods.append(item)

							elif item in ewcfg.cosmetic_names:
								bazaar_cosmetics.append(item)

							elif item in ewcfg.furniture_names:
								bazaar_furniture.append(item)

						market_data.bazaar_wares['slimecorp1'] = ewcfg.weapon_id_umbrella
						market_data.bazaar_wares['slimecorp2'] = ewcfg.cosmetic_id_raincoat

						market_data.bazaar_wares['generalitem'] = random.choice(bazaar_general_items)

						market_data.bazaar_wares['food1'] = random.choice(bazaar_foods)
						# Don't add repeated foods
						bw_food2 = None
						while bw_food2 is None or bw_food2 in market_data.bazaar_wares.values():
							bw_food2 = random.choice(bazaar_foods)

						market_data.bazaar_wares['food2'] = bw_food2

						market_data.bazaar_wares['cosmetic1'] = random.choice(bazaar_cosmetics)
						# Don't add repeated cosmetics
						bw_cosmetic2 = None
						while bw_cosmetic2 is None or bw_cosmetic2 in market_data.bazaar_wares.values():
							bw_cosmetic2 = random.choice(bazaar_cosmetics)

						market_data.bazaar_wares['cosmetic2'] = bw_cosmetic2

						bw_cosmetic3 = None
						while bw_cosmetic3 is None or bw_cosmetic3 in market_data.bazaar_wares.values():
							bw_cosmetic3 = random.choice(bazaar_cosmetics)

						market_data.bazaar_wares['cosmetic3'] = bw_cosmetic3

						market_data.bazaar_wares['furniture1'] = random.choice(bazaar_furniture)

						bw_furniture2 = None
						while bw_furniture2 is None or bw_furniture2 in market_data.bazaar_wares.values():
							bw_furniture2 = random.choice(bazaar_furniture)

						market_data.bazaar_wares['furniture2'] = bw_furniture2

						bw_furniture3 = None
						while bw_furniture3 is None or bw_furniture3 in market_data.bazaar_wares.values():
							bw_furniture3 = random.choice(bazaar_furniture)

						market_data.bazaar_wares['furniture3'] = bw_furniture3


						if random.random() < 0.05: # 1 / 20
							market_data.bazaar_wares['minigun'] = ewcfg.weapon_id_minigun


					market_data.persist()

					ewutils.logMsg('The time is now {}.'.format(market_data.clock))

					if not ewutils.check_fursuit_active(market_data.id_server):
						ewcosmeticitem.dedorn_all_costumes()

					if market_data.clock == 6 and market_data.day % 8 == 0:
						await ewapt.rent_time(id_server=server.id)

					market_data = EwMarket(id_server=server.id)

					market_data.persist()
					if market_data.clock == 6:
						response = ' The SlimeCorp Stock Exchange is now open for business.'
						await ewutils.send_message(client, channels_stockmarket.get(server.id), response)
					elif market_data.clock == 20:
						response = ' The SlimeCorp Stock Exchange has closed for the night.'
						await ewutils.send_message(client, channels_stockmarket.get(server.id), response)

					market_data = EwMarket(id_server = server.id)

					if random.randrange(3) == 0:
						pattern_count = len(ewcfg.weather_list)

						if pattern_count > 1:
							weather_old = market_data.weather

							# if random.random() < 0.4:
							# 	market_data.weather = ewcfg.weather_bicarbonaterain

							# Randomly select a new weather pattern. Try again if we get the same one we currently have.
							while market_data.weather == weather_old:
								pick = random.randrange(len(ewcfg.weather_list))
								market_data.weather = ewcfg.weather_list[pick].name

						# Log message for statistics tracking.
						ewutils.logMsg("The weather changed. It's now {}.".format(market_data.weather))

					# Persist new data.
					market_data.persist()

					await ewapt.setOffAlarms(id_server = server.id)

					# Decay slime totals
					ewutils.decaySlimes(id_server = server.id)

					# Increase hunger for all players below the max.
					#ewutils.pushupServerHunger(id_server = server.id)

					# Decrease inebriation for all players above min (0).
					ewutils.pushdownServerInebriation(id_server = server.id)

					# Remove fish offers which have timed out
					ewfish.kill_dead_offers(id_server = server.id)

					# kill advertisements that have timed out
					ewads.delete_expired_ads(id_server = server.id)

					await ewdistrict.give_kingpins_slime_and_decay_capture_points(id_server = server.id)

					await ewmap.kick(server.id)

					# Post leaderboards at 6am NLACakaNM time.
					if market_data.clock == 6:
						await ewleaderboard.post_leaderboards(client = client, server = server)

		except:
			ewutils.logMsg('An error occurred in the scheduled slime market update task:')
			traceback.print_exc(file = sys.stdout)

		# Parse files dumped into the msgqueue directory and send messages as needed.
		try:
			for msg_file in os.listdir(ewcfg.dir_msgqueue):
				fname = "{}/{}".format(ewcfg.dir_msgqueue, msg_file)

				msg = ewutils.readMessage(fname)
				os.remove(fname)

				msg_channel_names = []
				msg_channel_names_reverb = []

				if msg.channel != None:
					msg_channel_names.append(msg.channel)

				if msg.poi != None:
					poi = ewcfg.id_to_poi.get(msg.poi)
					if poi != None:
						if poi.channel != None and len(poi.channel) > 0:
							msg_channel_names.append(poi.channel)

						if msg.reverb == True:
							pois_adjacent = ewmap.path_to(poi_start = msg.poi)

							for poi_adjacent in pois_adjacent:
								if poi_adjacent.channel != None and len(poi_adjacent.channel) > 0:
									msg_channel_names_reverb.append(poi_adjacent.channel)

				if len(msg_channel_names) == 0:
					ewutils.logMsg('in file {} message for channel {} (reverb {})\n{}'.format(msg_file, msg.channel, msg.reverb, msg.message))
				else:
					# Send messages to every connected server.
					for server in client.guilds:
						for channel in server.channels:
							if channel.name in msg_channel_names:
								await ewutils.send_message(client, channel, "**{}**".format(msg.message))
							elif channel.name in msg_channel_names_reverb:
								await ewutils.send_message(client, channel, "**Something is happening nearby...\n\n{}**".format(msg.message))
		except:
			ewutils.logMsg('An error occurred while trying to process the message queue:')
			traceback.print_exc(file = sys.stdout)

		# Wait a while before running periodic tasks.
		await asyncio.sleep(15)

@client.event
async def on_member_join(member):
	ewutils.logMsg("New member \"{}\" joined. Configuring default roles / permissions now.".format(member.display_name))
	await ewrolemgr.updateRoles(client = client, member = member)
	ewplayer.player_update(
		member = member,
		server = member.guild
	)
	user_data = EwUser(member = member)

	if user_data.poi in ewcfg.tutorial_pois:
		await ewdungeons.begin_tutorial(member)

@client.event
async def on_message_delete(message):
	if message != None and message.guild != None and message.author.id != client.user.id and message.content.startswith(ewcfg.cmd_prefix):
		ewutils.logMsg("deleted message from {}: {}".format(message.author.display_name, message.content))
		await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, '**I SAW THAT.**'))

@client.event
async def on_message(message):
	time_now = int(time.time())
	ewcfg.set_client(client)
	
	""" do not interact with our own messages """
	if message.author.id == client.user.id or message.author.bot == True:
		return

	if message.guild != None:
		# Note that the user posted a message.
		active_map = active_users_map.get(message.guild.id)
		if active_map == None:
			active_map = {}
			active_users_map[message.guild.id] = active_map
		active_map[message.author.id] = True

		# Update player information.
		ewplayer.player_update(
			member = message.author,
			server = message.guild
		)
	
	content_tolower = message.content.lower()
	content_tolower_list = content_tolower.split(" ")
	
	re_awoo = re.compile('.*![a]+[w]+o[o]+.*')
	re_moan = re.compile('.*![b]+[r]+[a]+[i]+[n]+[z]+.*')

	# update the player's time_last_action which is used for kicking AFK players out of subzones
	if message.guild != None:

		try:
			ewutils.execute_sql_query("UPDATE users SET {time_last_action} = %s WHERE id_user = %s AND id_server = %s".format(
				time_last_action = ewcfg.col_time_last_action
			), (
				int(time.time()),
				message.author.id,
				message.guild.id
			))
		except:
			ewutils.logMsg('server {}: failed to update time_last_action for {}'.format(message.guild.id, message.author.id))
		
		user_data = EwUser(member = message.author)
		statuses = user_data.getStatusEffects()

		if ewcfg.status_strangled_id in statuses:
			strangle_effect = EwStatusEffect(id_status=ewcfg.status_strangled_id, user_data=user_data)
			source = EwPlayer(id_user=strangle_effect.source, id_server=message.guild.id)
			response = "You manage to break {}'s garrote wire!".format(source.display_name)
			user_data.clear_status(ewcfg.status_strangled_id)			
			return await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
		
		if ewutils.active_restrictions.get(user_data.id_user) == 3:
			user_data.trauma = ewcfg.trauma_id_environment
			die_resp = user_data.die(cause=ewcfg.cause_praying)
			user_data.persist()
			await ewrolemgr.updateRoles(client=client, member=message.author)
			await die_resp.post()

			response = "ENDLESS WAR completely and utterly obliterates {} with a bone-hurting beam.".format(message.author.display_name).replace("@", "\{at\}")
			return await ewutils.send_message(client, message.channel, response)
	
	if message.content.startswith(ewcfg.cmd_prefix) or message.guild == None or len(message.author.roles) < 2 or (any(swear in content_tolower_list for swear in ewcfg.curse_words.keys())):
		"""
			Wake up if we need to respond to messages. Could be:
				message starts with !
				direct message (server == None)
				user is swearing
		"""

		#Ignore users with weird characters in their name
		try:
			message.author.display_name[:3].encode('utf-8').decode('ascii')
		except UnicodeError:
			return await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, "We don't take kindly to moon runes around here."))

		# tokenize the message. the command should be the first word.
		try:
			tokens = shlex.split(message.content)  # it's split with shlex now because shlex regards text within quotes as a single token
		except:
			tokens = message.content.split(' ')  # if splitting via shlex doesnt work (odd number of quotes), use the old splitting method so it doesnt give an exception

		tokens_count = len(tokens)
		cmd = tokens[0].lower() if tokens_count >= 1 else ""

		# remove mentions to us
		mentions = list(filter(lambda user : user.id != client.user.id, message.mentions))
		mentions_count = len(mentions)

		# Create command object
		cmd_obj = ewcmd.EwCmd(
			tokens = tokens,
			message = message,
			client = client,
			mentions = mentions
		)
		
		"""
			Punish the user for swearing.
		"""
		if (any(swear in content_tolower_list for swear in ewcfg.curse_words.keys())):
			# print(content_tolower_list)
			swear_multiplier = 0
	
			playermodel = ewplayer.EwPlayer(id_user=message.author.id)
			usermodel = EwUser(id_user=message.author.id, id_server=playermodel.id_server)

			if usermodel != None:
				market_data = EwMarket(id_server=usermodel.id_server)

				# gather all the swear words the user typed.
				for swear in ewcfg.curse_words.keys():

					if swear == "buster" and usermodel.faction == ewcfg.faction_boober:
						continue
					if swear == "kraker" and usermodel.faction == ewcfg.faction_milkers:
						continue

					swear_count = content_tolower_list.count(swear)

					# Niche scenarios. If certain words are used, don't count their components as swears.
					# if swear == "shit" and "shit" not in content_tolower:
					# 	#print('swear detection turned off for {}.'.format(swear))
					# 	continue
					# elif swear == "fag" and "fag" not in content_tolower:
					# 	#print('swear detection turned off for {}.'.format(swear))
					# 	continue
					# elif swear == "fuck" and (content_tolower.count('<rowdyfucker431275088076079105>') > 0 or content_tolower.count('<fucker431424220837183489>') > 0):
					# 	#print('swear detection turned off for {}.'.format(swear))
					# 	continue
					# elif swear == "mick" and (content_tolower.count('gimmick') > 0):
					# 	#print('swear detection turned off for {}.'.format(swear))
					# 	continue

					for i in range(swear_count):
						swear_multiplier += ewcfg.curse_words[swear]

						market_data.global_swear_jar += 1

						usermodel.swear_jar += 1

				# don't fine the user or send out the message if there weren't enough curse words
				if swear_multiplier > 50:

					# fine the user for swearing, based on how much they've sworn right now, as well as in the past
					swear_jar_fee = usermodel.swear_jar * swear_multiplier * 100

					# prevent user from reaching negative slimecoin
					if swear_jar_fee > usermodel.slimecoin:
						swear_jar_fee = usermodel.slimecoin

					usermodel.change_slimecoin(n=-1 * swear_jar_fee, coinsource=ewcfg.coinsource_swearjar)
					
					response = 'ENDLESS EXPANSION judges you harshly!\n"**{}**"'.format(random.choice(ewcfg.curse_responses).upper())
					await ewutils.send_message(client, message.channel, response)
				#else:
					#print("swear threshold not met")

				market_data.persist()
				usermodel.persist()
			
			# if the message wasn't a command, we can stop here
			if not message.content.startswith(ewcfg.cmd_prefix):
				return

		"""
			Handle direct messages.
		"""
		if message.guild == None:
			playermodel = ewplayer.EwPlayer(id_user = message.author.id)
			usermodel = EwUser(id_user=message.author.id, id_server= playermodel.id_server)
			poi = ewcfg.id_to_poi.get(usermodel.poi)
			cmd_obj.guild = ewcfg.server_list[playermodel.id_server]
			# Direct message the player their inventory.
			if ewitem.cmd_is_inventory(cmd):
				return await ewitem.inventory_print(cmd_obj)
			elif cmd == ewcfg.cmd_inspect:
				return await ewitem.item_look(cmd_obj)
			elif cmd in ewcfg.zine_commands:
				return await ewbook.zine_dm_commands(cmd=cmd_obj)
			elif poi.is_apartment:
				return await ewapt.aptCommands(cmd=cmd_obj)
			elif ewcfg.cmd_gvs_grabbrainz in cmd_obj.message.content.lower():
				return await ewcmd.gvs_grabbrainz(cmd_obj)
			else:
				
				# Only send the help response once every thirty seconds. There's no need to spam it.
				# Also, don't send out response if the user doesn't actually type a command.
				if message.content.startswith(ewcfg.cmd_prefix):
					time_last = last_helped_times.get(message.author.id, 0)
					if (time_now - time_last) > 30:
						last_helped_times[message.author.id] = time_now
						direct_help_response = "ENDLESS WAR doesn't allow you to do that command in DMs.\nIf you're confused about what you're doing, you might want to get some **!help** over at the server."
						await ewutils.send_message(client, message.channel, direct_help_response)
				else:
					return

			# Nothing else to do in a DM.
			return

		# assign the appropriate roles to a user with less than @everyone, faction, both location roles
		if len(message.author.roles) < 4:
			await ewrolemgr.updateRoles(client = client, member = message.author)

		user_data = EwUser(member = message.author)
		if user_data.arrested:
			return

		mutations = user_data.get_mutations()
		# Scold/ignore offline players.
		if message.author.status == discord.Status.offline:

			if ewcfg.mutation_id_chameleonskin not in mutations or cmd not in ewcfg.offline_cmds:

				response = "You cannot participate in the ENDLESS EXPANSION while offline."
    
				return await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))


		if user_data.time_lastoffline > time_now - ewcfg.time_offline:

			if ewcfg.mutation_id_chameleonskin not in mutations or cmd not in ewcfg.offline_cmds:
				response = "You are too paralyzed by ENDLESS EXPANSION's judgemental stare to act."

				return await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))

		statuses = user_data.getStatusEffects()
		# Ignore stunned players
		if ewcfg.status_stunned_id in statuses:
			return

		# Check the main command map for the requested command.
		global cmd_map
		cmd_fn = cmd_map.get(cmd)
		print("timestamp 1: {}".format(int(time.time())))


		if user_data.poi in ewcfg.tutorial_pois:	
			return await ewdungeons.tutorial_cmd(cmd_obj)
			print("timestamp 1: {}".format(int(time.time())))
			
		elif cmd_fn != None:
			# Execute found command
			return await cmd_fn(cmd_obj)

		# FIXME debug
		# Test item creation
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createtestitem'):
			item_id = ewitem.item_create(
				item_type = 'medal',
				id_user = message.author.id,
				id_server = message.guild.id,
				item_props = {
					'medal_name': 'Test Award',
					'medal_desc': '**{medal_name}**: *Awarded to Krak by Krak for testing shit.*'
				}
			)

			ewutils.logMsg('Created item: {}'.format(item_id))
			item = EwItem(id_item = item_id)
			item.item_props['test'] = 'meow'
			item.persist()

			item = EwItem(id_item = item_id)

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, ewitem.item_look(item)))

		# Creates a poudrin
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createpoudrin'):
			for item in ewcfg.item_list:
				if item.context == "poudrin":
					ewitem.item_create(
						item_type = ewcfg.it_item,
						id_user = message.author.id,
						id_server = message.guild.id,
						item_props = {
							'id_item': item.id_item,
							'context': item.context,
							'item_name': item.str_name,
							'item_desc': item.str_desc,
						}
					),
					ewutils.logMsg('Created item: {}'.format(item.id_item))
					item = EwItem(id_item = item.id_item)
					item.persist()
			else:
				pass

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, "Poudrin created."))

		# Shows damage
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'damage'):
			user_data = EwUser(member = message.author, data_level = 1)
			slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 60)
			slimes_damage = int((slimes_spent * (10 + user_data.attack)) * (100 + (user_data.weaponskill * 5)) / 100.0)
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, "{}".format(slimes_damage)))

		# Gives the user some slime
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'getslime'):
			user_data = EwUser(member = message.author)
			user_initial_level = user_data.slimelevel

			response = "You get 1,000,000 slime!"

			levelup_response = user_data.change_slimes(n = 1000000)

			was_levelup = True if user_initial_level < user_data.slimelevel else False

			if was_levelup:
				response += " {}".format(levelup_response)

			user_data.persist()
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'getcoin'):
			user_data = EwUser(member=message.author)
			user_data.change_slimecoin(n=1000000000000, coinsource=ewcfg.coinsource_spending)

			response = "You get 1,000,000,000,000 slimecoin!"

			user_data.persist()
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))

		# Deletes all items in your inventory.
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'clearinv'):
			user_data = EwUser(member = message.author)
			ewitem.item_destroyall(id_server = message.guild.id, id_user = message.author.id)
			response = "You destroy every single item in your inventory."
			user_data.persist()
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))

		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createapple'):
			item_id = ewitem.item_create(
				id_user = message.author.id,
				id_server = message.guild.id,
				item_type = ewcfg.it_food,
				item_props = {
					'id_food': "direapples",
					'food_name': "Dire Apples",
					'food_desc': "This sure is a illegal Dire Apple!",
					'recover_hunger': 500,
					'str_eat': "You chomp into this illegal Dire Apple.",
					'time_expir': int(time.time() + ewcfg.farm_food_expir)
				}
			)

			ewutils.logMsg('Created item: {}'.format(item_id))
			item = EwItem(id_item = item_id)
			item.item_props['test'] = 'meow'
			item.persist()

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, "Apple created."))

		elif debug == True and cmd == (ewcfg.cmd_prefix + 'weathertick'):

			await ewapt.setOffAlarms(id_server=message.guild.id)

		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createhat'):
			patrician_rarity = 20
			patrician_smelted = random.randint(1, patrician_rarity)
			patrician = False

			if patrician_smelted == 1:
				patrician = True

			items = []

			for cosmetic in ewcfg.cosmetic_items_list:
				if patrician and cosmetic.rarity == ewcfg.rarity_patrician:
					items.append(cosmetic)
				elif not patrician and cosmetic.rarity == ewcfg.rarity_plebeian:
					items.append(cosmetic)

			item = items[random.randint(0, len(items) - 1)]

			item_props = ewitem.gen_item_props(item)

			item_id = ewitem.item_create(
				item_type = item.item_type,
				id_user = message.author.id,
				id_server = message.guild.id,
				item_props = item_props
			)

			ewutils.logMsg('Created item: {}'.format(item_id))
			item = EwItem(id_item = item_id)
			item.item_props['test'] = 'meow'
			item.persist()

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, "Hat created."))

		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createfood'):
			item = ewcfg.food_list[random.randint(0, len(ewcfg.food_list) - 1)]

			item_id = ewitem.item_create(
				item_type = ewcfg.it_food,
				id_user = message.author.id,
				id_server = message.guild.id,
				item_props = {
					'id_food': item.id_food,
					'food_name': item.str_name,
					'food_desc': item.str_desc,
					'recover_hunger': item.recover_hunger,
					'str_eat': item.str_eat,
					'time_expir': item.time_expir
				}
			)

			ewutils.logMsg('Created item: {}'.format(item_id))
			item = EwItem(id_item = item_id)
			item.item_props['test'] = 'meow'
			item.persist()

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, "Food created."))

		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createdye'):
			item = ewcfg.dye_list[random.randint(0, len(ewcfg.dye_list) - 1)]

			item_props = ewitem.gen_item_props(item)

			ewitem.item_create(
				item_type = item.item_type,
				id_user = message.author.id,
				id_server = message.guild.id,
				item_props = item_props
			)

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, "{} created.".format(item.str_name)))

		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createoldhat'):
			patrician_rarity = 20
			patrician_smelted = random.randint(1, patrician_rarity)
			patrician = False

			if patrician_smelted == 1:
				patrician = True

			cosmetics_list = []

			for result in ewcfg.cosmetic_items_list:
				if result.acquisition == ewcfg.acquisition_smelting:
					cosmetics_list.append(result)
				else:
					pass

			items = []

			for cosmetic in cosmetics_list:
				if patrician and cosmetic.rarity == ewcfg.rarity_patrician:
					items.append(cosmetic)
				elif not patrician and cosmetic.rarity == ewcfg.rarity_plebeian:
					items.append(cosmetic)

			item = items[random.randint(0, len(items) - 1)]

			ewitem.item_create(
				item_type = ewcfg.it_cosmetic,
				id_user = message.author.id,
				id_server = message.guild.id,
				item_props = {
					'id_cosmetic': item.id_cosmetic,
					'cosmetic_name': item.str_name,
					'cosmetic_desc': item.str_desc,
					'rarity': item.rarity,
					'adorned': 'false'
				}
			)

			response = "Success! You've smelted a {}!".format(item.str_name)

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createoldscalp'):
			ewitem.item_create(
				item_type = ewcfg.it_cosmetic,
				id_user = message.author.id,
				id_server = message.guild.id,
				item_props = {
					'id_cosmetic': 'scalp',
					'cosmetic_name': "My scalp",
					'cosmetic_desc': "A scalp.",
					'adorned': 'false'
				}
			)
			response = "Success! You've smelted a scalp!"

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'createoldsoul'):
			ewitem.item_create(
				id_user = message.author.id,
				id_server = message.guild.id,
				item_type = ewcfg.it_cosmetic,
				item_props = {
					'id_cosmetic': "soul",
					'cosmetic_name': "My soul",
					'cosmetic_desc': "The immortal soul of me. It dances with a vivacious energy inside its jar.\n If you listen to it closely you can hear it whispering numbers: me.",
					'rarity': ewcfg.rarity_patrician,
					'adorned': 'false',
					'user_id': "usermodel.id_user",
				}
			)

			response = "Success! You've smelted a soul!"

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))


		# FIXME debug
		# Test item deletion
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'delete'):
			items = ewitem.inventory(
				id_user = message.author.id,
				id_server = message.guild.id
			)

			for item in items:
				ewitem.item_delete(
					id_item = item.get('id_item')
				)

			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, 'ok'))

		# AWOOOOO
		elif re_awoo.match(cmd):
			return await ewcmd.cmd_howl(cmd_obj)
		elif re_moan.match(cmd):
			return await ewcmd.cmd_moan(cmd_obj)

		# Debug command to override the role of a user
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'setrole'):

			response = ""

			if mentions_count == 0:
				response = 'Set who\'s role?'
			else:
				roles_map = ewutils.getRoleMap(message.guild.roles)
				role_target = tokens[1]
				role = roles_map.get(role_target)

				if role != None:
					for user in mentions:
						try:
							await user.edit(roles=role)
						except:
							ewutils.logMsg('Failed to replace_roles for user {} with {}.'.format(user.display_name, role.name))

					response = 'Done.'
				else:
					response = 'Unrecognized role.'

			await ewutils.send_message(client, cmd.message.channel, ewutils.formatMessage(message.author, response))
			
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'getboober'):
			response = "Yeah get those fat boobs"
			user_data = EwUser(member=message.author)
			user_data.life_state = ewcfg.life_state_enlisted
			user_data.faction = ewcfg.faction_boober
			user_data.time_lastenlist = time_now + ewcfg.cd_enlist
			user_data.persist()
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
		
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'getmilkers'):
			response = "Yum yum mommy milk"
			user_data = EwUser(member=message.author)
			user_data.life_state = ewcfg.life_state_enlisted
			user_data.faction = ewcfg.faction_milkers
			user_data.time_lastenlist = time_now + ewcfg.cd_enlist
			user_data.persist()
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))

		elif debug == True and cmd == (ewcfg.cmd_prefix + 'getshambler'):
			response = "You get shambler. Jesus fucking Christ, why not, sure."
			user_data = EwUser(member=message.author)
			user_data.life_state = ewcfg.life_state_shambler
			user_data.persist()
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
			
		# Toggles rain on and off
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'toggledownfall'):
			market_data = EwMarket(id_server=message.guild.id)
			
			if market_data.weather == ewcfg.weather_bicarbonaterain:
				newweather = ewcfg.weather_sunny
				
				market_data.weather = newweather
				response = "Bicarbonate rain turned OFF. Weather was set to {}.".format(newweather)
			else:
				market_data.weather = ewcfg.weather_bicarbonaterain
				response = "Bicarbonate rain turned ON."
				
			market_data.persist()
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))

		elif debug == True and cmd == (ewcfg.cmd_prefix + 'dayforward'):
			market_data = EwMarket(id_server=message.guild.id)

			market_data.day += 1
			market_data.persist()

			response = "Time has progressed 1 day forward manually."
			
			if ewutils.check_fursuit_active(market_data.id_server):
				response += "\nIt's a full moon!"
				
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
			
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'hourforward'):
			market_data = EwMarket(id_server=message.guild.id)
			
			market_data.clock += 1
			response = "Time has progressed 1 hour forward manually."

			if market_data.clock >= 24 or market_data.clock < 0:
				market_data.clock = 0
				market_data.day += 1
				response += "\nMidnight has come. 1 day progressed forward."
				
			if ewutils.check_fursuit_active(market_data.id_server):
				response += "\nIt's a full moon!"
				
			market_data.persist()
			await ewutils.send_message(client, message.channel, ewutils.formatMessage(message.author, response))
			
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'postleaderboard'):
			try:
				for server in client.guilds:
					await ewleaderboard.post_leaderboards(client=client, server=server)
			except:
				pass
			
			
		# didn't match any of the command words.
		else:
			""" couldn't process the command. bail out!! """
			""" bot rule 0: be cute """
			randint = random.randint(1,3)
			msg_mistake = "ENDLESS EXPANSION is growing frustrated."
			if randint == 2:
				msg_mistake = "ENDLESS EXPANSION denies you her favor."
			elif randint == 3:
				msg_mistake = "ENDLESS EXPANSION pays you no mind."

			msg = await ewutils.send_message(client, cmd_obj.message.channel, msg_mistake, 2)
			await asyncio.sleep(2)
			try:
				await msg.delete()
				pass
			except:
				pass

	elif content_tolower.find(ewcfg.cmd_howl) >= 0 or content_tolower.find(ewcfg.cmd_howl_alt1) >= 0 or re_awoo.match(content_tolower):
		""" Howl if !howl is in the message at all. """
		return await ewcmd.cmd_howl(ewcmd.EwCmd(
			message = message,
			client = client
		))
	elif content_tolower.find(ewcfg.cmd_moan) >= 0 or re_moan.match(content_tolower):
		return await ewcmd.cmd_moan(ewcmd.EwCmd(
			message=message,
			client=client
		))

# find our REST API token
token = ewutils.getToken()

if token == None or len(token) == 0:
	ewutils.logMsg('Please place your API token in a file called "token", in the same directory as this script.')
	sys.exit(0)

# connect to discord and run indefinitely
try:
	client.run(token)
finally:
	ewutils.TERMINATE = True
	ewutils.logMsg("main thread terminated.")

