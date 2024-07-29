import requests
import json
# import csv
# import os
# from werkzeug.utils import secure_filename
# from pathlib import Path

#  GLOBALS
r = ""
parse_style = "TeamName_+_UserEmails"

'''7/29/2024 - Comment to trigger a secrets scan of this file. Delete this later..'''


def load_team_info():
    # Rich for testing purposes
    print("Attempting Request For Teams Info...")

    # get a refreshed dataset from CB. verify=False needs to be fixed to handle certificates
    global r
    r = requests.get("https://paychex.codebashing.com/api/v1/teams/team_info",
                     headers={"X-Api-Key": "X",
                              "Authorization": "Bearer Y"}, verify=False)

    # Rich for testing purposes
    print("Request For Teams Info Successful!")

    teams_rest_data = json.loads(r.text)

    # Rich for testing purposes
    print("Teams Info JSON Load Successful")

    #  Now that we have an object containing the Team Info, let's go to the _handler to see how the user
    #  wants to see the Team Info.
    parse_team_info_handler()




'''
For now, there's only one way we're parsing the Team Info data. This _exists to direct code flow later
wehn/if we introduce features to let the user select different ways to parse the Team Info. If that occurs, there
will be multiple parse_team_info_() methods to handle the different code flow and formatting for different selections. 

This approach will keep the parse_team_info_* methods cleaner as opposed to trying to write a bunch of ifs and elifs to 
handle the different output options. 

Right now, there's only one parse_style and it is hard-coded in the GLOBALS section.
'''
def parse_team_info_handler():
    print("Made it to parse_team_info_handler.")

    if parse_style == "TeamName_+_UserEmails":
        parse_team_info_teamname_useremails()


def parse_team_info_teamname_useremails():
    print("Made it to parse_team_info_teamname_useremails.")
    create_csv_teams_info_report("report_data", "report_headings")


def create_csv_teams_info_report(report_data, report_headings):
    '''
    Eventually, this needs to be handled like the other reports in main.py. But, for now, can just be a dead end.
    report_data will be the formatted team info. The report_headings will be a collection of strings representing the
    headings that will match the report output. Will have to import reporting.py for the call to work too.

    example:
    gen_rpt_missing_emails_filename = CreateCVSUnmatchedCbEmails(cb_emails_not_found,
                                                                     app.config['GENERATED_REPORT_FOLDER'])

    '''

    print("Made it to create_csv_teams_info_report.")
