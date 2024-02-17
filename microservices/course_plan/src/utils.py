import json
from llm_prompts import get_lesson_plan
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, '../config.json'), 'r') as infile:
	config = json.load(infile)

def update_lesson_plan(detailedCoursePlan, lesson_plan, section_index):

	# Update the course plan with the new lesson plan
	detailedCoursePlan[section_index]["lessonPlan"] = lesson_plan

	# Return the updated course plan
	return detailedCoursePlan
