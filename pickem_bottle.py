#!/usr/bin/env python

'''
Bottle server used to communicate with iOS app
'''

from bottle import (error, get, post, response, request,
                    route, run, static_file, template, url)

from nfldb_access.nfl import NFLDB

from userdb_access.userdb import USERDB

import os
import json

@error(404)
@error(500)
def error_page(error):
    '''
    Handles the errors.
    '''

    _e = response.status_code
    return template("response_html/error.html", error=_e, url=url)


@post('/authenticate')
def authenticate_user():
    '''
    Authenticates user on mobile app
    '''
    # Get json sent by mobile app
    r_json = request.json

    mydb = USERDB()

    print r_json

    # Check to see if user is registered
    if not mydb.userIsRegistered(r_json):
        response = {"success": "false", "error": "User does not exist."}
        return json.dumps(response)

    # Check to see if the username & password combo is correct
    if not mydb.correctUserAndPass(r_json):
        response = {"success": "false", "error": "User or password incorrect."}
        return json.dumps(response)

    # Credentials are correct
    access_credentials = mydb.getAccessCredentials(r_json)

    if access_credentials is "":
        # Something went wrong
        response = {"success": "false", "error": "Something went wrong."}
        return json.dumps(response)
    else:
        # return the OK'd access Credentials
        print access_credentials
        return template("response_html/user_tokens.html", tokens=access_credentials)

@post('GetGamePicks')
def get_game_picks():
    '''
    Sees if the user already has game picks submitted. Returns them if they do.
    '''
    r_json = request.json
    mydb = USERDB()
    picks = mydb.get_user_picks(json.loads(r_json))

    return template("response_html/user_game_picks.html", picks=picks)



@post('/registernewuser')
def register_new_user():
    '''
    Registers a new user in the database
    '''

    # Get the json sent by mobile app
    r_json = request.json
    mydb = USERDB()
    userdb_response = mydb.register_new_user(r_json)

    return template("response_html/user_registration.html", response=userdb_response)


@post('/SubmitPicks')
def submit_this_weeks_picks():
    '''
    Submits the picks for the user.
    '''
    # Get json sent by mobile app
    r_json  = request.json
    mydb = USERDB()
    userdb_response = mydb.saveUsersPicks(r_json)

    return template("response_html/submit_picks_response.html", response=userdb_response)


@get('/current-season-weeks')
def get_current_season_weeks():
    '''
    Returns available weeks for the current season_year
    '''

    mydb = NFLDB()
    weeks = mydb.getWeeks()
    return template("response_html/weekList.html", weekList=weeks)

@route('/gamelist')
def get_game_list():
    '''
    Returns the current week's game list
    '''
    mydb = NFLDB()
    games = mydb.getGameList(2017,6)
    return template("response_html/gameList.html", gameList=games)

run(host='localhost', port=8080, debug=True)
