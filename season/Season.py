#!/usr/bin/env python

import datetime
import psycopg2
import psycopg2.extras
import sys

class Season:
    '''
    Class used for all season info. This will be used with the Pickem App.
    '''

    def __init__(self):
        '''
        Establish connection with general database.
        '''


        self.dbname = "seasons"
        self.db_table_name = "seasons_info"

        try:
            self.conn = psycopg2.connect("dbname="+self.dbname+"")
        except:
            print "Cannot connect to database. Does it exist?"
            sys.exit()

        self.db = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.current_date = datetime.datetime.now()
        self.current_month = self.current_date.month
        self.current_year = self.current_date.year
        self.current_hour = self.current_date.hour
        self.current_minute = self.current_date.minute
        self.current_season_start_year = None
        self.update_current_season_year()

    def __del__(self):
        self.conn.close()
        self.db.close()

    def update_current_season_year(self):
        '''
        This figures out what season year we are in and updates self.current_season_start_year
        '''

        if self.current_month <= 2:
            self.current_season_start_year = self.current_year - 1
        else:
            self.current_season_start_year = self.current_year


    def start_season(self):
        '''
        Used to start season each year.
        '''

        # See if season already exists

        if self.does_season_exist() is True:
            print "Season already exists for "+str(self.current_season_start_year)+" season."
            return

        # Get season start date

        start_month = 9
        start_day = raw_input("First Game Day: September ")
        start_date = datetime.datetime(self.current_season_start_year, start_month, int(start_day), 8, 25)

        # Logic behind this line:
        # isoweekday() returns the day of the week that it is, 1 - Monday ... 5 - Friday
        # Take 7 days, subtract the day of the week to get # days from next Sunday
        # Add rest of the weeks of the season to that and get the end date
        end_date = start_date + datetime.timedelta(days=((7-start_date.isoweekday())+(16*7)))


        #self.query("insert into seasons (season_year, start_date, end_date) values ('"+str(self.current_season_start_year)+"','"+str(start_date)+"','"+str(end_date)+"');")

        #self.query("insert into "+self.db_table_name+" (season_year, start_date, end_date) values ('"+str(self.current_season_start_year)+"','"+str(start_date)+"','"+str(end_date)+"');")

        try:
            # Create season in the database
            self.query("insert into "+self.db_table_name+" (season_year, start_date, end_date) values ('"+str(self.current_season_start_year)+"','"+str(start_date)+"','"+str(end_date)+"');", True)
        except:
            print "Something went wrong with creating the database"
            sys.exit()


    def does_season_exist(self):
        '''
        Used to find out if there is already a started season.

        returns:
            True - if there is already a started season
            False - if no started season was found
        '''

        result = self.query("select exists (select season_year from "+self.db_table_name+" where season_year = '"+str(self.current_season_start_year)+"' limit 1);", False)

        if "True" in result:
            return True

        return False

    def get_season_year(self):
        return self.current_season_start_year

    def get_current_week(self):
        '''
        Returns the current week that the season is in.
        '''
        # Check if season was ever started

        if self.does_season_exist() is False:
            print "Could not find a started season."
            return


        # Subtract dates to get number of days since start

        start_date = self.get_season_start_date()

        if start_date is None:
            return

        current_date = datetime.datetime.now()

        # Week = (Num days / 7) + 1

        date_difference = (current_date - start_date).days

        current_week = int(date_difference/7) + 1

        return current_week



    def get_season_start_date(self):
        '''
        This gets the start date and returns it as a datetime.datetime() object
        '''

        if self.does_season_exist() is False:
            print "No season has been started yet for this year."
            return

        date = self.query("select start_date from "+self.db_table_name+" where season_year = '"+str(self.current_season_start_year)+"';", False)

        # Strip the brackets and single quotes

        date = date[2:]
        date = date[:len(date)-2]

        fh = (date.split()[0]).split('-')
        lh = (date.split()[1]).split(':')

        year = int(fh[0])
        month = int(fh[1])
        day = int(fh[2])

        hour = int(lh[0])
        minute = int(lh[1])

        return datetime.datetime(year, month, day, hour, minute)


    def user_can_submit(self):
        '''
        Returns true if the time is before the first game of the week, and false otherwise.
        '''

        # Get week it is

        # Add weeks to the start date

        # Check to see if it is before the start of the first game

    def query(self, query_string, save_option):
        '''
        Simple function used to make database queries. Returns the output of the query as a string.
        '''

        self.db.execute(query_string)

        if save_option is True:
            self.conn.commit()

        try:
            return str(self.db.fetchone())
        except:
            return
