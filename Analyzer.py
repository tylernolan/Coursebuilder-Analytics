#As far as splitting it into weeks goes...
#we don't have the ability to see the date which they got certified as far as I can tell
#we can get the date of their first pageview through evententity then check if they eventually achieved their goals, which is the easy level 0 approach.
#we can also check when their last pageview was and check if they got certified. We can split it into last pageviews to estimate what dates students got certified. This is kinda useless if people commonly come back to the course after getting certified.
#I opted for the level 0 approach, it was simpler to code and probably just as useful as the more complicated method.

import re
import time
import datetime
import operator
from collections import defaultdict

#list of IDs who are us. We don't want to look at us.
BAD_IDS = [109826466069707651355, 103354212105644696927, 112641320891641105135, 103465685207495274873, 117467779573370717441, 100859882456081059235, 104857072559651500217, 101207345425454011502, 110913348700576779777]

class Student():
	
	def __init__(self, event, surveyDict):
		self.userID = event.userID
		self.events = [event]
		self.importSurveyResponses(surveyDict)
			
	@staticmethod
	def spreadsheetHeader():
		header = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21}\n".format("User ID", 
		"Reasons for Taking Course", 
		"Completion Intent", 
		"Lego Robots Experience", 
		"EV3 Robots Experience", 
		"Non-Lego Robot Experience", 
		"Programming Experience", 
		"Project 1 Grade", 
		"Project 2 Grade", 
		"Project 3 Grade", 
		"Project 4 Grade", 
		"Project 5 Grade",
		"Project 6 Grade",
		"Certificate Downloaded",
		"Last Page Viewed",
		"Time between first and last pageview",
		"Week 1 Started",
		"Week 2 Started",
		"Week 3 Started",
		"Week 4 Started",
		"Week 5 Started",
		"Week 6 Started")
		return header
	def outputToMasterSheet(self):
		self.findBreakpoints()
		weeks = self.getWeeksViewed()
		try:
			return "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21}\n".format(self.userID,
																  self.surveyData["reasons"],
																  self.surveyData["completionIntent"],
																  self.surveyData["legoRobots"],
																  self.surveyData["EV3Robots"],
																  self.surveyData["robots"],
																  self.surveyData["programming"],
																  self.surveyData["p1"],
																  self.surveyData["p2"],
																  self.surveyData["p3"],
																  self.surveyData["p4"],
																  self.surveyData["p5"],
																  self.surveyData["p6"],
																  self.checkIfCertificateEarned(),
																  self.lastPageViewedLoc,
																  str(self.getTimeSpentInCourse()).replace(",",""),
																  weeks[0] == 1,
																  weeks[1] == 1,
																  weeks[2] == 1,
																  weeks[3] == 1,
																  weeks[4] == 1,
																  weeks[5] == 1)
		except KeyError:
			print "error"
			return ""

	def sortEventsByTimestamp(self):
		self.events.sort(key= lambda event: event.timestamp)
			
	def getAssessments(self):
		ret = []
		for event in self.events:
			if event.eventType == "tag-assessment":
				ret.append(event)
		return ret
	#uses the data from evententity to determine which weeks the student has viewed parts of.
	def getWeeksViewed(self):
		ret = [0 for x in range(6)]
		for event in self.events:
			ret[event.weekNum - 1] = 1
		return ret
	#could probably make all of this significantly faster by loading all 3 files into a dict, but it runs fast enough that it doesn't really matter either way.
	#finds the desired data from the survey responses and loads them into a dictionary, which is stored by the object in SurveyData and returned.
	def importSurveyResponses(self, surveyDict):
		self.surveyData = {}
		try:
			self.surveyData = surveyDict[self.userID]
			return self.surveyData
		except KeyError:
			pass
		#if not found, set to default values.
		self.surveyData["reasons"] = ""
		self.surveyData["completionIntent"] = ""
		self.surveyData["legoRobots"] = ""
		self.surveyData["EV3Robots"] = ""
		self.surveyData["robots"] = ""
		self.surveyData["programming"] = ""
		self.surveyData["p1"] = "0"
		self.surveyData["p2"] = "0"
		self.surveyData["p3"] = "0"
		self.surveyData["p4"] = "0"
		self.surveyData["p5"] = "0"
		self.surveyData["p6"] = "0"
		self.surveyData["completed"] = False
		return self.surveyData
	
	#if the student answered yes to the survey question about whether they intend to complete the course, returns true.
	def determineIntent(self):
		if self.surveyData != {}:
			if self.surveyData["completionIntent"] == "yes":
				return True
		return False
			
	#returns the time from their first pageview in the course to their last pageview in the course.
	def getTimeSpentInCourse(self):
		self.sortEventsByTimestamp()
		var = self.events[-1].timestamp - self.events[0].timestamp
		return var
		
	#returns true if student has earned a certificate of completion for the course
	#We check this by seeing if they have completed all of the assignments
	def checkIfCertificateEarned(self):
		if (int(self.surveyData["p1"]) + 
		    int(self.surveyData["p2"]) +
		    int(self.surveyData["p3"]) +
		    int(self.surveyData["p4"]) + 
		    int(self.surveyData["p5"]) + 
		    int(self.surveyData["p6"])) == 600: 
				return True
		else:	
			return False
		scores = self.buildScoresList()
		if len(scores) != 6:
			return False
		#make sure they didn't get 0s on any assessments
		for score in scores:
			if score == 100:
				continue
			else:
				return False
		return True
	
	#returns a dictionary of page:visitcount pairs. 
	def makeVisitCountDictionary(self):
		viewedUnits = {}
		for event in self.events:
			if event.eventType == 'visit-page':
				if event.location not in viewedUnits:
					viewedUnits[event.location] = 1
				else:
					viewedUnits[event.location] += 1
					
		return viewedUnits
	#checks to see if they've viewed various unit pages, and if they have, returns True, under the assumption they've viewed every video.
	#Ignores assessments
	def checkIfCompletedCourse(self):
		pagesToCheckFor = ['unit?unit=5&lesson=63', 'unit?unit=22&lesson=37', 'unit?unit=38&lesson=51', 'unit?unit=69&lesson=85', 'unit?unit=99&lesson=104', 'unit?unit=99&lesson=107']
		viewedUnits = self.makeVisitCountDictionary().keys()
		for page in pagesToCheckFor:
			if page in viewedUnits:
				continue
			else:
				return False
		return True

	#returns a list of pages where the student took a break of 2 hours or longer.
	#sets a variable for the last page the student has viewed
	def findBreakpoints(self):
		breakpoints = []
		prevEvent = None
		for event in self.events:
			if event.eventType == "visit-page":
				if prevEvent == None:
					pass
				else:
					if (event.timestamp - prevEvent.timestamp) > datetime.timedelta(hours = 2):
						if event.location == "course":
							breakpoints.append(prevEvent)
						else:
							breakpoints.append(event)
				if event.location != "course" and event.location != "student" and event.location != "answer":
					prevEvent = event
					
		self.lastPageViewed = prevEvent
		if self.lastPageViewed == None:
			self.lastPageViewedLoc = None
		else:
			self.lastPageViewedLoc = self.lastPageViewed.location
		return breakpoints

#class to organize and store events from eventEntity for reference by other parts of this application.
class EventEntity():
	weeks = ["unit=5", "unit=22", "unit=38", "unit=69", "unit=99", "unit=108"]
	def __init__(self, line):
		lines = line.split(",")
		self.location = ""
		try:
			self.eventType = lines[0]
		except:
			print "EVENTTYPE ERROR"
			print line
		try:
			self.userID = lines[1]
		except:
			print "USERID ERROR"
			print line
		try:
			self.timestamp = datetime.datetime.fromtimestamp(time.mktime(time.strptime(lines[-1].split(".")[0].strip(), "%Y-%m-%d %H:%M:%S")))
		except:
			print "TIMESTAMP ERROR"
			print line
			print lines[-1].split(".")[0]
		
		lines = line.split("{")
		attribs = lines[1].split(":")
		if self.eventType == "tag-assessment":
			attribs = lines[1].split(':"')
			try:
				try:
					self.answer = re.findall('answer\"\"\:\[.+\]', line)[0]
				except:
					self.answer = 0
				self.score = re.findall('score\"\"\:.+?,', line)[0].strip('score"":,')
				self.location = re.findall('(www.)?cs4hsev3robots.appspot.com/.+?\"', line)[0]#.split("/")[3].split('"')[0]

			except:
				print "assessment error"
			
		elif self.eventType == "visit-page":
			self.duration = attribs[1].split(",")[0]
			self.location = attribs[3].split("/")[3].split('"')[0] #just more unreadable write-once string manipulation code.

		else:
			pass
		try:
			self.weekNum = [1 if x in self.location else 0 for x in EventEntity.weeks].index(1) + 1
		except ValueError:
			self.weekNum = 0


			
#makes a dictionary from the data from the student datastore that was extracted with SDG.py.			
def buildSurveyDict(studentIDs):
	f = open("survey_data.csv").readlines()
	surveyDict = defaultdict(dict)
	for line in f[1:]:
		person = {}
		line = line.split(",")
		id = line[0]
		studentIDs.add(id)
		person["reasons"] = line[1].strip()
		person["completionIntent"] = line[2].strip()
		person["legoRobots"] = line[3].strip()
		person["EV3Robots"] = line[4].strip()
		person["robots"] = line[5].strip()
		person["programming"] = line[6].strip()
		person["p1"] = line[7].strip()
		person["p2"] = line[8].strip()
		person["p3"] = line[9].strip()
		person["p4"] = line[10].strip()
		person["p5"] = line[11].strip()
		person["p6"] = line[12].strip()
		person["completed"] = line[13].strip()
		surveyDict[id] = person
	return surveyDict			
	
#replaces all '}' characters in students.csv with '{'. Makes other parts of the script significantly more readable, and made it significantly easier to code.
def setupFile(filename = "students.csv"):
	file = open(filename, 'r')
	data = file.read()
	newfile = ""
	for char in data:
		if char == "}":
			newfile+="{"
		else:
			newfile+=char
	file.close()
	file = open(filename, 'w')
	file.write(newfile)
	file.close()
		
#prints pairs of #OfWeeksAgoRegistered : HasCompletedGoals ratios. It is assumed that every student who didn't intend to complete the course had no goals, as we don't have any real way of discerning what their actual goals were.
def splitStudentsIntoWeekCategories(students, RegistrationOrLastAssessment):
	for student in students:
		student.sortEventsByTimestamp()
	
	weeklyStudentList = {}
	currentWeekIndex = 0
	stillWorking = False
	placeholderStudents = students[:]
	while True:
		stillWorking = False
		for student in placeholderStudents:
			stillWorking = True
			if RegistrationOrLastAssessment == "LastAssessment":
				data = student.getAssessments()
				if len(data) == 0:
					inRange = False
				else:
					inRange = student.getAssessments()[-1].timestamp > datetime.datetime.today() - datetime.timedelta(days = 7+currentWeekIndex)
			elif RegistrationOrLastAssessment == "Registration":
				inRange = student.events[-1].timestamp > datetime.datetime.today() - datetime.timedelta(days = 7+currentWeekIndex)
			if inRange:
				if student.determineIntent() and student.checkIfCertificateEarned():
					try:
						weeklyStudentList[currentWeekIndex/7] += 1
					except KeyError:
						weeklyStudentList[currentWeekIndex/7] = 1
				placeholderStudents.remove(student)
		if stillWorking == False:
			break
		currentWeekIndex += 7
		
	for thing in weeklyStudentList.keys():
		print str(thing)+ " : "+str(weeklyStudentList[thing])
		
#takes events and sorts them into Student objects.
def sortIntoStudents(events, studentIDs):
	seenIDs = set()
	students = {}
	surveyDict = buildSurveyDict(studentIDs)
	for event in events:
		if event.userID not in seenIDs:
			students[event.userID] = Student(event, surveyDict)
			seenIDs.add(event.userID)
		else:
			students[event.userID].events.append(event)
				
	for student in students.keys():
		if int(student) in BAD_IDS:
			del students[student]
		else:
			students[student].sortEventsByTimestamp()
	return [s for s in students.values()]

#finds popular places where people leave the course for a period of 2 hours or longer.
def findPopularBreakpoints(students):
	breakpoints = {}
	for student in students:
		temp = student.findBreakpoints()
		for point in temp:
			if point.location not in breakpoints.keys():
				breakpoints[point.location] = 1
			else:
				breakpoints[point.location] += 1
	#for key in breakpoints.keys():
	#	print str(key) + ":" + str(breakpoints[key])
	return sorted(breakpoints.items(), key=lambda x : x[1])

def printPopularBreakpoints(students):
	breakpoints = findPopularBreakpoints(students)
	for breakpoint in breakpoints:
		print breakpoint
	
def findWhereStudentsLeaveTheCourseForever(students):
	FinalPages = {}
	breakpoints = findPopularBreakpoints(students)
	try:
		for student in students:
			if student.lastPageViewed.location not in FinalPages:
				FinalPages[student.lastPageViewed.location] = 1
			else:
				FinalPages[student.lastPageViewed.location] += 1
	except AttributeError:
		pass
	return sorted(FinalPages.items(), key=lambda x: x[1])

def printWhereStudentsLeave(students):
	pages = findWhereStudentsLeaveTheCourseForever(students)
	for page in pages:
		print page
		
#returns a list of students who viewed most if not all the pages in the course.
def getListOfStudentsWhoCompletedCourse(students):
	hasCompleted = []
	for student in students:
		if student.checkIfCompletedCourse():
			hasCompleted.append(student)
	return hasCompleted
#returns a list of students who earned their certificates of completion for the course
def getListOfStudentsWithCertificate(students):
	hasCompleted = []
	for student in students:
		if student.checkIfCertificateEarned():
			hasCompleted.append(student)
	return hasCompleted

def printTimeSpentInCourseByThoseWithCertificates(students):
	hasCompleted = getListOfStudentsWhoCompletedCourse(students)
	for student in hasCompleted:
		print student.getTimeSpentInCourse()
		
def printTimeSpentInCourseByThoseWhoCompletedCourse(students):
	hasCompleted = getListOfStudentsWhoCompletedCourse(students)
	for student in hasCompleted:
		print student.getTimeSpentInCourse()
#prints the number of people who intended to get their certificate upon registering. 	
def printIntents(students):
	counter = 0
	for student in students:
		if student.determineIntent():
			counter += 1
	print counter
	
if __name__ == "__main__":		
	#load data into the application
	
	#slightly modify the students.csv file for easier processing.
	setupFile()
	file = open('EventEntity.csv', 'r').readlines()[1:]
	events = []
	print "loading..."
	for line in file:
		events.append(EventEntity(line))
	studentIDs = set()
	students = sortIntoStudents(events, studentIDs)
	print len(students)
	print "\n\nMenu:"
	print "(1) Print pages at which students take a break"
	print "(2) Print the time spent in the course by students who have completed the course and gotten their certificate"
	print "(3) Print the points where students give up and leave the course"
	print "(4) Print #OfWeeksAgoTheyRegistered:IntentAndCompletion pairs"
	print "(5) Print #OfWeeksAgoTheyViewedTheLastAssessment:IntentAndCompletion pairs"
	print "(6) Build big spreadsheet"
	print "\n"
	
	validInputs = [1, 2, 3, 4, 5, 6]
	userInput = -1
	while userInput not in validInputs:
		userInput = input("Select an option number: ")
	if userInput == 1:
		printPopularBreakpoints(students)
	elif userInput == 2:
		printTimeSpentInCourseByThoseWithCertificates(students)
	elif userInput == 3:
		printWhereStudentsLeave(students)
	elif userInput == 4:
		splitStudentsIntoWeekCategories(students, "Registration")
	elif userInput == 5:
		splitStudentsIntoWeekCategories(students, "LastAssessment")
	elif userInput == 6:
		f = open("bigSheet.csv", 'w')
		f.write(Student.spreadsheetHeader())
		for student in students:
			if student.userID in studentIDs:
				f.write(student.outputToMasterSheet())
		f.close()
	#printPopularBreakpoints(students)
	#printWhereStudentsLeave(students)
	#sample code using checkIfCertificateEarned method
	#counter = 0
	#for student in students:
	#	if student.checkIfCertificateEarned():
	#		counter+=1
	#print counter
	
	#sample code using checkIfCompletedCourse method
	#counter = 0
	#for student in students:
	#	if student.checkIfCompletedCourse():
	#		counter += 1
	#print counter
	
	#Sample code for using the findBreakpoints method
	#for student in students:
	#	thing = student.findBreakpoints()
	#	for breakpoint in thing:
	#		print breakpoint.location
	
	#Sample code for using the makeVisitCountDictionary method
	#thing = students[1].makeVisitCountDictionary()
	#for key in thing.keys():
	#	print key + ":" + str(thing[key])