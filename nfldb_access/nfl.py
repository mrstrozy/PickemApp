import nfldb
import json


class NFLDB():
    '''
    Class for interacting with NFLDB
    '''
    def __init__(self):
        '''
        Init/Establish connection with database
        '''
        self.db = nfldb.connect()

    def __del__(self):
        '''
        Close the connection with the db
        '''
        self.db.close()

    def getWeeks(self):
        '''
        Returns the weeks that are available
        '''
        weeks = []
        weekDict = {}

        q = nfldb.Query(self.db)
        q.game(season_year=2017, season_type='Regular')

        for game in q.as_games():
            game_str = str(game).split()
            if game_str[3] not in weeks:
                weeks.append(int(game_str[3]))

        weekDict['available_weeks'] = str(sorted(set(weeks)))
        return json.dumps(weekDict)


    def getGameList(self, year, week):
        '''
        Returns the list of the week's games in json
        '''

        q = nfldb.Query(self.db)
        q.game(season_year=year, week=week, season_type='Regular')

        statistics = {'stats': []}
        #statistics = []

        for game in q.as_games():
            game_stats = {}
            game_str = str(game).split()
            game_stats['week'] = game_str[3]
            game_stats['date'] = game_str[5]
            game_stats['away_team'] = game_str[8]
            game_stats['home_team'] = game_str[11]

            # Convert time to 24hr clock time
            time = str(game_str[7]).split(',')[0]

            if "pm" in time.lower():
                # Make into array split by ":"
                t = (time.lower().split('pm'))[0].split(":")

                # Add 12 hours for conversion
                t[0] = str(int(t[0]) + 12)

                time = ':'.join(t)
            game_stats['time'] = time

            statistics['stats'].append(game_stats)

        return json.dumps(statistics)


#print NFLDB().getGameList(2017, 6)
