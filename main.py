import time
import requests
import telepot
from telepot.loop import MessageLoop
from bs4 import BeautifulSoup as bs
bot = telepot.Bot('token')
favs = {}
def handle(msg):
    printStr = ''
    
    # Taking command and parameters from the message text
    msgText = msg['text'].split(' ')
    if len(msgText)>1: command, params = msgText[0], msgText[1:]
    else: command, params = msgText[0], ''
        
    userId = msg['from']['id']
    chatId = msg['chat']['id']
    
    
    if(command=='/start'):
        bot.sendMessage(chatId, 'Hello! If you want to get your Showdown ELO, send me the command: \n/get USERNAME') 
    
    
    elif(command=='/get'):
        
        if not(params): # If there are no params, warn the user
            bot.sendMessage(chatId, 'You have to put a username after /get!')
            
        elif(len(params)==1):
            mId = bot.sendMessage(chatId, 'Received username: '+params[0]+'\nSearching...')
            page = bs(requests.get('https://pokemonshowdown.com/users/'+params[0]).text, 'html.parser') # Getting the User Score Page
            if page.find('small').get_text() == '(Unregistered)': # Checking if the User exists
                bot.sendMessage(chatId, 'The user do not exists! Search another user')
                return
            
            tr = page.findAll('tr') # Saving into tr the table with scores
            for i in tr:
                if i.find('th'): continue # Don't need infos stored in th
                if i.find('td'):
                    # If a td is found, take the first td (Meta name) and the second td (score)
                    printStr += 'Meta: ' + i.findAll('td')[0].get_text() + ' \nELO: ' + i.findAll('td')[1].get_text() +'\n\n'
            
            bot.editMessageText(telepot.message_identifier(mId), printStr)
            
        else:
            # In this case, the first parameter must be the user name and the second must be the meta name
            mId = bot.sendMessage(chatId, 'Received username: '+params[0]+'\nReceived meta: '+params[1]+'\nSearching...')
            
            page = bs(requests.get('https://pokemonshowdown.com/users/'+params[0]).text, 'html.parser')
            if page.find('small').get_text() == '(Unregistered)':
                bot.editMessageText(telepot.message_identifier(mId), 'The user do not exists! Search another user')
                return
            
            tr = page.findAll('tr')
            for i in tr:
                if i.find('th'): continue
                if i.find('td'):
                    if i.findAll('td')[0].get_text()==params[1]:
                        printStr = 'Meta: ' + params[1] + ' \nELO: ' + i.findAll('td')[1].get_text()
                        break
                        
            # If no meta is found, printStr will be blank
            if not(printStr): printStr = 'Meta not found! Try with another meta and remember that the name of a meta always start with "gen#" and has no spaces!'
            bot.editMessageText(telepot.message_identifier(mId), printStr)
            
    elif(command=="/fav"):
 
        if len(params)<2: # The parameters must be user name and meta name
            bot.sendMessage(chatId, "Not enough parameters! To set favorite metas use the command /fav user metaname")
            return
        
        page = bs(requests.get('https://pokemonshowdown.com/users/'+params[0]).text, 'html.parser')
        if page.find('small').get_text() == '(Unregistered)':
            bot.sendMessage(chatId, 'The user do not exists! Can\'t add to favorites, try with another user')
            return
        
        tr = page.findAll('tr')
        for i in tr:
            if i.find('th'): continue
            if i.find('td'):
                if i.findAll('td')[0].get_text()==params[1]:
                    printStr = 'Meta: ' + params[1] + ' \nELO: ' + i.findAll('td')[1].get_text()
                    break
            if not(printStr): 
            bot.sendMessage(chatId, 'Meta not found! Can\'t add to favorites, try with another meta')
            return
        
        if userId not in favs:
            favs[userId] = [] # If the user never created a favorite list, create one
        favs[userId].append([params[0], params[1]])
        bot.sendMessage(chatId, params[0]+"'s "+params[1]+" added to favorites!")
        
    elif(command=='/delfav'): # The parameters must be user name and meta name
        
        if(len(params)<2):
            bot.sendMessage(chatId, 'The user do not exists! Can\'t add to favorites, try with another user')
            return
        
        if [params[0], params[1]] in favs[userId]:
            favs[userId].remove([params[0], params[1]]) # Remove the user-specified user name and meta name from the favorite list
            bot.sendMessage(chatId, params[0]+"'s "+params[1]+" deleted from favorites")
        else: bot.sendMessage(chatId, "This combination of user and meta was not in your favorites, thus it was not deleted")
    
    elif(command=='/listfav'): # This takes no params, just shows a list of all favorites
        printStr = "List of favorites: \n"
        for fav in favs[userId]:
            printStr += "\nUser: " + fav[0] + "\nMeta: " + fav[1] + "\n"
        bot.sendMessage(chatId, printStr)
    
    elif(command=='/getfav'): # This takes no params, just shows a list of all favorites with the respective score
        mId = bot.sendMessage(chatId, "Getting all the data about your favorites! Please, wait...")
        printStr = ''
        
        if userId not in favs or len(favs[userId])==0:
            bot.editMessageText(telepot.message_identifier(mId), "You do not have any favorite! Try adding some favorites with /fav")
        
        for fav in favs[userId]:
            page = bs(requests.get('https://pokemonshowdown.com/users/'+fav[0]).text, 'html.parser')
            # Here I don't check if the user exists because I checked before entering the favorite in the list
            tr = page.findAll('tr')
            for i in tr:
                if i.find('th'): continue
                if i.find('td'):
                    if i.findAll('td')[0].get_text()==fav[1]:
                        elo = i.findAll('td')[1].get_text()
                        break
            printStr += "User: " + fav[0] + "\nMeta: " + fav[1] + "\nELO: " + elo + "\n\n"
       
        bot.editMessageText(telepot.message_identifier(mId), printStr)
    
    elif(command == "/help"):
        printStr = "/get (USER)\nGet all the ratings in every meta of the user\n\n/get (USER) (META)\nGet the rating of the user in the specified meta\n\n/fav (USER) (META)\nSet this combination of user and meta in the favorites, to access them easier\n\n/getfav\nAccess all the ratings in your favorites\n\n/listfav\nFast list of all your favorites\n\n/delfav (USER) (META)\nDeletes this specific combination of user and meta from your favorites"
        bot.sendMessage(chatId, printStr)
        
MessageLoop(bot, handle).run_as_thread()
while 1:
    time.sleep(10)
