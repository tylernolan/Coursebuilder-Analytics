# 0) Setting up GAE and GCloud #
Install the Python SDKs located at the following 2 links:
https://cloud.google.com/appengine/downloads
and
https://cloud.google.com/sdk/downloads

The 2nd one will ask you to login, login with your account that is an admin on the appengine. You can change this later, but it's easiest if you just use the right account the first time.

# 1) Downloading datastores  #
On a windows machine, the process is somewhat straightforward with a couple of "gotchas" along the way. 
First off, make sure you're added as an admin on the appengine. If you're not, your login credentials won't let you download the datastores.

Open a cmd window as administrator (If you open it as a regular user, you will get an access denied error with no explanation.) then:
cd C:\Program Files (x86)\Google\google_appengine
or wherever your appengine install is. You want the folder with appcfg.py, along a bunch of other .py files and folders, which should be the rootmost folder in the google_appengine directory, but if not navigate to find it. 

Copy/Paste the "generated_bulkloader_csv.yaml" file from this repository into the appengine folder.
run the following command:
> python appcfg.py download_data --application=cs4hsev3robots --url=http://cs4hsev3robots.appspot.com/_ah/remote_api --filename=students.csv --config_file=generated_bulkloader_csv.yaml --kind=Student --namespace=ns_data

This command will download the contents of the Student datastore into a csv file called "students.csv"
To download EventEntity:
> python appcfg.py download_data --application=cs4hsev3robots --url=http://cs4hsev3robots.appspot.com/_ah/remote_api --filename=EventEntity.csv --config_file=generated_bulkloader_csv.yaml --kind=EventEntity --namespace=ns_data

This one takes a pretty long time to download, I'd recommend running it overnight. At the time I'm writing this it takes a few hours to finish, but it's constantly growing. Make sure you're on a stable internet connection as well, if you can help it don't download it on the school wireless.

Now you have downloaded the raw data, unfortunately this raw data needs quite a bit of processing to be even remotely useful. The scripts in this repository are here to preprocess this data into a more useful form.

# 2) Scraping Survey Response Data / Project Grades #
run the following command from the folder where you cloned this repository:
> python SDG.py <location_of_students.csv>
if you move students.csv to the same folder as SDG.py, you can just run:
> python SDG.py
	
the data will be stored in "survey_data.csv" in the same folder as SDG.py.

# Event Entity Data #
Analyzer.py has a bunch of options for building some data from EventEntity. The code itself isn't the cleanest I've written, but it should be extendable enough for most future uses.
>	"(1) Print pages at which students take a break"
This prints (page, number of students) pairs for the pages at which students take a 2 hour or longer break before moving on to another page.
>	"(2) Print the time spent in the course by students who have completed the course and gotten their certificate"
for each person who completed the course, it prints the amount of time between their first and last page view.
>	"(3) Print the points where students give up and leave the course"
for each page in the course, this prints how many people left the course forever after visiting that page.
>	"(4) Print #OfWeeksAgoTheyRegistered:IntentAndCompletion pairs"
Prints a list of weeksAgoRegistered : Number of Students who Completed the course pairs, only looking at students who said in the survey that they intended to complete the course.
>	"(5) Print #OfWeeksAgoTheyViewedTheLastAssessment:IntentAndCompletion pairs"
Prints a list of weeksAgoOfLastPageView : Number of Students who Completed the course pairs, only looking at students who said in the survey that they intended to complete the course.
This functionality is currently broken, and I'm not sure why. Remind me to fix this before I graduate if this is something we actually want going forward. 
>	"(6) Build big spreadsheet"
"big spreadsheet" is currently the same as survey_data.csv but with a additional columns for the last page the user visited in the course, and the time between their first and last pageview. 