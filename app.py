from shiny import App, render, ui, reactive, session
import pandas as pd
from collections import Counter
from models.course import Course
from models.course_selected import CourseSelected
from models.data_service import DataService
from faicons import icon_svg as icon
from views.style_service import StyleService



version = "1.3.5" # major.sprint.release
    
app_ui = ui.page_fixed(

 ui.row(     
     ui.column(12, ui.panel_title(
         ui.row(
            ui.column(6,ui.h1(f"Course Selection Tool"), ui.div(f"(v{version})"), ui.output_ui("select_degree"),),
            ui.column(3,ui.output_ui('course_personas')),
            ui.column(3, 
                        ui.row(ui.output_ui('share_choices_button')),
                        ui.row( ui.output_ui('total_credits'),  ui.output_ui('total_credits_warning')),
                        ui.row( ui.output_ui('overall_themes'))
                        )
        ))),style= StyleService.style_section_box()
        ),
 ui.row(
    ui.column(4, 
              ui.h2("Available Courses:"),
              ui.output_ui("filter_panel"),
               ui.output_ui("list_all_courses")
               ,style= StyleService.style_section_box()),
              ui.column(8,ui.h2("Your Courses:"),
              ui.output_ui('grid_selected_courses'),style= StyleService.style_section_box())
), 
ui.tags.script("""
        Shiny.addCustomMessageHandler('navigate', function(url) {
            window.location.href = url;
        });
    """),
ui.tags.script("""
        function copyToClipboard() {
            let copyText = document.getElementById("course_choices");
            copyText.select();
            copyText.setSelectionRange(0, 99999); // For mobile devices
            navigator.clipboard.writeText(copyText.value);
            alert("Link to your choices has been coppied, so you can paste it anywhere now (link is " + copyText.value+")");
            return false;
        }
    """),

   
style = "max-width: 1240px; padding: 20px"
)

def server(input, output, session):

    courses_data = reactive.value(DataService())
    input_states = reactive.value({})
    initial_url_loaded_already = False
    colors = reactive.value({})

    def current_degree_id():
        url_query = session.input[".clientdata_url_search"]()
        selected_degree_id = DataService.url_to_degree(url_query)
        return selected_degree_id
    
    @reactive.effect
    def load_data():
        nonlocal courses_data
        data_service = courses_data.get()
        
        data_service.refresh_data(current_degree_id())
        data_service.degree_selected_id = current_degree_id()
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
            
            ui.row(
                ui.column(7,
                          ui.input_text("filter_name",  "Filter by: Name or ID",           
                )),
                ui.column(5,ui.p(" "),
                          ui.input_action_link("button_filter_reset","Reset Filters 🔄"))),
            ui.row(
                ui.column(4,
                          ui.input_select("filter_year",  "Year", 
                            choices = {"all": "All","1":"Year 1", "2": "Year 2",  "3": "Year 3"},
                )),
                ui.column(4,
                          ui.input_select("filter_block", "Block", 
                            choices = {"all": "All","1":"Block 1", "2": "Block 2", "3": "Block 3", "4": "Block 4" , "5": "Block 5" , "6": "Block 6"  },
                )),
                ui.column(4,
                          ui.input_select("filter_theme", "Theme", 
                            choices = {  key: f"{value['emoji']} {value['name']}"
                                for (key, value) in StyleService.theme_infos().items()},
                ))
            )
        )




    @output
    @render.ui
    def select_degree():
        nonlocal courses_data
        degree_options = {degree.id: degree.name 
                          for degree in courses_data.get().degrees }
        return ui.input_select("select_degree_dropdown", "Your program of study:", choices = degree_options, selected=current_degree_id(), width="90%;") 



    @reactive.Effect
    @reactive.event(input.select_degree_dropdown, ignore_init=True)
    async def degree_selected():
        degree_id =  input.select_degree_dropdown.get()
        await session.send_custom_message("navigate", DataService.url_to_doashboard_with_degree(session, degree_id))


    def course_has_word(course_info, word):
        word = word.lower()
        if len(word) == 0:
            return True
        elif (course_info.name.lower().find(word) != -1 
                     or course_info.id.lower().find(word) != -1):
            return True
        else:
            return False

    @output
    @render.ui
    def list_all_courses():
        nonlocal courses_data
        blocks_to_keep = [1,2,3,4,5,6] if input.filter_block.get() == "all" else [int(input.filter_block.get())]
        years_to_keep = [1,2,3] if input.filter_year.get() == "all" else [int(input.filter_year.get())]
        text_to_keep = input.filter_name.get().strip().lower()
        themes_to_keep = list(StyleService.theme_infos().keys()) if input.filter_theme.get() == "all" else [input.filter_theme.get()]

        courses_cards = [
            course_obj.as_card( current_degree_id() in course_obj.degree_ids) 
            for course_obj in courses_data.get().course_infos
            if course_obj.takeable_in_any(years_to_keep, blocks_to_keep)
            and course_has_word(course_obj, text_to_keep)
            and len(list(set(course_obj.themes) & set(themes_to_keep))) > 0
        ]
        return courses_cards if len(courses_cards) > 0 else ui.div("No courses match these criteria")
    
    def sharable_link(link_text, selected_courses_as_string):
        sharable_url = sharable_url( selected_courses_as_string)
        return ui.a(link_text,  href=sharable_url)
    
    def sharable_url( selected_courses_as_string):
        # TODO: clean this up. currently in many places
        nonlocal courses_data
        # degree_id = courses_data.get().degree_selected.get().id

        site_protocol = session.input[".clientdata_url_protocol"]()
        site_port = session.input[".clientdata_url_port"]()
        site_url = session.input[".clientdata_url_hostname"]()
        pathname = session.input[".clientdata_url_pathname"]()

        link_to_share = f"{site_protocol}//{site_url}"
        if len(str(site_port)) > 1: # eg. ignore just "/"
            link_to_share += f":{site_port}"
        if len(pathname) > 1: # eg. ignore just "/"
            link_to_share += f"{pathname}"
        link_to_share += f"?degree_id={current_degree_id()}&courses={selected_courses_as_string}"

        return link_to_share
       

    @output
    @render.ui 
    def share_choices_button():
        nonlocal courses_data
        selected_courses_as_string = courses_data.get().selected_choices_as_string()
        number_of_choices =  len(courses_data.get().selected_courses.get())
        if number_of_choices == 0:
            return ui.div(f"🛒 Choose courses to create sharable link")
        else:
            return ui.div(ui.div(f"Share your {number_of_choices} choices:"),
                          ui.tags.textarea( sharable_url(selected_courses_as_string), id= "course_choices", hidden = True),
                          ui.a("COPY LINK", href=sharable_url(selected_courses_as_string),onclick="copyToClipboard(); return false;"),
                          ui.a("SHARE via EMAIL", href=f'''mailto:?subject=My Course Choices&body=Follow this link to see my course choices

                            {sharable_url(selected_courses_as_string)}''', style="padding: 10px;")
                          )




    @output
    @render.ui
    def course_personas():
        personas_links = [
            persona.sharable_link(session)
            for persona in courses_data.get().personas
            if persona.degree_id == current_degree_id()]

        course_help = ui.row(
               ui.span("Example pathways:"),
               *personas_links
               )
        return course_help

    @output
    @render.ui
    def grid_selected_courses():
        nonlocal courses_data
        current_degree = DataService.degree_with_id_or_default( current_degree_id())

        # dissertation_selected = CourseSelected(courses_data.get().get_dissertation(),3,1)

        
        right_most_column =  ui.column(1, 
                                    ui.row(ui.h5("YEAR 3", style = "padding: 0px"),get_credits_information(3, shortened=True)),
                                    ui.row( 
                                         courses_data.get().as_card_selected(CourseSelected(courses_data.get().get_dissertation(), 3, 1), dissertation = True),
                                         courses_data.get().as_card_nothing_selected(3, 1),
                                           style ="writing-mode: vertical-rl;text-orientation: upright;padding: 16px 0px;"),
                                    hidden = current_degree.years < 3
                                    )




        rows  = [ui.row(
                ui.column(2,ui.div("Block", style="padding-top: 32px")),
                ui.column(5, ui.row( ui.column(5,ui.h5("YEAR 1")), ui.column(7,get_credits_information(1)))),
                ui.column(5, ui.row( ui.column(5,ui.h5("YEAR 2")), ui.column(7,get_credits_information(2))), hidden = current_degree.years < 2))
            ]
        block_dates = {1: "16 Sep - 18 Oct", 2: "28 Oct - 29 Nov", 
                       3: "6 Jan - 7 Feb", 4: "17 Feb - 21 Mar", 
                       5: "7 Apr - 9 May", 6: "19 May - 20 Jun"}
        

        for block in range(1,7):
            years_widgets = []
            for year in [1,2]:
                courses_in_this_block = [ 
                    courses_data.get().as_card_selected(CourseSelected(course, year, block))
                    for course in courses_data.get().all_options_in(year, block)]
                courses_in_this_block.append(courses_data.get().as_card_nothing_selected(year, block))

                years_widgets.append(courses_in_this_block)

            new_row = ui.row(
                ui.column(2, ui.h5(block), ui.p(block_dates[block],style="font-size: small;"), style="padding-right: -20;"),
                ui.column(5, years_widgets[0]),
                ui.column(5, years_widgets[1], hidden = current_degree.years < 2),
                style = "padding: 16px 0px;"
            )
            rows.append(new_row)
        return ui.row(ui.column(11, rows), right_most_column)

    def get_credits_information(year = None, shortened=False):
        nonlocal courses_data
        current_degree = DataService.degree_with_id_or_default( current_degree_id())
        if year == None:
            total_credits = sum([(course.get_credits()) 
                                 for course in courses_data.get().selected_courses.get()])
        else:  
            total_credits = sum([(course.get_credits()) 
                                 for course in courses_data.get().selected_courses.get()
                                 if course.year == year])
            
        if year == None: # total for whole degree
            max_credits = current_degree.years * 60
        else: # just showing one year
            max_credits = 60
        
        if shortened:
            text = f"{total_credits} of {max_credits}"
        else:
            text = f"Credits: {total_credits} of {max_credits}"
        return ui.div(text, style = "padding: 0px")
    
    @output
    @render.text
    def total_credits():
        return  get_credits_information()
    


    def one_theme_count(themename,value):
        theme = StyleService.theme_infos()[themename]
        return StyleService.single_theme(themename, 1, text = f"{theme['emoji']} {value}")
    # ui.div(theme['name'],value, style=StyleService.style_theme_single(themename)) 

    @output
    @render.ui
    def overall_themes():
        nonlocal courses_data
        all_themes = [ theme
            for selected_course in courses_data.get().selected_courses.get()
            for theme in selected_course.course_info.themes
            ]
        theme_counts = dict(Counter(all_themes))
        theme_counts = dict(sorted(theme_counts.items(), key=lambda key_value: key_value[0]))
  
        return ui.popover( ui.div( [
            one_theme_count(theme_name, 
                            theme_counts[theme_name])
            for theme_name in list(theme_counts.keys())],
            style="display:flex;"
        ) , StyleService.theme_balance(theme_counts))
    

    

    @output
    @render.ui
    def total_credits_warning():
        nonlocal courses_data
        total_credits = sum([(course.get_credits()) for course in courses_data.get().selected_courses.get()])
        current_degree = DataService.degree_with_id_or_default( current_degree_id())

        max_credits = current_degree.years * 60

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
        return DataService.all_inputs_ids(current_degree_id())
    
    def get_all_inputs_add_remove():
        all_inputs = get_all_inputs_add_remove_info().values()
        print(get_all_inputs_add_remove_info().keys())
        return  all_inputs

    def get_all_inputs_add_remove_info():
        # print("session",session.input[".clientdata_url_search"]())
        return { button_id: getattr(input, button_id) 
                for button_id in  DataService.all_inputs_ids()}

    # def get_all_input_info():
    #     return { button_id: getattr(input, button_id) 
    #             for button_id in  DataService.all_inputs_ids()}
    
    def get_all_filter_buttons_info():
        return {
            **{
            f"buttonfilter_{year}_{block}" : getattr(input, f"buttonfilter_{year}_{block}") 
            for year in ["1", "2"]
            for block in ["1", "2", "3", "4", "5", "6"]
            },
            **{f"buttonfilter_3_1" : getattr(input, f"buttonfilter_3_1")}
        }
    # TODO: is there a way to not hardcode it?
    
    def get_all_filter_buttons():
        return get_all_filter_buttons_info().values()

    def which_input_changed( ):
        nonlocal input_states
        new_states = {}
        all_inputs ={**get_all_inputs_add_remove_info(), **get_all_filter_buttons_info()}
        #print("which_input_changed+",all_inputs,len(all_inputs.items()))
        for input_id, input_object in all_inputs.items():
            new_states[input_id] = input_object()

        # {"but_45678": button_oibject} # turn those into
        # {"but_45678": 2}  # those. where number is how many times I was clicked
        # old [0,0,1]
        # new [0,0,2]
        # print("inputstates",input_states.get().keys())
        if (len(input_states.get().keys()) == 0):
            old_states = {new_state_key: 0
                for new_state_key, new_state_value in new_states.items()}
        else:
            old_states = input_states.get()

        keys_that_changed = [old_state_key
                            for old_state_key, old_state_value in old_states.items()
                            if old_state_value != new_states[old_state_key]]
        
        # print("keys that changed",keys_that_changed)
        
        input_states.set(new_states)
        return keys_that_changed if len(keys_that_changed) > 0 else None
    
    @reactive.Effect
    @reactive.event(input.button_filter_reset)
    def reset_filters():
        ui.update_select( "filter_name",selected=""),
        ui.update_select( "filter_year",selected="all"),
        ui.update_select( "filter_block",selected="all")
        ui.update_select( "filter_theme",selected="all")



    @reactive.Effect
    @reactive.event(*get_all_filter_buttons())
    def any_filter_button_clicked():
        nonlocal courses_data
        clicked_button_id = which_input_changed( )
        print("CLICKED!", clicked_button_id)

        if clicked_button_id == None:
            print("--- any_course_button_clicked Isssue, nothing changes")
            return

        for click in clicked_button_id:
            year, block = courses_data.get().get_year_and_block_from_filter_button_id(click)
            ui.update_select( "filter_year",selected=f"{year}"),
            ui.update_select( "filter_block",selected=f"{block}")
            ui.update_select( "filter_name",selected=f"")
            ui.update_select( "filter_theme",selected=f"all")

    @reactive.Effect
    @reactive.event(*get_all_inputs_add_remove())
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
        courses_data.set(data_service)
    
app = App(app_ui, server)#, debug=True)