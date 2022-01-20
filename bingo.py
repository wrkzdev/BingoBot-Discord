#!/usr/bin/env python3.6
# ./bingo.py
# Github:   https://github.com/wrkzdev/BingoBot-Discord
# Author:   CapEtn (Discord ID: 386761001808166912)
# Donation:
# Wrkz: WrkzRNDQDwFCBynKPc459v3LDa1gEGzG3j962tMUBko1fw9xgdaS9mNiGMgA9s1q7hS1Z8SGRVWzcGc8Sh8xsvfZ6u2wJEtoZB
# TRTL: TRTLv2k5RgwQkcXsZpue9ELGq49PEQbgZ7sAncv82GqTc3rehKqRLM7jomrji4zek76hWiYkKKizQFfny1TvvcvyBxqnvcsTfKi
# Dego: dg4nUdJyHV1ZCrYV7kHvTE9HkKT9ynKCW1Antm1ku8ihhsN1PkiH2fFfwsGt2y7UsN3rALr4gg8oz87vpxjaVF8g1uUWKH7pE

# This Bot requires to have blockchain in MySQL. Please see:
# https://github.com/TurtlePay/blockchain-data-collection-agent
# And https://github.com/TurtlePay/blockchain-cache-api
# Without that, you need to customized it on your own.
#
# Portion of board generator is from: https://github.com/jetpacktuxedo/bingo

import discord
from discord.ext import commands
from discord.ext.commands import Bot, AutoShardedBot
from discord.utils import get

import click
import json

import sys, os, random, textwrap
import time, timeago
from datetime import datetime

# Loggin
import logging

# MySQL
import pymysql
import pymysql.cursors
import aiomysql
from aiomysql.cursors import DictCursor

# Setting up asyncio to use uvloop if possible, a faster implementation on the event loop
import asyncio
from config import config
import sys, traceback

pool = None
pool_chain = None

remindedStart = 0
remindedBlock = 0
conn = None
connBlockchain = None

maintainerOwner = [ config.discord.ownerID ] # list owner
BOT_LISTEN_ONLYCHAN = [ config.discord.channelID ] # #bingo

TIPBOTID = config.discord.TipBotID
EMOJI_MONEYFACE = "\U0001F911"
EMOJI_ERROR = "\u274C"
# Blocks where Bot will start + topblock
BINGO_STARTAT = 40
# Bingo to start ping user after 180 blocks.
BINGO_ALERT_BLOCKS = 120

EMOJI_WRKZ = "\U0001F477"
EMOJI_TRTL = "\U0001F422"
EMOJI_DEGO = "\U0001F49B"

EMPTY_DISPLAY = '⬛' # ⬛ :black_large_square:

LIST_TIPREACT = [EMOJI_WRKZ, EMOJI_TRTL, EMOJI_DEGO]
EMOJI_ERROR = "\u274C"
DENY_TIPREACT = EMOJI_ERROR

MIN_PLAYER = 3
BLOCK_MIN_PLAYER = 30
INCREASE_REWARD = 1000
INCREASE_PLAYREWARD = 200

bot_description = "Discord Bingo Game with WrkzCoin hash"
bot_help_board = "Create or show your bingo board"
bot_help_card = "Create or show your bingo board in ascii format"
bot_help_bingo = "Certain command with bingo"
bot_help_balls = "Show last few ball numbers"

bot = AutoShardedBot(command_prefix=['.', '!', '?'], case_insensitive=True)
bot.remove_command("help")

token = config.discord.token
channelID = config.discord.channelID


@bot.event
async def on_ready():
    print("Hello, I am Bingo Bot!")
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print("Guilds: {}".format(len(bot.guilds)))
    print("Users: {}".format(sum([x.member_count for x in bot.guilds])))
    game = discord.Game(name="Playing Bingo!!!")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.event
async def on_shard_ready(shard_id):
    print(f'Shard {shard_id} connected')


@bot.event
async def on_message(message):
    # do some extra stuff here
    if not isinstance(message.channel, discord.DMChannel):
        if message.channel.id not in BOT_LISTEN_ONLYCHAN:
            return
        else:
            pass
    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    global channelID
    botChan = bot.get_channel(int(channelID))
    """The on_message event handler for this module

    Args:
        reaction (discord.Reaction): Input reaction
        user (discord.User): The user that added the reaction
    """

    # Simplify reaction info
    emoji = reaction.emoji
    if user != reaction.message.channel.guild.me:
        if int(user.id) == TIPBOTID and bot.user in reaction.message.mentions:
            if reaction.message.channel.id == channelID and (reaction.emoji in LIST_TIPREACT):
                # OK in bingo channel
                TipThanksMsg = ['Thank you a lot %s!', '%s is kind :)', 'I like %s :) Thank you', 'It is very kind of you, %s', 'Thank you %s'] # created message array
                userMention = '<@'+str(reaction.message.author.id)+'>'
                randMessageTip = str(random.choice(TipThanksMsg)).replace('%s', userMention)
                await botChan.send(f'{randMessageTip}')
            if reaction.message.channel.id == channelID and reaction.emoji == EMOJI_ERROR:
                TipThanksMsg = ['No problem %s!', '%s :) merci quand même', 'Thank you %s ;) '] # created message array
                userMention = '<@'+str(reaction.message.author.id)+'>'
                randMessageTip = str(random.choice(TipThanksMsg)).replace('%s', userMention)
                await botChan.send(f'{randMessageTip}')
            return


def generateBoard():
    bingoList = []
    bingoListB = []
    i = 1
    while i <= 15:
        bingoListB.append(str(i))
        i += 1
    filter(None, bingoListB)
    random.shuffle(bingoListB)
  
    bingoListI = []
    i = 16
    while i <= 30:
        bingoListI.append(str(i))
        i += 1
    filter(None, bingoListI)
    random.shuffle(bingoListI)

    bingoListN = []
    i = 31
    while i <= 45:
        bingoListN.append(str(i))
        i += 1
    filter(None, bingoListN)
    random.shuffle(bingoListN)

    bingoListG = []
    i = 46
    while i <= 60:
        bingoListG.append(str(i))
        i += 1
    filter(None, bingoListG)
    random.shuffle(bingoListG)

    bingoListO = []
    i = 61
    while i <= 75:
        bingoListO.append(str(i))
        i += 1
    filter(None, bingoListO)
    random.shuffle(bingoListO)
    
    bingoList.extend([bingoListB[0], bingoListI[0], bingoListN[0], bingoListG[0], bingoListO[0]])
    bingoList.extend([bingoListB[1], bingoListI[1], bingoListN[1], bingoListG[1], bingoListO[1]])
    bingoList.extend([bingoListB[2], bingoListI[2], 'FREE SPACE', bingoListG[2], bingoListO[2]])
    bingoList.extend([bingoListB[3], bingoListI[3], bingoListN[3], bingoListG[3], bingoListO[3]])
    bingoList.extend([bingoListB[4], bingoListI[4], bingoListN[4], bingoListG[4], bingoListO[4]])
    return bingoList[:25]


# openConnection
async def openConnection():
    global pool
    try:
        if pool is None:
            pool = await aiomysql.create_pool(host=config.mysql.host, port=3306, minsize=2, maxsize=4, 
                                                   user=config.mysql.user, password=config.mysql.password,
                                                   db=config.mysql.db, autocommit=True) # cursorclass=DictCursor
    except:
        traceback.print_exc(file=sys.stdout)


async def openConnectionBlockchain():
    global pool_chain
    try:
        if pool_chain is None:
            pool_chain = await aiomysql.create_pool(host=config.mysql.host_blockcache, port=3306, minsize=2, maxsize=4, 
                                                   user=config.mysql.user_blockcache, password=config.mysql.password_blockcache,
                                                   db=config.mysql.db_blockcache, autocommit=True, cursorclass=DictCursor)
    except:
        traceback.print_exc(file=sys.stdout)


async def CheckUser(userID, userName, GameID):
    global pool
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT started, board_json, board_jsonStar, kicked, kicked_when, gameID 
                          FROM `bingo_active_players` WHERE `discord_id`=%s AND `gameID`=%s LIMIT 1 """
                await cur.execute(sql, (userID, GameID))
                result = await cur.fetchone()
                if result is None:
                    # Insert
                    board = generateBoard()
                    boardJson = json.dumps(board)
                    current_Date = datetime.now()
                    sql = """ INSERT INTO bingo_active_players (`discord_id`, `discord_name`, `started`, `board_json`, 
                              `board_jsonStar`, `GameID`) 
                              VALUES (%s, %s, %s, %s, %s, %s) """
                    await cur.execute(sql, (str(userID), str(userName), current_Date, boardJson, boardJson, GameID))
                    await conn.commit()
                    return board
                else:
                    # Show data
                    return json.loads(result[1])
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


async def CheckUserBoard(userID, gameID):
    global pool_chain, pool
    GameStart = await Bingo_LastGame()
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT started, board_json, board_jsonStar, kicked, kicked_when, gameID 
                          FROM `bingo_active_players` WHERE `discord_id`=%s AND `gameID`=%s AND `kicked`='NO' LIMIT 1 """
                await cur.execute(sql, (str(userID), gameID))
                result = await cur.fetchone()
                if result:
                    # Start connection to blockchain
                    ListChain = []  # For unique list of numbers
                    try:
                        await openConnectionBlockchain()
                        async with pool_chain.acquire() as connBlockchain:
                            async with connBlockchain.cursor() as curBlockchain:
                                sql = """ SELECT `height`, `hash`, `difficulty`,`timestamp` 
                                          FROM blocks WHERE height > %s ORDER BY height DESC  LIMIT 10000 """
                                await curBlockchain.execute(sql, (GameStart[1]))
                                rows = await curBlockchain.fetchall()
                                for row in rows:
                                    sum_75 = int(sumOfDigits(str(row['hash'])) % 75) + 1
                                    if sum_75 not in ListChain:
                                        ListChain.append(sum_75)
                    except Exception as e:
                        traceback.print_exc(file=sys.stdout)
                    # End connection to blockchain
                    k = 0
                    UserBingoList = json.loads(result[1])
                    for row in ListChain:
                        for n, i in enumerate(UserBingoList):
                            if str(i) == str(row):
                                k += 1
                                UserBingoList[n] = '*'+str(row)+'*'
                    return UserBingoList
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    return None


async def CheckUserBingoType(userID, gameID, Type):
    global pool_chain, pool
    GameStart = await Bingo_LastGame()
    if GameStart[2].upper() == 'COMPLETED':
        return None
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT started, board_json, board_jsonStar, kicked, kicked_when, gameID 
                          FROM `bingo_active_players` WHERE `discord_id`=%s AND `gameID`=%s AND `kicked`='NO' LIMIT 1 """
                await cur.execute(sql, (userID, gameID))
                result = await cur.fetchone()
                if result:
                    # SELECT height, hash, difficulty from blocks where height BETWEEN 254400 AND 254481 ORDER BY height DESC
                    try:
                        await openConnectionBlockchain()
                        async with pool_chain.acquire() as connBlockchain:
                            async with connBlockchain.cursor() as curBlockchain:
                                sql = """ SELECT `height`, `hash`, `difficulty`,`timestamp` 
                                          FROM blocks where height > %s ORDER BY height DESC  LIMIT 10000 """
                                await curBlockchain.execute(sql, (GameStart[1]))
                                rows = await curBlockchain.fetchall()
                                ListChain = []  # For unique list of numbers
                                for row in rows:
                                    sum_75 = int(sumOfDigits(str(row['hash'])) % 75) + 1
                                    if sum_75 not in ListChain:
                                        ListChain.append(sum_75)
                    except Exception as e:
                        traceback.print_exc(file=sys.stdout)
                    # End of select from wrkz_blockchain
                    if Type.upper() == 'FOUR CORNERS':
                        # FOUR CORNERS, four numbers at corner to win
                        number_list = []
                        k = 0
                        UserBingoList = json.loads(result[1])
                        number_list.extend([UserBingoList[0], UserBingoList[4], UserBingoList[20], UserBingoList[24]])
                        j = 0
                        for row in ListChain:
                            for (n, i) in enumerate(number_list):
                                if str(i) == str(row):
                                    k += 1
                        if k == 4:
                            return Type
                        else:
                            return k
                    elif Type.upper() == 'LINE':
                        # LINE: a single line can win either diagonal
                        k = 0
                        UserBingoList = json.loads(result[1])
                        z = 0
                        # Horizontal
                        while z < 5:
                            m = 0
                            number_list = []
                            if z != 2:
                                number_list.extend([UserBingoList[5*z], UserBingoList[5*z+1], UserBingoList[5*z+2], UserBingoList[5*z+3], UserBingoList[5*z+4]])
                            else:
                                number_list.extend([UserBingoList[5*z], UserBingoList[5*z+1], UserBingoList[5*z+3], UserBingoList[5*z+4]])
                            for row in ListChain:
                                for (n, i) in enumerate(number_list):
                                    if str(i) == str(row):
                                        m += 1
                            if (z != 2 and m==5) or (z == 2 and m==4):
                                k += 1
                            z += 1
                        # Vertical
                        z = 0
                        while z < 5:
                            m = 0
                            number_list = []
                            if z != 2:
                                number_list.extend([UserBingoList[z], UserBingoList[z+5], UserBingoList[z+10], UserBingoList[z+15], UserBingoList[z+20]])
                            else:
                                number_list.extend([UserBingoList[z], UserBingoList[z+5], UserBingoList[z+15], UserBingoList[z+20]])
                            for row in ListChain:
                                for (n, i) in enumerate(number_list):
                                    if str(i) == str(row):
                                        m += 1
                            if (z != 2 and m==5) or (z == 2 and m==4):
                                k += 1
                            z += 1
                        # Diagonal 1
                        m = 0
                        number_list = []
                        number_list.extend([UserBingoList[0], UserBingoList[6], UserBingoList[18], UserBingoList[24]])
                        for row in ListChain:
                            for (n, i) in enumerate(number_list):
                                if str(i) == str(row):
                                    m += 1
                        # If matches 4 numbers, add k+
                        if m == 4:
                            k += 1
                        m = 0  # reset m to 0
                        # Diagonal 2
                        number_list = []
                        number_list.extend([UserBingoList[4], UserBingoList[8], UserBingoList[16], UserBingoList[20]])
                        for row in ListChain:
                            for (n, i) in enumerate(number_list):
                                if str(i) == str(row):
                                    m += 1
                        # If matches 4 numbers, add k+
                        if m == 4:
                            k += 1
                        if k >= 1:
                            # print(k) ## this will return number of straight line vertical or horizontal
                            return Type
                        else:
                            return k
                    elif Type.upper() == 'DIAGONALS':
                        # DIAGONALS: X lines 0, 4, 6, 8, 16,18 , 20, 24
                        number_list = []
                        k = 0
                        UserBingoList = json.loads(result[1])
                        number_list.extend([UserBingoList[0], UserBingoList[6], UserBingoList[18], UserBingoList[24]])
                        number_list.extend([UserBingoList[4], UserBingoList[8], UserBingoList[16], UserBingoList[20]])
                        j = 0
                        for row in ListChain:
                            for (n, i) in enumerate(number_list):
                                if str(i) == str(row):
                                    k += 1
                        if k == 8:
                            return Type
                        else:
                            return k
                    elif Type.upper() == 'FULL HOUSE':
                        # FULL HOUSE: all numbers in
                        k = 0
                        UserBingoList = json.loads(result[1])
                        for row in ListChain:
                            for n, i in enumerate(UserBingoList):
                                if str(i) == str(row):
                                    k += 1
                        if k >= 24:
                            return Type
                        else:
                            return k
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    return None


async def KickUser(userID, GameID):
    global pool
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT started, board_json, board_jsonStar, kicked, kicked_when, gameID 
                          FROM `bingo_active_players` WHERE `discord_id`=%s AND `gameID`=%s LIMIT 1 """
                await cur.execute(sql, (str(userID), GameID))
                result = await cur.fetchone()
                if result:
                    try:
                        current_Date = datetime.now()
                        await openConnection()
                        async with pool.acquire() as conn:
                            async with conn.cursor() as cur:
                                sql = """ UPDATE bingo_active_players SET `kicked`=%s,`kicked_when`=%s WHERE `discord_id`=%s AND `gameID`=%s """
                                await cur.execute(sql, ('YES', str(current_Date), str(userID), str(GameID)))
                                await conn.commit()
                    except Exception as e:
                        traceback.print_exc(file=sys.stdout) 
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


async def List_bingo_active_players(GameID):
    global pool
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT discord_id, discord_name, started, board_json, board_jsonStar, kicked, kicked_when, gameID 
                          FROM `bingo_active_players` WHERE `gameID`=%s """
                await cur.execute(sql, GameID)
                result = await cur.fetchall()
                return result
    except Exception as e:
        traceback.print_exc(file=sys.stdout)



async def Bingo_CreateGame(startedBlock, discord_id, discord_name, gameType: str=None):
    global pool
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT id, startedBlock, status, completed_when, winner_id, creator_discord_id, creator_discord_name, created_when 
                          FROM `bingo_gamelist` WHERE status!='COMPLETED' LIMIT 1 """
                await cur.execute(sql,)
                result = await cur.fetchone()
                if result is None:
                    # Let's insert starting block info
                    current_Date = datetime.now()
                    topBlock = await gettopblock()
                    if startedBlock - 20 <= topBlock['height']:
                        return None
                    else:
                        if gameType is None:
                            # randomType = random.choice(['FOUR CORNERS','LINE','DIAGONALS'])
                            # if want to change random later
                            randomType = 'ANY'
                            sql = """ INSERT INTO bingo_gamelist (`startedBlock`, `status`, `gameType`, `creator_discord_id`, `creator_discord_name`, created_when) 
                                      VALUES (%s, %s, %s, %s, %s, %s) """
                            await cur.execute(sql, (int(startedBlock), 'OPENED', randomType, discord_id, discord_name, current_Date))
                            await conn.commit()
                        else:
                            sql = """ INSERT INTO bingo_gamelist (`startedBlock`, `status`, `gameType`, `creator_discord_id`, `creator_discord_name`, created_when) 
                                      VALUES (%s, %s, %s, %s, %s, %s) """
                            await cur.execute(sql, (int(startedBlock), 'OPENED', gameType, discord_id, discord_name, current_Date))
                            await conn.commit()
                        # Return array of below. return block height oif created.
                        sql = """ SELECT id, startedBlock, status, completed_when, winner_id, creator_discord_id, creator_discord_name, created_when, gameType 
                                  FROM `bingo_gamelist` ORDER BY id DESC LIMIT 1 """
                        await cur.execute(sql,)
                        result = await cur.fetchone()
                        return result
                else:
                    # Let's show result. return their status
                    return result
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


async def Bingo_LastGame():
    global pool
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT id, startedBlock, status, completed_when, winner_id, gameType, reward, rewardTx, 
                          rewardNotWin, creator_discord_id, creator_discord_name, created_when, remark 
                          FROM `bingo_gamelist` ORDER BY id DESC LIMIT 1 """
                await cur.execute(sql,)
                result = await cur.fetchone()
                return result
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


async def Bingo_LastGameResult():
    global pool
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT id, startedBlock, status, completed_when, winner_id, winner_name, claim_Atheight, gameType 
                          FROM `bingo_gamelist` WHERE `status`='COMPLETED' ORDER BY id DESC LIMIT 1 """
                await cur.execute(sql,)
                result = await cur.fetchone()
                return result
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


async def Bingo_LastGameResultList():
    global pool
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ SELECT id, startedBlock, status, completed_when, winner_id, winner_name, claim_Atheight, gameType 
                          FROM `bingo_gamelist` WHERE `status`='COMPLETED' ORDER BY id DESC LIMIT 5 """
                await cur.execute(sql,)
                result = await cur.fetchall()
                if result:
                    return [[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]] for row in result]
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    return None


async def Bingo_ShowBallNumber(height):
    global pool_chain
    # Get from blockchain
    card = ''
    try:
        await openConnectionBlockchain()
        async with pool_chain.acquire() as connBlockchain:
            async with connBlockchain.cursor() as curBlockchain:
                sql = """ SELECT `height`, `hash`, `difficulty`,`timestamp` 
                          FROM blocks where height=%s ORDER BY height LIMIT 1 """
                await curBlockchain.execute(sql, (height))
                row = await curBlockchain.fetchone()
                if row:
                    sum_75 = int(sumOfDigits(str(row['hash'])) % 75) + 1
                    card = str('__Height__: '+ str('{:,.0f}'.format(row['height'])) + ' Ball number: '+str(sum_75))
                else:
                    card = str('No ball at that height. __'+str('{:,.0f}'.format(height))+'__')
                return card
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    # End of getting from blockchain	


async def Bingo_ShowCards(lastCardNum, gameID):
    global pool_chain
    GameStart = await Bingo_LastGame()
    if GameStart[2].upper() == 'COMPLETED':
        return None
    else:
        gameID = GameStart[0]
    # Get from blockchain
    try:
        await openConnectionBlockchain()
        async with pool_chain.acquire() as connBlockchain:
            async with connBlockchain.cursor() as curBlockchain:
                sql = """ SELECT `height`, `hash`, `difficulty`,`timestamp` 
                          FROM blocks where height > %s ORDER BY height DESC """
                await curBlockchain.execute(sql, (GameStart[1]))
                rows = await curBlockchain.fetchall()
                card = []
                listNumberHashes = []
                i = 0
                for row in rows:
                    sum_75 = int(sumOfDigits(str(row['hash'])) % 75) + 1
                    if (sum_75 not in listNumberHashes):
                        card.append('__Height__: '+ str('{:,.0f}'.format(row['height'])) + ' Ball number: '+str(sum_75))
                        listNumberHashes.append(sum_75)
                    else:
                        card.append('__Height__: '+ str('{:,.0f}'.format(row['height'])) + ' `Ball number: '+str(sum_75)+'`')
                    i += 1
                    if i >= int(lastCardNum):
                        return card
                return card
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    # End of getting from blockchain	


async def Bingo_Extend(gameID: int, topBlock: int):
    global pool
    newBlock = str(topBlock + BLOCK_MIN_PLAYER)
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ UPDATE bingo_gamelist SET startedBlock="""+newBlock+""" WHERE `id`=%s """
                await cur.execute(sql, gameID)
                await conn.commit()
                sql = """ UPDATE bingo_gamelist SET reward=reward+"""+str(INCREASE_REWARD)+""" WHERE `id`=%s """
                await cur.execute(sql, gameID)
                await conn.commit()
                sql = """ UPDATE bingo_gamelist SET rewardNotWin=rewardNotWin+"""+str(INCREASE_PLAYREWARD)+""" WHERE `id`=%s """
                await cur.execute(sql, gameID)
                await conn.commit()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


async def Bingo_ChangeStatusGame(gameID: int, status: str):
    global pool
    if status not in ["COMPLETED", "OPENED", "ONGOING"]:
        return None
    try:
        await openConnection()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """ UPDATE bingo_gamelist SET `status`=%s WHERE `id`=%s """
                await cur.execute(sql, (status.upper(), int(gameID)))
                await conn.commit()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


@bot.command(pass_context=True, name='sayme')
async def sayme(ctx):
    global maintainerOwner
    if ctx.author.id in maintainerOwner:
        try:
            await ctx.send(str(ctx.message.content).replace(".sayme", ""))
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
        return


@bot.command(pass_context=True, name='board', aliases=['b', 'boards'], help=bot_help_board)
async def board(ctx, *args):
    # If private DM, OK pass
    global channelID
    botChan = bot.get_channel(int(channelID))
    if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.id == channelID:
        pass
    else:
        await ctx.channel.send('This command only available via DM or through <#'+str(channelID)+'>')
        return
    GameStart = await Bingo_LastGame()
    em = discord.Embed(title=f'Your Bingo Board: {ctx.author.name}', description='Play Bingo at WrkzCoin Discord #'+'{:,.0f}'.format(GameStart[0])+' Type: ***'+str(GameStart[5])+'***', timestamp=datetime.utcnow(), color=0xDEADBF)
    em.set_author(name='BingoBot', icon_url=bot.user.default_avatar_url)

    if GameStart is None:
        await ctx.send(f'{ctx.author.mention}, There is no game opened yet.')
        return
    if GameStart[2].upper() == 'ONGOING':
        try:
            board = await CheckUserBoard(ctx.author.id, GameStart[0])
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
        if board is None:
            await ctx.send(f'{ctx.author.mention}, Game is already on going. Please wait for a new one.')
            return
        # Let's embed
        em.add_field(name="-", value=f"{15*EMPTY_DISPLAY}\n"+ f"{2*EMPTY_DISPLAY}:regional_indicator_w::regional_indicator_r::regional_indicator_k::regional_indicator_z:{2*EMPTY_DISPLAY}"
            f":regional_indicator_b::regional_indicator_i::regional_indicator_n::regional_indicator_g::regional_indicator_o:{2*EMPTY_DISPLAY}\n" + f"{15*EMPTY_DISPLAY}\n", inline=False)
        LineEm = ''
        LineEm_str = ''
        for (n, i) in enumerate(board):
            # enumerate
            ThisNum = ''
            if str(i).startswith('*'):
                ThisNum = ':white_check_mark::white_check_mark:' + EMPTY_DISPLAY
            elif str(i).startswith('FREE'):
                ThisNum = ':free::free:' + EMPTY_DISPLAY
            else:
                # It is number
                ThisNum = '{:02d}'.format(int(i))
                ThisNum = ThisNum.replace('0',':zero:')
                ThisNum = ThisNum.replace('1',':one:')
                ThisNum = ThisNum.replace('2',':two:')
                ThisNum = ThisNum.replace('3',':three:')
                ThisNum = ThisNum.replace('4',':four:')
                ThisNum = ThisNum.replace('5',':five:')
                ThisNum = ThisNum.replace('6',':six:')
                ThisNum = ThisNum.replace('7',':seven:')
                ThisNum = ThisNum.replace('8',':eight:')
                ThisNum = ThisNum.replace('9',':nine:')
                ThisNum += EMPTY_DISPLAY
            if n >= 0 and (n+1) % 5 != 0:
                LineEm += ThisNum
            elif n > 0 and (n+1) % 5 == 0:
                LineEm += ThisNum
                LineEm_str += LineEm + "\n"
                LineEm_str += 15*EMPTY_DISPLAY + "\n"
                LineEm = ''
        em.add_field(name=f"-", value=LineEm_str, inline=False)
        em.add_field(name="OTHER LINKS", value="{} / {} / {}".format("[Use TipBot?](http://invite.discord.bot.tips)", "[Support Server](https://discord.com/invite/GpHzURM)", "[TipBot Github](https://github.com/wrkzcoin/TipBot)"), inline=False)
        if GameStart[12]:
            em.add_field(name="Remark", value=GameStart[12], inline=False)
        topBlock = await gettopblock()

        em.set_footer(text="Started at height "+str('{:,.0f}'.format(GameStart[1]))+" | Current Height: "+str('{:,.0f}'.format(topBlock['height'])))
        ListActivePlayer = await List_bingo_active_players(GameStart[0])

        if len(ListActivePlayer) < 20:
            try:
                await ctx.send(embed=em)
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
            return
        else:
            if ctx.message.channel.id == channelID:
                try:
                    await ctx.send(f'{ctx.author.mention}, Please check your DM.')
                    await ctx.author.send(embed=em)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
            if isinstance(ctx.message.channel, discord.DMChannel):
                try:
                    await ctx.author.send(embed=em)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
        return
    elif GameStart[2].upper() == 'COMPLETED':
        await ctx.send(f'{ctx.author.mention}, Game is already completed.')
        return
    elif GameStart[2].upper() == 'OPENED':
        # Avoid game still OPENED.
        ListActivePlayer = await List_bingo_active_players(GameStart[0])
        topBlock = await gettopblock()
        RemainHeight = int(GameStart[1]) - int(topBlock['height'])
        # to avoid some bug game hasn't started
        if int(RemainHeight) <= 0:
            # Mentioning people that game start.
            # If number of players is less than three, let's extend 30 more blocks.
            ListMention = ''
            for (i, item) in enumerate(ListActivePlayer):
                ListMention = ListMention + '<@'+str(item[0])+'>'+' '
            if len(ListActivePlayer) >= MIN_PLAYER:
                await Bingo_ChangeStatusGame(GameStart[0], "ONGOING")
                await botChan.send(f'{ListMention}\nGame started. `.board` registration is closed. Good luck!')
                return
            else:
                # Extend
                try:
                    await botChan.send(f'{ListMention}\nGame extends {BLOCK_MIN_PLAYER} '
                                       'blocks for new players.\n'
                                       f'Reward increased by: {INCREASE_REWARD}WRKZ '
                                       f'and played reward by: {INCREASE_PLAYREWARD}WRKZ')
                    await Bingo_Extend(int(GameStart[0]), int(topBlock['height']))
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)

        board = await CheckUser(str(ctx.author.id), ctx.message.author.name, GameStart[0])
        ListActivePlayer = await List_bingo_active_players(GameStart[0])
        board = await CheckUserBoard(ctx.author.id, GameStart[0])
        em.add_field(name="-", value=f"{15*EMPTY_DISPLAY}\n"+ f"{2*EMPTY_DISPLAY}:regional_indicator_w::regional_indicator_r::regional_indicator_k::regional_indicator_z:{2*EMPTY_DISPLAY}"
            f":regional_indicator_b::regional_indicator_i::regional_indicator_n::regional_indicator_g::regional_indicator_o:{2*EMPTY_DISPLAY}\n" + f"{15*EMPTY_DISPLAY}\n", inline=False)
        LineEm = ''
        LineEm_str = ''
        for (n, i) in enumerate(board):
            # enumerate
            ThisNum = None
            if str(i).startswith('*'):
                ThisNum = ':white_check_mark::white_check_mark:'
            elif str(i).startswith('FREE'):
                ThisNum = ':free::free:' + EMPTY_DISPLAY
            else:
                # It is number
                ThisNum = '{:02d}'.format(int(i))
                ThisNum = ThisNum.replace('0',':zero:')
                ThisNum = ThisNum.replace('1',':one:')
                ThisNum = ThisNum.replace('2',':two:')
                ThisNum = ThisNum.replace('3',':three:')
                ThisNum = ThisNum.replace('4',':four:')
                ThisNum = ThisNum.replace('5',':five:')
                ThisNum = ThisNum.replace('6',':six:')
                ThisNum = ThisNum.replace('7',':seven:')
                ThisNum = ThisNum.replace('8',':eight:')
                ThisNum = ThisNum.replace('9',':nine:')
                ThisNum += EMPTY_DISPLAY
            if n >= 0 and (n+1) % 5 != 0:
                LineEm += ThisNum
            elif n > 0 and (n+1) % 5 == 0:
                LineEm += ThisNum
                LineEm_str += LineEm + "\n"
                LineEm_str += 15*EMPTY_DISPLAY + "\n"
                LineEm = ''
        em.add_field(name=f"-", value=LineEm_str, inline=False)
        em.add_field(name="OTHER LINKS", value="{} / {} / {}".format("[Use TipBot?](http://invite.discord.bot.tips)", "[Support Server](https://discord.com/invite/GpHzURM)", "[TipBot Github](https://github.com/wrkzcoin/TipBot)"), inline=False)
        if GameStart[12]:
            em.add_field(name="Remark", value=GameStart[12], inline=False)

        topBlock = await gettopblock()
        em.set_footer(text="Will start at height "+str('{:,.0f}'.format(GameStart[1]))+" | Current Height: "+str('{:,.0f}'.format(topBlock['height'])))

        if len(ListActivePlayer) < 20:
            try:
                await ctx.send(embed=em)
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
            return
        else:
            if isinstance(ctx.message.channel, discord.DMChannel):
                try:
                    await ctx.author.send(embed=em)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
                return
            if ctx.message.channel.id == channelID:
                try:
                    await ctx.send('Please check your DM.')
                    await ctx.author.send(embed=em)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
            return
        return


@bot.command(pass_context=True, name='card', aliases=['c', 'cards'], help=bot_help_card)
async def card(ctx, *args):
    global channelID
    botChan = bot.get_channel(int(channelID))
    # If private DM, OK pass
    if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.id == channelID:
        pass
    else:
        await ctx.send(f'{ctx.author.mention}, This command only available via DM or through <#'+str(channelID)+'>')
        return
    GameStart = await Bingo_LastGame()

    if GameStart is None:
        await ctx.send('There is no game opened yet.')
        return
    if GameStart[2].upper() == 'ONGOING':
        board = await CheckUserBoard(ctx.author.id, GameStart[0])
        if board is None:
            await ctx.send(f'{ctx.author.mention}, Game is already on going. Please wait for a new one.')
            return
        else:
            boardOutput = '`' + boardDump(smallWords(board, 6), 6) + '`'
            if GameStart[12]:
                boardOutput = boardOutput + '\n' + '*Remark*: '+str(GameStart[12])

            ListActivePlayer = await List_bingo_active_players(GameStart[0])
            if len(ListActivePlayer) < 20:
                await ctx.send(str(ctx.message.author.name)+': Your created board for game *#'+str(GameStart[0])+'* TYPE: ***'+str(GameStart[5])+'***\n'+boardOutput)
            else:
                if ctx.message.channel.id == channelID:
                    await ctx.send('Please check your DM.')
                await ctx.author.send('Your created board for game *#'+str(GameStart[0])+'* TYPE: ***'+str(GameStart[5])+'***\n'+boardOutput)
            return
    elif GameStart[2].upper() == 'COMPLETED':
        await ctx.send(f'{ctx.author.mention}, Game is already completed.')
        return
    elif GameStart[2].upper() == 'OPENED':
        # Avoid game still OPENED.
        ListActivePlayer = await List_bingo_active_players(GameStart[0])
        topBlock = await gettopblock()
        RemainHeight = int(GameStart[1]) - int(topBlock['height'])
        # to avoid some bug game hasn't started
        if int(RemainHeight) <= 0:
            # Mentioning people that game start.
            # If number of players is less than three, let's extend 30 more blocks.
            ListMention = ''
            for (i, item) in enumerate(ListActivePlayer):
                ListMention = ListMention + '<@'+str(item[0])+'>'+' '
            if len(ListActivePlayer)>= MIN_PLAYER:
                await Bingo_ChangeStatusGame(GameStart[0], "ONGOING")
                await botChan.send(f'{ListMention}\n Game started. `.board` registration is closed. Good luck!')
                return
            else:
                # Extend
                try:
                    await botChan.send(f'{ListMention}\nGame extends {BLOCK_MIN_PLAYER} '
                                       'blocks for new players.\n'
                                       f'Reward increased by: {INCREASE_REWARD}WRKZ '
                                       f'and played reward by: {INCREASE_PLAYREWARD}WRKZ')
                    await Bingo_Extend(int(GameStart[0]), int(topBlock['height']))
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)

        board = await CheckUser(str(ctx.author.id), ctx.message.author.name, GameStart[0])
        boardOutput = '`' + boardDump(smallWords(board, 6), 6) + '`'
        if GameStart[12]:
            boardOutput = boardOutput + '\n' + '*Remark*: '+str(GameStart[12])
        ListActivePlayer = await List_bingo_active_players(GameStart[0])
        if len(ListActivePlayer) < 20:
            await ctx.send(str(ctx.message.author.name)+': Your board for game #'+str(GameStart[0])+' TYPE: ***'+str(GameStart[5])+'***\n'+boardOutput)
        else:
            if ctx.message.channel.id == channelID:
                await ctx.send('Please check your DM.')
            await ctx.author.send('Your board for game #'+str(GameStart[0])+' TYPE: ***'+str(GameStart[5])+'***\n'+boardOutput)
        return


@bot.command(pass_context=True, name='ball', aliases=['ballz', 'balls'], help=bot_help_balls)
async def ball(ctx, *args):
    global channelID
    botChan = bot.get_channel(int(channelID))
    if isinstance(ctx.channel, discord.DMChannel) == False and ctx.channel.id != channelID:
        await ctx.send(f'{ctx.author.mention}, This command only available via DM or through <#'+str(channelID)+'>')
        return
    ArgQ = (' '.join(args)).split()
    GameStart = await Bingo_LastGame()
    if len(ArgQ) == 1:
        # If there is one argument like .ball height
        try:
            height = int(ArgQ[0])
            ballNum = await Bingo_ShowBallNumber(height)
            await ctx.send(ballNum)
            return
        except ValueError:
            await ctx.send(f'{ctx.author.mention}, Ball height must be integer.')
            return
    else:
        cards = await Bingo_ShowCards(8, GameStart[0])
        if GameStart[2].upper() != 'ONGOING':
            await ctx.send(f'{ctx.author.mention}, Game has not started yet.')
            return	
        if cards:
            cardMsg = ''
            for i in range(len(cards)):
                cardMsg = cardMsg + cards[i] +'\n'
            await ctx.send(str(cardMsg))
            return
        else:
            await ctx.send(f'{ctx.author.mention}, No active ball yet.')
            return


@bot.command(pass_context=True, name='bingo', aliases=['bing'], help=bot_help_bingo)
async def bingo(ctx, *args):
    global maintainerOwner, channelID, BINGO_ALERT_BLOCKS, pool
    botChan = bot.get_channel(int(channelID))
    topBlock = await gettopblock()
    # If private DM, OK pass
    if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.id == channelID:
        pass
    else:
        await ctx.send('This command only available via DM or through <#'+str(channelID)+'>')
        return

    ArgQ = (' '.join(args)).split()
    GameStart = await Bingo_LastGame()
    if len(ArgQ) == 0:
        # If no argument .bingo
        BingoMSG = ''
        if GameStart is None:
            # Tell game is not start
            BingoMSG = 'There is no game started yet. Please ask to start.'
        else:
            PassedBlocks = int(topBlock['height']) - int(GameStart[1])
            # If there is any game.
            ListActivePlayer = await List_bingo_active_players(GameStart[0])
            names = ''
            mentions = ''
            names_kick = ''
            if GameStart[2] == 'ONGOING':
                BingoMSG += 'Game was started at height: `'+str('{:,.0f}'.format(GameStart[1])) +'`\n'
                BingoMSG += 'Type `.bingo lastgame` for result of last game. '
                BingoMSG += 'Game type: `' + str(GameStart[5])+'` with reward: `'+ str('{:,.2f}'.format(GameStart[6]))+'WRKZ`'+' and play reward: `'+ str('{:,.2f}'.format(GameStart[8]))+'WRKZ`'
                if ListActivePlayer:
                    kickedPlayer = 0
                    totalPlayer = 0
                    for (i, item) in enumerate(ListActivePlayer):
                        names += ' ' + item[1]
                        if item[5].upper() != 'YES':
                            mentions += ' ' + '<@' + str(item[0]) + '>'
                        if(item[5]=='YES'):
                            kickedPlayer += 1
                            names_kick = names_kick + ' ' + item[1]
                        totalPlayer += 1
                    BingoMSG += '\n' + 'Current players: `'+str(totalPlayer)+'`. Kicked: `'+ str(kickedPlayer)+'`'
                if PassedBlocks > BINGO_ALERT_BLOCKS:
                    BingoMSG += '\nHello ' + mentions + ' Please check your bingo.'
            elif GameStart[2].upper() == 'COMPLETED':
                BingoMSG += 'Game was completed.\n'
                BingoMSG += 'Please start a new one. Ttype `.bingo lastgame` for result.\n'
            elif GameStart[2].upper() == 'OPENED':
                RemainHeight = int(GameStart[1]) - int(topBlock['height'])
                # to avoid some bug game hasn't started
                if int(RemainHeight) <= 0:
                    # Mentioning people that game start.
                    # If number of players is less than three, let's extend 30 more blocks.
                    ListMention = ''
                    for (i, item) in enumerate(ListActivePlayer):
                        ListMention = ListMention + '<@'+str(item[0])+'>'+' '
                    if len(ListActivePlayer) >= MIN_PLAYER:
                        await Bingo_ChangeStatusGame(GameStart[0], "ONGOING")
                        await botChan.send(f'{ListMention}\nGame started. `.board` registration is closed. Good luck!')
                        return
                    else:
                        # Extend
                        try:
                            await botChan.send(f'{ListMention}\nGame extends {BLOCK_MIN_PLAYER} '
                                               'blocks for new players.\n'
                                               f'Reward increased by: {INCREASE_REWARD}WRKZ '
                                               f'and played reward by: {INCREASE_PLAYREWARD}WRKZ')
                            await Bingo_Extend(int(GameStart[0]), int(topBlock['height']))
                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                BingoMSG += 'Game will start at height: `'+str('{:,.0f}'.format(GameStart[1]))+'`. Remaining `' +str(RemainHeight) +'` block(s) more.\n'
                BingoMSG += 'Game type: `' + str(GameStart[5])+'` with reward: `'+ str('{:,.2f}'.format(GameStart[6]))+'WRKZ`'+' and play reward: `'+ str('{:,.2f}'.format(GameStart[8]))+'WRKZ`'
                if ListActivePlayer:
                    kickedPlayer = 0
                    totalPlayer = 0
                    for (i, item) in enumerate(ListActivePlayer):
                        names = names + ' ' + item[1]
                        if item[5].upper() == 'YES':
                            kickedPlayer += 1
                            names_kick = names_kick + ' ' + item[1]
                        totalPlayer += 1
                    BingoMSG += '\n' + 'Current registered players: `' + str(totalPlayer)+'`'
            if PassedBlocks <= BINGO_ALERT_BLOCKS:
                if len(names) > 0:
                    BingoMSG += '\n' + 'Registered: ' + names
                if len(names_kick) > 0:
                    BingoMSG += '\n' + 'Kicked: ' + names_kick
        await ctx.send(f'{BingoMSG}')
        return
    elif len(ArgQ) == 1 or len(ArgQ) == 2:
        # Check game if started by if there is any date in blocks
        if ArgQ[0].upper() == 'START':
            # OK let's show when it will start or when it was started
            # .bingo start # show when or none
            if GameStart is None:
                await ctx.send(f'{ctx.author.mention}, There is no game started yet. Please ask to start.')
                return
            else:
                if GameStart[2] == 'ONGOING':
                    await ctx.send(f'{ctx.author.mention}, Game was started at height: '+str(GameStart[1]))
                elif GameStart[2] == 'COMPLETED':
                    await ctx.send(f'{ctx.author.mention}, Game was completed. Please start a new one.')
                elif GameStart[2] == 'OPENED':
                    await ctx.send(f'{ctx.author.mention}, Game is still open. Please register using `.board`')
                return
        elif ArgQ[0].upper() == 'REMINDER' or ArgQ[0].upper() == 'REMIND':
            # OK let's OFF and ON
            remindMsg = ''
            try:
                await openConnection()
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        sql = """ SELECT `discord_id`, `discord_name` FROM `bingo_reminder` WHERE `discord_id`=%s """
                        await cur.execute(sql, (str(ctx.author.id)))
                        result = await cur.fetchone()
                        if result is None:
                            # Insert to remind
                            sql = """ INSERT INTO bingo_reminder (`discord_id`, `discord_name`) VALUES (%s, %s) """
                            await cur.execute(sql, (str(ctx.author.id), str(ctx.message.author.name)))
                            await conn.commit()
                            remindMsg = 'You have toggle to get __alert__ from bot when game opened.'
                        else:
                            # Insert to remind
                            sql = """ DELETE FROM bingo_reminder WHERE `discord_id`=%s """
                            await cur.execute(sql, (str(ctx.author.id)))
                            await conn.commit()
                            remindMsg = 'You will __not__ getting an alert from bot when game opened. `.bingo remind` again to enable.'
            except Exception as e:
                traceback.print_exc(file=sys.stdout)

            await ctx.send(f'{remindMsg}')
            return
        elif ArgQ[0].upper() == 'STARTNOW' or ArgQ[0].upper() == 'STARTNEW' or ArgQ[0].upper() == 'NEW':
            if GameStart[2].upper() == 'ONGOING' or GameStart[2].upper() == 'OPENED':
                await ctx.send('Game is already ONGOING or OPENED. Type `.bingo` for more info.')
                return                
            topBlock = await gettopblock()
            bingoStarted = await Bingo_CreateGame(int(topBlock['height'])+BINGO_STARTAT, ctx.author.id, ctx.message.author.name)
            if bingoStarted is None:
                await ctx.send(f'{ctx.author.mention}, Internal error during creating game.')
                return
            elif bingoStarted:
                createdMsg = ['%s is wonderful!', 'Thanks to %s! We all love you', '%s is smart :) Let\'s join', 'Anybody saw? %s just made a new bingo game,', 'Let\'s join bingo with %s', 'Do not make %s upset with this new game.']  # created message array
                userMention = '<@'+str(ctx.author.id)+'>'
                randMessageCreate = str(random.choice(createdMsg)).replace('%s', userMention)
                # let's alert reminding.
                remindMsg = 'Game created. ID: #'+'{:,.0f}'.format(bingoStarted[0])+' at height: '+'{:,.0f}'.format(bingoStarted[1])+'. TYPE: '+bingoStarted[8]+'\n'

                # let's create straightaway to game starter
                board = await CheckUser(str(ctx.author.id), ctx.message.author.name, bingoStarted[0])
                boardOutput = '`' + boardDump(smallWords(board, 6), 6) + '`'
                # let's post his board straightaway

                result = None
                try:
                    await openConnection()
                    async with pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            sql = """ SELECT `discord_id`, `discord_name` FROM `bingo_reminder` """
                            await cur.execute(sql,)
                            result = await cur.fetchall()
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)

                try:
                    if result:
                        for each in result:
                            member = bot.get_user(id=int(each[0]))
                            if member in ctx.guild.members and member.bot == False:
                                # Add mentioned to the list.
                                remindMsg = remindMsg + '<@'+str(each[0])+'> '
                    await botChan.send(remindMsg + '\n\n' + str(ctx.message.author.name)+': Your board for game **#'+'{:,.0f}'.format(bingoStarted[0])+'**\n'+boardOutput+'\n\n'+randMessageCreate)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)

                if result:
                    for each in result:
                        # Add mentioned to the list.
                        user = bot.get_user(id=int(each[0]))
                        try:
                            await user.send('New Bingo Game created. ID: #'+'{:,.0f}'.format(bingoStarted[0]))
                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                return
        elif ArgQ[0].upper() == 'MODE' or ArgQ[0].upper() == 'TYPE':
            # OK let's show when it will start or when it was started
            # .bingo start # show when or none
            if ctx.author.id in maintainerOwner:
                # OK Owner do it
                if len(ArgQ) == 1:
                    await ctx.author.send('You need to input type of game F: FULL HOUSE, L: LINE, D: DIAGONALS, C: FOUR CORNERS, A: ANY. Example: `MODE A`')
                    return
                else:
                    try:
                        gameType = str(ArgQ[1])
                    except ValueError:
                        await ctx.author.send('MODE MUST BE LETTER: F, L, D OR C')
                        return
                    if GameStart[2] == 'ONGOING' or GameStart[2] == 'OPENED':
                        # Change game mode
                        if ArgQ[1].upper() == 'F' or ArgQ[1].upper() == 'FULL':
                            gameType = 'FULL HOUSE'
                        elif ArgQ[1].upper() == 'L' or ArgQ[1].upper() == 'LINE':
                            gameType = 'LINE'
                        elif ArgQ[1].upper() == 'D' or ArgQ[1].upper() == 'DIAGONALS' or ArgQ[1].upper() == 'DIAGONAL':
                            gameType = 'DIAGONALS'
                        elif ArgQ[1].upper() == 'C' or ArgQ[1].upper() == 'CORNERS' or ArgQ[1].upper() == 'CORNER':
                            gameType = 'FOUR CORNERS'
                        elif ArgQ[1].upper() == 'A' or ArgQ[1].upper() == 'ANY':
                            gameType = 'ANY'
                        else:
                            gameType = 'ANY'
                        try:
                            await openConnection()
                            async with pool.acquire() as conn:
                                async with conn.cursor() as cur:
                                    sql = """ UPDATE bingo_gamelist SET `gameType`=%s WHERE `id`=%s """
                                    await cur.execute(sql, (gameType, GameStart[0]))
                                    await conn.commit()
                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)

                        await ctx.author.send('Game type changed to: `'+gameType+'`')
                        return
                    else:
                        await ctx.author.send('Game must be in either ONGOING or OPENED state to use that command.')
                        return
        elif ArgQ[0].upper() == 'REWARD' or ArgQ[0].upper() == 'PRICE':
            # OK let's show when it will start or when it was started
            # .bingo start # show when or none
            if ctx.author.id in maintainerOwner:
                # OK Owner do it
                if len(ArgQ) == 1:
                    await ctx.author.send('You need to input type the reward of this game. ie. `reward 10000`')
                    return
                else:
                    try:
                        RewardPrice = int(ArgQ[1])
                    except ValueError:
                        await ctx.author.send('REWARD MUST BE INTEGER')
                        return
                    if GameStart[2] == 'ONGOING' or GameStart[2] == 'OPENED':
                        if RewardPrice > 100000:
                            await ctx.author.send('Reward price is too big.')
                            return
                        try:
                            await openConnection()
                            async with pool.acquire() as conn:
                                async with conn.cursor() as cur:
                                    sql = """ UPDATE bingo_gamelist SET `reward`=%s WHERE `id`=%s """
                                    await cur.execute(sql, (RewardPrice, GameStart[0]))
                                    await conn.commit()
                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)

                        await ctx.author.send('Game reward changed to: `'+str(RewardPrice)+'`')
                        return
                    else:
                        await ctx.author.send('Game must be in either ONGOING or OPENED state to use that command.')
                        return
        elif ArgQ[0].upper() == 'PLAYREWARD' or ArgQ[0].upper() == 'REWARDPLAY':
            # OK let's show when it will start or when it was started
            # .bingo start # show when or none
            if ctx.author.id in maintainerOwner:
                # OK Owner do it
                if len(ArgQ) == 1:
                    await ctx.author.send('You need to input type the reward of this game. ie. `reward 10000`')
                    return
                else:
                    try:
                        RewardPrice = int(ArgQ[1])
                    except ValueError:
                        await ctx.author.send('REWARD MUST BE INTEGER')
                        return
                    if GameStart[2] == 'ONGOING' or GameStart[2] == 'OPENED':
                        if RewardPrice > 10000:
                            await ctx.author.send('Reward non-win price is too big.')
                            return
                        try:
                            await openConnection()
                            async with pool.acquire() as conn:
                                async with conn.cursor() as cur:
                                    sql = """ UPDATE bingo_gamelist SET `rewardNotWin`=%s WHERE `id`=%s """
                                    await cur.execute(sql, (RewardPrice, GameStart[0]))
                                    await conn.commit()
                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)

                        await ctx.author.send('Game non-win reward changed to: `'+str(RewardPrice)+'`')
                        return
                    else:
                        await ctx.author.send('Game must be in either ONGOING or OPENED state to use that command.')
                        return
        elif ArgQ[0].upper() == 'BINGO':
            # .bingo bingo. Check if user wins
            if GameStart is None:
                await ctx.send(f'{ctx.author.mention}, There is no game started yet. Please ask to start.')
                return
            else:
                if GameStart[2] == 'OPENED':
                    await ctx.send(f'{ctx.author.mention}, Game is still opened for new players.')
                    return
                # Check user card with blocks hash
                elif GameStart[2] == 'COMPLETED':
                    await ctx.send(f'{ctx.author.mention}, Game is completed. Please start a new one.')
                    return
                # Check user card with blocks hash
                elif GameStart[2] == 'ONGOING':
                    board = await CheckUserBoard(ctx.author.id, GameStart[0])
                    # If no board, reply user.
                    if board is None:
                        await ctx.send(f'{ctx.author.mention}, You are late. Game is already ongoing. Please wait for a new one.')
                        return
                    UserBingo = None
                    if str(GameStart[5])=='ANY':
                        # ANY GAME:
                        try:
                            UserBingo1 = await CheckUserBingoType(ctx.author.id, GameStart[0], 'FOUR CORNERS')
                            if str(UserBingo1) == 'FOUR CORNERS':
                                UserBingo = 'ANY'
                            UserBingo2 = await CheckUserBingoType(ctx.author.id, GameStart[0], 'LINE')
                            if str(UserBingo2) == 'LINE':
                                UserBingo = 'ANY'
                            UserBingo3 = await CheckUserBingoType(ctx.author.id, GameStart[0], 'DIAGONALS')
                            if str(UserBingo3) == 'DIAGONALS':
                                UserBingo = 'ANY'
                            UserBingo4 = await CheckUserBingoType(ctx.author.id, GameStart[0], 'FULL HOUSE')
                            if str(UserBingo4) == 'FULL HOUSE':
                                UserBingo = 'ANY'
                        except:
                            pass
                    else:
                        try:
                            UserBingo = await CheckUserBingoType(ctx.author.id, GameStart[0], str(GameStart[5]))
                        except:
                            pass
                if UserBingo is None:
                    await KickUser(ctx.author.id, GameStart[0])
                    await ctx.send(f'{ctx.author.mention}, Did you check? No BINGO yet!! You\'re out from the game now.')
                    await botChan.send(str(ctx.message.author.name)+' was kicked from .bingo in DM.')						
                    return
                else:
                    if str(UserBingo) == str(GameStart[5]):
                        ListMentions = ''
                        # Tip player (not winner)
                        if int(GameStart[8]) > 1:
                            ListActivePlayer = await List_bingo_active_players(GameStart[0])
                            if ListActivePlayer:
                                for (i, item) in enumerate(ListActivePlayer):
                                    if int(item[0]) != ctx.author.id:
                                        ListMentions = ListMentions + '<@'+str(item[0])+'>'+' '
                                rewardNotWin = '.tip '+str(GameStart[8]) + ' ' + ListMentions + 'Thank you for playing.'
                        try:
                            current_Date = datetime.now()
                            topBlock = await gettopblock()
                            await openConnection()
                            async with pool.acquire() as conn:
                                async with conn.cursor() as cur:
                                    sql = """ UPDATE bingo_gamelist SET `status`=%s, `completed_when`=%s, `winner_id`=%s, `winner_name`=%s, `claim_Atheight`=%s WHERE `id`=%s """
                                    await cur.execute(sql, ('COMPLETED', str(current_Date), str(ctx.author.id), str(ctx.message.author.name), str(topBlock['height']), str(GameStart[0])))
                                    await conn.commit()
                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)

                        try:
                            await openConnection()
                            async with pool.acquire() as conn:
                                async with conn.cursor() as cur:
                                    sql = """ INSERT INTO bingo_active_players_archive SELECT * FROM bingo_active_players; """
                                    await cur.execute(sql,)
                                    await conn.commit()
                                    sql = """ INSERT INTO bingo_active_blocks_archive SELECT * FROM bingo_active_blocks; """
                                    await cur.execute(sql,)
                                    await conn.commit()
                                    sql = """ TRUNCATE TABLE bingo_active_players; """
                                    await cur.execute(sql,)
                                    await conn.commit()
                                    sql = """ TRUNCATE TABLE bingo_active_blocks; """
                                    await cur.execute(sql,)
                                    await conn.commit()
                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)

                        winMsg = 'You win. Bingo! Please wait to start new game.\nWinner is: <@'+str(ctx.author.id)+'>'
                        await botChan.send(f'{winMsg}')
                        def check(reaction, user):
                            return reaction.message.channel.id == channelID and user.id == TIPBOTID and str(reaction.emoji) in LIST_TIPREACT and reaction.message.author == bot.user
                        if int(GameStart[6]) > 1:
                            winMsg = '.tip '+str(GameStart[6])+' '+'<@'+str(ctx.author.id)+'> You win. Bingo! Please wait to start new game.'
                            await botChan.send(f'{winMsg}')                        
                        if rewardNotWin:
                            await botChan.send(f'{rewardNotWin}')
                        return
                    else:
                        await KickUser(ctx.author.id, GameStart[0])
                        await botChan.send('<@'+str(ctx.author.id)+'>! Did you check? No BINGO yet!! You\'re out from the game now.')
                        return
        elif ArgQ[0].upper() == 'BALL':  
            # .bingo card. Check last ball
            if GameStart is None:
                await ctx.send(f'{ctx.author.mention}, There is no game started yet. Please ask to start.')
                return
            else:
                # show last card numbers
                if GameStart[2] != 'ONGOING':
                    await ctx.send(f'{ctx.author.mention}, Game not started yet. It is sill opened for new players.')
                    return
                cards = await Bingo_ShowCards(1, GameStart[0])
                if cards:
                    cardMsg = ''
                    for i in range(len(cards)):
                        cardMsg = cardMsg + cards[i] +'\n'
                    if cardMsg:
                        await ctx.send(f'{cardMsg}')
                        return
                    else:
                        await ctx.send(f'{ctx.author.mention}, No active ball yet.')
                        return
                else:
                    await ctx.send(f'{ctx.author.mention}, No active ball yet.')
                    return
        elif ArgQ[0].upper() == 'BALLS':  
            # .bingo card. Check last card
            if GameStart is None:
                await ctx.send(f'{ctx.author.mention}, There is no game started yet. Please ask to start.')
                return
            else:
                # show last FIVE card numbers
                if GameStart[2].upper() != 'ONGOING':
                    await ctx.send(f'{ctx.author.mention}, Game not started yet. It is sill opened for new players.')
                    return
                cards = await Bingo_ShowCards(10, GameStart[0])
                if cards:
                    cardMsg = ''
                    for i in range(len(cards)):
                        cardMsg = cardMsg + cards[i] + '\n'
                    if cardMsg:
                        await ctx.author.send(f'{cardMsg}')
                        return
                    else:
                        await ctx.send(f'{ctx.author.mention}, No active ball yet.')
                        return
                else:
                    await ctx.send(f'{ctx.author.mention}, No active ball(s) yet.')
                    return
        elif ArgQ[0].upper() == 'LASTGAME' or ArgQ[0].upper() == 'LAST':  
            # .bingo lastgame. show last game result
            LastGameRes = await Bingo_LastGameResult()
            if LastGameRes is None:
                await ctx.send(f'{ctx.author.mention}, There is no last game result yet.')
                return
            else:
                # show last card numbers
                whenWin = datetime.strptime(LastGameRes[3].split(".")[0], '%Y-%m-%d %H:%M:%S')
                ago = timeago.format(whenWin, datetime.now())

                LastGameMsg = ''
                LastGameMsg = '**Last game #'+'{:,.0f}'.format(LastGameRes[0])+'**\n'
                LastGameMsg += '__Started block__: '+'{:,.0f}'.format(LastGameRes[1])+', Claimed to win block: '+'{:,.0f}'.format(LastGameRes[6])+'\n'
                LastGameMsg += '__Winner was__: <@'+LastGameRes[4]+'>\n'
                LastGameMsg += '__When__: '+str(ago) + '. Game type:`'+str(LastGameRes[7])+'`'
                await ctx.send(str(LastGameMsg))
                return
        elif ArgQ[0].upper() == 'LASTGAMES':  
            # .bingo lastgame. show last game result
            LastGameRes = await Bingo_LastGameResultList()
            if LastGameRes is None:
                await ctx.send(f'{ctx.author.mention}, There is no last game result yet.')
                return
            else:
                LastGameMsg = ''
                # show last card numbers
                for n, msg in enumerate(LastGameRes):
                    # Show:
                    whenWin = datetime.strptime(msg[3].split(".")[0], '%Y-%m-%d %H:%M:%S')
                    ago = timeago.format(whenWin, datetime.now())
                    LastGameMsg += '**Last game #'+'{:,.0f}'.format(msg[0])+'**\n'
                    LastGameMsg += '__Started block__: '+'{:,.0f}'.format(msg[1])+', Claimed to win block: '+'{:,.0f}'.format(msg[6])+'\n'
                    LastGameMsg += '__Winner was__: `'+msg[5]+'`\n'
                    LastGameMsg += '__When__: '+str(ago) + '. Game type:`'+str(msg[7]) + '`\n\n'
                await ctx.send(str(LastGameMsg))
                return
        elif ArgQ[0].upper() == 'RESTART' or ArgQ[0].upper() == 'RELOAD':
            # Check permission
            if ctx.author.id in maintainerOwner:
                await ctx.author.send('Bot is rebooting...')
                await asyncio.sleep(2)
                sys.exit(0)
            else:
                await ctx.author.send('Access denied...')
            return
        elif ArgQ[0].upper() == 'END' and (ctx.author.id in maintainerOwner):
            # let's end the game and let BingoBot win
            if GameStart is None:
                await ctx.send(f'{ctx.author.mention}, There is no game started yet. Please ask to start.')
                return
            else:
                if GameStart[2] == 'ONGOING':
                    # OK game is ONGOING, let's END
                    ListMentions = ''
                    # Tip player (not winner)
                    if int(GameStart[8]) > 1:
                        ListActivePlayer = await List_bingo_active_players(GameStart[0])
                        if ListActivePlayer:
                            for (i, item) in enumerate(ListActivePlayer):
                                if int(item[0]) != bot.user.id:
                                    ListMentions = ListMentions + '<@'+str(item[0])+'>'+' '
                            rewardNotWin = '.tip '+str(GameStart[8]) + ' ' + ListMentions + 'Thank you for playing.'
                    try:
                        current_Date = datetime.now()
                        topBlock = await gettopblock()
                        await openConnection()
                        async with pool.acquire() as conn:
                            async with conn.cursor() as cur:
                                sql = """ UPDATE bingo_gamelist SET `status`=%s, `completed_when`=%s, `winner_id`=%s, `winner_name`=%s, `claim_Atheight`=%s WHERE `id`=%s """
                                await cur.execute(sql, ('COMPLETED', str(current_Date), str(bot.user.id), str(bot.user.name), str(topBlock['height']), str(GameStart[0])))
                                await conn.commit()
                    except Exception as e:
                        traceback.print_exc(file=sys.stdout)
                    try:
                        await openConnection()
                        async with pool.acquire() as conn:
                            async with conn.cursor() as cur:
                                sql = """ INSERT INTO bingo_active_players_archive SELECT * FROM bingo_active_players; """
                                await cur.execute(sql,)
                                await conn.commit()
                                sql = """ INSERT INTO bingo_active_blocks_archive SELECT * FROM bingo_active_blocks; """
                                await cur.execute(sql,)
                                await conn.commit()
                                sql = """ TRUNCATE TABLE bingo_active_players; """
                                await cur.execute(sql,)
                                await conn.commit()
                                sql = """ TRUNCATE TABLE bingo_active_blocks; """
                                await cur.execute(sql,)
                                await conn.commit()
                    except Exception as e:
                        traceback.print_exc(file=sys.stdout)

                    winMsg = '**Game Over**. Winner is: <@'+str(bot.user.id)+'>'
                    await botChan.send(f'{winMsg}')

                    if rewardNotWin:
                        await botChan.send(f'{rewardNotWin}')
                    return
                elif GameStart[2] == 'COMPLETED':
                    await ctx.send(f'{ctx.author.mention}, Game was completed. Please start a new one.')
                    return
                elif GameStart[2] == 'OPENED':
                    await ctx.send(f'{ctx.author.mention}, Game is still open. Please register using `.board`')
                    return


# Breaks each entry in the input list into chunks. Returns a list 
# of list chunks
def smallWords(bingoList, chunkSize):
    for index, var in enumerate(bingoList):
        temp = textwrap.wrap(var, chunkSize)
        while len(temp) < 3:
            temp.append(" ")
        bingoList[index] = temp
    return bingoList


def boardDump(bingoList, width):
    Output = ''
    Output = Output + str("=" * (6 + (width * 5)))+ '\n'
    Output = Output + str("|" + "B".center(width) + "|" + "I".center(width) + "|" + \
            "N".center(width) + "|" + "G".center(width) + "|" + \
            "O".center(width) + "|")+'\n'
    Output = Output + str("=" * (6 + (width * 5)))+ '\n'
    for i in range(0,5):
        for j in range(0,2):
            Output = Output + str("|" + bingoList[i*5][j].center(width) + "|" + \
                    bingoList[(i*5)+1][j].center(width) + "|" + \
                    bingoList[(i*5)+2][j].center(width) + "|" + \
                    bingoList[(i*5)+3][j].center(width) + "|" + \
                    bingoList[(i*5)+4][j].center(width) + "|") + '\n'
        Output = Output + str("=" * (6 + (width * 5))) + '\n'
    return Output


async def gettopblock():
    global pool_chain
    try:
        await openConnectionBlockchain()
        async with pool_chain.acquire() as connBlockchain:
            async with connBlockchain.cursor() as curBlockchain:
                sql = """ SELECT `height`, `hash` FROM blocks ORDER BY height DESC LIMIT 1 """
                await curBlockchain.execute(sql,)
                row = await curBlockchain.fetchone()
                return row
    except Exception as e:
        traceback.print_exc(file=sys.stdout)


# Sum of all digits 0 to 9 in a string and return numbers:
#
# print(sumOfDigits('1c2aa8e1ab52959410c4f2e51260e2a2dfe0a9394351f80c06270d3bf3f8a50c'))=>147
# print(sumOfDigits('e6d6c5724428f633a6a70f22608e004ed66046504ad6fa5ec1c6a7689aba7da3'))=>180
# print(sumOfDigits('c7c293953fb6e90aae9e90ea27a8e3796cdb23c077cf25b77dbeb1937e169669'))=>210


def sumOfDigits(sentence):
    sumof = 0
    for x in sentence:
        if x.isdigit() == True:
            sumof += int(x)
    return sumof


async def show_msgCard():
    global channelID, pool
    botChan = bot.get_channel(id=int(channelID))
    GameStart = await Bingo_LastGame()
    SomeTips = ['You can use `.board` only during game OPENED and ONGOING (if you register one).', 'To register during game opening, use `.board`', 'Please also check pinned messages for updates.', 'I am giving reward through TipBot. Tip me some Wrkz for every winner :)'] # new list

    # Add some remind list who is online but not play
    if GameStart[2].upper()=='OPENED':
        SomeTips.append('Eat, sleep, and play bingo <#524572420468899860>')
        SomeTips.append('Chicks dig guys with big numbers on their balls.')
        SomeTips.append('Don\'t drive me crazy, drive me to bingo!')
        SomeTips.append('Born to yell BINGO!')
        SomeTips.append('I only play bingo on days that end in Y.')
        SomeTips.append('Keep Grandma off the streets. Take her to bingo.')
        SomeTips.append('If there\'s no bingo in heaven I\'m not going.')
        SomeTips.append('It takes balls to yell bingo.')
        SomeTips.append('A simple `.board` can have you in bingo :) ')
        # reminderListIds = [] ## List reminder
        ListActivePlayer = await List_bingo_active_players(GameStart[0])
        playerIDs = [] # list ID
        for player in ListActivePlayer:
            playerIDs.append(int(player[0]))
        try:
            await openConnection()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    sql = """ SELECT `discord_id`, `discord_name` FROM `bingo_reminder` """
                    await cur.execute(sql,)
                    result = await cur.fetchall()
                    if result:
                        for row in result:
                            # If they are online
                            # reminderListIds.append(int(row[0]))
                            # Check if user in the guild
                            try:
                                member = bot.get_user(int(row[0]))
                                if member and int(row[0]) not in playerIDs:
                                    SomeTips.append('Do you want to play bingo? <@'+str(row[0])+'>. It is not late yet.  `.bingo remind` If you want me to stop this ping.')
                            except Exception as e:
                                traceback.print_exc(file=sys.stdout)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
    elif GameStart[2].upper() == 'COMPLETED':
        SomeTips.append('Eat, sleep, and play bingo <#524572420468899860>. Why nobody interests to start a new game?')
        SomeTips.append('Don\'t drive me crazy, drive me to `.bingo new`')
        SomeTips.append('Keep Grandma off the streets take her to type `.bingo new`.')
        SomeTips.append('Eat, sleep, and play bingo <#524572420468899860>')
        SomeTips.append('If I could use keyboard, I would `.bingo new`')
        SomeTips.append('I doubt if everybody is sleeping now.')
        SomeTips.append('I broke my phone screen and I can\'t start any bingo :( ') 
        SomeTips.append('After I wake up, I need to see who is the winner.')
        SomeTips.append('Game completed? Anyone can start a new one by `.bingo startnew`')
    elif GameStart[2].upper() == 'ONGOING':
        SomeTips.append('Check your bingo board in gameplay, use `.board`')
        SomeTips.append('Check last ball or last five balls, use `.bingo ball` or `.bingo balls`')
        SomeTips.append('If you have all numbers with **, win it by `.bingo bingo`. If you do this wrongly, you will be kicked out from the current game.')
        SomeTips.append('Got kicked? OK, wait for next :) ')
        SomeTips.append('We know the winner only they type `.bingo bingo`')
        SomeTips.append('Don\'t wait to win. I will not tell you until you `.bingo bingo`')
        SomeTips.append('What do you want me more than bingo?')
        SomeTips.append('Haha... too quiet? Check `.board` You can be the next winner')
        SomeTips.append('Too late? Game already started? Let me remind you :) `.bingo remind` If I call you and no respond, it is your problem.')
        SomeTips.append('Don\'t be too lazy. I always respond for any `.bingo`')
        SomeTips.append('I always respond for any `.board`. Don\'t be too lazy')
    randMessageTo = random.choice(SomeTips)
    if GameStart is None:
        # Show some game when it hasn't started. There is no game
        await botChan.send(f'{randMessageTo}.')
    else:
        # Show some game when it hasn't started. Game is opened, ongoing
        if GameStart[2].upper() == 'OPENED' or GameStart[2].upper()=='COMPLETED':
            await botChan.send(f'{randMessageTo}.')
        elif GameStart[2].upper() == 'ONGOING':
            if random.randint(0, 9)<= 4:
                await botChan.send(f'{randMessageTo}.')
            else:
                cards = await Bingo_ShowCards(3, GameStart[0])
                if cards:
                    cardMsg = ''
                    for i in range(len(cards)):
                        cardMsg = cardMsg + cards[i] + '\n'
                    if cardMsg.strip() != "":
                        try:
                            await botChan.send(f'{cardMsg}')
                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)


async def show_checkOpenedGame():
    global channelID, remindedStart, remindedBlock, pool
    botChan = bot.get_channel(int(channelID))
    GameStart = await Bingo_LastGame()
    # Insert only if game is start
    if GameStart:
        ListActivePlayer = await List_bingo_active_players(GameStart[0])
        topBlock = await gettopblock()
        if GameStart[2].upper() == 'OPENED':
            if int(GameStart[1]) <= int(topBlock['height']):
                # Mentioning people that game start.
                # If number of players is less than three, let's extend 30 more blocks.
                ListMention = ''
                for (i, item) in enumerate(ListActivePlayer):
                    ListMention = ListMention + '<@'+str(item[0])+'>'+' '
                if len(ListActivePlayer)>= MIN_PLAYER:
                    await Bingo_ChangeStatusGame(GameStart[0], "ONGOING")
                    await botChan.send(f'{ListMention}\nGame started. `.board` registration is closed. Good luck!')
                    return
                else:
                    # Alert to players that we extend:
                    try:
                        await botChan.send(f'{ListMention}\nGame extends {BLOCK_MIN_PLAYER} blocks for new players.\n'
                                           f'Reward increased by: {INCREASE_REWARD}WRKZ and played reward by: {INCREASE_PLAYREWARD}WRKZ.')
                        await Bingo_Extend(int(GameStart[0]), int(topBlock['height']))
                    except Exception as e:
                        traceback.print_exc(file=sys.stdout)
            else:
                # if can remind
                RemainHeight = int(GameStart[1]) - int(topBlock['height'])
                if RemainHeight % 10 == 0 and remindedStart == 0 and remindedBlock != (int(topBlock['height'])):
                    botChan = bot.get_channel(int(channelID))
                    await botChan.send(f'***{RemainHeight}*** blocks more before game starts.')
                    remindedStart = 1
                    remindedBlock = int(topBlock['height'])
                else:
                    remindedStart = 0
        elif GameStart[2].upper() == 'ONGOING':
            # If player just only one. Let him win
            if len(ListActivePlayer) == 1:
                for (i, item) in enumerate(ListActivePlayer):
                    winner_id = item[0]
                    winner_name = item[1]
                try:
                    current_Date = datetime.now()
                    topBlock = await gettopblock()
                    await openConnection()
                    async with pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            sql = """ UPDATE bingo_gamelist SET `status`=%s, `completed_when`=%s, `winner_id`=%s, `winner_name`=%s, 
                                      `claim_Atheight`=%s WHERE `id`=%s """
                            await cur.execute(sql, ('COMPLETED', str(current_Date), str(winner_id), str(winner_name), str(topBlock['height']), str(GameStart[0])))
                            await conn.commit()
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
                try:
                    await openConnection()
                    async with pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            sql = """ INSERT INTO bingo_active_players_archive SELECT * FROM bingo_active_players; """
                            await cur.execute(sql,)
                            await conn.commit()
                            sql = """ INSERT INTO bingo_active_blocks_archive SELECT * FROM bingo_active_blocks; """
                            await cur.execute(sql,)
                            await conn.commit()
                            sql = """ TRUNCATE TABLE bingo_active_players; """
                            await cur.execute(sql,)
                            await conn.commit()
                            sql = """ TRUNCATE TABLE bingo_active_blocks; """
                            await cur.execute(sql,)
                            await conn.commit()
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
                winMsg = '<@'+str(winner_id)+'> wins the game alone.'
                if int(GameStart[6]) > 1:
                    winMsg = '.tip '+str(GameStart[6])+' '+'<@'+str(winner_id)+'> Please wait to start new game.'
                botChan = bot.get_channel(int(channelID))
                botChan.send(f'{winMsg}')
        elif GameStart[2].upper() == 'COMPLETED' or GameStart[2].upper() == 'SUSPENDED':
            pass


@bot.event
async def on_command_error(error, _: commands.Context):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.author.send(_.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await ctx.author.send(_.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.MissingRequiredArgument):
        pass
    elif isinstance(error, commands.CommandNotFound):
        pass


async def checkOpenedGame():
    await asyncio.sleep(5)
    while True:
        try:
            await asyncio.sleep(5)  # 5 second before doing anything. Especially sending message to server
            await show_checkOpenedGame()
            await asyncio.sleep(5)  # sleep 5 seconds
        except Exception as e:
            traceback.print_exc(file=sys.stdout)


async def show_randomMsg():
    await asyncio.sleep(5)
    while True:
        await asyncio.sleep(5)  # 5 second before doing anything
        try:
            await show_msgCard()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
        await asyncio.sleep(120)  # sleep 3mn


@click.command()
def main():
    bot.loop.create_task(checkOpenedGame())
    bot.loop.create_task(show_randomMsg())
    bot.run(token)


if __name__ == '__main__':
    main()

