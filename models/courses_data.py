import pandas as pd
from shiny import ui
from models.course import Course
from models.selected_course import SelectedCourse

class CoursesData:

    def __init__(self):
        print("**create CoursesData")
        self.selected_courses = []
        self.course_infos = []

    def refresh_data(self):
        print("**refresh_data CoursesData")
        self.course_infos = CoursesData.load_data()

    def all_inputs_ids():
        ids =  [ button_id
            for course in CoursesData.load_data()
            for button_id in course.all_possible_button_ids()
        ]
        print("all_inputs_ids")
        print("all_inputs_ids",ids)
        return ids


    def load_data():
        loaded_df = pd.read_csv(f'./data/example_course_outline.csv')
        return [ Course(row)
                for _, row in loaded_df.iterrows()]

    def all_options_in(self, year, block):
        all_options = []
        for course in self.course_infos:
            if course.takeable_in(year, block):
                all_options.append(course)
        # print(f"all_options_in {year}, {block} = {all_options}")
        return all_options

    def is_taken_in(self, course, year, block):
        print("is_taken_in")
        print("is_taken_in",len(self.selected_courses), course.id, year, block)

        for selected_course in self.selected_courses:
            if selected_course.course_info.id == course.id and selected_course.year == year and selected_course.block == block:
                return True
        return False
    
    def course_dict_from_button_id(self, button_id):
        button_id = button_id.replace("buttonadd_","")
        button_id = button_id.replace("buttonremove_","")
        #"button_{course['course_id']}_{year}_{block}"
        course_id, year, block = button_id.split("_")
        return {'course_id':course_id, 'year': int(year), 'block': int(block)}

    def respond_to_clicked_button_id(self, button_id):
        # print("respond_to_clicked_button_id",button_id)
        is_this_add_button = "buttonadd_" in button_id
        course_dict = self.course_dict_from_button_id(button_id)
        course_obj = self.course_with_id(course_dict['course_id'])
        # print("respond_to_clicked_button_id",course_obj, course_dict)
        if is_this_add_button:
            self.add_course(course_obj,course_dict['year'],course_dict['block'])
        else:
            self.remove_course(course_obj,course_dict['year'],course_dict['block'])

    def course_with_id(self, course_id):
        courses_with_id = [course
                            for course in self.course_infos
                            if course.id == course_id]
        return courses_with_id[0] if len(courses_with_id) > 0 else None

    def as_card_selected(self, course, year, block):
        return course.as_card_selected(self.is_taken_in(course, year, block))

    def add_course(self, course, year, block):
        # print("add_course", course)
        if not self.is_taken_in(course, year, block):
            new_course = SelectedCourse(course, year, block)
            self.selected_courses.append(new_course)

    def remove_course(self, course, year, block):
        if not self.is_taken_in(course, year, block):
            new_course = SelectedCourse(course, year, block)
            self.selected_courses.remove(new_course)

    def __str__(self):
        courses_str = ', '.join(str(course) for course in self.course_infos)
        courses_selected_str = ', '.join(str(course) for course in self.selected_courses)
        return f"Selected Courses: [{courses_str}], {courses_selected_str}"

# selected_courses = SelectedCourses()
# selected_courses.add_course('', 1, 2)
# selected_courses.add_course('', 1, 3)
# # new_course = SelectedCourse('ncow', 1, 2)
# print(selected_courses)