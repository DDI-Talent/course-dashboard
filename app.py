from shiny import App, render, ui, reactive, session
import pandas as pd
from models.course import Course
from models.selected_course import SelectedCourse
from models.courses_data import CoursesData


version = "0.5.3" # major.sprint.release
    
app_ui = ui.page_sidebar(
    ui.sidebar("Pin Course Options", 
               ui.output_ui("list_all_courses"),
               width=250,
               bg = '#579a9f6d',
               ),
    ui.panel_title(ui.row(
        ui.column(8,ui.h1(f"Your Pinned courses (v{version})")),
        ui.column(4,ui.output_ui('share_choices_button')),
        )),
    ui.output_ui('grid_selected_courses')
)

def server(input, output, session):
    global courses_data
    global input_states
    global initial_url_loaded_already

    courses_data = reactive.value(CoursesData())
    input_states = reactive.value({})
    initial_url_loaded_already = False

    @reactive.effect
    def load_data():
        global courses_data
        data_service = courses_data.get()
        data_service.refresh_data()
        courses_data.set(data_service)


    @reactive.effect
    def load_initial_url():
        global courses_data
        global initial_url_loaded_already

        if not initial_url_loaded_already:
            initial_url_loaded_already = True
            print("load_initial_url")
            # reacts to url in format .../?courses=HEIN11037_1_1+HEIN11055_2_2
            url_query = session.input[".clientdata_url_search"]()
            courses_data_temp = courses_data.get()
            courses_data_temp.react_to_loaded_url(url_query)  
            courses_data.set(courses_data_temp)  
            
    @output
    @render.ui
    def list_all_courses():
        return [
            course_obj.as_card() 
          for course_obj in courses_data.get().course_infos
        ]
    
    @output
    @render.ui 
    def share_choices_button():
        global courses_data
        site_protocol = session.input[".clientdata_url_protocol"]()
        site_port = session.input[".clientdata_url_port"]()
        site_url = session.input[".clientdata_url_hostname"]()
        pathname = session.input[".clientdata_url_pathname"]()
        # print("!",site_protocol,site_port,site_url,pathname,"!")
        # ! https:  ddi-talent.shinyapps.io /course-dashboard/ !
        selected_courses_as_string = courses_data.get().selected_choices_as_string()
        link_to_share = f"{site_protocol}//{site_url}"
        if len(str(site_port)) > 1: # eg. ignore just "/"
            link_to_share += f":{site_port}"
        if len(pathname) > 1: # eg. ignore just "/"
            link_to_share += f"{pathname}"
        link_to_share += f"?courses={selected_courses_as_string}"
        number_of_choices =  len(courses_data.get().selected_courses.get())
        print("link_to_share",link_to_share)
        if number_of_choices == 0:
            return ui.a(f"🛒 Pin courses to share your selection")
        else:
            return ui.a(f"🛒 Copy and share this link to share your {number_of_choices} Choices", href=link_to_share)
        # return "coming soon"

    @output
    @render.ui
    def grid_selected_courses():
        global courses_data
        rows  = [ui.row(
                ui.column(1, ""),
                ui.column(5, ui.p("YEAR 1")),
                ui.column(1, ""),
                ui.column(5, ui.p("YEAR 2")),
            )]
        for block in range(1,7):
            years_widgets = []
            for year in [1,2]:
                years_widgets.append([ 
                    courses_data.get().as_card_selected(SelectedCourse(course, year, block))
                    for course in courses_data.get().all_options_in(year, block)])

            new_row = ui.row(
                ui.column(1, ui.p(block)),
                ui.column(5, years_widgets[0]),
                ui.column(1, ui.p(block)),
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

        if clicked_button_id == None:
            print("--- any_course_button_clicked Isssue, nothing changes")
            return

        data_service = courses_data.get()
        data_service.respond_to_clicked_button_id( clicked_button_id  )
        courses_data.set(data_service)
    
app = App(app_ui, server)#, debug=True)