import praw
import time
import pickle
from datetime import datetime
from random import randint, random, seed
from pymongo import MongoClient
from uuid import uuid4
seed()
class Trivia:
    def __init__(self, username="r_u_srs_srsly", password="", user_agent_input="r_u_srs_srsly bot"):
        self.mc = MongoClient()
        user_agent = (user_agent_input)
        self.reddit = praw.Reddit(user_agent = user_agent)
        self.reddit.login(username = username, password = password)
        self.active_questions = []
        self.blacklist = set([username])

        
    def pose_question(self, sub, title, text, good_answers, bad_answers, first_bonus=35, min_doge=5, max_doge=20):
        self.active_questions.append({"thread":self.reddit.submit(sub, title, text=text).id, 
                                      "paid_users":set(), 
                                      "good_answers":good_answers,
                                      "bad_answers":bad_answers,
                                      "first_bonus":first_bonus,
                                      "min_doge":min_doge,
                                      "max_doge":max_doge})

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
    
    def pay_users(self):
        payment_line = "such appreciation\n\n\n\n+/u/dogetipbot %s doge"
        for question in self.active_questions:
            submission = self.reddit.get_submission(submission_id=question['thread'])
            for comment in submission.comments:
                try:
                    if comment.author.name in question['paid_users'] or comment.author.name in self.blacklist:
                        pass
                        #TODO: maybe log something here about why users are skipped
                    else:
                        user = self._get_user_from_comment(comment)
                        if user['age'] > 25 or user['verified']:
                            good_answer = False
                            for answer in question['good_answers']:
                                good_answer = good_answer or answer in comment.body.lower()
                            if not good_answer:
                                pass
                                #TODO: maybe tell the user the answer is incorrect?
                            else:
                                tip_ammount = randint(question["min_doge"], question["max_doge"])+random()+question["first_bonus"]
                                tip_comment = payment_line %(str(tip_ammount)[:8])
                                user['gifts'].append({"thread":question["thread"], "ammount":tip_ammount, "timestamp":datetime.now()})
                                user['gifted'] += tip_ammount
                                comment.reply(tip_comment)
                                comment.upvote()
                                question['paid_users'].add(comment.author.name)
                            self.mc.dogelympics.users.save(user)
                except AttributeError:
                    pass #some user probably deleted their comment
            if question["paid_users"]:
                question["first_bonus"] = 0
