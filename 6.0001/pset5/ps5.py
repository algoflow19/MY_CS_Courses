# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz


#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================


class NewsStory(object):
    def __init__(self,guid,title,description,link, pubdate):
        self.guid=guid
        self.title=title
        self.description=description
        self.link=link
        self.pubdate=pubdate
    def get_guid(self):
        return self.guid
    def get_title(self):
        return self.title
    def get_description(self):
        return self.description
    def get_link(self):
        return self.link
    def get_pubdate(self):
        return self.pubdate
    
        
#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS
class PhraseTrigger(Trigger):
    def __init__(self,phrase):
        self.phrase=phrase.lower()
    #def is_phrase_in(self,phrase):
        #phrase=""
        #if(phrase.startswith(' ') or phrase.endswith(' ')):
            #return False
        #last_letter=''
        #for letter in phrase:
            #if(letter in string.punctuation):
                #return False
            #if(last_letter==' ' and letter==' '):
                #return False
            #last_letter=letter
            
    def is_phrase_in(self,text):
        text=text.lower()
        for letter in text:
            if(letter in string.punctuation):
                text=text.replace(letter,' ')
        tmp_list=text.split(" ")
        word_list=[]
        for word in tmp_list:
            if(word != ''):
                word_list.append(word)
        phrase_list=self.phrase.split(" ")
        phrase_length=len(phrase_list)
        for i in range(len(word_list)):
            if(word_list[i]==phrase_list[0]):
                if( len(word_list)-i>=phrase_length and word_list[i:i+phrase_length] == phrase_list):
                    return True
        return False
#        text=" ".join(word_list)
#        return text==self.phrase or text.find(" "+self.phrase+" ")!=-1 or text.startswith(self.phrase+" ") or text.endswith(" "+self.phrase)
        

               


# Problem 3
class TitleTrigger(PhraseTrigger):
    def evaluate(self,story):
        return self.is_phrase_in(story.get_title())

# Problem 4
class DescriptionTrigger(PhraseTrigger):
    def evaluate(self,story):
        return self.is_phrase_in(story.get_description())


# TIME TRIGGERS

# Problem 5

class TimeTrigger(Trigger):
    def __init__(self,str_time):
        self.pubdate=datetime.strptime(str_time,"%d %b %Y %H:%M:%S")
        self.pubdate=self.pubdate.replace(tzinfo=pytz.timezone("EST"))
        
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.

# Problem 6
# TODO: BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def evaluate(self,story):
        try:
            return story.pubdate<self.pubdate
        except:
            return story.pubdate.replace(tzinfo=pytz.timezone("EST"))<self.pubdate
class AfterTrigger(TimeTrigger):
    def evaluate(self,story):
        try:
            return story.pubdate>self.pubdate
        except:
            return story.pubdate.replace(tzinfo=pytz.timezone("EST"))>self.pubdate

# COMPOSITE TRIGGERS

# Problem 7
class NotTrigger(Trigger):
    def __init__(self,trigger):
        self.hold_trigger=trigger
    def evaluate(self,story):
        return not self.hold_trigger.evaluate(story)


# Problem 8
class AndTrigger(Trigger):
    def __init__(self,t1,t2):
        self.t1,self.t2=t1,t2
    def evaluate(self,story):
        return self.t1.evaluate(story) and self.t2.evaluate(story)
    
# Problem 9
class OrTrigger(Trigger):
    def __init__(self,t1,t2):
        self.t1,self.t2=t1,t2
    def evaluate(self,story):
        return self.t1.evaluate(story) or self.t2.evaluate(story)    


#======================
# Filtering
#======================

# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    #return stories
    triggered_stories_list=[]
    for story in stories:
        for trigger in triggerlist:
            if(trigger.evaluate(story)):
                triggered_stories_list.append(story)
                break
        
    return triggered_stories_list



#======================
# User-Specified Triggers
#======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    
    
    def get_instance(type,params_list,all_trigger_dict):
        if(len(params_list)==1):
            return type( all_trigger_dict.get(params_list[0],params_list[0]))
        if(len(params_list)==2):
            return type(all_trigger_dict.get(params_list[0],params_list[0]),all_trigger_dict.get(params_list[1],params_list[1]))
        else:
            raise NotImplementedError("Haven't Implement %d params fun, but you in fact don't need this, right?" %len(params_list))
    
    trigger_file = open(filename, 'r')
    
    lines = []
    class_dict = {'TITLE': TitleTrigger, 'DESCRIPTION': DescriptionTrigger, 'AFTER': AfterTrigger, 'BEFORE': BeforeTrigger, 'NOT': NotTrigger, 'AND': AndTrigger, 'OR': OrTrigger}
    
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)
    all_trigger_dict={}
    trigger_added=[]
    for line in lines:
        tmp_list=line.split(',')
        if(tmp_list[0]=='ADD'):
            del(tmp_list[0])
            for t in tmp_list:
                trigger_added.append(all_trigger_dict[t])
                
        else:
            all_trigger_dict[tmp_list[0]]=get_instance(class_dict[tmp_list[1]],tmp_list[2:],all_trigger_dict)

    print(lines) # for now, print it so you see what it contains!
    return trigger_added


SLEEPTIME = 30 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    #try:
        #t1 = TitleTrigger("Trump")
        #t2 = DescriptionTrigger("Trump")
        #t3 = DescriptionTrigger("Clinton")
        #t4 = AndTrigger(t2, t3)
        #triggerlist = [t1, t4]
        
        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line 
        triggerlist = read_trigger_config('triggers.txt')
        
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.yahoo.com/rss/topstories")

            # Get stories from Yahoo's Top Stories RSS news feed
            #stories.extend(process("http://news.yahoo.com/rss/topstories"))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    #except Exception as e:
     #   raise e


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

