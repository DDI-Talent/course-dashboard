import pandas as pd
from shiny import ui
from models.course import Course
from models.selected_course import SelectedCourse

class SelectedCourses:

    def __init__(self):
        self.selected_courses = []


    def contains(self, course, year, block):
        for selected_course in self.selected_courses:
            if selected_course.course_info == course and selected_course.year == year and selected_course.block == block:
                return True
        return False

    def add_course(self, course, year, block):
        if not self.contains(course, year, block):
            new_course = SelectedCourse(course, year, block)
            self.selected_courses.append(new_course)

    def remove_course(self, course, year, block):
        if not self.contains(course, year, block):
            new_course = SelectedCourse(course, year, block)
            self.selected_courses.remove(new_course)

    def __str__(self):
        courses_str = ', '.join(str(course) for course in self.selected_courses)
        return f"Selected Courses: [{courses_str}]"

# selected_courses = SelectedCourses()
# selected_courses.add_course('', 1, 2)
# selected_courses.add_course('', 1, 3)
# # new_course = SelectedCourse('ncow', 1, 2)
# print(selected_courses)