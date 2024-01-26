import logging
from main import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Get the length and width parameters from the event object. The 
    # runtime converts the event object to a Python dictionary
    course_options: CourseOptions = event.get('course_options', {})

    print("Course plan query for user @ {}".format(time.time()))
    data = main_course_plan(course_options)

    logger.info(f"CloudWatch logs group: {context.log_group_name}")

    # return the course plan object
    return json.dumps(data)