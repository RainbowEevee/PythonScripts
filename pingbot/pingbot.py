from pprint import pprint
import discord
import asyncio
import logging
import time
import threading
import re


#sets up logger and discord client
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()

with open("client_token.txt") as token:
    client_token = token.read()

    
def getServerList():
    serverList = []
    for server in client.servers:
        tempDict = {}
        tempDict["name"] = server.name
        tempDict["id"] = server.id
        abb = ""
        for match in re.finditer(r'(\w+|[^\w ]| )', server.name):
            if match.group(0) != " ":
                abb += match.group(0)[0]
        abb = ''.join(abb)
        tempDict["abbr"] = abb.lower()
        serverList.append(tempDict)
    for i in range(len(serverList)):
        print('[' + str(i + 1) + '] ' + serverList[i]["name"])
    print ("--------")
    return serverList
    
def getChannelList(serverId):
    channelList = []
    serverName = ''
    for server in client.servers:
        if server.id == serverId:
            serverName = server.name
            for channel in server.channels:
                if channel.type != discord.ChannelType.voice:
                    tempDict = {}
                    tempDict["name"] = channel.name
                    tempDict["id"] = channel.id
                    channelList.append(tempDict)
    print('\nConnected to: ' + serverName + '')
    print('Can access the following channels:\n')
    for x in range(len(channelList)):
        print(channelList[x]["name"])
    print ('--------')
    return channelList

#handles command parsing on another thread, and also controls which server is currently selected    
def commandLine():
    msgId = ''
    serverId = ''
    serverList = getServerList()
    channelList = getChannelList(serverId)
    cmdList = []
    while True:
        cmd = input('Enter a command: ')
        cmdList = cmd.split()
        if cmdList[0] == 'servers':
            getServerList()
        if cmdList[0] == 'channels':
            channelList = getChannelList(serverId)
        if cmdList[0] == 'switch':
            match = re.search(r'\d+', cmdList[1])
            if match:
                try:
                    pos = int(cmdList[1]) - 1
                    serverId = serverList[pos]["id"]
                    channelList = getChannelList(serverId)
                except IndexError:
                    print('Invalid position number or abbreviation.')
            check = re.search(r'\D+', cmdList[1])
            if check:
                    for server in serverList:
                        if cmdList[1] == server["abbr"]:
                            serverId = server["id"]
                    channelList = getChannelList(serverId)
        if cmdList[0] == 'msg':
            for channel in channelList:
                if cmdList[1] == channel["name"]:
                    msgId = channel["id"]
                    break
                else:
                    msgId = cmdList[1]
            messageList = cmdList[2:]
            message = ' '.join(messageList)
            asyncio.run_coroutine_threadsafe(client.send_message(discord.Object(id=msgId), message), client.loop)
        if cmdList[0] == 'setgame':
            game = ' '.join(cmdList[1:])
            print (game)
            asyncio.run_coroutine_threadsafe(client.change_presence(game=discord.Game(name=game)), client.loop)
                
def displayReady():
    servCount = str(len(client.servers))
    print('Logged in as: ' + client.user.name)
    print('Client ID: ' + client.user.id)
    if servCount == '1':
        print('Conneceted to 1 server.')
    else:
        print('Connected to ' + servCount + ' servers:')

threadObj = threading.Thread(target=commandLine)

@client.event
async def on_ready():
    displayReady()
    threadObj.start()
    
@client.event
async def on_message(message):
    if message.content.startswith('!ping'):
        await client.send_message(message.channel, 'Pong!')
    elif message.content.startswith('!head'):
        if message.author.name == 'ShadowFoxNixill':
            await client.send_message(message.channel, '*Nix puts his head on his desk.*')
        if message.author.name == 'Rainbow':
            await client.send_message(message.channel, '*Rai puts his head on his desk.*')

client.run(client_token)
