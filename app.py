from shiny import App, render, ui, reactive, session
import pandas as pd
from collections import Counter
from models.course import Course
from models.course_selected import CourseSelected
from models.data_service import DataService
from faicons import icon_svg as icon
from views.style_service import StyleService
from htmltools import head_content


version = "1.7.3" # major.sprint.prodrelease.devrelease 
# i.e. when releasing to dev, increase devrelease number, when releasing to prod, increase prodrelease number
    
app_ui = ui.page_fixed(

 ui.head_content(ui.include_css("styles.css")),   

 ui.row(     
     ui.column(12, ui.panel_title(
         ui.row(
            ui.column(6,ui.h1(f"Course Selection Tool").add_class("align-left"), 
                      ui.div(f"(v{version})").add_class("align-left"), 
                      ui.div(ui.output_ui('about_button')).add_class("align-left"), 
                      ui.output_ui("select_degree"),),
            ui.column(3,ui.output_ui('course_personas')),
            ui.column(3, 
                        ui.row(ui.output_ui('share_choices_button')),
                        ui.row( ui.output_ui('total_credits'),  ui.output_ui('total_credits_warning')),
                        ui.row( ui.output_ui('overall_themes'))
                        )
        )))
        ),
        # .add_class("section-box"),
 ui.row(
    ui.column(4, 
                ui.h2("Available Courses:"),
                ui.output_ui("filter_panel"),
                ui.output_ui("list_all_courses")
              ).add_class("section-box"),
              ui.column(8,ui.h2("Your Courses:"),
              ui.output_ui('grid_selected_courses')
            ).add_class("section-box")
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
            prompt("Link to your choices has been coppied, so you can paste it anywhere now. Link is:", copyText.value);
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
                            choices = {"all": "All","1":"1st Year", "2": "2nd Year",  "3": "3rd Year"},
                )),
                ui.column(4,
                          ui.input_select("filter_block", "Block", 
                            choices = {"all": "All","1":"1st Block", "2": "2nd Block", "3": "3rd Block", "4": "4th Block" , "5": "5th Block" , "6": "6th Block"  },
                )),
                ui.column(4,
                          ui.input_select("filter_theme", "Theme", 
                            choices = { theme.id: f"{theme.emoji} {theme.name}"
                                for theme in StyleService.get_themes()},
                ))
            )
        ).add_class("row-tight")

    @output
    @render.ui
    def select_degree():
        nonlocal courses_data
        degree_options = {degree.id: degree.name 
                          for degree in courses_data.get().degrees }
        return ui.input_select("select_degree_dropdown", "Your program of study at the Usher Institute:", choices = degree_options, selected=current_degree_id(), width="90%;") 



    @reactive.Effect
    @reactive.event(input.select_degree_dropdown, ignore_init=True)
    async def degree_selected():
        degree_id =  input.select_degree_dropdown.get()
        await session.send_custom_message("navigate", DataService.url_to_doashboard_with_degree(session, degree_id, include_core_courses = True))


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
        current_degree = DataService.degree_with_id_or_default( current_degree_id())
        # only keep course in the years that are allowed in this degree
        years_to_keep = list(range(1, 4))
        if input.filter_year.get() != "all":
            years_to_keep = [int(input.filter_year.get())]
        
        text_to_keep = input.filter_name.get().strip().lower()
        themes_to_keep = [theme.id for theme in StyleService.themes] if input.filter_theme.get() == "all" else [input.filter_theme.get()]

        selected_courses_ids = [course.course_info.id
                                for course in courses_data.get().selected_courses.get()]
        courses_cards = [
            course_obj.as_card( show = current_degree_id() in course_obj.degree_ids, selected = course_obj.id in selected_courses_ids, degree_years = current_degree.years) 
            for course_obj in courses_data.get().course_infos
            if course_obj.takeable_in_any(years_to_keep, blocks_to_keep)
            and course_has_word(course_obj, text_to_keep)
            and len(list(set(course_obj.themes) & set(themes_to_keep))) > 0
        ]
        return courses_cards if len(courses_cards) > 0 else ui.div("No courses match these criteria")
    
    def sharable_link(link_text, selected_courses_as_string):
        sharable_url = sharable_url( selected_courses_as_string)
        return ui.a(link_text,  href=sharable_url)
    
    def ahref_link_to_ms_form(selected_courses_as_string):
        current_degree = DataService.degree_with_id_or_default( current_degree_id())
        # format changes "a{}b{}".format(1,2) into a1b2 
        ms_forms_link_filled = current_degree.link_to_ms_form.format(selected_courses_as_string, current_degree.id)
        ms_forms_link_filled.encode()
        return ms_forms_link_filled

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
    def about_button():
       return ui.popover( ui.div(ui.a(f"INFO",  href="#", action="return false;"), icon("circle-info")), about_panel().add_class('popover-large'))
    
    
    def about_panel():
            return ui.row(
                ui.column(6, ui.div(ui.h3("How to use this course-selection tool:"),
                          ui.div(f"Students at some programs at Usher Institute can use this tool to choose their elective courses and design their learning pathway."),
                          ui.tags.ol(
                            ui.tags.li(f"CHOOSE your program of study (top left)"),
                            ui.tags.li(f"ADD courses which you'd like to take (left). Yellow pin 📌 buttons will add courses to your timetable. Click info icon ℹ️ to find out more about each course."),
                            ui.tags.li(f"SEE courses appearing in each of 6 blocks for each year (right)"),
                            ui.tags.li(f"BALANCE different themes/skills and academic credits (top right). Click bar with emoji to see more details."),
                            ui.tags.li(f"FILTER available courses to know what you can pick. You can filter using dropdowns (middle left) or clicking empty blocks on timetable (right)"),
                            ui.tags.li(f"SHARE your choices with someone (top right) using a link, or submit them via online form to your course organiser."),
                            ui.tags.li(f"EXPLORE pre-selected pathways (top middle), to get inspired what courses are available."),
                          ),
                          ui.p(f"This tool is a work in progress."),
                          ui.p(f"Build using Shiny Python."),
                          ui.a("See code on Github", href= "https://github.com/DDI-Talent/course-dashboard/"),
                          ui.a("About Usher Institute", href= "https://www.ed.ac.uk/usher", target="_blank").add_style("margin-left: 10px;"),
                          )
                ),ui.column(6,ui.HTML("""<iframe id="kaltura_player" type="text/javascript"  src='https://cdnapisec.kaltura.com/p/2010292/embedPlaykitJs/uiconf_id/55171522?iframeembed=true&entry_id=1_vy5677t2&config[provider]={"widgetId":"1_tdt6q0k2"}'  style="width: 304px;height: 231px;border: 0;" allowfullscreen webkitallowfullscreen mozAllowFullScreen allow="autoplay *; fullscreen *; encrypted-media *" sandbox="allow-forms allow-same-origin allow-scripts allow-top-navigation allow-pointer-lock allow-popups allow-modals allow-orientation-lock allow-popups-to-escape-sandbox allow-presentation allow-top-navigation-by-user-activation" title="Kaltura Player"></iframe>"""))
            )



    @output
    @render.ui 
    def share_choices_button():
        nonlocal courses_data
        selected_courses_as_string = courses_data.get().selected_choices_as_string()
        number_of_choices =  len(courses_data.get().selected_courses.get())


        return ui.popover( ui.div(ui.a(f"SHARE ({number_of_choices}) CHOICES ",  href="#", action="return false;"), icon("share-from-square")), share_choices_panel())
    
    
    def share_choices_panel():
        nonlocal courses_data
        selected_courses_as_string = courses_data.get().selected_choices_as_string()
        number_of_choices =  len(courses_data.get().selected_courses.get())
        if number_of_choices == 0:
            return ui.div(f"🛒 Choose courses to create sharable link")
        else:
            return ui.div(ui.div(f"Share your {number_of_choices} choices:"),
                    
                          ui.a("COPY LINK", href=sharable_url(selected_courses_as_string),onclick="copyToClipboard(); return false;").add_class("plain-external-link full-width"),
                          ui.a("SUBMIT CHOICES via FORM", href=ahref_link_to_ms_form(selected_courses_as_string), target="_blank").add_class("plain-external-link full-width"),
                          ui.a("REFRESH URL", href=sharable_url(selected_courses_as_string)).add_class("plain-external-link full-width"),
                          ui.tags.textarea( sharable_url(selected_courses_as_string), id= "course_choices").add_class("full-width"),
                          )




    @output
    @render.ui
    def course_personas():
        personas_links = [
            persona.sharable_link(session)
            for persona in courses_data.get().personas
            if persona.degree_id == current_degree_id()]

        course_help = ui.row(
               ui.span("Pre-load example choices:"),
               *personas_links
               )
        return course_help



    @output
    @render.ui
    def grid_selected_courses():
        nonlocal courses_data
        current_degree = DataService.degree_with_id_or_default( current_degree_id())
        # dissertation_selected = CourseSelected(courses_data.get().get_dissertation(),3,1)
        
        # TODO: needs cleanup

        courses_in_year_3 = [ 
                    selected_course.course_info
                    for selected_course in courses_data.get().selected_courses.get()
                    if selected_course.year == 3
                    ]


        took_only_dissertation = len(courses_in_year_3) >= 1 and any(map( lambda course: course.credits == 60, courses_in_year_3))
    
        rows  = [ui.row(
                    ui.column(4, ui.row( ui.h5("YEAR 1").add_class("align-left"), get_credits_information(1).add_class("align-left"))),
                    ui.column(4, ui.row( ui.h5("YEAR 2").add_class("align-left"), get_credits_information(2).add_class("align-left")), hidden = current_degree.years < 2).add_class('middle-course-column'),
                    ui.column(4, ui.row( ui.h5("YEAR 3").add_class("align-left"), get_credits_information(3).add_class("align-left")), hidden = current_degree.years < 3)
                ).add_class("row-of-courses")

            ]
        block_dates = {1: "15 Sep - 24 Oct 2025", 2: "27 Oct - 5 Dec  2025", 
                       3: "5 Jan - 13 Feb 2026", 4: "16 Feb - 27 Mar 2026", 
                       5: "6 Apr - 15 May 2026", 6: "18 May - 26 Jun 2026"}
        

        for block in range(1,7):
            years_widgets = []
            for year in [1,2,3]:
                courses_in_this_block = [ 
                    course
                    for course in courses_data.get().all_options_in(year, block)]
                
                course_widgets_in_this_block = [ 
                    courses_data.get().as_card_selected(CourseSelected(course, year, block))
                    for course in courses_in_this_block]
                # hide filter button if dissertation is already picked, or there is nothing to take there
                took_dissertation_so_hide_other_year_3 = (year == 3 and block != 1 and took_only_dissertation) 
                any_allowed_courses_in_block = any([ 
                    current_degree_id() in course.degree_ids
                    for course in courses_data.get().all_options_in(year, block)])
                force_hide =  took_dissertation_so_hide_other_year_3 or len(courses_in_this_block) == 0 or not any_allowed_courses_in_block
                course_widgets_in_this_block.append(courses_data.get().as_card_nothing_selected(year, block, force_hide= force_hide))

# or (took_dissertation and block >1) # todo: shall we hide filters in year 3 if dissertation is taken
                years_widgets.append(course_widgets_in_this_block)

            new_rows = [
                ui.row(
                    ui.h5( f"Block {block}").add_class("align-left"), ui.p( f"({block_dates[block]})").add_class("align-left")
                ),
                ui.row(
                    StyleService.year_divider_mobile(1),
                    ui.column(4, years_widgets[0]),
                    StyleService.year_divider_mobile(2, hidden=current_degree.years < 2),
                    ui.column(4, years_widgets[1], hidden = current_degree.years < 2).add_class('middle-course-column'),
                    StyleService.year_divider_mobile(3, hidden=current_degree.years < 3),
                    ui.column(4, years_widgets[2], hidden = current_degree.years < 3 )
                ).add_class("row-of-courses")
            ]
            rows.extend(new_rows)
        return ui.row(ui.column(12, rows), style="margin: 0px;")

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
            text = f"({total_credits} of {max_credits} credits)"
        return ui.div(text, style = "padding: 0px")
    
    @output
    @render.text
    def total_credits():
        return  get_credits_information()
    


    def one_theme_count(theme_id,value):
        theme = StyleService.get_theme(theme_id)
        return StyleService.single_theme(theme_id, 1, text = f"{theme.emoji} {value}")

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
            style="display:flex; ",
        ) , StyleService.theme_balance(theme_counts))
    

    @output
    @render.ui
    def total_credits_warning():
        nonlocal courses_data
        print([(course.get_credits()) for course in courses_data.get().selected_courses.get()])
        total_credits = sum([(course.get_credits()) for course in courses_data.get().selected_courses.get()])
        current_degree = DataService.degree_with_id_or_default( current_degree_id())

        max_credits = current_degree.years * 60

        if total_credits == max_credits:
            warning = ""
            style_class = ""
        elif total_credits > max_credits:
            warning = f"(remove {total_credits - max_credits})"
            style_class="warning warning_too_much"
        else: 
            warning = f" (add {max_credits - total_credits})"
            style_class="warning warning_too_little"
        return ui.div(warning).add_class(style_class)

    def get_all_inputs_ids():
        return DataService.all_inputs_ids(current_degree_id())
    
    def get_all_inputs_add_remove():
        all_inputs = get_all_inputs_add_remove_info().values()

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
            f"buttonfilter_{year}_{block}" : getattr(input, f"buttonfilter_{year}_{block}") 
            for year in ["1", "2","3"]
            for block in ["1", "2", "3", "4", "5", "6"]
        }
    # TODO: is there a way to not hardcode it?
    
    def get_all_filter_buttons():
        return get_all_filter_buttons_info().values()

    def which_input_changed( ):
        nonlocal input_states
        new_states = {}
        all_inputs ={**get_all_inputs_add_remove_info(), **get_all_filter_buttons_info()}

        print("CLICKED!")
        # for k,v in all_inputs.items():
        #     print(f"{k:>50}, {v}")


        #print("which_input_changed+",all_inputs,len(all_inputs.items()))
        for input_id, input_object in all_inputs.items():
            print("CLICKED!a", input_id)
            new_states[input_id] = input_object()
            print("CLICKED!b", input_id)
            


        # {"but_45678": button_oibject} # turn those into
        # {"but_45678": 2}  # those. where number is how many times I was clicked
        # old [0,0,1]
        # new [0,0,2]
        # print("inputstates",input_states.get().keys())
        print("CLICKED 1")

        if (len(input_states.get().keys()) == 0):
            old_states = {new_state_key: 0
                for new_state_key, new_state_value in new_states.items()}
        else:
            old_states = input_states.get()

        print("CLICKED 2")

        keys_that_changed = [old_state_key
                            for old_state_key, old_state_value in old_states.items()
                            if old_state_value != new_states[old_state_key]]
        
        print("keys that changed",keys_that_changed)
        
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
