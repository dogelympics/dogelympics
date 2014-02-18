import praw
import leveldb
import time
from datetime import datetime
from random import randint, random, seed
from pymongo import MongoClient
from uuid import uuid4
seed()
class Sweepstakes:
    def __init__(self, username="r_u_srs_srsly", password="", user_agent_input="r_u_srs_srsly bot"):
        self.mc = MongoClient()
        user_agent = (user_agent_input)
        self.reddit = praw.Reddit(user_agent = user_agent)
        self.reddit.login(username = username, password = password)
        self.current_thread = None
        self.blacklist = set([username])
        
    def create_thread(self, sub, title, text):
        if not self.current_thread:
            self.current_thread = self.reddit.submit(sub, 
                                                    title, 
                                                    text=text).id   
    def close_thread(self, ):
        #consider updating post to say over
        self.current_thread = None
    
    def _get_user_from_comment(self, comment):
        user = None
        try:
            user = list(self.mc.dogelympics.users.find({"name":comment.author.name}))[0]
        except IndexError:
            user = {"name":comment.author.name,
                    "verified":comment.author.has_verified_email, 
                    "created":comment.author.created_utc,
                    "age":(time.time()-comment.author.created_utc)/60/24,
                    "gifted":0,
                    "gifts":[]}
        
        user['age'] = (time.time()-comment.author.created_utc)/60/24
        return user
    
    def _get_doge_tip(self, min_doge, max_doge, total_gifts):
        return randint(min_doge,max_doge)+random()
    
    def run_round(self, 
                  round_name,
                  min_doge=5,
                  max_doge=6):
        dogeline = "    such appreciation\n\n\n\n+/u/dogetipbot %s doge"
        round_data = {"round_name": round_name,
                      "users": [],
                      "timestamp":datetime.now()}
        submission = self.reddit.get_submission(submission_id=self.current_thread)
        for comment in submission.comments:
            try:
                if comment.author.name in round_data["users"] or comment.author.name in self.blacklist:
                    pass
                    #TODO: maybe respond to user why this comment wont work
                else:
                    user = self._get_user_from_comment(comment)
                    if user['age'] > 25:
                        tip_ammount = self._get_doge_tip(min_doge, max_doge, user['gifted'])
                        tip_comment = dogeline %(str(tip_ammount)[:8])
                        user['gifts'].append({"thread":self.current_thread, "ammount":tip_ammount, "timestamp":datetime.now()})
                        user['gifted'] += tip_ammount
                        round_data["users"].append(comment.author.name)
                        comment.reply("              "+round_name+"\n\n"+tip_comment)
                        comment.upvote()
                        self.mc.dogelympics.users.save(user)
            except AttributeError:
                pass #user probably deleted their post
        self.mc.dogelympics.rounds.save(round_data)
        print datetime.now() 
        
