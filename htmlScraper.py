# This code is taken from
# http://stackoverflow.com/questions/1480356/how-to-submit-query-to-aspx-page-in-python
# Import various libraries
import urllib, bs4, requests, sys, re

# Define URL (stupidass .aspx link)
url = "https://my.sa.ucsb.edu/public/curriculum/coursesearch.aspx"

# Define class types to run this with
subjects = ["PSTAT",
            "MATH",
            "CMPSC",
            "ECON",
            "ENGR"]

# Define quarters and corresponding numbers with it
quarters = {"winter": 1,
            "spring": 2,
            "summer": 3,
            "fall": 4}

# First get sesson info
def get_session_info():

  # Entered in User-Agent 
  headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
  }

  # This part comes from:
  # https://github.com/hgielar/GOLD-schedule-exporter/blob/master/GOLD_Schedule_Tracker.py

  # First make a session
  # Then Put in the specific headers
  # Enter the URL
  # Then extract the HTML output using the html.parser

  sesh = requests.Session()
  sesh.headers.update(headers)
  req = sesh.get(url)
  content = bs4.BeautifulSoup(req.content, "html.parser")

  # Scrape HTML to retrieve these values, will be used later on when logging in the first time
  # Using the first set of form data
  VIEWSTATE = content.find(id = "__VIEWSTATE")['value']
  VIEWSTATEGENERATOR = content.find(id = "__VIEWSTATEGENERATOR")['value']
  EVENTVALIDATION = content.find(id = "__EVENTVALIDATION")['value']
  keyzNCookies = sesh.cookies.get_dict()
  COOKIE = keyzNCookies["ASP.NET_SessionId"]

  get_class_lists(VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION, COOKIE, sesh)

def get_class_lists(VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION, COOKIE, session):

  # A little thanks thoughhhh
  print("Thank for for using the official DS @ UCSB GOLD Schedule Exporter")
  print("Developed by Nathan Fritter, Timothy Nguyen, and Brittany Cain")
  
  # Ask for quarter you want classes for
  # Gives list of instructions on how to enter
  print("Please enter the quarter you are inquiring about")
  print("It needs to be one of the following: Winter, Spring, Summer, or Fall")

  # Now check to see if user has entered a valid quarter
  valid = False
  while valid == False:
    quarter = input("Please enter your choice here: ").lower()
    # If it works then we get the key pair value
    if quarter in quarters:
      number = quarters[quarter]
      valid = True
    # Otherwise have them do it again
    else:
      print("Class inquiry failed. Please run the program again and make sure you have entered one of the following: Winter, Spring, Summer, Fall")

  # Ask for year you want classes for
  # Also gives instructions on how to enter
  print("Please enter the year you are inquiring about")
  print("It needs to be numeric and length of four digits")

  # Checking for valid number
  valid = False
  while valid == False:
    year = input("Please enter the year you are inquiring about: ")
    # Make sure length of year entered is four digits and numeric
    if len(year) == 4:
      try:
        value = int(year)
        valid = True
      except ValueError:
        print("Year does not appear to be the correct format. Please re-enter the number with the correct format")
    # Otherwise keep entering stupid
    else:
      print("Year does not appear to be the correct length. Please re-enter the number with the correct length")
  
  # Now take number and concatenate that shit due to formatting of input
  # In order to input the year and quarter into the request
  fullString = year + str(number)
  fullNumber = int(fullString)

  # Iterate through class list and output a file for each set of subjects
  for subject in subjects:
    # Here we enter the fields of interest and necessary states
    # Classes, quarter, course levels
    formData = {b"__VIEWSTATE": VIEWSTATE,
                b"__VIEWSTATEGENERATOR": VIEWSTATEGENERATOR,
                b"__EVENTVALIDATION": EVENTVALIDATION,
                b"__ASP.NET_SessionId": COOKIE,
                b"ctl00$pageContent$courseList": subject,
                b"ctl00$pageContent$quarterList": fullNumber, # Represents 2017 and "fourth" quarter of year
                b"ctl00$pageContent$dropDownCourseLevels": "Undergraduate", # Undergrad classes
                b"ctl00$pageContent$searchButton.x": 24,
                b"ctl00$pageContent$searchButton.y": 7
    }

    # req = sesh.post(url, data = formData)
    # text = sesh.get() 
    req2 = session.post(url, data = formData)

    listOfClasses = bs4.BeautifulSoup(req2.text, "html.parser")


    # IF YOU GET AN SSL CERTIFICATE ERROR FOLLOW BELOW:
    # http://stackoverflow.com/questions/42098126/mac-osx-python-ssl-sslerror-ssl-certificate-verify-failed-certificate-verify

    #classHTML = listOfClasses.contents
    prettyHTML = listOfClasses.prettify("utf-8")
    with open("{}.html".format(subject), "wb") as finalFile:
        finalFile.write(prettyHTML)


def parse_html():
  # Parse the new HTML files
  # First make a regular expression object
  #pattern = re.compile("ctl00_pageContent_repeaterSearchResults_ctl1**_labelTitle$")
  # This is what a section looks like
  """
  <td style="text-align: left; vertical-align: middle;">
  </td>
  <td style="text-align: left; vertical-align: middle;">
    T
  </td>
  <td style="text-align: left; vertical-align: top; white-space: nowrap; padding-left: 5px;
                        padding-right: 5px;">
   8:00 am - 8:50 am
  </td>
  <td style="text-align: left; vertical-align: middle;">
   PHELP2532
  </td>
  <td style="text-align: right; vertical-align: middle;">
   0 / 25
  </td>
  <td class="Section" style="color: transparent;">
   False
  </td>
  """
  # And this is what the actual class looks like:
  """
  <td style="text-align: left; vertical-align: middle;">
   BIGELOW S J
   <br/>
  </td>
  <td style="text-align: left; vertical-align: middle;">
   M W F
  </td>
  <td style="text-align: left; vertical-align: top; white-space: nowrap; padding-left: 5px;
                    padding-right: 5px;">
   9:00 am - 9:50 am
  </td>
  <td style="text-align: left; vertical-align: middle;">
   IV   THEA1
  </td>
  <td style="text-align: right; vertical-align: middle;">
   0 / 75
  </td>
  <td class="Section" style="color: transparent;">
   True
  </td>
  """

  for subject in subjects:
    classInfo = []
    with open("{}.html".format(subject), "rb") as htmlFile:
      soup = bs4.BeautifulSoup(htmlFile, "html.parser")
      classes = soup.find_all("td", attrs = {"class": "CourseInfoRow"})
      #strings = list(classes.stripped_strings)
      """
      # The above line creates a 'bs4.element.ResultSet' element
      # Need to loop through this through this method
      for shit in soup:
        #class_list.extend(shit.find_all("span", {"id": re.compile(".*_labelTitle$")}))

        classInfo.extend(soup.find_all("span", {"id": re.compile(".*HyperLinkPrimaryCourse")}))
        classInfo.extend(soup.find_all("td", {"style": "vertical-align: middle;"}))
        classInfo.extend(soup.find_all("td", {"style": "text-align: left; vertical-align: top;\
        white-space: nowrap; padding-left: 5px; padding-right: 5px;"}))
      """
      #print(classInfo)


get_session_info() 
parse_html()
