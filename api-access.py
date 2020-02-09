import mysql.connector
import urllib.request
import json

def connect():
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost',
                                        database='mysql',
                                        user='root',
                                        password='Trippy@245')
        if conn.is_connected():
            print('Connected to MySQL database')
    
    except Error as e:
        print(e)
    
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

# gets the players basic info and adds it to the database
def getPlayerInfo(id, cursor, conn):

    url_string = "https://statsapi.web.nhl.com/api/v1/people/{}".format(id)
    print("ID {} Info".format(id))
    try:
        url = urllib.request.urlopen(url_string)
        data = json.loads(url.read().decode())

        if data["people"][0]["active"]:
            # print("Active player, adding to DB")
            p_id = data["people"][0]["id"]
            firstname = data["people"][0]["firstName"]
            lastname = data["people"][0]["lastName"]
            j_num = data["people"][0]["primaryNumber"]
            b_date = data["people"][0]["birthDate"]
            curr_team = data["people"][0]["currentTeam"]["name"]
            pos = data["people"][0]["primaryPosition"]["abbreviation"]
            roster = data["people"][0]["rosterStatus"]
            try:
                cursor.execute("INSERT INTO PlayerInfo VALUES (?,?,?,?,?,?,?,?)",
                               p_id, firstname, lastname, j_num, b_date, curr_team, pos, roster)
            except pyodbc.IntegrityError as err:
                if err.args[0] == '23000':
                    print("Duplicate Entry")
                else:
                    raise
        else:
            print("Not active. No add")
    except urllib.error.HTTPError as err:
        if err.code == 404:
            print("404'd")
            # stop = True
        else:
            raise

    return


# gets the player ID's for all the players currently listed on the team's active roster through the NHL stats API
def getPlayerList():
    team_id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16,
               17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 52, 53, 54]
    pList = []
    for x in team_id:
        url_string = "https://statsapi.web.nhl.com/api/v1/teams/{}/roster".format(
            x)
        url = urllib.request.urlopen(url_string)
        rosterData = json.loads(url.read().decode())

        num_players = len(rosterData["roster"])

        for y in range(0, num_players):
            pList.append(rosterData["roster"][y]["person"]["id"])

    return pList


def getPlayerStats(cursor, conn):
    cursor.execute(
        "SELECT P_ID, First_Name, Last_Name FROM PlayerInfo where Position <> 'G'")

    for row in cursor.fetchall():
        id = row[0]
        print(row[1] + ' ' + row[2])

        url_string = "https://statsapi.web.nhl.com/api/v1/people/{}/stats?stats=statsSingleSeason&season=20192020".format(
            id)
        print("ID {} stats".format(id))
        try:
            url = urllib.request.urlopen(url_string)
            data = json.loads(url.read().decode())

            p_id = id
            name = "{} {}".format(row[1],row[2])
            if data["stats"][0]["splits"] != []:

                # print("Active player, adding to DB")
                g = data["stats"][0]["splits"][0]["stat"]["goals"]
                a = data["stats"][0]["splits"][0]["stat"]["assists"]
                p = data["stats"][0]["splits"][0]["stat"]["points"]
                pim = data["stats"][0]["splits"][0]["stat"]["pim"]
                shots = data["stats"][0]["splits"][0]["stat"]["shots"]
                games = data["stats"][0]["splits"][0]["stat"]["games"]
                hits = data["stats"][0]["splits"][0]["stat"]["hits"]
                ppg = data["stats"][0]["splits"][0]["stat"]["powerPlayGoals"]
                ppp = data["stats"][0]["splits"][0]["stat"]["powerPlayPoints"]
                gwg = data["stats"][0]["splits"][0]["stat"]["gameWinningGoals"]
                otg = data["stats"][0]["splits"][0]["stat"]["overTimeGoals"]
                shg = data["stats"][0]["splits"][0]["stat"]["shortHandedGoals"]
                shp = data["stats"][0]["splits"][0]["stat"]["shortHandedPoints"]
                pm = data["stats"][0]["splits"][0]["stat"]["plusMinus"]
                block = data["stats"][0]["splits"][0]["stat"]["blocked"]
                shift = data["stats"][0]["splits"][0]["stat"]["shifts"]

                try:
                    cursor.execute("INSERT INTO PlayerStats VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                   p_id, name, g, a, p, pim, shots, games, hits, ppg, ppp, gwg, otg, shg, shp, pm, block, shift)
                except pyodbc.IntegrityError as err:
                    if err.args[0] == '23000':
                        print("Duplicate Entry")
                    else:
                        raise
            else:
                print("Empty stat list")
                try:
                    cursor.execute("INSERT INTO PlayerStats(ID, FullName) VALUES (?,?)",
                                   p_id, name)
                except pyodbc.IntegrityError as err:
                    if err.args[0] == '23000':
                        print("Duplicate Entry")
                    else:
                        raise
                

        except urllib.error.HTTPError as err:
            if err.code == 404:
                print("404'd")
                # stop = True
            else:
                raise

    return


def getGoalieStats(cursor, conn):
    cursor.execute(
        "SELECT P_ID, First_Name, Last_Name FROM PlayerInfo where Position = 'G'")

    for row in cursor.fetchall():
        id = row[0]

        url_string = "https://statsapi.web.nhl.com/api/v1/people/{}/stats?stats=statsSingleSeason&season=20192020".format(
            id)
        print("ID {} stats".format(id))
        try:
            url = urllib.request.urlopen(url_string)
            data = json.loads(url.read().decode())
            if data["stats"][0]["splits"] != []:

                # print("Active player, adding to DB")
                p_id = id
                name = str(row[1] + ' ' + row[2])
                gp = data["stats"][0]["splits"][0]["stat"]["games"]
                gs = data["stats"][0]["splits"][0]["stat"]["gamesStarted"]
                w = data["stats"][0]["splits"][0]["stat"]["wins"]
                l = data["stats"][0]["splits"][0]["stat"]["losses"]
                otl = data["stats"][0]["splits"][0]["stat"]["ot"]
                so = data["stats"][0]["splits"][0]["stat"]["shutouts"]
                saves = data["stats"][0]["splits"][0]["stat"]["saves"]
                sa = data["stats"][0]["splits"][0]["stat"]["shotsAgainst"]
                pp_sa = data["stats"][0]["splits"][0]["stat"]["powerPlayShots"]
                sh_sa = data["stats"][0]["splits"][0]["stat"]["shortHandedShots"]
                ev_sa = data["stats"][0]["splits"][0]["stat"]["evenShots"]
                ga = data["stats"][0]["splits"][0]["stat"]["goalsAgainst"]
                gaa = data["stats"][0]["splits"][0]["stat"]["goalAgainstAverage"]
                pp_save = data["stats"][0]["splits"][0]["stat"]["powerPlaySaves"]
                sh_save = data["stats"][0]["splits"][0]["stat"]["shortHandedSaves"]
                ev_save = data["stats"][0]["splits"][0]["stat"]["evenSaves"]
                s_per = data["stats"][0]["splits"][0]["stat"]["savePercentage"]
                if 'powerPlaySavePercentage' in data["stats"][0]["splits"][0]["stat"]:
                    pp_save_per = data["stats"][0]["splits"][0]["stat"]["powerPlaySavePercentage"]
                else:
                    pp_save_per = 0
                if 'shortHandedSavePercentage' in data["stats"][0]["splits"][0]["stat"]:
                    sh_save_per = data["stats"][0]["splits"][0]["stat"]["shortHandedSavePercentage"]
                else:
                    sh_save_per = 0
                if 'evenStrengthSavePercentage' in data["stats"][0]["splits"][0]["stat"]:
                    ev_save_per = data["stats"][0]["splits"][0]["stat"]["evenStrengthSavePercentage"]
                else:
                    ev_save_per = 0
                try:
                    cursor.execute("INSERT INTO GoalieStats VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                   p_id, name, gp, gs, w, l, otl, so, saves, sa, pp_sa, sh_sa, ev_sa, ga, gaa, pp_save, sh_save, ev_save, s_per, pp_save_per, sh_save_per, ev_save_per)
                except pyodbc.IntegrityError as err:
                    if err.args[0] == '23000':
                        print("Duplicate Entry")
                    else:
                        raise

        except urllib.error.HTTPError as err:
            if err.code == 404:
                print("404'd")
                # stop = True
            else:
                raise

    return


if __name__ == "__main__":

    connect()

    # choice = input("1 to generate player info\n2 to generate player stats\n3 to generate goalie stats\n")

    # if choice == '1':
    #     plist = getPlayerList()
    #     for x in plist:
    #         print("Getting player info")
    #         getPlayerInfo(x, cursor, conn)
    # elif choice == '2':
    #     print("Getting player stats")
    #     getPlayerStats(cursor, conn)
    # elif choice == '3':
    #     print("Getiting goalie stats")
    #     getGoalieStats(cursor, conn)
    # else:
    #     print("Invalid option. Quitting")

    # conn.commit()
