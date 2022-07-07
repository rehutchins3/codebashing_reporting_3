from flask import Flask

# This file just a placeholder for some of Chris's original code.



# This function can be deprecated in favor of get_employee_progress_date_forward()
def getCurrPercentComplete(empResponse):
    totalPercentage = 0
    totalPercentage += float(empResponse["java.completed_percentage"])
    totalPercentage += float(empResponse["dotnet.completed_percentage"])
    totalPercentage += float(empResponse["php.completed_percentage"])
    totalPercentage += float(empResponse["nodejs.completed_percentage"])
    totalPercentage += float(empResponse["ruby.completed_percentage"])
    totalPercentage += float(empResponse["python.completed_percentage"])
    totalPercentage += float(empResponse["scala.completed_percentage"])
    totalPercentage += float(empResponse["cplus.completed_percentage"])
    totalPercentage += float(empResponse["ios.completed_percentage"])
    totalPercentage += float(empResponse["android.completed_percentage"])
    totalPercentage += float(empResponse["go.completed_percentage"])
    totalPercentage += float(empResponse["frontend.completed_percentage"])
    totalPercentage += float(empResponse["http.completed_percentage"])
    totalPercentage += float(empResponse["source_codes.completed_percentage"])
    totalPercentage += float(empResponse["backend_java.completed_percentage"])
    totalPercentage += float(empResponse["backend_dotnet.completed_percentage"])
    totalPercentage += float(empResponse["java_advanced_lessons.completed_percentage"])
    # Rich removed as microlessons no longer being reported in api
    # totalPercentage += float(empResponse["microlessons.completed_percentage"])
    # This course is being doubler-counted
    # totalPercentage += float(empResponse["source_codes.completed_percentage"])
    totalPercentage += float(empResponse["dotnet_advanced_lessons.completed_percentage"])
    # Rich added courses below as new Codebashing content for 2021.
    totalPercentage += float(empResponse["angular.completed_percentage"])
    totalPercentage += float(empResponse["python_advanced_lessons.completed_percentage"])
    totalPercentage += float(empResponse["angular_js.completed_percentage"])
    totalPercentage += float(empResponse["dotnet_api_security.completed_percentage"])
    totalPercentage += float(empResponse["java_api_security.completed_percentage"])
    totalPercentage += float(empResponse["application_security_for_qa.completed_percentage"])
    totalPercentage += float(empResponse["application_security_for_decision_makers.completed_percentage"])
    totalPercentage += float(empResponse["java_advanced_lessons2.completed_percentage"])
    totalPercentage += float(empResponse["dotnet_advanced_lessons2.completed_percentage"])
    totalPercentage += float(empResponse["python_advanced_lessons2.completed_percentage"])
    totalPercentage += float(empResponse["react.completed_percentage"])

    return totalPercentage

# This function can be deprecated in favor of get_employee_progress_date_forward()
def getNumberOfCoursesComplete(empResponse):
    totalCoursesCompleted = 0
    if empResponse["java.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["dotnet.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["php.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["nodejs.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["ruby.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["python.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["scala.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["cplus.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["ios.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["android.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["go.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["frontend.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["http.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["source_codes.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["backend_java.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["backend_dotnet.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["java_advanced_lessons.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    # Rich removed as microlessons no longer being reported in api
    # if empResponse["microlessons.completed_percentage"] == 100.00:
    # totalCoursesCompleted += 1
    # The course below is being double-counted
    # if empResponse["source_codes.completed_percentage"] == 100.00:
    # totalCoursesCompleted += 1
    if empResponse["dotnet_advanced_lessons.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    # Rich added courses below as new Codebashing content for 2021.
    if empResponse["angular.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["python_advanced_lessons.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["angular_js.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["dotnet_api_security.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["java_api_security.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["application_security_for_qa.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["application_security_for_decision_makers.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["java_advanced_lessons2.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["dotnet_advanced_lessons2.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["python_advanced_lessons2.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1
    if empResponse["react.completed_percentage"] == 100.00:
        totalCoursesCompleted += 1

    return totalCoursesCompleted




app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/dates')
def date_compare():
    # Repurpose this rather overdone function if you need to check to see
    # if Codebashing data occurred on or after a particular date. This is
    # useful to simply see if progress is part of the current Codebashing
    # training campaign.

    print("Global data start date:")
    print(data_start_date)
    print("")

    t_usr_start_date_str = "2021-10-01"
    print("User's start date: " + t_usr_start_date_str)

    t_cb_date_str = "2021-10-01T15:45:33.000"
    print("Codebashing date string: " + t_cb_date_str)

    t_cd_date_substr = (t_cb_date_str.rpartition('T')[0])
    print("Substring of CB date: " + t_cd_date_substr)
    print("")

    t_usr_start_date_obj = date.fromisoformat(t_usr_start_date_str)
    print("User's start date as an object:")
    print(t_usr_start_date_obj)

    t_cb_date_obj = date.fromisoformat(t_cd_date_substr)
    print("Codebashing's date as an object:")
    print(t_cb_date_obj)
    print("")

    if t_usr_start_date_obj > t_cb_date_obj:
        print("Codebashing data occurs before user-defined start date and will be omitted.")
    else:
        print("Codebashing data will be included in report.")

    return "Function Complete"


if __name__ == '__main__':
    app.run()
