#!/usr/bin/env python3.6
## ./bingo.py
## Github:   https://github.com/wrkzdev/BingoBot-Discord
## Author:   CapEtn (Discord ID: 386761001808166912)
## Donation:
## Wrkz: WrkzRNDQDwFCBynKPc459v3LDa1gEGzG3j962tMUBko1fw9xgdaS9mNiGMgA9s1q7hS1Z8SGRVWzcGc8Sh8xsvfZ6u2wJEtoZB
## TRTL: TRTLv2k5RgwQkcXsZpue9ELGq49PEQbgZ7sAncv82GqTc3rehKqRLM7jomrji4zek76hWiYkKKizQFfny1TvvcvyBxqnvcsTfKi
## Dego: dg4nUdJyHV1ZCrYV7kHvTE9HkKT9ynKCW1Antm1ku8ihhsN1PkiH2fFfwsGt2y7UsN3rALr4gg8oz87vpxjaVF8g1uUWKH7pE

## This Bot requires to have blockchain in MySQL. Please see:
## https://github.com/TurtlePay/blockchain-data-collection-agent
## And https://github.com/TurtlePay/blockchain-cache-api
## Without that, you need to customized it on your own.
##
## Portion of board generator is from: https://github.com/jetpacktuxedo/bingo

import asyncio
import click
import discord
from discord.ext import commands
from discord.utils import get
import requests, json
import json

import sys, os, random, textwrap
import time, timeago
from datetime import datetime

# MySQL
import pymysql
conn = None
connBlockchain = None

## remind every for counting game start
remindedStart = 0
remindedBlock = 0

# CapEtn: 386761001808166912
maintainerOwner = [ 386761001808166912 ] ## list owner
## TipBot to listen on reaction
TipBotID = 474841349968101386

EMOJI_ERROR = "\u274C"
# Bot Token ID
## BOT ID: 485353052107440145
token = 'BotTokenHere'
## ChannelID where BingoBot Game is running
channelID = 524572420468899860
## Invite Bot
# https://discordapp.com/oauth2/authorize?client_id=BOT_ID_HERE&scope=bot

mysqlGame = [] ## MySQL information for storing game data
mysqlGame['server'] = 'localhost'
mysqlGame['username'] = 'dbusername'
mysqlGame['db'] = 'dbname'
mysqlGame['password'] = 'yourpassword'

mysqlBlockchain = [] ## MySQL information for blockchain
mysqlBlockchain['server'] = 'localhost'
mysqlBlockchain['username'] = 'blockchain'
mysqlBlockchain['db'] = 'blockchain'
mysqlBlockchain['password'] = 'yourpassword'

bot_description = "Discord Bingo Game with WrkzCoin hash"
bot_help_board = "Create or show your bingo board"
bot_help_bingo = "Certain command with bingo"
bot_help_balls = "Show last few ball numbers"

## Call for topblock URL. You can customize this to something else without blockchain-cache-api
TopBlockCall = "http://127.0.0.1:1270/block/header/top"

bot = commands.Bot(case_insensitive=True, command_prefix='.', pm_help=True)

@bot.event
async def on_ready():
    print('Ready!')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    print('Servers connected to:')
    for server in bot.servers:
        print(server.name)

@bot.event
async def on_reaction_add(reaction, user):
    global channelID, TipBotID
    """The on_message event handler for this module

    Args:
        reaction (discord.Reaction): Input reaction
        user (discord.User): The user that added the reaction
    """

    # Simplify reaction info
    server = reaction.message.server
    emoji = reaction.emoji
    if user != reaction.message.channel.server.me:
        print('watching reaction')
        if(int(user.id) == TipBotID and (bot.user in reaction.message.mentions)):
            ## OK there is me
            ## Change the name of emoji to what tipbot React
            emoji = get(bot.get_all_emojis(), name='WRKZFront')
            if (int(reaction.message.channel.id) == channelID and reaction.emoji == emoji):
                ## OK in bingo channel
                TipThanksMsg = ['Thank you a lot %s!', '%s is kind :)', 'I like %s :) Thank you', 'It is very kind of you, %s'] ## created message array
                TipThanksMsg.append('Thank you %s')
                userMention = '<@'+str(reaction.message.author.id)+'>'
                randMessageTip = str(random.choice(TipThanksMsg)).replace('%s', userMention)
                await bot.send_message(discord.Object(id=channelID),
                    f'{randMessageTip}')
                return
            ## If tipbot react with X or any Error
            if (int(reaction.message.channel.id) == channelID and reaction.emoji == EMOJI_ERROR):
                ## OK in bingo channel
                TipThanksMsg = ['No problem %s!', '%s :) merci quand même', 'Thank you %s ;) '] ## created message array
                userMention = '<@'+str(reaction.message.author.id)+'>'
                randMessageTip = str(random.choice(TipThanksMsg)).replace('%s', userMention)
                await bot.send_message(discord.Object(id=channelID),
                    f'{randMessageTip}')
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

def openConnection():
    global conn, mysqlGame
    try:
        if(conn is None):
            conn = pymysql.connect(mysqlGame['server'], user=mysqlGame['username'], passwd=mysqlGame['password'], db=mysqlGame['db'], connect_timeout=5)
        elif (not conn.open):
            conn = pymysql.connect(mysqlGame['server'], user=mysqlGame['username'], passwd=mysqlGame['password'], db=mysqlGame['db'], connect_timeout=5)
    except:
        print("ERROR: Unexpected error: Could not connect to MySql bingogame instance.")
        sys.exit()

def openConnectionBlockchain():
    global connBlockchain, mysqlBlockchain
    try:
        if(connBlockchain is None):
            conn = pymysql.connect(mysqlBlockchain['server'], user=mysqlBlockchain['username'], passwd=mysqlBlockchain['password'], db=mysqlBlockchain['db'], connect_timeout=5)
        elif (not connBlockchain.open):
            conn = pymysql.connect(mysqlBlockchain['server'], user=mysqlBlockchain['username'], passwd=mysqlBlockchain['password'], db=mysqlBlockchain['db'], connect_timeout=5)  
    except:
        print("ERROR: Unexpected error: Could not connect to MySql blockchain instance.")
        sys.exit()

def CheckUser(userID, userName, GameID):
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT started, board_json, board_jsonStar, kicked, kicked_when, gameID FROM `bingo_active_players` WHERE `discord_id`=%s AND `gameID`=%s LIMIT 1"
            cur.execute(sql, (userID, GameID))
            result = cur.fetchone()
            if (result is None):
                # Insert
                board = generateBoard()
                boardJson = json.dumps(board)
                current_Date = datetime.now()
                sql = "INSERT INTO bingo_active_players (`discord_id`, `discord_name`, `started`, `board_json`, `board_jsonStar`, `GameID`) VALUES (%s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (str(userID), str(userName), current_Date, boardJson, boardJson, GameID))
                conn.commit()
                return board
            else:
                # Show data
                return json.loads(result[1])
            cur.close() 
    except Exception as e:
        print(e)
    finally:
        conn.close()

def CheckUserBoard(userID, gameID):
    GameStart = Bingo_LastGame()
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT started, board_json, board_jsonStar, kicked, kicked_when, gameID FROM `bingo_active_players` WHERE `discord_id`=%s AND `gameID`=%s AND `kicked`='NO' LIMIT 1"
            cur.execute(sql, (userID, gameID))
            result = cur.fetchone()
            if (result is None):
                return None
            else:
                # Show data
                ## Start connection to blockchain
                ListChain = [] ## For unique list of numbers
                try:
                    openConnectionBlockchain()
                    with connBlockchain.cursor() as curBlockchain:
                        sql = "SELECT `height`, `hash`, `difficulty`,`timestamp` from blocks where height > %s ORDER BY height DESC  LIMIT 10000"
                        curBlockchain.execute(sql, (GameStart[1]))
                        rows = curBlockchain.fetchall()
                        for row in rows:
                            sum_75 = int(sumOfDigits(str(row[1])) % 75) + 1
                            if (sum_75 not in ListChain):
                                ListChain.append(sum_75)
                except Exception as e:
                    print(e)
                finally:
                    connBlockchain.close()
                ## End connection to blockchain
                k = 0
                UserBingoList = json.loads(result[1])
                for row in ListChain:
                    for n, i in enumerate(UserBingoList):
                        if str(i) == str(row):
                            print('Hash matches: '+ str(row)+'== Total k:'+str(k))
                            k += 1
                            UserBingoList[n] = '*'+str(row)+'*'
                return UserBingoList
            cur.close() 
    except Exception as e:
        print(e)
    finally:
        conn.close()

def CheckUserBingoType(userID, gameID, Type):
    GameStart = Bingo_LastGame()
    if (GameStart[2] == 'COMPLETED'):
        return None
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT started, board_json, board_jsonStar, kicked, kicked_when, gameID FROM `bingo_active_players` WHERE `discord_id`=%s AND `gameID`=%s AND `kicked`='NO' LIMIT 1"
            cur.execute(sql, (userID, gameID))
            result = cur.fetchone()
            if (result is None):
                return None
            else:
                # Select data from blockchain
                try:
                    openConnectionBlockchain()
                    with connBlockchain.cursor() as curBlockchain:
                        sql = "SELECT `height`, `hash`, `difficulty`,`timestamp` from blocks WHERE height > %s ORDER BY height DESC  LIMIT 10000"
                        curBlockchain.execute(sql, (GameStart[1]))
                        rows = curBlockchain.fetchall()
                        ListChain = [] ## For unique list of numbers
                        for row in rows:
                            sum_75 = int(sumOfDigits(str(row[1])) % 75) + 1
                            if (sum_75 not in ListChain):
                                ListChain.append(sum_75)
                except Exception as e:
                    print(e)
                finally:
                    connBlockchain.close()
                ## End of select from wrkz_blockchain
                if (Type == 'FOUR CORNERS'):
                    #FOUR CORNERS, four numbers at corner to win
                    number_list = []
                    k = 0
                    UserBingoList = json.loads(result[1])
                    number_list.extend([UserBingoList[0], UserBingoList[4], UserBingoList[20], UserBingoList[24]])
                    j = 0
                    for row in ListChain:
                        for (n, i) in enumerate(number_list):
                            if str(i) == str(row):
                                k += 1
                    if (k==4):
                        return Type
                    else:
                        return k
                elif (Type == 'LINE'):
                    #LINE: a single line can win either diagonal
                    k = 0
                    UserBingoList = json.loads(result[1])
                    z = 0
                    ## Horizontal
                    while z < 5:
                        m = 0
                        number_list = []
                        if (z != 2):
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
                    ## Vertical
                    z = 0
                    while z < 5:
                        m = 0
                        number_list = []
                        if (z != 2):
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
                    ## Diagonal 1
                    m = 0
                    number_list = []
                    number_list.extend([UserBingoList[0], UserBingoList[6], UserBingoList[18], UserBingoList[24]])
                    for row in ListChain:
                        for (n, i) in enumerate(number_list):
                            if str(i) == str(row):
                                m += 1
                    # If matches 4 numbers, add k+
                    if(m==4):
                        k += 1
                    m = 0 # reset m to 0
                    ## Diagonal 2
                    number_list = []
                    number_list.extend([UserBingoList[4], UserBingoList[8], UserBingoList[16], UserBingoList[20]])
                    for row in ListChain:
                        for (n, i) in enumerate(number_list):
                            if str(i) == str(row):
                                m += 1
                    # If matches 4 numbers, add k+
                    if(m==4):
                        k += 1
                    if (k>=1):
                        #print(k) ## this will return number of straight line vertical or horizontal
                        return Type
                    else:
                        return k
                elif (Type == 'DIAGONALS'):
                    #DIAGONALS: X lines 0, 4, 6, 8, 16,18 , 20, 24
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
                    if (k==8):
                        return Type
                    else:
                        return k
                elif (Type == 'FULL HOUSE'):
                    #FULL HOUSE: all numbers in
                    k = 0
                    UserBingoList = json.loads(result[1])
                    for row in ListChain:
                        for n, i in enumerate(UserBingoList):
                            if str(i) == str(row):
                                k += 1
                    if (k>=24):
                        return Type
                    else:
                        return k
            cur.close() 
    except Exception as e:
        print(e)
    finally:
        conn.close()

def KickUser(userID, GameID):
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT started, board_json, board_jsonStar, kicked, kicked_when, gameID FROM `bingo_active_players` WHERE `discord_id`=%s AND `gameID`=%s LIMIT 1"
            cur.execute(sql, (userID, GameID))
            result = cur.fetchone()
            if (result is not None):
                try:
                    current_Date = datetime.now()
                    openConnection()
                    with conn.cursor() as cur:
                        sql = "UPDATE bingo_active_players SET `kicked`=%s,`kicked_when`=%s WHERE `discord_id`=%s AND `gameID`=%s"
                        cur.execute(sql, ('YES', str(current_Date), str(userID), str(GameID)))
                        conn.commit()
                except Exception as e:
                    print(e) 
    except Exception as e:
        print(e)
    finally:
        conn.close()

def List_bingo_active_players(GameID):
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT discord_id, discord_name, started, board_json, board_jsonStar, kicked, kicked_when, gameID FROM `bingo_active_players` WHERE `gameID`=%s"
            cur.execute(sql, (GameID))
            result = cur.fetchall()
            if (result is None):
                return None
            else:
                 return result
    except Exception as e:
        print(e)
    finally:
        conn.close()

def Bingo_CreateGame(startedBlock, discord_id, discord_name):
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT id, startedBlock, status, completed_when, winner_id, creator_discord_id, creator_discord_name, created_when FROM `bingo_gamelist` WHERE status!='COMPLETED' LIMIT 1"
            cur.execute(sql,)
            result = cur.fetchone()
            if (result is None):
                #Let's insert starting block info
                print('OK, there is none in game list.')
                current_Date = datetime.now()
                #Get topBlock
                topBlock = gettopblock()
                if ((startedBlock - 60) <= topBlock['height']):
                    ## less than 1 hours or 120 blocks from started
                    return None
                else:
                    #If bigger than 1 hours
                    sql = "INSERT INTO bingo_gamelist (`startedBlock`, `status`, `creator_discord_id`, `creator_discord_name`, created_when) VALUES (%s, %s, %s, %s, %s)"
                    cur.execute(sql, (int(startedBlock), 'OPENED', discord_id, discord_name, current_Date))
                    conn.commit()
                    # Return array of below. return block height oif created.
                    sql = "SELECT id, startedBlock, status, completed_when, winner_id, creator_discord_id, creator_discord_name, created_when FROM `bingo_gamelist` ORDER BY id DESC LIMIT 1"
                    cur.execute(sql,)
                    result = cur.fetchone()
                    return result
            else:
                #Let's show result. return their status
                return result
            cur.close() 
    except Exception as e:
        print(e)
    finally:
        conn.close()

def Bingo_LastGame():
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT id, startedBlock, status, completed_when, winner_id, gameType, reward, rewardTx, rewardNotWin, creator_discord_id, creator_discord_name, created_when, remark FROM `bingo_gamelist` ORDER BY id DESC LIMIT 1"
            cur.execute(sql,)
            result = cur.fetchone()
            if (result is None):
                return None
            else:
                return result
            cur.close() 
    except Exception as e:
        print(e)
    finally:
        conn.close()

def Bingo_LastGameResult():
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT id, startedBlock, status, completed_when, winner_id, winner_name, claim_Atheight, gameType FROM `bingo_gamelist` WHERE `status`='COMPLETED' ORDER BY id DESC LIMIT 1"
            cur.execute(sql,)
            result = cur.fetchone()
            if (result is None):
                return None
            else:
                return result
            cur.close() 
    except Exception as e:
        print(e)
    finally:
        conn.close()

def Bingo_LastGameResultList():
    try:
        openConnection()
        with conn.cursor() as cur:
            sql = "SELECT id, startedBlock, status, completed_when, winner_id, winner_name, claim_Atheight, gameType FROM `bingo_gamelist` WHERE `status`='COMPLETED' ORDER BY id DESC LIMIT 5"
            cur.execute(sql,)
            result = cur.fetchall()
            if (result is None):
                return None
            else:
                listRow = []
                for row in result:
                    listRow.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
                print(listRow)
                return listRow
            cur.close() 
    except Exception as e:
        print(e)
    finally:
        conn.close()

def Bingo_ShowBallNumber(height):
    ### Get from blockchain
    card = ''
    try:
        openConnectionBlockchain()
        with connBlockchain.cursor() as curBlockchain:
            sql = "SELECT `height`, `hash`, `difficulty`,`timestamp` from blocks where height=%s ORDER BY height LIMIT 1"
            curBlockchain.execute(sql, (height))
            row = curBlockchain.fetchone()
            if (row is not None):
                sum_75 = int(sumOfDigits(str(row[1])) % 75) + 1
                card = str('__Height__: '+ str(row[0]) + ' Ball number: '+str(sum_75))
                return card
            else:
                card = str('No ball at that height. __'+height+'__')
                return card
            curBlockchain.close()
    except Exception as e:
        print(e)
    finally:
        connBlockchain.close()
    ### End of getting from blockchain	

def Bingo_ShowCards(lastCardNum, gameID):
    GameStart = Bingo_LastGame()
    if (GameStart[2] == 'COMPLETED'):
        return None
    else:
        gameID = GameStart[0]
    ### Get from blockchain
    try:
        openConnectionBlockchain()
        with connBlockchain.cursor() as curBlockchain:
            sql = "SELECT `height`, `hash`, `difficulty`,`timestamp` from blocks where height > %s ORDER BY height DESC"
            curBlockchain.execute(sql, (GameStart[1]))
            rows = curBlockchain.fetchall()
            card = []
            listNumberHashes = []
            i = 0
            for row in rows:
                sum_75 = int(sumOfDigits(str(row[1])) % 75) + 1
                if (sum_75 not in listNumberHashes):
                    card.append('__Height__: '+ str(row[0]) + ' Ball number: '+str(sum_75))
                    listNumberHashes.append(sum_75)
                else:
                    card.append('__Height__: '+ str(row[0]) + ' `Ball number: '+str(sum_75)+'`')
                i += 1
                if (i>=int(lastCardNum)):
                    return card
            if (card is None):
                return None
            else:
                return card
            curBlockchain.close() 
    except Exception as e:
        print(e)
    finally:
        connBlockchain.close()
    ### End of getting from blockchain

## start board command
@bot.command(pass_context=True, name='board', aliases=['b', 'card', 'cards'], help=bot_help_board)
async def board(context: commands.Context, *args):
    ## If private DM, OK pass
    global channelID
    print(int(context.message.channel.id))
    if (int(context.message.channel.id) == channelID or str(context.message.channel.type).lower() == "private"):
        pass
    else:
        await bot.send_message(
            context.message.author, 'This command only available via DM or through <#'+str(channelID)+'>')
        return
    GameStart = Bingo_LastGame()
    ArgQ = (' '.join(args)).split()
    em = discord.Embed(title='BINGO', description=('PLAY BINGO WITH WRKZCOIN #'+str(GameStart[0]))+' TYPE: ***'+str(GameStart[5])+'***', color=0xDEADBF)
    em.set_author(name='BingoBot', icon_url=bot.user.default_avatar_url)

    if (GameStart is None):
        print('Game is off')
        await bot.reply(
            'There is no game opened yet.')
        return
    if(GameStart[2].upper()=='ONGOING'):
        print('Game is ongoing. Please wait')
        board = CheckUserBoard(context.message.author.id, GameStart[0])
        if (len(ArgQ) != 0):
            ## Let's embed
            em.add_field(name="-", value=":regional_indicator_w::regional_indicator_r::regional_indicator_k::regional_indicator_z:       "
                ":regional_indicator_b::regional_indicator_i::regional_indicator_n::regional_indicator_g::regional_indicator_o:", inline=False)
            LineEm = ''
            for (n, i) in enumerate(board):
                # enumerate
                ThisNum = ''
                if str(i).startswith('*'):
                    ThisNum = ':white_check_mark::white_check_mark:'
                elif str(i).startswith('FREE'):
                    ThisNum = ':free::free:'
                else:
                    ## It is number
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
                if (n >= 0 and (n+1) % 5 != 0):
                    LineEm = LineEm + ThisNum + '     '
                elif (n > 0 and (n+1) % 5 == 0):
                    #print(LineEm)
                    LineEm = LineEm + ThisNum + '     '
                    em.add_field(name="-", value=LineEm, inline=False)
                    LineEm = ''
            if (GameStart[12] is not None):
                em.add_field(name="Remark", value=GameStart[12], inline=False)
            topBlock = gettopblock()
            em.set_footer(text="https://chat.wrkz.work | Current Height: "+str(topBlock['height']))
        if (board is None):
            await bot.reply(
                'Game is already on going. Please wait for a new one.')
            return
        else:
            boardOutput = '`' + boardDump(smallWords(board, 6), 6) + '`'
            if (GameStart[12] is not None):
                boardOutput = boardOutput + '\n' + '*Remark*: '+str(GameStart[12])
            #print(ListActivePlayer)
            ListActivePlayer = List_bingo_active_players(GameStart[0])
            if (len(ListActivePlayer)<8):
                print('Less player 8, reply otherwise DM')
                if (len(ArgQ) != 0):
                    await bot.say(embed=em)
                else:
                    await bot.say(
                        str(context.message.author.name)+': Your created board for game *#'+str(GameStart[0])+'* TYPE: ***'+str(GameStart[5])+'***\n'+boardOutput)
            else:
                if (int(context.message.channel.id) == channelID):
                    await bot.reply(
                        'Please check your DM.')
                if (len(ArgQ) != 0):
                    await bot.send_message(context.message.author, embed=em)
                else:
                    await bot.send_message(
                        context.message.author, 'Your created board for game *#'+str(GameStart[0])+'* TYPE: ***'+str(GameStart[5])+'***\n'+boardOutput)
            return
    elif(GameStart[2].upper()=='COMPLETED'):
        print('Game is completed. Please wait for a new game soon.')
        await bot.reply(
            'Game is already completed.')
        return
    elif(GameStart[2].upper()=='OPENED'):
        print('OK create board if there is no board.')
        board = CheckUser(context.message.author.id, context.message.author.name, GameStart[0])
        boardOutput = '`' + boardDump(smallWords(board, 6), 6) + '`'
        if (GameStart[12] is not None):
            boardOutput = boardOutput + '\n' + '*Remark*: '+str(GameStart[12])
        ListActivePlayer = List_bingo_active_players(GameStart[0])
        if (len(ArgQ) != 0):
            board = CheckUserBoard(context.message.author.id, GameStart[0])
            ## Let's embed
            em.add_field(name="-", value=":regional_indicator_w::regional_indicator_r::regional_indicator_k::regional_indicator_z:       "
                ":regional_indicator_b::regional_indicator_i::regional_indicator_n::regional_indicator_g::regional_indicator_o:", inline=False)
            LineEm = ''
            for (n, i) in enumerate(board):
                # enumerate
                ThisNum = ''
                if str(i).startswith('*'):
                    ThisNum = ':white_check_mark::white_check_mark:'
                elif str(i).startswith('FREE'):
                    ThisNum = ':free::free:'
                else:
                    ## It is number
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
                if (n >= 0 and (n+1) % 5 != 0):
                    LineEm = LineEm + ThisNum + '     '
                elif (n > 0 and (n+1) % 5 == 0):
                    #print(LineEm)
                    LineEm = LineEm + ThisNum + '     '
                    em.add_field(name="-", value=LineEm, inline=False)
                    LineEm = ''
            if (GameStart[12] is not None):
                em.add_field(name="Remark", value=GameStart[12], inline=False)
            topBlock = gettopblock()
            em.set_footer(text="https://chat.wrkz.work | Current Height: "+str(topBlock['height']))
        if (len(ListActivePlayer)<8):
            if (len(ArgQ) != 0):
                await bot.say(embed=em)
            else:
                await bot.say(
                    str(context.message.author.name)+': Your board for game #'+str(GameStart[0])+' TYPE: ***'+str(GameStart[5])+'***\n'+boardOutput)
        else:
            if (int(context.message.channel.id) == channelID):
                await bot.reply(
                    'Please check your DM.')
            if (len(ArgQ) != 0):
                await bot.send_message(context.message.author, embed=em)
            else:
                await bot.send_message(
                    context.message.author, 'Your board for game #'+str(GameStart[0])+' TYPE: ***'+str(GameStart[5])+'***\n'+boardOutput)
        return

@bot.command(pass_context=True, name='ball', aliases=['ballz', 'balls'], help=bot_help_balls)
async def ball(context: commands.Context, *args):
    ## If private DM, OK pass
    global channelID
    if (int(context.message.channel.id) == channelID or str(context.message.channel.type).lower() == "private"):
        pass
    else:
        await bot.send_message(
            context.message.author, 'This command only available via DM or through <#'+str(channelID)+'>')
        return
    ArgQ = (' '.join(args)).split()
    GameStart = Bingo_LastGame()
    print(ArgQ)
    if (len(ArgQ) == 1):
        ## If there is one argument like .ball height
        try:
            height = int(ArgQ[0])
            ballNum = Bingo_ShowBallNumber(height)
            await bot.say(
                ballNum)
            return
        except ValueError:
            await bot.send_message(context.message.author,
                'Ball height must be integer.')
            return
    else:
        cards = Bingo_ShowCards(8, GameStart[0])
        if(GameStart[2] != 'ONGOING'):
            await bot.reply(
                'Game has not started yet.')
            return	
        if (cards is not None):
            cardMsg = ''
            for i in range(len(cards)):
                cardMsg = cardMsg + cards[i] +'\n'
            await bot.reply(
                str(cardMsg))
            return
        else:
            await bot.reply(
                'No active ball yet.')
            return


@bot.command(pass_context=True, name='bingo', aliases=['bing'], help=bot_help_bingo)
async def bingo(context: commands.Context, *args):
    global maintainerOwner, channelID
    ## If private DM, OK pass
    if (int(context.message.channel.id) == channelID or str(context.message.channel.type).lower() == "private"):
        pass
    else:
        await bot.send_message(
            context.message.author, 'This command only available via DM or through <#'+str(channelID)+'>')
        return
    ArgQ = (' '.join(args)).split()
    GameStart = Bingo_LastGame()
    if (len(ArgQ) == 0):
        #If no argument .bingo
        BingoMSG = ''
        if (GameStart is None):
            #Tell game is not start
            BingoMSG = 'There is no game started yet. Please ask to start.'
        else:
            #If there is any game.
            ListActivePlayer = List_bingo_active_players(GameStart[0])
            if (GameStart[2] == 'ONGOING'):
                BingoMSG = BingoMSG + 'Game was started at height: `'+str(GameStart[1]) +'`\n'
                BingoMSG = BingoMSG + 'Type `.bingo lastgame` for result of last game. '
                BingoMSG = BingoMSG + 'Type `.board` to show your bingo board.\n'
                BingoMSG = BingoMSG + 'Game type: `' + str(GameStart[5])+'` with reward: `'+ str(GameStart[6])+'Wrkz`'+' and play reward: `'+ str(GameStart[8])+'Wrkz`'
                if (ListActivePlayer is not None):
                    kickedPlayer=0
                    totalPlayer=0
                    for (i, item) in enumerate(ListActivePlayer):
                        #print(i, item)
                        if(item[5]=='YES'):
                            kickedPlayer += 1
                        totalPlayer += 1
                    BingoMSG = BingoMSG + '\n' + 'Current players: `'+str(totalPlayer)+'`. Kicked: `'+ str(kickedPlayer)+'`'
            elif (GameStart[2] == 'COMPLETED'):
                BingoMSG = BingoMSG +  'Game was completed.\n'
                BingoMSG = BingoMSG +  'Please start a new one. Ttype `.bingo lastgame` for result.\n'
            elif (GameStart[2] == 'OPENED'):
                topBlock = gettopblock()
                RemainHeight = int(GameStart[1]) - int(topBlock['height'])
                BingoMSG = BingoMSG + 'Game will start at height: `'+str(GameStart[1])+'`. Remaining `' +str(RemainHeight) +'` block(s) more.\n'
                BingoMSG = BingoMSG + 'Please register/show it by using `.board` .\n'
                BingoMSG = BingoMSG + 'Game type: `' + str(GameStart[5])+'` with reward: `'+ str(GameStart[6])+'Wrkz`'+' and play reward: `'+ str(GameStart[8])+'Wrkz`'
                if (ListActivePlayer is not None):
                    kickedPlayer=0
                    totalPlayer=0
                    for (i, item) in enumerate(ListActivePlayer):
                        if(item[5]=='YES'):
                            kickedPlayer += 1
                        totalPlayer += 1
                    BingoMSG = BingoMSG + '\n' + 'Current registered players: `'+str(totalPlayer)+'`'
        await bot.reply(
            f'{BingoMSG}')
        return
    elif (len(ArgQ) == 1 or len(ArgQ) == 2):
        # Check game if started by if there is any date in blocks
        if (ArgQ[0].upper() == 'START'):
            #OK let's show when it will start or when it was started
            # .bingo start # show when or none
            if (GameStart is None):
                await bot.reply(
                    'There is no game started yet. Please ask to start.')
                return
            else:
                if (GameStart[2] == 'ONGOING'):
                    await bot.reply(
                        'Game was started at height: '+str(GameStart[1]))
                elif (GameStart[2] == 'COMPLETED'):
                    await bot.reply(
                        'Game was completed. Please start a new one.')
                elif (GameStart[2] == 'OPENED'):
                    await bot.reply(
                        'Game is still open. Please register using `.board`')
                return
        elif (ArgQ[0].upper() == 'REMINDER' or ArgQ[0].upper() == 'REMIND'):
            # OK let's OFF and ON
            # .bingo start # show when or none
            remindMsg = ''
            try:
                openConnection()
                with conn.cursor() as cur:
                    sql = "SELECT `discord_id`, `discord_name` FROM `bingo_reminder` WHERE `discord_id`=%s"
                    cur.execute(sql, (str(context.message.author.id)))
                    result = cur.fetchone()
                    if (result is None):
                        ## Insert to remind
                        sql = "INSERT INTO bingo_reminder (`discord_id`, `discord_name`) VALUES (%s, %s)"
                        cur.execute(sql, (str(context.message.author.id), str(context.message.author.name)))
                        conn.commit()
                        remindMsg = 'You have toggle to get __alert__ from bot when game opened.'
                    else:
                        ## Insert to remind
                        sql = "DELETE FROM bingo_reminder WHERE `discord_id`=%s"
                        cur.execute(sql, (str(context.message.author.id)))
                        conn.commit()
                        remindMsg = 'You will __not__ getting an alert from bot when game opened. `.bingo remind` again to enable.'
            except Exception as e:
                print(e)
            finally:
                conn.close()
            await bot.reply(
                f'{remindMsg}')
            return
        elif (ArgQ[0].upper() == 'STARTNOW' or ArgQ[0].upper() == 'STARTNEW' or ArgQ[0].upper() == 'NEW'):
            # .bingo start # show when or none
            # if (int(context.message.author.id) in maintainerOwner):
            # OK Owner do it if you want to do that. Otherwise everyone can start
            if((GameStart[2] == 'ONGOING') or (GameStart[2] == 'OPENED')):
                await bot.reply(
                    'Game is already ONGOING or OPENED. Type `.bingo` for more info.')
                return                
            topBlock = gettopblock()
            ## Bingo create game by default is 80 after the top block
            bingoStarted = Bingo_CreateGame(int(topBlock['height'])+80, context.message.author.id, context.message.author.name)
            if (bingoStarted is None):
                await bot.reply(
                    'Internal error during creating game.')
                return
            elif (bingoStarted is not None):
                createdMsg = ['%s is wonderful!', 'Thanks to %s! We all love you', '%s is smart :) Let\'s join'] ## created message array
                createdMsg.append('Anybody saw? %s just made a new bingo game')
                createdMsg.append('Let\'s join bingo with %s')
                createdMsg.append('Do not make %s upset with this new game')
                userMention = '<@'+str(context.message.author.id)+'>'
                randMessageCreate = str(random.choice(createdMsg)).replace('%s', userMention)
                ## let's alert reminders
                remindMsg = ''
                remindMsg = 'Game created. ID: #'+str(bingoStarted[0])+' at height: '+str(bingoStarted[1])+'\n'
                try:
                    openConnection()
                    with conn.cursor() as cur:
                        sql = "SELECT `discord_id`, `discord_name` FROM `bingo_reminder`"
                        cur.execute(sql,)
                        result = cur.fetchall()
                        if (result is not None):
                            for row in result:
                            ## Add mentioned to the list.
                                remindMsg = remindMsg + '<@'+str(row[0])+'> '
                except Exception as e:
                    print(e)
                finally:
                    conn.close()
                await bot.send_message(discord.Object(id=channelID),
                    f'{remindMsg}')
                await bot.send_message(discord.Object(id=channelID),
                    f'{randMessageCreate}')
                return
        elif (ArgQ[0].upper() == 'MODE' or ArgQ[0].upper() == 'TYPE'):
            # OK let's show when it will start or when it was started
            # .bingo start # show when or none
            if (int(context.message.author.id) in maintainerOwner):
                #OK Owner do it
                if (len(ArgQ) == 1):
                    await bot.send_message(
                        context.message.author, 'You need to input type of game F: FULL HOUSE, L: LINE, D: DIAGONALS, C: FOUR CORNERS, A: ANY. Example: `MODE A`')
                    return
                else:
                    try:
                        gameType = str(ArgQ[1])
                    except ValueError:
                        await bot.send_message(
                            context.message.author, 'MODE MUST BE LETTER: F, L, D OR C')
                        return
                    if ((GameStart[2] == 'ONGOING') or (GameStart[2] == 'OPENED')):
                        # Change game mode
                        if (ArgQ[1].upper() == 'F' or ArgQ[1].upper() == 'FULL'):
                            gameType = 'FULL HOUSE'
                        elif (ArgQ[1].upper() == 'L' or ArgQ[1].upper() == 'LINE'):
                            gameType = 'LINE'
                        elif (ArgQ[1].upper() == 'D' or ArgQ[1].upper() == 'DIAGONALS' or ArgQ[1].upper() == 'DIAGONAL'):
                            gameType = 'DIAGONALS'
                        elif (ArgQ[1].upper() == 'C' or ArgQ[1].upper() == 'CORNERS' or ArgQ[1].upper() == 'CORNER'):
                            gameType = 'FOUR CORNERS'
                        elif (ArgQ[1].upper() == 'A' or ArgQ[1].upper() == 'ANY'):
                            gameType = 'ANY'
                        else:
                            gameType = 'ANY'
                        try:
                            openConnection()
                            with conn.cursor() as cur:
                                sql = "UPDATE bingo_gamelist SET `gameType`=%s WHERE `id`=%s"
                                cur.execute(sql, (gameType, GameStart[0]))
                                conn.commit()
                        except Exception as e:
                            print(e)
                        finally:
                            conn.close()
                        await bot.send_message(
                            context.message.author, 'Game type changed to: `'+gameType+'`')
                        return
                    else:
                        await bot.send_message(
                            context.message.author, 'Game must be in either ONGOING or OPENED state to use that command.')
                        return
        elif (ArgQ[0].upper() == 'REWARD' or ArgQ[0].upper() == 'PRICE'):
            # Set reward for winner
            if (int(context.message.author.id) in maintainerOwner):
                #OK Owner do it
                if (len(ArgQ) == 1):
                    await bot.send_message(
                        context.message.author, 'You need to input type the reward of this game. ie. `reward 10000`')
                    return
                else:
                    try:
                        RewardPrice = int(ArgQ[1])
                    except ValueError:
                        await bot.send_message(
                            context.message.author, 'REWARD MUST BE INTEGER')
                        return
                    if ((GameStart[2] == 'ONGOING') or (GameStart[2] == 'OPENED')):
                        ## Just need to set what is the max price can do via discord.
                        if (RewardPrice>100000):
                            await bot.send_message(
                                context.message.author, 'Reward price is too big.')
                            return
                        try:
                            openConnection()
                            with conn.cursor() as cur:
                                sql = "UPDATE bingo_gamelist SET `reward`=%s WHERE `id`=%s"
                                cur.execute(sql, (RewardPrice, GameStart[0]))
                                conn.commit()
                        except Exception as e:
                            print(e)
                        finally:
                            conn.close()
                        await bot.send_message(
                            context.message.author, 'Game reward changed to: `'+str(RewardPrice)+'`')
                        return
                    else:
                        await bot.send_message(
                            context.message.author, 'Game must be in either ONGOING or OPENED state to use that command.')
                        return
        elif (ArgQ[0].upper() == 'PLAYREWARD' or ArgQ[0].upper() == 'REWARDPLAY'):
            # set price for playing
            if (int(context.message.author.id) in maintainerOwner):
                #OK Owner do it
                if (len(ArgQ) == 1):
                    await bot.send_message(
                        context.message.author, 'You need to input type the reward of this game. ie. `reward 10000`')
                    return
                else:
                    try:
                        RewardPrice = int(ArgQ[1])
                    except ValueError:
                        await bot.send_message(
                            context.message.author, 'REWARD MUST BE INTEGER')
                        return
                    if ((GameStart[2] == 'ONGOING') or (GameStart[2] == 'OPENED')):
                        ## set max reward for playing
                        if (RewardPrice>10000):
                            await bot.send_message(
                                context.message.author, 'Reward non-win price is too big.')
                            return
                        try:
                            openConnection()
                            with conn.cursor() as cur:
                                sql = "UPDATE bingo_gamelist SET `rewardNotWin`=%s WHERE `id`=%s"
                                cur.execute(sql, (RewardPrice, GameStart[0]))
                                conn.commit()
                        except Exception as e:
                            print(e)
                        finally:
                            conn.close()
                        await bot.send_message(
                            context.message.author, 'Game non-win reward changed to: `'+str(RewardPrice)+'`')
                        return
                    else:
                        await bot.send_message(
                            context.message.author, 'Game must be in either ONGOING or OPENED state to use that command.')
                        return
        elif (ArgQ[0].upper() == 'BINGO'):
            #.bingo bingo. Check if user wins
            if (GameStart is None):
                await bot.send_message(
                    context.message.author, 'There is no game started yet. Please ask to start.')
                return
            else:
                if (GameStart[2] != 'ONGOING'):
                    await bot.send_message(
                        context.message.author, 'Game not started yet. It is sill opened for new players.')
                    return
                #Check user card with blocks hash
                if (str(GameStart[5])=='ANY'):
                    #ANY GAME:
                    UserBingo1 = CheckUserBingoType(int(context.message.author.id), GameStart[0], 'FOUR CORNERS')
                    if(str(UserBingo1) == 'FOUR CORNERS'):
                        UserBingo = 'ANY'
                    UserBingo2 = CheckUserBingoType(int(context.message.author.id), GameStart[0], 'LINE')
                    if(str(UserBingo2) == 'LINE'):
                        UserBingo = 'ANY'
                    UserBingo3 = CheckUserBingoType(int(context.message.author.id), GameStart[0], 'DIAGONALS')
                    if(str(UserBingo3) == 'DIAGONALS'):
                        UserBingo = 'ANY'
                    UserBingo4 = CheckUserBingoType(int(context.message.author.id), GameStart[0], 'FULL HOUSE')
                    if(str(UserBingo4) == 'FULL HOUSE'):
                        UserBingo = 'ANY'
                else:
                    UserBingo = CheckUserBingoType(int(context.message.author.id), GameStart[0], str(GameStart[5]))
                if (UserBingo is None):
                    if (CheckUserBoard(int(context.message.author.id), GameStart[0]) is None):
                        await bot.reply(
                            'You haven\'t joined the game or has been kicked.')
                        return
                    else:
                        KickUser(int(context.message.author.id), GameStart[0])
                        await bot.reply(
                            'NO.... You are out!')
                        return
                else:
                    print('UserBingo: '+str(UserBingo))
                    print('GameStart[5]: '+str(GameStart[5]))
                    if (str(UserBingo) == str(GameStart[5])):
                        ## Tip player (not winner)
                        if (int(GameStart[8])>1):
                            ListActivePlayer = List_bingo_active_players(GameStart[0])
                            if (ListActivePlayer is not None):
                                ListMentions = ''
                                for (i, item) in enumerate(ListActivePlayer):
                                    if (int(item[0]) != int(context.message.author.id)):
                                        ListMentions = ListMentions + '<@'+item[0]+'>'+' '
                                rewardNotWin = '.tip '+str(GameStart[8]) + ' ' + ListMentions + 'Thank you for playing.'
                        try:
                            current_Date = datetime.now()
                            topBlock = gettopblock()
                            openConnection()
                            with conn.cursor() as cur:
                                sql = "UPDATE bingo_gamelist SET `status`=%s, `completed_when`=%s, `winner_id`=%s, `winner_name`=%s, `claim_Atheight`=%s WHERE `id`=%s"
                                cur.execute(sql, ('COMPLETED', str(current_Date), str(context.message.author.id), str(context.message.author.name), str(topBlock['height']), str(GameStart[0])))
                                conn.commit()
                        except Exception as e:
                            print(e)
                        finally:
                            pass
                        try:
                            openConnection()
                            with conn.cursor() as cur:
                                sql = "INSERT INTO bingo_active_players_archive SELECT * FROM bingo_active_players;"
                                cur.execute(sql,)
                                conn.commit()
                                sql = "TRUNCATE TABLE bingo_active_players;"
                                cur.execute(sql,)
                                conn.commit()
                        except Exception as e:
                            print(e)
                        finally:
                            conn.close()
                        winMsg = 'You win. Bingo! Please wait to start new game.\nWinner is: <@'+context.message.author.id+'>'
                        if (int(GameStart[6])>1):
                            winMsg = '.tip '+str(GameStart[6])+' '+'<@'+context.message.author.id+'> You win. Bingo! Please wait to start new game.'
                        await bot.send_message(discord.Object(id=channelID),
                            f'{winMsg}')
                        if (rewardNotWin is not None):
                            await bot.send_message(discord.Object(id=channelID),
                                f'{rewardNotWin}')
                        return
                    else:
                        KickUser(int(context.message.author.id), GameStart[0])
                        await bot.send_message(discord.Object(id=channelID),
                            '<@'+context.message.author.id+'> Did you check? No BINGO yet!! You\'re out from the game now.')
                        return
        elif (ArgQ[0].upper() == 'BALL'):  
            #.bingo card. Check last ball
            if (GameStart is None):
                await bot.reply(
                    'There is no game started yet. Please ask to start.')
                return
            else:
                #show last card numbers
                if (GameStart[2] != 'ONGOING'):
                    await bot.reply(
                        'Game not started yet. It is sill opened for new players.')
                    return
                cards = Bingo_ShowCards(1, GameStart[0])
                if (cards is not None):
                    cardMsg = ''
                    for i in range(len(cards)):
                        cardMsg = cardMsg + cards[i] +'\n'
                    if (cardMsg is not None):
                        await bot.reply(
                            f'{cardMsg}')
                        return
                    else:
                        await bot.reply(
                            'No active ball yet.')
                        return
                else:
                    await bot.reply(
                        'No active ball yet.')
                    return
        elif (ArgQ[0].upper() == 'BALLS'):  
            #.bingo card. Check last card
            if (GameStart is None):
                await bot.reply(
                    'There is no game started yet. Please ask to start.')
                return
            else:
                #show last FIVE card numbers
                if (GameStart[2] != 'ONGOING'):
                    await bot.reply(
                        'Game not started yet. It is sill opened for new players.')
                    return
                cards = Bingo_ShowCards(10, GameStart[0])
                if (cards is not None):
                    cardMsg = ''
                    for i in range(len(cards)):
                        cardMsg = cardMsg + cards[i] +'\n'
                    if (cardMsg is not None):
                        await bot.reply(
                            f'{cardMsg}')
                        return
                    else:
                        await bot.reply(
                            'No active ball yet.')
                        return
                else:
                    await bot.reply(
                        'No active ball(s) yet.')
                    return
        elif (ArgQ[0].upper() == 'CARD' or ArgQ[0].upper() == 'CARDS'):
            await bot.send_message(
                context.message.author, str(board_function(context.message)))
            return
        elif (ArgQ[0].upper() == 'LASTGAME' or ArgQ[0].upper() == 'LAST'):  
            #.bingo lastgame. show last game result
            LastGameRes = Bingo_LastGameResult()
            if (LastGameRes is None):
                await bot.reply(
                    'There is no last game result yet.')
                return
            else:
                #show last card numbers
                whenWin = datetime.strptime(LastGameRes[3].split(".")[0], '%Y-%m-%d %H:%M:%S')
                ago = timeago.format(whenWin, datetime.now())
                #print(ago)
                LastGameMsg = ''
                LastGameMsg = '**Last game #'+str(LastGameRes[0])+'**\n'
                LastGameMsg = LastGameMsg + '__Started block__: '+str(LastGameRes[1])+', Claimed to win block: '+str(LastGameRes[6])+'\n'
                LastGameMsg = LastGameMsg + '__Winner was__: <@'+LastGameRes[4]+'>\n'
                LastGameMsg = LastGameMsg + '__When__: '+str(ago) + '. Game type:`'+str(LastGameRes[7])+'`'
                await bot.reply(
                    str(LastGameMsg))
                return
        elif (ArgQ[0].upper() == 'LASTGAMES'):  
            #.bingo lastgame. show last game result
            LastGameRes = Bingo_LastGameResultList()
            if (LastGameRes is None):
                await bot.reply(
                    'There is no last game result yet.')
                return
            else:
                LastGameMsg = ''
                #show last card numbers
                for n, msg in enumerate(LastGameRes):
                    ## Show:
                    whenWin = datetime.strptime(msg[3].split(".")[0], '%Y-%m-%d %H:%M:%S')
                    ago = timeago.format(whenWin, datetime.now())
                    #print(ago)
                    LastGameMsg = LastGameMsg + '**Last game #'+str(msg[0])+'**\n'
                    LastGameMsg = LastGameMsg + '__Started block__: '+str(msg[1])+', Claimed to win block: '+str(msg[6])+'\n'
                    LastGameMsg = LastGameMsg + '__Winner was__: `'+msg[5]+'`\n'
                    LastGameMsg = LastGameMsg + '__When__: '+str(ago) + '. Game type:`'+str(msg[7]) + '`\n\n'
                await bot.say(
                    str(LastGameMsg))
                return
        elif (ArgQ[0].upper() == 'RESTART' or ArgQ[0].upper() == 'RELOAD'):
            #Check permission
            if (int(context.message.author.id) in maintainerOwner):
                await bot.say('Bot is rebooting...')
                await asyncio.sleep(2)
                sys.exit(0)
            else:
                await bot.say('Access denied...')
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

def gettopblock():
    global TopBlockCall
    resp = requests.get(TopBlockCall)
    return resp.json()

## Sum of all digits 0 to 9 in a string and return numbers:
#print(sumOfDigits('1c2aa8e1ab52959410c4f2e51260e2a2dfe0a9394351f80c06270d3bf3f8a50c'))=>147
#print(sumOfDigits('e6d6c5724428f633a6a70f22608e004ed66046504ad6fa5ec1c6a7689aba7da3'))=>180
#print(sumOfDigits('c7c293953fb6e90aae9e90ea27a8e3796cdb23c077cf25b77dbeb1937e169669'))=>210

def sumOfDigits(sentence):
    sumof=0
    for x in sentence:
        if x.isdigit()== True:
            sumof+=int(x)
    return sumof

async def checkOpenedGame():
    while not bot.is_closed:
        await asyncio.sleep(5) # 5 second before doing anything. Especially sending message to server
        await show_checkOpenedGame()
        await asyncio.sleep(10) ## sleep 10 seconds

async def show_randomMsg():
    while not bot.is_closed:
        await asyncio.sleep(5) # 5 second before doing anything
        await show_msgCard()
        await asyncio.sleep(120) ## sleep 3mn

async def show_msgCard():
    global channelID
    GameStart = Bingo_LastGame()
    SomeTips = [] # new list
    SomeTips.append('You can use `.board` only during game OPENED and ONGOING (if you register one).')
    SomeTips.append('To register during game opening, use `.board`')
    SomeTips.append('Please also check pinned messages for updates.')
    SomeTips.append('I am giving reward through TipBot. Tip me some Wrkz for every winner :)')

    ## Add some remind list who is online but not play
    if(GameStart[2].upper()=='OPENED'):
        SomeTips.append('Eat, sleep, and play bingo <#'+str(channelID)+'>')
        SomeTips.append('Chicks dig guys with big numbers on their balls.')
        SomeTips.append('Don\'t drive me crazy, drive me to bingo!')
        SomeTips.append('Born to yell BINGO!')
        SomeTips.append('I only play bingo on days that end in Y.')
        SomeTips.append('Keep Grandma off the streets take her to bingo.')
        SomeTips.append('If there\'s no bingo in heaven I\'m not going.')
        SomeTips.append('It takes balls to yell bingo.')
        SomeTips.append('A simple `.board` can have you in bingo :) ')
        #reminderListIds = [] ## List reminder
        ListActivePlayer = List_bingo_active_players(GameStart[0])
        playerIDs = [] # list ID
        for player in ListActivePlayer:
            playerIDs.append(int(player[0]))
        try:
            openConnection()
            with conn.cursor() as cur:
                sql = "SELECT `discord_id`, `discord_name` FROM `bingo_reminder`"
                cur.execute(sql,)
                result = cur.fetchall()
                if (result is not None):
                    for row in result:
                        ## If they are online
                        #reminderListIds.append(int(row[0]))
                        if (int(row[0]) not in playerIDs):
                            SomeTips.append('Do you want to play bingo? <@'+str(row[0])+'>. It is not late yet.  `.bingo remind` If you want me to stop this ping.')
        except Exception as e:
            print(e)
        finally:
            conn.close()
    elif(GameStart[2].upper()=='COMPLETED'):
        SomeTips.append('Eat, sleep, and play bingo <#'+str(channelID)+'>. Why nobody interests to start a new game?')
        SomeTips.append('Don\'t drive me crazy, drive me to `.bingo new`')
        SomeTips.append('Keep Grandma off the streets take her to type `.bingo new`.')
        SomeTips.append('Eat, sleep, and play bingo <#'+str(channelID)+'>')
        SomeTips.append('If I could use keyboard, I would `.bingo new`')
        SomeTips.append('I doubt if everybody is sleeping now.')
        SomeTips.append('I broke my phone screen and I can\'t start any bingo :( ') 
        SomeTips.append('After I wake up, I need to see who is the winner.')
        SomeTips.append('Game completed? Anyone can start a new one by `.bingo startnew`')
    elif(GameStart[2].upper()=='ONGOING'):
        SomeTips.append('Check your bingo board in gameplay, use `.board`')
        SomeTips.append('Check last ball or last five balls, use `.bingo ball` or `.bingo balls`')
        SomeTips.append('If you have all numbers with **, win it by `.bingo bingo`. If you do this wrongly, you will be kicked out from the current game.')
        SomeTips.append('Got kicked? OK, wait for next :) ')
        SomeTips.append('We know the winner only they type `.bingo bingo`')
        SomeTips.append('Don\'n wait to win. I will not tell you until you `.bingo bingo`')
        SomeTips.append('What do you want me more than bingo?')
        SomeTips.append('Haha... too quiet? Check `.board` You can be the next winner')
        SomeTips.append('Too late? Game already started? Let me remind you :) `.bingo remind` If I call you and no respond, it is your problem.')
        SomeTips.append('Don\'t be too lazy. I always respond for any `.bingo`')
        SomeTips.append('I always respond for any `.board`. Don\'t be too lazy')
    print(SomeTips)
    randMessageTo = random.choice(SomeTips)
    if (GameStart is None):
        #Show some game when it hasn't started. There is no game
        await bot.send_message(discord.Object(id=channelID),
                        f'{randMessageTo}.')
    else:
        #Show some game when it hasn't started. Game is opened, ongoing
        if(GameStart[2].upper()=='OPENED'):
            await bot.send_message(discord.Object(id=channelID),
                            f'{randMessageTo}.')
        if(GameStart[2].upper()=='COMPLETED'):
            await bot.send_message(discord.Object(id=channelID),
                            f'{randMessageTo}.')
        elif(GameStart[2].upper()=='ONGOING'):
            if (random.randint(0, 9)<=4):
                await bot.send_message(discord.Object(id=channelID),
                               f'{randMessageTo}.')
            else:
                cards = Bingo_ShowCards(3, GameStart[0])
                if (cards is not None):
                    cardMsg = ''
                    for i in range(len(cards)):
                        cardMsg = cardMsg + cards[i] +'\n'
                    await bot.send_message(discord.Object(id=channelID),
                                    f'{cardMsg}')

async def show_checkOpenedGame():
    global channelID, remindedStart, remindedBlock
    GameStart = Bingo_LastGame()
    #Insert only if game is start
    if (GameStart is None):
        print('Game is off')
    else:
        ListActivePlayer = List_bingo_active_players(GameStart[0])
        topBlock = gettopblock()
        if(GameStart[2].upper()=='OPENED'):
            print('Game is opened. Not to start syncing.')
            if(int(GameStart[1])<=int(topBlock['height'])):
                # If game to start height bigger or equal to topblock, set status to ONGOING
                print('OK change status of game')
                ## Mentioning people that game start.
                ## If number of players is less than three, let's extend 30 more blocks.
                ListMention = ''
                for (i, item) in enumerate(ListActivePlayer):
                    ListMention = ListMention + '<@'+str(item[0])+'>'+' '
                if(len(ListActivePlayer)>=3):
                    await bot.send_message(discord.Object(id=channelID),
                                    f'{ListMention}\nGame started. `.board` registration is closed. Good luck!')
                    try:
                        current_Date = datetime.now()
                        openConnection()
                        with conn.cursor() as cur:
                            sql = "UPDATE bingo_gamelist SET `status`=%s WHERE `id`=%s"
                            cur.execute(sql, ('ONGOING', GameStart[0]))
                            conn.commit()
                    except Exception as e:
                        print(e)
                    finally:
                        conn.close()
                else:
                    ## Alert to players that we extend if there is less than 3 players. 30 Blocks extension:
                    await bot.send_message(discord.Object(id=channelID),
                                    f'{ListMention}\nGame extends 30 blocks for new players.')
                    try:
                        current_Date = datetime.now()
                        openConnection()
                        with conn.cursor() as cur:
                            sql = "UPDATE bingo_gamelist SET startedBlock=startedBlock+30 WHERE `id`=%s"
                            cur.execute(sql, (GameStart[0]))
                            conn.commit()
                    except Exception as e:
                        print(e)
                    finally:
                        conn.close()
            else:
                # if can remind
                RemainHeight = int(GameStart[1]) - int(topBlock['height'])
                if (RemainHeight % 10 == 0 and remindedStart == 0 and remindedBlock != (int(topBlock['height']))):
                    await bot.send_message(discord.Object(id=channelID),
                                    f'***{RemainHeight}*** blocks more before game starts.')
                    remindedStart = 1
                    remindedBlock = int(topBlock['height'])
                else:
                    remindedStart = 0
        elif(GameStart[2].upper()=='ONGOING'):
            print('Game is ongoing.')
            ## If player just only one. Let him win
            if(len(ListActivePlayer)==1):
                for (i, item) in enumerate(ListActivePlayer):
                    winner_id = item[0]
                    winner_name = item[1]
                try:
                    current_Date = datetime.now()
                    topBlock = gettopblock()
                    openConnection()
                    with conn.cursor() as cur:
                        sql = "UPDATE bingo_gamelist SET `status`=%s, `completed_when`=%s, `winner_id`=%s, `winner_name`=%s, `claim_Atheight`=%s WHERE `id`=%s"
                        cur.execute(sql, ('COMPLETED', str(current_Date), str(winner_id), str(winner_name), str(topBlock['height']), str(GameStart[0])))
                        conn.commit()
                except Exception as e:
                    print(e)
                finally:
                    pass
                try:
                    openConnection()
                    with conn.cursor() as cur:
                        sql = "INSERT INTO bingo_active_players_archive SELECT * FROM bingo_active_players;"
                        cur.execute(sql,)
                        conn.commit()
                        sql = "TRUNCATE TABLE bingo_active_players;"
                        cur.execute(sql,)
                        conn.commit()
                except Exception as e:
                    print(e)
                finally:
                    conn.close()
                winMsg = '<@'+str(winner_id)+'> wins the game alone.'
                if (int(GameStart[6])>1):
                    winMsg = '.tip '+str(GameStart[6])+' '+'<@'+str(winner_id)+'> Please wait to start new game.'
                await bot.send_message(discord.Object(id=channelID),
                    f'{winMsg}')
        elif(GameStart[2].upper()=='COMPLETED'):
            print('Game is completed. Please create a new one.')       
        elif(GameStart[2].upper()=='SUSPENDED'):
            print('Game is suspended.')

@bot.event
async def on_command_error(error, _: commands.Context):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(_.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(_.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.MissingRequiredArgument):
        command = _.message.content.split()[0].strip('.')
        pass
    elif isinstance(error, commands.CommandNotFound):
        pass

# start bot
@click.command()
def main():
    bot.loop.create_task(checkOpenedGame())
    bot.loop.create_task(show_randomMsg())
    bot.run(token)

if __name__ == '__main__':
    main()

