from main import *

course_options = {
    "topic": "Neural net for Robotics",
	"duration": "5 weeks",
	"teachingStyle": "easy to understand language, quiz me after every lesson, give practice assignments",
	"focusOn": "",
	"purposeFor": "",
	"previousKnowledge": "",
	"otherConsiderations": ""
}

result = main_course_plan(course_options)
print(result)