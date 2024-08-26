from shiny import App, render, ui, reactive, session
import pandas as pd
from models.course import Course
from models.course_selected import CourseSelected
from models.data_service import DataService
from faicons import icon_svg as icon
from views.style_service import StyleService


version = "0.6.1" # major.sprint.release
    
app_ui = ui.page_fixed(

 ui.row(     
     ui.column(12, ui.panel_title(
         ui.row(
            ui.column(6,ui.h1(f"Your Pinned courses (v{version})")),
            ui.column(3,ui.output_ui('course_personas')),
            ui.column(3, 
                        ui.row(ui.output_ui('share_choices_button')),
                        ui.row( ui.output_ui('total_credits'),  ui.output_ui('total_credits_warning'))
                        )
        ))),style= StyleService.style_section_box()
        ),
 ui.row(
    ui.column(4, 
              ui.h2("Choose your courses"),
              ui.output_ui("filter_panel"),
               ui.output_ui("list_all_courses")
               ,style= StyleService.style_section_box()),
    ui.column(8,ui.h2("Your Selected Courses"),ui.output_ui('grid_selected_courses'),style= StyleService.style_section_box())
))

def server(input, output, session):
    # global courses_data
    # global input_states
    # global initial_url_loaded_already
    # global colors

    courses_data = reactive.value(DataService())
    input_states = reactive.value({})
    initial_url_loaded_already = False
    colors = reactive.value({})

    @reactive.effect
    def load_data():
        nonlocal courses_data
        data_service = courses_data.get()
        data_service.refresh_data()
        courses_data.set(data_service)

    @reactive.effect
    def load_initial_url():
        nonlocal courses_data
        nonlocal initial_url_loaded_already

        if not initial_url_loaded_already:
            initial_url_loaded_already = True
            # reacts to url in format .../?courses=HEIN11037_1_1+HEIN11055_2_2
            url_query = session.input[".clientdata_url_search"]()
            courses_data_temp = courses_data.get()
            courses_data_temp.react_to_loaded_url(url_query)  
            courses_data.set(courses_data_temp)  
            
    @output
    @render.ui
    def filter_panel():
        return ui.row( 
            
            ui.input_text("filter_name", 
                            "Filter by name", 
                           
            ),
            ui.input_select("filter_year", 
                            "Filter by year", 
                           choices = {"all": "All","1":"Year 1", "2": "Year 2"},
            ),
            ui.input_select("filter_block", 
                            "Filter by block", 
                           choices = {"all": "All","1":"Block 1", "2": "Block 2", "3": "Block 3", "4": "Block 4" , "5": "Block 5" , "6": "Block 6"  },
            ),
            ui.input_action_link("button_filter_reset","Reset filters 🔄"),
        )


    @output
    @render.ui
    def list_all_courses():
        nonlocal courses_data
        blocks_to_keep = [1,2,3,4,5,6] if input.filter_block.get() == "all" else [int(input.filter_block.get())]
        years_to_keep = [1,2] if input.filter_year.get() == "all" else [int(input.filter_year.get())]
        text_to_keep = input.filter_name.get().strip().lower()



        courses_cards = [
            course_obj.as_card() 
            for course_obj in courses_data.get().course_infos
            if course_obj.takeable_in_any(years_to_keep, blocks_to_keep)
            and (len(text_to_keep) < 0 or  course_obj.name.lower().find(text_to_keep) != -1)
        ]
        return courses_cards
    
    def sharable_link(link_text, selected_courses_as_string):
        nonlocal courses_data
        site_protocol = session.input[".clientdata_url_protocol"]()
        site_port = session.input[".clientdata_url_port"]()
        site_url = session.input[".clientdata_url_hostname"]()
        pathname = session.input[".clientdata_url_pathname"]()

        link_to_share = f"{site_protocol}//{site_url}"
        if len(str(site_port)) > 1: # eg. ignore just "/"
            link_to_share += f":{site_port}"
        if len(pathname) > 1: # eg. ignore just "/"
            link_to_share += f"{pathname}"
        link_to_share += f"?courses={selected_courses_as_string}"

        return ui.a(link_text,  href=link_to_share)
       

    @output
    @render.ui 
    def share_choices_button():
        nonlocal courses_data
        selected_courses_as_string = courses_data.get().selected_choices_as_string()
        number_of_choices =  len(courses_data.get().selected_courses.get())
        if number_of_choices == 0:
            return sharable_link(f"🛒 Pin some courses to create sharable link", selected_courses_as_string)
        else:
            return sharable_link(f"🛒 Copy and share this link ({number_of_choices} Choices)",selected_courses_as_string)

    @output
    @render.ui
    def course_personas():
        course_help = ui.row(
               ui.span("load a persona:"), 
               sharable_link("👾 code focused", "PUHR11063_1_5+HEIN11037_1_1+HEIN11037_1_2+HEIN11045_1_4+HEIN11039_1_3+HEIN11068_1_6+HEIN11055_2_2+HEIN11040_2_3+HEIN11048_2_4+HEIN11057_2_6+HEIN11046_2_5"), 
               sharable_link("😎 balanced", "HEIN11059_1_3+HEIN11043_1_5+HEIN11041_1_4+HEIN11037_1_1+HEIN11037_1_2+HEIN11068_1_6+HEIN11045_2_4+HEIN11056_2_5+HEIN11044_2_3+HEIN11057_2_6+HEIN11054_2_2"),
               sharable_link("❌ empty", "HEIN11037_1_1+HEIN11037_1_2+HEIN11057_2_1+HEIN11057_2_6")
               )
        return course_help

    @output
    @render.ui
    def grid_selected_courses():
        nonlocal courses_data
        right_most_column =  ui.column(1, 
                                       ui.row(ui.p("YEAR 3")),
                                       ui.row( "DISSERTATION"  ,  style ="writing-mode: vertical-rl;text-orientation: upright;"+StyleService.style_course_box())
                                       )
        rows  = [ui.row(
                ui.column(1, ""),
                ui.column(5, ui.p("YEAR 1")),
                ui.column(5, ui.p("YEAR 2")),
            )]
        for block in range(1,7):
            years_widgets = []
            for year in [1,2]:
                courses_in_this_block = [ 
                    courses_data.get().as_card_selected(CourseSelected(course, year, block))
                    for course in courses_data.get().all_options_in(year, block)]
                courses_in_this_block.append(courses_data.get().as_card_nothing_selected(year, block))

                years_widgets.append(courses_in_this_block)

            new_row = ui.row(
                ui.column(1, ui.p(block)),
                ui.column(5, years_widgets[0]),
                ui.column(5, years_widgets[1]),
            )
            rows.append(new_row)
        return ui.row(ui.column(11, rows), right_most_column)

    @output
    @render.text
    def total_credits():
        nonlocal courses_data
        total_credits = sum([(course.get_credits()) for course in courses_data.get().selected_courses.get()])

        return ui.div(f"Credits: {total_credits} of 120")
    

    @output
    @render.ui
    def total_credits_warning():
        nonlocal courses_data
        total_credits = sum([(course.get_credits()) for course in courses_data.get().selected_courses.get()])
        max_credits = 120

        if total_credits == max_credits:
            warning = ""
            style = ""
        elif total_credits > max_credits:
            warning = f"(remove {total_credits - max_credits})"
            style="background-color: #ff0000; color: #ffffff; margin-left: 10px;"
        else: 
            warning = f" (add {max_credits - total_credits} more)"
            style="background-color: #0000ff; color: #ffffff; margin-left: 10px;"
        return ui.div(warning, style=style)

    def get_all_inputs_ids():
        return DataService.all_inputs_ids()
    
    def get_all_inputs():
        return get_all_input_info().values()

    def get_all_input_info():
        return { button_id: getattr(input, button_id) 
                for button_id in  DataService.all_inputs_ids()}

    def which_input_changed( ):
        nonlocal input_states
        new_states = {}
        all_inputs = get_all_input_info()
        #print("which_input_changed+",all_inputs,len(all_inputs.items()))
        for input_id, input_object in all_inputs.items():
            new_states[input_id] = input_object()

        # {"but_45678": button_oibject} # turn those into
        # {"but_45678": 2}  # those. where number is how many times I was clicked
        # old [0,0,1]
        # new [0,0,2]
        print("inputstates",input_states.get().keys())
        if (len(input_states.get().keys()) == 0):
            old_states = {new_state_key: 0
                for new_state_key, new_state_value in new_states.items()}
        else:
            old_states = input_states.get()

        keys_that_changed = [old_state_key
                            for old_state_key, old_state_value in old_states.items()
                            if old_state_value != new_states[old_state_key]]
        
        print("keys that changed",keys_that_changed)
        
        input_states.set(new_states)
        return keys_that_changed if len(keys_that_changed) > 0 else None
    
    @reactive.Effect
    @reactive.event(input.button_filter_reset)
    def reset_filters():
        ui.update_select(
            "filter_name",
            selected="",
        )
        ui.update_select(
            "filter_year",
            selected="all",
        )
        ui.update_select(
            "filter_block",
            selected="all",
        )

    @reactive.Effect
    @reactive.event(*get_all_inputs())
    def any_course_button_clicked():
        nonlocal courses_data
        clicked_button_id = which_input_changed( )
        print("CLICKED!", clicked_button_id)


        if clicked_button_id == None:
            print("--- any_course_button_clicked Isssue, nothing changes")
            return

        data_service = courses_data.get()
        for click in clicked_button_id:
            data_service.respond_to_clicked_button_id(click)
        #data_service.respond_to_clicked_button_id( clicked_button_id  )
        courses_data.set(data_service)
        # print("test",data_service.card_color)
    
app = App(app_ui, server)#, debug=True)