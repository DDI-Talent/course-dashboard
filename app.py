from shiny import App, render, ui, reactive, session
import pandas as pd
from models.course import Course
from models.selected_course import SelectedCourse
from models.courses_data import CoursesData


version = "0.4.1" # major.sprint.release
    
app_ui = ui.page_sidebar(
    ui.sidebar("Courses", 
               ui.output_ui("list_all_courses"),
               ui.input_action_button("clickme","click me"),
               width=400,
               bg = '#579a9f6d',
               ),
    ui.panel_title(f"Course Dashbaord v{version}"),
    ui.output_table('grid_selected_courses')
)


def server(input, output, session):
    # global selected_courses_objects
    global courses_data
    global input_states

    # courses_objects = reactive.value([]) 
    # new_data = 
    # print("new_data")
    # print(new_data)
    courses_data = reactive.value(CoursesData())
    input_states = reactive.value({})
    # print("new_data2")
    # print("new_data3")

    # courses_data.set(CoursesData())

    @reactive.effect
    def load_data():
        global courses_data
        # print("------------LOAD DATA! 1 @reactive.effect")
        # print("------------LOAD DATA! 1")
        # print(courses_data)
        # print(courses_data.get())
        data_service = courses_data.get()
        data_service.refresh_data()
        courses_data.set(data_service)
        # print("------------LOAD DATA! 2")
        # print(courses_data)
        # print(courses_data.get())
        # print("------------LOAD DATA! 3")



    # def list_to_str(number_list):
    #     return "&".join([f"{year}" for year in number_list])

    # def course_to_button_id(course, year, block, action = "buttonadd_"):
    #     return f"{action}{course.id}_{year}_{block}"

    # def course_dict_to_button_id(course_dict, action = "buttonadd_"):
    #     return f"{action}{course_dict.id}_{course_dict['year']}_{course_dict['block']}"

    def is_this_add_button(button_id):
        return "buttonadd_" in button_id

    # def course_from_button_id(button_id):
    #     button_id = button_id.replace("buttonadd_","")
    #     button_id = button_id.replace("buttonremove_","")
    #     #"button_{course['course_id']}_{year}_{block}"
    #     course_id, year, block = button_id.split("_")
    #     return {'course_id':course_id, 'year': int(year), 'block': int(block)}

    @output
    @render.ui
    def list_all_courses():
        # global courses_objects
        # courses_df_no_duplicates = courses_objects.get().drop_duplicates(subset='course_name')

        return [
            course_obj.as_card() 
          for course_obj in courses_data.get().course_infos
        ]

    def add_course( course_as_dictionary):
        global courses_data
        courses_data.get().add_course(course_as_dictionary, 
                                    course_as_dictionary['year'], 
                                    course_as_dictionary['block'])

    def remove_course(course_as_dictionary):
        global courses_data
        courses_data.get().remove_course(course_as_dictionary, 
                                    course_as_dictionary['year'], 
                                    course_as_dictionary['block'])

    # courses_data.set(load_data()) # TODO, do we actually need this one?

    # selected_courses_objects.set(load_selected_courses())

    def get_courses(courses_df, year=None, block=None, columns_to_keep = ['course_name', 'course_id']):
        global courses_data
        return courses_data.get().all_options_in(year,block)

      
    # @reactive.value
    def create_selected_courses_output_ui():
        global courses_data
        print("REFRESH create_selected_courses_output_ui", len(courses_data.get().selected_courses.get()))
        rows  = []
        for block in range(1,7):
            # DRY this up
            year = 1
            year1_widgets = [ 
                courses_data.get().as_card_selected(SelectedCourse(course, year, block))
                for course in courses_data.get().all_options_in(year, block)]
            # print("year1_widgets",len(year1_widgets))
            year = 2
            year2_widgets = [ 
                courses_data.get().as_card_selected(SelectedCourse(course, year, block))
                for course in courses_data.get().all_options_in(year, block)]

            new_row = ui.row(
                ui.column(2, ui.p(block)),
                ui.column(5, year1_widgets),
                ui.column(5, year2_widgets)
            )
            rows.append(new_row)
        return ui.column(12, rows)
    

    def course_data_from_button_id(button_id):
        global courses_objects
        if "buttonadd_" in button_id:
            action = "buttonadd_"
        else:
            action = "buttonremove_"

        selected_courses = [course 
                            for course in courses_objects.get() 
                            for year in course.years
                            for block in course.blocks
                            if course.course_to_button_id(year,block, action=action) ==  button_id]
        return selected_courses[0] if len(selected_courses) > 0 else None

    # tod cleanup two below finctions into something more DRY
    # @reactive.effect
    def get_all_inputs_ids():
        all_inputs_ids = CoursesData.all_inputs_ids()
        return all_inputs_ids
    
    def get_all_inputs():
        global courses_data
        # print("######1")
        # print("######2")
        inputs_stuff = get_all_input_info().values()
        # print("######3")
        # print("inputs_stuff")
        # inputs_stuff = [input.clickme]
        # print("inputs_stuff",inputs_stuff)
        return inputs_stuff

    def get_all_input_info():
        global courses_data
        all_ids = get_all_inputs_ids( )
        # print("all_ids",all_ids)
        # print("input", getattr(input, "clickme"))
        # print("input", getattr(input, all_ids[0]))
        input_values_dict = {button_id: getattr(input, button_id) 
                             for button_id in  all_ids}
        # print("all_ids",input_values_dict)

        return input_values_dict

    def which_input_changed( ):
        global input_states
        new_states = {}
        all_inputs = get_all_input_info()
        # print("which_input_changed+",all_inputs,len(all_inputs.items()))
        for input_id, input_object in all_inputs.items():
            new_states[input_id] = input_object()

        # {"but_45678": button_oibject} # turn those into
        # {"but_45678": 2}  # those. where number is how many times I was clicked
        
        # old [0,0,1]
        # new [0,0,2]
        if (len(input_states.get().keys()) == 0):
            old_states = {new_state_key: 0
                for new_state_key, new_state_value in new_states.items()}
        else:
            old_states = input_states.get()

        keys_that_changed = [old_state_key
                            for old_state_key, old_state_value in old_states.items()
                            if old_state_value != new_states[old_state_key]]
        
        input_states.set(new_states)
        return keys_that_changed[0] if len(keys_that_changed) > 0 else None

    def id_button_to_course(button_id):
        return button_id.replace("button_","")
    
    @reactive.Effect
    @reactive.event(*get_all_inputs())
    def any_course_button_clicked():
        global courses_data
        # print("CLICKED!1")
        clicked_button_id = which_input_changed( )
        # print("CLICKED!2")
        print("CLICKED!2", clicked_button_id)

        if clicked_button_id == None:
            print("--- any_course_button_clicked Isssue, nothing changes")
            return

        data_service = courses_data.get()
        # print("len(data_service.selected_courses)")
        # print(len(data_service.selected_courses))
        data_service.respond_to_clicked_button_id( clicked_button_id  )
        # print(len(data_service.selected_courses))
        courses_data.set(data_service)
        reactive.invalidate_later(1)


    @render.ui
    def grid_selected_courses():
        # global courses_data
        # global selected_courses_objects
        # global courses_objects
        print("///grid_selected_courses//")        
        return create_selected_courses_output_ui()
    
 

app = App(app_ui, server)