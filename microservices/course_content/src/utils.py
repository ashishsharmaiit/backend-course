import json
from llm_prompts import get_lesson_plan
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, '../config.json'), 'r') as infile:
	config = json.load(infile)

def load_section_details(detailedCoursePlan, sectionNumber: int):
    for index, section in enumerate(detailedCoursePlan):
        if section["sectionNumber"] == str(sectionNumber):  # Convert sectionNumber to string for comparison
            return section, index
    return None, -1  # Return None and -1 if the section is not found


'''
def check_lesson_exists(detailedCoursePlan, uniqueLessonId):
	highest_unique_lesson_num = -1  # Initialize to -1 to indicate none found
	sec_index_of_highest = -1  # Initialize to -1 to indicate none found

	for section_index, section in enumerate(detailedCoursePlan):
		if "subsection" in section:
			subsection = section["subsection"]
			for chapter_index, chapter in enumerate(lesson_plan["chapters"]):
				for lesson_index, lesson in enumerate(chapter["lessons"]):
					current_lesson_num = lesson.get("uniqueLessonId", -1)
					# Update highest_unique_lesson_num if a higher value is found
					if current_lesson_num > highest_unique_lesson_num:
						highest_unique_lesson_num = current_lesson_num
						sec_index_of_highest = section_index
					# Check if the current lesson matches the uniqueLessonId
					if current_lesson_num == uniqueLessonId:
						# If found, return True with the location details
						return True, section_index, chapter_index, lesson_index

	# After checking all lessons, determine the return value based on the highest_unique_lesson_num found
	if highest_unique_lesson_num == -1:
		# If no lessons with a uniqueLessonId were found at all
		return False, 0, -1, -1
	else:
		# If uniqueLessonId was not found but other lessons with uniqueLessonId exist
		return False, sec_index_of_highest+1, -1, -1
'''



def update_lesson_plan(detailedCoursePlan, lesson_plan, section_index):

	# Update the course plan with the new lesson plan
	detailedCoursePlan[section_index]["lessonPlan"] = lesson_plan

	# Return the updated course plan
	return detailedCoursePlan
