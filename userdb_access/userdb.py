#!/usr/bin/env python

import psycopg2
import psycopg2.extras
import json
import random
import string

class USERDB:
    '''
    Class for interacting with user_login_info DB
    '''

    def __init__(self):
        '''
        Establish connection with database
        '''
        self.conn = psycopg2.connect("dbname=user_info")
        self.db = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.userIsLoggedIn = False

    def __del__(self):
        self.conn.close()
        self.db.close()

    def register_new_user(self, u_info):
        '''
        Registers a new user in the DB if it is not a duplicate.

        @params
           u_info - a json object with the user information
        '''

        response = {}

        #############################################################
        # Check to see if the user already exists via email address #
        #############################################################

        #self.db.execute("select exists (select email_address from user_info where email_address = '"+str(u_info['email'])+"' limit 1);")
        #row = self.db.fetchone()

        if self.userIsRegistered(u_info):
            # User is already in the system
            print "User already exists"
            response["success"] = "false"
            response["error"] = "User already exists."
            return json.dumps(response)

        # User is not in the DB anymore.. we can add to DB now
        self.db.execute("INSERT INTO user_login_info (first_name, last_name, email_address, password) VALUES (\'"+str(u_info["firstName"])+"\', \'"+str(u_info["lastName"])+"\',\'"+str(u_info["userEmail"])+"\', \'"+str(u_info["password"])+"\');")

        self.conn.commit()

        response["success"] = "true"

        return json.dumps(response)

    def userIsRegistered(self, u_info):
        '''
        Used to check if the user trying to login is actually registered

        @params
            u_info - a json object with the user information
        '''

        email_address = str(u_info["userEmail"])

        self.db.execute("select exists (select email_address from user_login_info where email_address = '"+email_address+"' limit 1);")
        if "True" in str(self.db.fetchone()):
            return True
        else:
            return False



    def correctUserAndPass(self, u_info):
        '''
        Checks if the username and password are correct. If they are then it
        returns True. If not it returns false.

        @params
            u_info - a json object with the user information
        '''

        email_address = str(u_info["userEmail"])
        p = str(u_info["userPassword"])

        self.db.execute("select exists (select email_address from user_login_info where email_address = '"+email_address+"' and password = '"+p+"' limit 1);")

        if "True" in str(self.db.fetchone()):
            return True
        else:
            return False


    def getAuthToken(self, u_info):
        '''
        Gets the auth token from the database for the u_info Credentials

        @params
            u_info - a json object with the user information
        '''

        email_address = str(u_info["userEmail"])

        self.db.execute("select auth_token from user_login_info where email_address = '"+email_address+"';")
        return self.db.fetchone()[0]

    def getUserId(self, u_info):
        '''
        Gets the userId from the database for the u_info Credentials

        @params
            u_info - a json object with the user information
        '''

        email_address = str(u_info["userEmail"])

        self.db.execute("select user_id from user_login_info where email_address = '"+email_address+"';")
        return self.db.fetchone()[0]


    def getAccessCredentials(self, u_info):
        '''
        Returns the userId and access token for the logged in user ONLY if there
        is a user already logged in. If not, it errors out.
        '''

        response = {}

        # Double check to make sure this is good
        if self.correctUserAndPass(u_info) is False:
            return ""

        email_address = str(u_info["userEmail"])

        new_token = str(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25)))

        # Set new auth token
        self.db.execute("update user_login_info set auth_token = '"+new_token+"' where email_address = '"+email_address+"';")
        self.conn.commit()


        # Get auth token just to be sure
        response["success"] = "true"
        response["token"] = self.getAuthToken(u_info)
        response["id"] = str(self.getUserId(u_info))

        return json.dumps(response)

    def getUsersPicks(self, payload):
        '''
        This checks to see if the user has submitted picks yet. If they have then it
        will return their picks
        '''

        #p = json.loads(payload)
        #token = p["accessToken"]
        #user_id = p["userId"]
        response = {}
        user_id = '4'


        # Check to make sure the auth token is good
        #if not checkAccessToken(user_id, token):
            #response["success"] = "false"
            #response["error"] = "Unauthorized"
            #return json.dumps(response)

        # Run query for the game picks
        self.db.execute("select game_picks from game_picks_week_9 where user_id = "+user_id+";")

        query_result = self.db.fetchone()

        if query_result is None:
            response["success"] = "true"
            response["error"] = "No submission"
            return json.dumps(response)


        response["success"] = "true"
        response["game_picks"] = str(query_result[0]).split(",")

        return json.dumps(response)


    def saveUsersPicks(self, payload):

        #p = json.loads(payload)
        token = payload["accessToken"]
        user_id = payload["userId"]
        picks = []
        response = {}

        for p in payload["gamePicks"]:
            picks.append(str(p))

        picks = ','.join(picks)

        # Check if time is good



        # Check to make sure the access Token is good

        if not self.checkAccessToken(user_id, token):
            response["success"] = "false"
            response["error"] = "Unauthorized"
            return json.dumps(response)


        # See if the user has already made an entry
        self.db.execute("select exists (select user_id from game_picks_week_9 where user_id = '"+user_id+"' limit 1);")
        if "True" in str(self.db.fetchone()):
            self.db.execute("update game_picks_week_9 set game_picks = '"+picks+"' where user_id = '"+user_id+"';")
        else:
            self.db.execute("insert into game_picks_week_9 (user_id, game_picks) values ("+user_id+", '"+picks+"');")

        self.conn.commit()

        response["success"] = "true"

        return json.dumps(response)

    def checkAccessToken(self, username, accessToken):
        '''
        Returns true if the access token matches the user's accessToken and
        false if not
        '''

        self.db.execute("select exists (select auth_token from user_login_info where auth_token = '"+accessToken+"' and user_id = "+username+" limit 1);")
        if "True" in str(self.db.fetchone()):
            return True
        else:
            return False

    def get_user_picks(self, payload):
        '''
        Checks to see if the user already has game picks and returns them.
        '''

        response = {}

        if not self.checkAccessToken(payload["userId"], payload["accessToken"]):
            response = {"success": "false", "error": "User logged in on another device. Please login again."}
            return json.dumps(response)

        # See if there are any game picks
        self.db.execute("select exists (select user_id from game_picks_week_9 where user_id = '"+payload["userId"]+"' limit 1);")
        if "False" in str(self.db.fetchone()):
            response = {"success": "true"}
            return json.loads(response)

        self.db.execute("select game_picks from game_picks_week_9 where user_id = '"+payload["userId"]+"';")
        picks = str(self.db.fetchone())
        response["picks"] = picks[2:len(picks)-2].split(',')
        response["success"] = "true"

        return json.dumps(response)
