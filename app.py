from shiny import App, render, ui, reactive, session
import pandas as pd
from models.course import Course
from models.selected_course import SelectedCourse
from models.courses_data import CoursesData


version = "0.4.8" # major.sprint.release
    
app_ui = ui.page_sidebar(
    ui.sidebar("Courses", 
               ui.output_ui("list_all_courses"),
            #    ui.input_action_button("clickme","click me"),
               width=250,
               bg = '#579a9f6d',
               ),
    ui.panel_title(f"Course Dashboard v{version}"),
    ui.output_table('grid_selected_courses')
)

def server(input, output, session):
    global courses_data
    global input_states
    global colors

    courses_data = reactive.value(CoursesData())
    input_states = reactive.value({})
    # colors = reactive.value({})

    @reactive.effect
    def load_data():
        global courses_data
        data_service = courses_data.get()
        data_service.refresh_data()
        courses_data.set(data_service)
    
    @output
    @render.ui
    def list_all_courses():
        global colors
        # return [
        #     course_obj.as_card("background-color: #ffffff") 
        #   for (course_obj) in (courses_data.get().course_infos)
        # ]    
        color_data = courses_data.get().card_color.get()
        print(color_data)   
        return [
            course_obj.as_card(color) 
          for (course_obj, color) in zip(courses_data.get().course_infos, color_data.values())
        ]
    
    @output
    @render.ui
    def grid_selected_courses():
        global courses_data
        # print(courses_data.get())
        print("REFRESH create_selected_courses_output_ui", len(courses_data.get().selected_courses.get()))
        rows  = []
        for block in range(1,7):
            years_widgets = []
            for year in [1,2]:
                years_widgets.append([ 
                    courses_data.get().as_card_selected(SelectedCourse(course, year, block))
                    for course in courses_data.get().all_options_in(year, block)])

            new_row = ui.row(
                ui.column(2, ui.p(block)),
                ui.column(5, years_widgets[0]),
                ui.column(5, years_widgets[1])
            )
            rows.append(new_row)
        return ui.column(12, rows)


    def get_all_inputs_ids():
        return CoursesData.all_inputs_ids()
    
    def get_all_inputs():
        return get_all_input_info().values()

    def get_all_input_info():
        return { button_id: getattr(input, button_id) 
                for button_id in  CoursesData.all_inputs_ids()}

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
    
    @reactive.Effect
    @reactive.event(*get_all_inputs())
    def any_course_button_clicked():
        global courses_data
        clicked_button_id = which_input_changed( )
        print("CLICKED!", clicked_button_id)
        card_color = f"background-color: #c3c3c3"

        if clicked_button_id == None:
            print("--- any_course_button_clicked Isssue, nothing changes")
            return

        data_service = courses_data.get()
        data_service.respond_to_clicked_button_id( clicked_button_id  )
        courses_data.set(data_service)
    
app = App(app_ui, server)