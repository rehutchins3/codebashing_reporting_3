from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, DateField, FileField
from wtforms.validators import DataRequired, Optional
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import date
from reporting import CreateCSVExport, CreateCVSUnmatchedCbEmails
import requests
import json
import csv
import os
import re
# import main   # I don't know where this line came from. Think from use of main. to access the global vars?


app = Flask(__name__)


# Flask-WTF requires an encryption key - the string can be anything
# Random key courtesy of https://randomkeygen.com/
app.config['SECRET_KEY'] = 'Sw?'
app.config['UPLOAD_FOLDER'] = Path("uploaded_files")
app.config['MAX_CONTENT_PATH'] = '5000'
app.config['GENERATED_REPORT_FOLDER'] = Path("generated_reports")


# Flask-Bootstrap requires this line
Bootstrap(app)


# -------------------------------------------------------------------------------
#
#                   GLOBALS
#
# -------------------------------------------------------------------------------
employeeList = []  # Object array of employees. (This really is an array of Objects.)
managerList = []  # Object array of managers (users are either employees or managers)
cb_emails_not_found = []  # list of all of the emails in CB not found in hierarchy list
report_unmatched_emails = True  # Option for the user to run this report; default to True
hierarchy_report_filename = ""  # The name of the file the user uploaded that contains user and manager info.
gen_rpt_all_employee_data_filename = ""  # Filename of the generated report. Needed to create download hyperlink.
gen_rpt_missing_emails_filename = ""  # Filename of the generated report. Needed to create download hyperlink.

# Note: These dates only impact Course completions. In-progress courses will always be reported.
data_start_date = date(2020, 1, 1)  # Date object; Include only course COMPLETIONS on or after this date (YYYY, MM, DD)
data_end_date = date(2099, 12, 31)  # Date object; Include only course COMPLETIONS on or before this date (YYYY, MM, DD)

# String array of valid courses. Append 'percentage' or 'date' to use as
# key in empResponse list object.
valid_course_list = ["java.completed_",
                     "dotnet.completed_",
                     "php.completed_",
                     "nodejs.completed_",
                     "ruby.completed_",
                     "python.completed_",
                     "scala.completed_",
                     "cplus.completed_",
                     "ios.completed_",
                     "android.completed_",
                     "go.completed_",
                     "frontend.completed_",
                     "http.completed_",
                     "source_codes.completed_",
                     "backend_java.completed_",
                     "backend_dotnet.completed_",
                     "java_advanced_lessons.completed_",
                     "dotnet_advanced_lessons.completed_",
                     "angular.completed_",
                     "python_advanced_lessons.completed_",
                     "angular_js.completed_",
                     "dotnet_api_security.completed_",
                     "java_api_security.completed_",
                     "application_security_for_qa.completed_",
                     "application_security_for_decision_makers.completed_",
                     "java_advanced_lessons2.completed_",
                     "dotnet_advanced_lessons2.completed_",
                     "python_advanced_lessons2.completed_",
                     "react.completed_"]


class Manager:
    email = ""
    fullName = ""  # Between 0 and 1
    srLeader = ""
    portfolio = ""

    def __init__(self, email, fullName, srLeader, portfolio):
        self.email = email
        self.fullName = fullName
        self.srLeader = srLeader
        self.portfolio = portfolio


class Employee:
    courses_completed = 0
    completion_percentage = 0  # Between 0 and 1
    courses_in_progress = 0
    courses_in_progress_completion_percentage = 0

    managerId = ""
    employeeId = ""
    employeeDomain = ""

    CbTeam = ""
    Level1Mgr = ""
    Level2Mgr = ""
    Level3Mgr = ""
    Portfolio = ""

    def __init__(self, employeeId, managerId, employeeDomain):
        self.managerId = managerId
        self.employeeId = employeeId
        self.employeeDomain = employeeDomain

    def serialize(self):
        return {"employeeId": self.employeeId,
                "employeeDomain": self.employeeDomain,
                "managerId": self.managerId,
                "courses_completed": self.courses_completed,
                "completion_percentage": self.completion_percentage,
                "courses_in_progress": self.courses_in_progress,
                "courses_in_progress_completion_percentage": self.courses_in_progress_completion_percentage,
                "Codebashing Team": self.CbTeam,
                "Level 1 Mgr": self.Level1Mgr,
                "Level 2 Mgr": self.Level2Mgr,
                "Level 3 Mgr": self.Level3Mgr,
                "Portfolio": self.Portfolio}


class CbDataForm(FlaskForm):
    frm_hierarchy_file = FileField('Select the hierarchy file for your organization.', validators=[DataRequired()])
    frm_report_start_date = DateField('Enter an optional start date for the report (YYYY-MM-DD)',
                                      validators=[Optional()])
    frm_report_end_date = DateField('Enter an optional end date for the report (YYYY-MM-DD)', validators=[Optional()])
    frm_unmatched_emails_bool = BooleanField('Export list of unmatched e-mails?')
    submit = SubmitField('Submit')


# Load managers from the CSV
# As of 11-23-2021 this function is not referenced anywhere.
def loadManagers():
    print(" Starting Manager Load ")

    with open('curr_codebashing_users_2021.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["privileges"] == "Manager":
                managerList.append(
                    Manager(row['email'], row['teams'], lookupSrLeader(row['teams']), lookupOrgName(row['teams'])))

    print(" Manager Load Complete ")

# As of 11-23-2021, this function can be rewritten to use the information in the file
# the user uploads, which contains their list of codebashing employees and hierarchy (hierarchy_report_filename).
def loadEmployees():
    print(" Starting Employee Load ")
    with open('curr_codebashing_users_2021.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Need to add check to verify that the user isn't a manager -
            if ((row["privileges"] == "User") and (isManager(row['email']) == False)):
                employeeList.append(Employee(row['email'], row['teams'], lookupOrgName(row['teams'])))

    print(" Employee Load Complete ")


'''
This is the main functionality of the script.
For each employee, it iterates over the CB JSON object, pulling the
course progress.
'''


def get_employee_progress(empResponse):
    total_courses_completed = 0
    total_percentage_complete = 0
    total_number_courses_in_progress = 0
    total_percentage_in_progress = 0
    for course in valid_course_list:
        # Get the course completion info for the employee
        cb_course_complete_pct_float = float(empResponse[course + "percentage"])
        cb_course_complete_date_str = empResponse[course + "date"]

        if cb_course_complete_date_str is not None:
            # print("cb_course_complete_date_str :" + cb_course_complete_date_str)
            cb_course_complete_date_obj = get_date_obj_from_date_str(cb_course_complete_date_str)

        # If the cb_courses_complete_pct_float is 100.00 then
        #   Check to see if the course was completed on or after the report_start_date.
        #       If YES, then update the total_courses_completed and total_percentage_complete.
        #       If NO, then do nothing.
        # If the cb_course_complete_pct_float is not 0 and not 100.00 then
        #       Update the total_number_courses_in_progress
        #       Update the total_percentage_in_progress
        # After all evaluation is complete, divide the total_percentage_in_progress by the
        # total_percentage_in_progress to calculate the average percentage complete.
        if cb_course_complete_pct_float == 100.00:
            # if compare_report_start_date_to_cb_completed_date(cb_course_complete_date_obj):
            if compare_cb_date_to_report_dates(cb_course_complete_date_obj):
                total_courses_completed += 1
                total_percentage_complete += 100.00
        else:
            if cb_course_complete_pct_float != 0:
                total_number_courses_in_progress += 1
                total_percentage_in_progress += cb_course_complete_pct_float

    return {'total_courses_completed': total_courses_completed, 'total_percentage_complete': total_percentage_complete,
            'total_number_courses_in_progress': total_number_courses_in_progress,
            'total_percentage_in_progress': total_percentage_in_progress}


'''
Trying out a method here to validate that the user input for dates was not tampered with in ttransit
by checking to make sure it only contains numbers, dashes, and in the specified pattern NNNN-NN-NN.
If the data is offered in any other way, the code will return False.
'''


def validate_user_input_date_field(user_date):
    regex = r"\d{4}-\d{1,2}-\d{1,2}"
    matches = re.finditer(regex, user_date, re.MULTILINE)

    if matches is None:
        return False
    else:
        return True

'''
This function takes the date from the CB JSON response and turns it into a Date object
that can be used for comparisons with the globals data_start_date and data_end_date
'''


def get_date_obj_from_date_str(date_str):
    cd_date_substr = date_str[0:10]
    cb_date_obj = date.fromisoformat(cd_date_substr)

    return cb_date_obj


'''
This function takes the date from the CB JSON response and compares it with
the global data_start_date. This function is not currently being called anywhere.
It could be deprecated, but keeping it around in case it's needed later.
'''


def compare_report_start_date_to_cb_completed_date(date_obj):
    if data_start_date > date_obj:
        return False
    else:
        return True


'''
This function takes the date from the CB JSON response and compares it with
the global data_start_date and data_end_date. This is needed to support the
ability to report a start and end date for the report and exclude data that
does not fall on or between those dates.
'''


def compare_cb_date_to_report_dates(date_obj):
    if (date_obj >= data_start_date) and (date_obj <= data_end_date):
        return True
    else:
        return False


def isManager(userEmail):
    for currManager in managerList:
        if currManager.email == userEmail:
            return True

    return False


# --------------------------------------------------------------------------------------------------
# This function gets the employee's management hierarchy and portfolio information from the
# uploaded hierarchy_report_filename.
#
# ---------------------------------------------------------------------------------------------------
def lookup_org_structure(cb_email):

    with open(os.path.join(app.config['UPLOAD_FOLDER'], hierarchy_report_filename), newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        print("Obtaining Org Structure for Employee " + cb_email)
        org_structure = [org_dict for org_dict in reader if org_dict['user_email'] == cb_email]
        if len(org_structure) == 0:
            cb_emails_not_found.append(cb_email)
            print("Org Structure for Employee " + cb_email + " not found. Adding to missing emails list.")
        else:
            org_structure_dict = (org_structure[0])
            print("Org Structure for Employee " + cb_email + " Complete")
            # print(org_structure_dict)
            return org_structure_dict


# --------------------------------------------------------------------------------------------------
# Input: name of the Front-Line manager
# Output: AppOwner that the FLM reports to
#
# --------------------------------------------------------------------------------------------------
def lookupSrLeader(managerName):
    with open('sr_leader_map.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        print("Manager Fields")
        for currEle in headers:
            print(currEle)

        for row in reader:
            if row['managerof'] == managerName:
                return row['appowner']
        # If the manager name can't be found in the
        return "NA"


# --------------------------------------------------------------------------------------------------
# Input: name of the Front-Line manager
# Output: Organization that the FLM is part of
#
# --------------------------------------------------------------------------------------------------
def lookupOrgName(managerName):
    with open('sr_leader_map.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['managerof'] == managerName:
                return row['orgname']
        # If the manager name can't be found in the
        return "NA"


# -------------------------------------------------------------------------------
# Input     : list of employees to have their completion rate and number of courses completed  populated
# Output    :
#
# -------------------------------------------------------------------------------
def loadCompletionRates():
    # Rich for testing purposes
    print("Attempting Request")

    # get a refreshed dataset from CB. verify=False needs to be fixed to handle certificates
    r = requests.get("https://paychex.codebashing.com/api/v1/users/sign_in_and_course_info",
                     headers={"X-Api-Key": "djf",
                              "Authorization": "Bearer Jho"}, verify=False)



    # Rich for testing purposes
    print("Request Successful")

    user_rest_data = json.loads(r.text)

    # Rich for testing purposes
    print("json load Successful")

    # for each user in the json object being passed to us, populate their completion stats
    for currRespEmp in user_rest_data:
        # Try to find that user's email in the employee list that was passed to the
        for currListEmp in employeeList:
            # If the current user is the same as the Rest data user...
            if currListEmp.employeeId == currRespEmp['email']:

                employee_data_dict = get_employee_progress(currRespEmp)
                currListEmp.courses_completed = employee_data_dict['total_courses_completed']
                currListEmp.completion_percentage = employee_data_dict['total_percentage_complete']
                currListEmp.courses_in_progress = employee_data_dict['total_number_courses_in_progress']
                currListEmp.courses_in_progress_completion_percentage = employee_data_dict['total_percentage_in_progress']

                employee_org_structure_dict = lookup_org_structure(currRespEmp['email'])

                if employee_org_structure_dict is not None:
                    currListEmp.CbTeam = employee_org_structure_dict['teams']
                    currListEmp.Level1Mgr = employee_org_structure_dict['Level_1']
                    currListEmp.Level2Mgr = employee_org_structure_dict['Level_2']
                    currListEmp.Level3Mgr = employee_org_structure_dict['Level_3']
                    currListEmp.Portfolio = employee_org_structure_dict['Portfolio']

    print("Missing cb_emails list compiled successfully.")
    # print(cb_emails_not_found)


# ------------------------------------------------------------------------------------------------------
# About @app.route in this script:
# app.route '/' and app.route is required. To force the app to start on the form, might want to assign that
# index route (/) to contain the code that's currently in /home
# If you want to step through the data updates or subroutines manually:
    # Run /update-data to get updated codebashing completion data then...
    # Run /employees to view the updated codebashing completion data...
    # Run /report-csv to export the results to a csv file.
# The program flow is as follows:
    # /home is the way to start the app with the input form; likely how we want to run this going forward
    # /home collects report params and then calls /data-refresh which kicks off a bunch of updates
    # /data-refresh then calls /report-csv to generate the report(s) the user selected
    # /data-refresh then redirects to /download-page which is the html page with links to download the reports
    # /download accepts a function name and param from the html page and downloads the selected file
# ------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return 'Index Page'


# How to JSONify a list of objects - https://stackoverflow.com/questions/21411497/flask-jsonify-a-list-of-objects
@app.route('/employees')
def getEmps():
    return jsonify(emps=[e.serialize() for e in employeeList])


@app.route('/data-refresh')
def data_refresh():
    # loadManagers()
    loadEmployees()
    loadCompletionRates()
    getEmps()
    make_report_csv()

    print("Data Refresh Successful!")
    return redirect(url_for('create_download_page'))


@app.route('/report-csv')
def make_report_csv():

    global gen_rpt_all_employee_data_filename
    gen_rpt_all_employee_data_filename = CreateCSVExport(employeeList, app.config['GENERATED_REPORT_FOLDER'])

    if report_unmatched_emails:
        global gen_rpt_missing_emails_filename
        gen_rpt_missing_emails_filename = CreateCVSUnmatchedCbEmails(cb_emails_not_found,
                                                                     app.config['GENERATED_REPORT_FOLDER'])
        print(cb_emails_not_found)

    return None


@app.route('/download-page')
def create_download_page():

    rendered = render_template('download_rpts.html', showfield=report_unmatched_emails)

    return rendered


@app.route('/<rpt_name>/download', methods=['GET', 'POST'])
def download_file(rpt_name):
    # The path var, the two assignments in the conditionals and the last return statement
    # all go together as part of the last return statement. I switched to a more secure
    # way of delivering the file using send_from_directory, which takes different arguments.
    # Long way of saying, those lines can be deleted after some additional testing.
    # path = ""

    if rpt_name:
        if rpt_name == "progress":
            file = gen_rpt_all_employee_data_filename
            # path = os.path.join(app.root_path, app.config['GENERATED_REPORT_FOLDER'], file)
            return send_from_directory(app.config['GENERATED_REPORT_FOLDER'], file, as_attachment=True)
        else:
            if rpt_name == "email":
                file = gen_rpt_missing_emails_filename
                # path = os.path.join(app.root_path, app.config['GENERATED_REPORT_FOLDER'], file)
                return send_from_directory(app.config['GENERATED_REPORT_FOLDER'], file, as_attachment=True)

        # return send_file(path, as_attachment=True)
    else:
        return "No report type specified or the specified file does not exist."


@app.route('/home', methods=['GET', 'POST'])
def get_report_input():
    form = CbDataForm()

    # Get data from the form
    usr_frm_hierarchy = form.frm_hierarchy_file.data
    usr_form_start = form.frm_report_start_date.data
    usr_form_end = form.frm_report_end_date.data
    usr_form_collect_unmatched_emails = form.frm_unmatched_emails_bool.data

    if form.validate_on_submit():

        # Convert the dates from the form to date objects to be used in code then set globals
        # that are referenced to pull progress data.
        global data_start_date
        data_start_date = get_date_obj_from_date_str(str(usr_form_start))
        global data_end_date
        data_end_date = get_date_obj_from_date_str(str(usr_form_end))

        # Set the Global based on user selection.
        global report_unmatched_emails
        report_unmatched_emails = form.frm_unmatched_emails_bool.data

        # Grab the hierarchy file the user provided and put it in the UPLOAD_FOLDER then set the
        # Global so we know which file to use when we pull employee progress.
        f = request.files['frm_hierarchy_file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        global hierarchy_report_filename
        hierarchy_report_filename = secure_filename(f.filename)

        # Once we're done with all of the form data, let the app do its magic!
        return redirect(url_for('data_refresh'))
    else:
        message = "Please fill in all fields on this page."

    # If form.validate_on_submit() hasn't been called (new form) or it's failed, display the form with the values below
    return render_template('reportpage.html', hierarchy=usr_frm_hierarchy, start=usr_form_start,
                           end=usr_form_end, unmatched=usr_form_collect_unmatched_emails, form=form, message=message)


if __name__ == "__main__":
    data_refresh
