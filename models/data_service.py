import pandas as pd
from shiny import ui
from models.course import Course
from models.persona import Persona
from models.degree import Degree
from models.course_selected import CourseSelected
from shiny import reactive
# this class is a data service: it holds all informationm and distributes it
class DataService:

    def __init__(self):
        self.selected_courses = reactive.value([])
        self.course_infos = reactive.value([])
        self.personas = reactive.value([])
        self.degrees = reactive.value([])
        self.degree_selected_id =  None

    def degree_with_id_or_default(degree_id = None):
        degrees = DataService.load_degrees()
        if degree_id == None:
            degree = degrees[0]
        else:
            degree = [degree for degree in degrees if degree.id == degree_id][0]

        return degree

    def refresh_data(self, degree_id = None):
        print("refresh_data",degree_id)
        self.degrees = DataService.load_degrees()
        self.course_infos = DataService.load_data()
        self.personas = DataService.load_personas()
        # TODO: ugh, this should not be hardcoded :(
        # if DataService.degree_with_id_or_default().years == 3:
        #     self.select_dissertation()
  
    def select_dissertation(self):
        dissertation_selected = CourseSelected(self.get_dissertation(),3,1)
        self.add_course(dissertation_selected)

    def get_dissertation(self):
        return [course 
                for course in self.course_infos
                if course.id == "DISSERTATION"][0]


    def all_inputs_ids():
        ids =  [ button_id
            for course in DataService.load_data()
            for button_id in course.all_possible_button_ids()
        ]
        return ids

    def all_course_ids():
        ids =  [ course.id
            for course in DataService.load_data()
        ]
        return ids

    def load_data(filename = "courses.csv"):
        loaded_df = pd.read_csv(f'./data/{filename}')
        return [ Course(row)
                for _, row in loaded_df.iterrows()]
    
    def load_personas(filename = "personas.csv"):
        loaded_df = pd.read_csv(f'./data/{filename}')
        return [ Persona(row)
                for _, row in loaded_df.iterrows()]
    
        
    def load_degrees():
        loaded_df = pd.read_csv(f'./data/degrees.csv')
        return [ Degree(row)
                for _, row in loaded_df.iterrows()]

    def all_options_in(self, year, block):
        all_options = []
        for course in self.course_infos:
            if course.takeable_in(year, block):
                all_options.append(course)
        return all_options
    


    def number_of_taken_courses_in(self, year, block):
        taken_courses_in = [course
                            for course in self.selected_courses.get() 
                            if year == course.year and block == course.block]
        return len(taken_courses_in)



    def is_taken_in_selected_course(self, selected_course):
        for known_selected_course in self.selected_courses.get():
            if known_selected_course.as_string() == selected_course.as_string():
                return True
        return False
    
    def selected_course_from_button_id(self, button_id):
        # when we have more buttons, pre_ stripping goes here, until we DRY this up
        button_id = button_id.replace("buttonadd_","")
        button_id = button_id.replace("buttonremove_","")
        try:
           return self.selected_course_from_string(button_id)
        except Exception as e: 
            # hthis can happen eg. when int() casting goes wrong
            print(f"selected_course_from_button_id ERRORED with string {button_id} and {e}")
            return None

    def selected_course_from_string(self, selected_course_string):
        string_bits = selected_course_string.split("_")
        # check if course id is valud and year and block are in range 
        # button_id like "ABCD_1_6" holds courseid, year, block. eg string_bits would be ['ABCD',1,6]
        if len(string_bits) == 3 and string_bits[0] in DataService.all_course_ids() and int(string_bits[1]) in range(1,4) and int(string_bits[2]) in range(1,7):
            course_obj = self.course_with_id(string_bits[0])
            selectedCourse = CourseSelected(course_obj, int(string_bits[1]), int(string_bits[2]))
            return selectedCourse
        else:
            print(f"selected_course_from_button_id FAILED with string {selected_course_string} bits {string_bits}")
            return None

    def get_year_and_block_from_filter_button_id(self, button_id):
        button_id = button_id.replace("buttonfilter_","")
        string_bits = button_id.split("_")
        print("get_year_and_block_from_filter_button_id",button_id,string_bits)
        return (int(string_bits[0]), int(string_bits[1])) if len(string_bits) == 2 else ("all", "all")

    def respond_to_clicked_button_id(self, button_id):
        is_this_add_button = "buttonadd_" in button_id
        is_this_remove_button = "buttonremove_" in button_id
        selectedCourse = self.selected_course_from_button_id(button_id)

        if selectedCourse == None:
            print("no course for",button_id)
            return

        if is_this_add_button:
            self.add_course(selectedCourse)
        elif is_this_remove_button:
            self.remove_course(selectedCourse)
        

    def selected_choices_as_string(self):
        return "+".join([
            selected_course.to_selected_button_id(action="")
            for selected_course in self.selected_courses.get()
        ])

    def course_with_id(self, course_id):
        courses_with_id = [course
                            for course in self.course_infos
                            if course.id == course_id]
        return courses_with_id[0] if len(courses_with_id) > 0 else None

    def as_card_selected(self, courseSelected, dissertation = False):
        return courseSelected.as_card_selected( self.is_taken_in_selected_course(courseSelected),dissertation)

    def as_card_nothing_selected(self, year, block):
        number_of_taken_courses = self.number_of_taken_courses_in(year, block)
        show = number_of_taken_courses == 0
        return CourseSelected.as_card_nothing_selected( year, block, show )

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


    def react_to_loaded_url(self, url_query):
        selected_courses_from_url = self.url_to_selected_courses_list(url_query)
        selected_courses_temp = self.selected_courses.get()
        selected_courses_temp.extend(selected_courses_from_url)
        self.selected_courses.set(selected_courses_temp)

    def url_to_degree( url_query):
        # url_query is .../?degree_id=DS_HSC&courses=ABCD_1_2,BGHF_2_5,CDER_1_5&fruit=banana
        default_degree =  "DS_HSC3"
        if len(url_query) == 0:
            return default_degree
        url_variables = {}
        for key_value_string in url_query[1:].split("&"):
            key, value = key_value_string.split("=")
            url_variables[key] = value

        # degree_id is like "DS_HSC"
        return url_variables.get('degree_id',default_degree)


    def url_to_selected_courses_list(self, url_query):
        # url_query is .../?courses=ABCD_1_2,BGHF_2_5,CDER_1_5&fruit=banana
        if len(url_query) == 0:
            return []
        url_variables = {}
        for key_value_string in url_query[1:].split("&"):
            key, value = key_value_string.split("=")
            url_variables[key] = value

        # url_variables is {'courses':'ABCD_1_2,BGHF_2_5,CDER_1_5','fruit':'banana}
        selected_courses = []
        for course_string in url_variables.get('courses', "").split("+"):
            new_selected_course = self.selected_course_from_button_id(course_string)
            if new_selected_course != None:
                selected_courses.append(new_selected_course)
        
        # selected_courses is [SelectedCourse object, SelectedCourse object, ... ]
        return selected_courses


    def url_to_doashboard_with_degree(session, degree_id):
        # TODO, this is repeated in a few places
        site_protocol = session.input[".clientdata_url_protocol"]()
        site_port = session.input[".clientdata_url_port"]()
        site_url = session.input[".clientdata_url_hostname"]()
        pathname = session.input[".clientdata_url_pathname"]()

        link_to_share = f"{site_protocol}//{site_url}"
        if len(str(site_port)) > 1: # eg. ignore just "/"
            link_to_share += f":{site_port}"
        if len(pathname) > 1: # eg. ignore just "/"
            link_to_share += f"{pathname}"
        link_to_share += f"?degree_id={degree_id}"

        return link_to_share

    def __str__(self):
        courses_str = ', '.join(str(course) for course in self.course_infos)
        courses_selected_str = ', '.join(str(course) for course in self.selected_courses.get())
        return f"Selected Courses: [{courses_str}], {courses_selected_str}"
