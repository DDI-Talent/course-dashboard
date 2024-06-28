import pandas as pd
from shiny import ui

class SelectedCourses:

    def __init__(self):
        self.selected_courses = []


    def contains(self, course, year, block):
        for selected_course in self.selected_courses:
            if selected_course.course_info == course and selected_course.year == year and selected_course.block == block:
                return True
        return False
