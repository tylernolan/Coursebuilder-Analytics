import re
import sys
from Analyzer import setupFile
class User():
	def __init__(self, name, ID, reasons, completion, legoRobots, programmingExperience, EV3Experience, RobotExperience, scoreList):
		try:
			self.name = name[0]
		except: self.name = ""
		try:
			self.ID = ID[0].strip(",")
		except: self.ID = ""
		try:
			self.reasons = reasons[0]
		except: self.reasons = ""
		try:
			self.completion = completion[0]
		except: self.completion = ""
		try:
			self.legoRobots = legoRobots[0]
		except: self.legoRobots = ""
		try:
			self.programmingExperience = programmingExperience[0]
		except: self.programmingExperience = ""
		try:
			self.EV3Experience = EV3Experience[0]
		except: self.EV3Experience = ""
		try:
			self.RobotExperience = RobotExperience[0]
		except: self.RobotExperience = ""
		self.scoreList = scoreList
		
	def isCertificateEarned(self):
		return self.scoreList[0] + self.scoreList[1] + self.scoreList[2] + self.scoreList[3] + self.scoreList[4] + self.scoreList[5] == 600
		
	def stringlayout(self):
		return "{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(self.ID, self.reasons, self.completion, self.legoRobots, self.EV3Experience, self.RobotExperience, self.programmingExperience, self.scoreList[0], self.scoreList[1], self.scoreList[2], self.scoreList[3], self.scoreList[4], self.scoreList[5], self.isCertificateEarned())
	
	def header(self):
		return "ID, Reasons, Completion, LegoRobots Experience, EV3 robot experience, non-lego robot experience, programming experience, Project 1, Project 2, Project 3, Project 4, Project 5, Project 6, Certificate Earned\n"

if __name__ == "__main__":
	filename = "students.csv"
	try:
		filename = sys.argv[1]
	except:
		pass
	setupFile(filename=filename)
	file = open(filename).readlines()
	users = []
	for line in file:
		name = re.findall('""name"", ""(.+?)"', line)
		programming = re.findall('"programming",.+?]',line)
		ID = re.findall(',\d+?,', line)
		reasons = re.findall('""reasons"", ""(.+?)"', line)
		completion = re.findall('""completion"", ""(.+?)"', line)
		legoRobots = re.findall('""LEGO_robots"", ""(.+?)"', line)
		programmingExperience = re.findall('""programming"", ""(.+?)"', line)
		EV3Experience = re.findall('""EV3_robots"", ""(.+?)"', line)
		RobotExperience = re.findall('""non-LEGO_robots"", ""(.+?)"', line)
		
		scoreList = []
		if "{" in line:
			line = line.split("{")[1]
			scores = line.split(",")
			for score in scores:
				scoreList.append(int(score.split(":")[1]))
		while len(scoreList) < 6:
			scoreList.append(0)
		users.append(User(name, ID, reasons, completion, legoRobots, programmingExperience, EV3Experience, RobotExperience, scoreList))

	output = open("survey_data.csv", "w")
	output.write(users[0].header())
	for user in users:
		outStr = user.stringlayout()
		if not outStr.startswith(","):
			output.write(outStr)
		
	output.close()