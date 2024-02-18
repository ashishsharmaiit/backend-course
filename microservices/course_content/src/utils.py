import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, '../config.json'), 'r') as infile:
	config = json.load(infile)

def getPreviousContent(courseContent, sectionId, lessonId):
    # Helper function to find the highest lessonId in the previous section
    def find_highest_lessonId_in_previous_section(courseContent, previous_sectionId):
        lessonIds = [int(key.split('.')[1]) for key in courseContent.keys() if key.startswith(f"{previous_sectionId}.")]
        return max(lessonIds) if lessonIds else -1  # Returns -1 if no lessons found

    contents = []
    current_section = sectionId
    current_lesson = lessonId
    count = 0
    while count < 3:
        key = f"{current_section}.{current_lesson}"
        if key in courseContent:
            contents.append(f"Content from {key}:\n{courseContent[key]['content']}\n\n")
            count += 1
            logging.debug(f"contents: {contents}")
        else:
            # If the lessonId falls below -1, move to the previous section's highest lessonId
            if current_lesson <= -1:
                current_section -= 1
                current_lesson = find_highest_lessonId_in_previous_section(courseContent, current_section)
                logging.debug(f"contents: {contents}")
                # If no more previous sections, break out of the loop
                if current_lesson == -1:
                    break
                continue  # Skip the decrement below for this case as we just set current_lesson
        current_lesson -= 1  # Move to the previous lessonId for the next iteration
    return "".join(contents[::-1])  # Reverse the list to maintain the chronological order
