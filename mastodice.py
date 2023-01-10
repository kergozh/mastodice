###
# Mastodice, bot que tira los dados :-)
# Fork (cada vez más lejano) del bot "info" original de @spla@mastodont.cat
# En https://git.mastodont.cat/spla/info
###  

from pybot.mastobot import Mastobot
from pybot.config import Config
from pybot.logger import Logger
from pybot.translator import Translator

import re
import random

BOT_NAME = "Dicebot"
MAX_LENGHT = 490


class Bot(Mastobot):

    def __init__(self, botname: str = BOT_NAME) -> None:

        super().__init__(botname = botname)

        self.init_replay_bot()
        self.init_translator()


    def run(self, botname: str = BOT_NAME) -> None:

        notifications = self.mastodon.notifications()
 
        for notif in notifications:

            content = self.check_notif(notif, "mention")

            if content != "":
                self.replay_toot(self.find_text(notif), notif)

        super().run(botname = botname)


    def find_text(self, notif):        

        language = notif.status.language
        username = notif.account.acct
        post_text  = "@" + username + ", "

        self._translator.fix_language (language)
        _text     = self._translator.get_text

        self._logger.debug("notif language: " + language)                    

        txt = notif.status.content
        txt = self.cleanhtml(txt)
        txt = self.unescape(txt)
        txt = txt[txt.index(" ") + 1:]
        txt = re.sub("(test)","", txt).strip()
        self._logger.debug("txt: " + txt)                    

        rs = self._actions.get(("roll_dice.rolls"))
        rg = "(^(\d{1,2}[dD](" + rs + "))|(\d{1,2}))((\s*\+\s*\d{1,2}[dD](" + rs + "))*(\s*\+\s*\d{1,2})*)*$"
        x = re.search(rg, txt)

        text1 = text2 = ""
        total = 0
        dice = 0
        primer = True
        max_dice = False

        if x == None:
            post_text = post_text + _text("error")  
        else:    
            txt = txt.lower()
            ops = txt.split("+")
            for op in ops:
                if max_dice:
                    break
                op = op.strip()
                if op.isdigit():
                    total = total + int(op)
                    text1 = text1+ " + " + op
                    text2 = text2 + " + " + op
                else:
                    n = op[:op.index("d")]
                    d = op[op.index("d") + 1:]
                    if primer:
                        text2 = n + "d" + d
                    else:
                        text2 = text2 + " + " + n + "d" + d
                    for x in range (int(n)):
                        dice = dice + 1
                        if dice > 50:
                            max_dice = True
                            break
                        a = random.randint(1, int(d))
                        total = total + a
                        if primer:
                            text1 = str(a)
                            primer = False
                        else:
                            text1= text1 + " + " + str(a)
            text1 = text1 + " = " + str(total)

            if max_dice:
                post_text = post_text + _text("max")
            else:
                if len(post_text) + len(text1) + len(text2) + 2 < MAX_LENGHT:
                    post_text  = post_text + "\n" + text2 + "\n" + text1
                else:     
                    post_text  = post_text + "\n" + text1

        post_text = (post_text[:MAX_LENGHT] + '... ') if len(post_text) > MAX_LENGHT else post_text

        self._logger.debug ("answer text\n" + post_text)

        return post_text


# main

if __name__ == '__main__':
    Bot().run()
