import pandas as pd
from shiny import ui
from models.course import Course
from models.selected_course import SelectedCourse
from shiny import reactive
# this class is a data service: it holds all informationm and distributes is
class CoursesData:

    def __init__(self):
        self.selected_courses = reactive.value([])
        self.course_infos = reactive.value([])
        self.card_color = reactive.value("")

    def refresh_data(self):
        self.course_infos = CoursesData.load_data()

    def all_inputs_ids():
        ids =  [ button_id
            for course in CoursesData.load_data()
            for button_id in course.all_possible_button_ids()
        ]
        return ids

    def load_data():
        loaded_df = pd.read_csv(f'./data/all_courses.csv')
        return [ Course(row)
                for _, row in loaded_df.iterrows()]

    def all_options_in(self, year, block):
        all_options = []
        for course in self.course_infos:
            if course.takeable_in(year, block):
                all_options.append(course)
        return all_options


    def is_taken_in_selected_course(self, selected_course):
        for known_selected_course in self.selected_courses.get():
            if known_selected_course.as_string() == selected_course.as_string():
                return True
        return False
    
    def selected_course_from_button_id(self, button_id):
        button_id = button_id.replace("buttonadd_","")
        button_id = button_id.replace("buttonremove_","")
        course_id, year, block = button_id.split("_")
        course_obj = self.course_with_id(course_id)
        selectedCourse = SelectedCourse(course_obj, int(year), int(block))
        return selectedCourse

    def respond_to_clicked_button_id(self, button_id):
        is_this_add_button = "buttonadd_" in button_id
        selectedCourse = self.selected_course_from_button_id(button_id)
        if is_this_add_button:
            self.add_course(selectedCourse)
            self.card_color.set("background-color: #c3c3c3")
            # print(self.card_color.get())
        else:
            self.remove_course(selectedCourse)
            self.card_color.set("background-color: #ffffff")


    def course_with_id(self, course_id):
        courses_with_id = [course
                            for course in self.course_infos
                            if course.id == course_id]
        return courses_with_id[0] if len(courses_with_id) > 0 else None

    def as_card_selected(self, courseSelected):
        return courseSelected.as_card_selected( self.is_taken_in_selected_course(courseSelected))

    def add_course(self, new_selected_course):
        if not self.is_taken_in_selected_course(new_selected_course):
            self.selected_courses.set(self.selected_courses.get() + [new_selected_course])

    def remove_course(self, course_to_remove):
        if self.is_taken_in_selected_course(course_to_remove):
            temp_courses = self.selected_courses.get()
            temp_courses = [selected_course
                            for selected_course in temp_courses
                            if selected_course.as_string() != course_to_remove.as_string()]
            self.selected_courses.set(temp_courses)  


    def __str__(self):
        courses_str = ', '.join(str(course) for course in self.course_infos)
        courses_selected_str = ', '.join(str(course) for course in self.selected_courses.get())
        return f"Selected Courses: [{courses_str}], {courses_selected_str}"
