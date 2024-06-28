from shiny import App, render, ui, reactive, session
import pandas as pd
from models.course import Course


version = "0.4.1" # major.sprint.release
    
app_ui = ui.page_sidebar(
    ui.sidebar("Courses", 
               ui.output_ui("list_all_courses"),
               ui.input_action_button("clickme","click me"),
               width=400,
               bg = '#579a9f6d',
               ),
    ui.panel_title(f"Course Dashbaord v{version}"),
    # ui.output_table('grid_selected_courses')
)


def server(input, output, session):
    global selected_courses
    global courses_objects
    global input_states

    courses_objects = reactive.value([]) 
    selected_courses = reactive.value([])
    input_states = reactive.value({})
    
    def list_to_str(number_list):
        return "&".join([f"{year}" for year in number_list])

    def course_to_button_id(course, year, block, action = "buttonadd_"):
        return f"{action}{course.id}_{year}_{block}"

    def course_dict_to_button_id(course_dict, action = "buttonadd_"):
        return f"{action}{course_dict.id}_{course_dict['year']}_{course_dict['block']}"

    def is_this_add_button(button_id):
        return "buttonadd_" in button_id

    def course_from_button_id(button_id):
        button_id = button_id.replace("buttonadd_","")
        button_id = button_id.replace("buttonremove_","")
        #"button_{course['course_id']}_{year}_{block}"
        course_id, year, block = button_id.split("_")
        return {'course_id':course_id, 'year': int(year), 'block': int(block)}



    # def card_for_course_info(course):
    #     button_label = f"{course['course_name']}"
    #     courses_df_temp = courses_objects.get()
    #     # course_instances is one or more
    #     course_instances = courses_df_temp[courses_df_temp['course_name'] == course['course_name']]
    #     buttons = []
    #     for index, course_instance in course_instances.iterrows():
    #         for year in course_instance['year']:
    #             for block in course_instance['block']:
    #                 button_uid = course_to_button_id(course, year, block) #TODO: use course year and block in id
    #                 buttons.append(ui.input_action_button(button_uid, 
    #                                 f"TAKE in Y{year} B{block}")
    #                             )

    #     return ui.card(
    #             ui.card_header(button_label),
    #             *buttons,
    #             ui.card_footer(f"some course description here"),
    #             full_screen=True,
    #         )

    @output
    @render.ui
    def list_all_courses():
        # global courses_objects
        # courses_df_no_duplicates = courses_objects.get().drop_duplicates(subset='course_name')
        print('test')
        print(courses_objects.get())
        return [
            course_obj.as_card() 
          for course_obj in courses_objects.get()
        ]

    def add_course( course_as_dictionary):
        global selected_courses
        if course_as_dictionary not in selected_courses.get() : 
            selected_courses.set(selected_courses.get() + [course_as_dictionary])
            # print("selected_courses.get()",selected_courses.get())

    def remove_course(course_as_dictionary):
        global selected_courses
        selected_courses_new = [course 
                            for course in selected_courses.get()
                            if course != course_as_dictionary]
        selected_courses.set(selected_courses_new)

    
    # turns string like "1 or 2" into ([(1, 'or') (2, 'or')]). turns "1" into [1[], and "banana" into []
    def string_to_list(string_to_parse):
        if "or" in string_to_parse:
            return [(int(item.strip()), 'or') for item in string_to_parse.split('or')]
        elif "and" in string_to_parse:
            return [(list(map(int, string_to_parse.split('and'))), 'and')]
        else:
            try:
                return [(int(string_to_parse), '')]
            except:
                return []
 
    # @render.ui
    def load_data():
        loaded_df = pd.read_csv(f'./data/example_course_outline.csv')

        # loaded_df['year'] = loaded_df['year'].apply(string_to_list)
        # loaded_df['block'] = loaded_df['block'].apply(string_to_list)
        
        # TODO: at what point do we need to duplicate two-year-option courses
        # loaded_df = loaded_df.explode('year').reset_index(drop=True)

        # loaded_df['year'] = loaded_df['year'].apply(lambda x: [x[0]])
        # loaded_df['block'] = loaded_df['block'].apply(lambda x: x[0][0])
        return [ Course(row)
                for _, row in loaded_df.iterrows()]

    def load_selected_courses():
           # for testing 
        selected_courses = [   ]
        return selected_courses


    courses_objects.set(load_data())
    selected_courses.set(load_selected_courses())


    def get_courses(courses_df, year=None, block=None, columns_to_keep = ['course_name', 'course_id']):
        if "year" in courses_df.columns and  year is not None:
            courses_df = courses_df[courses_df['year'].eq(year)]
        if  "block" in courses_df.columns  and block is not None:
            courses_df = courses_df[courses_df['block'].eq(block)]
        return [course for _, course in courses_df.iterrows()]
        # return courses_df[columns_to_keep].values.tolist() if courses_df.shape[0] > 0 else  []

    def filter_taken_courses(courses_df, taken_courses, include_all = False):
        if include_all:
            taken_courses_to_use = [
                course_as_dict(course.course_id, year, block) 
                for _, course in courses_df.iterrows()
                for year in course['year']
                for block in course['block']
            ]
        else:
            taken_courses_to_use = taken_courses

        final_df = pd.DataFrame()
        for course_info in taken_courses_to_use:
            new_item_df = courses_df.loc[
                        (courses_df['year'].apply(lambda items: course_info['year'] in items)) &
                        (courses_df['block'].apply(lambda items: course_info['block'] in items)) &
                        (courses_df['course_id'].eq(course_info['course_id']))].copy()
            # once we know course is being taken, modify it in output to only include desired year and block
            new_item_df['year'] = int(course_info['year'])
            new_item_df['block'] = course_info['block']
            final_df = pd.concat([final_df, new_item_df ])
        return final_df

    def taken_course_to_widget(course, hide = False):
        # print("taken_course_to_widget",course, hide)
        return ui.card(
            ui.card_header(course.id),
            ui.p(course.name),
            ui.input_action_button(course.as_button(action="buttonremove_"), "remove"),
            hidden = hide
        )
        
    def create_taken_courses_output_ui_all_experiment(courses_df, taken_courses):
        courses_df = filter_taken_courses(courses_df, taken_courses, include_all=True) # what if we don;t filter
     
        rows  = []
        for block in range(1,7):
            # DRY this up
            year1_courses = get_courses(courses_df, year=1, block=block)
            if len(year1_courses) > 0:
                # course = year1_courses[0]
                year1_widget = []
                for course in year1_courses:
                    hide = course_df_as_dict(course) not in taken_courses
                    year1_widget.append( taken_course_to_widget(course, hide = hide))

            year2_courses = get_courses(courses_df, year=2, block=block)
            if len(year2_courses) > 0:
                year2_widget = []
                for course in year2_courses:
                    hide = course_df_as_dict(course) not in taken_courses
                    year2_widget.append( taken_course_to_widget(course, hide = hide))        

            new_row = ui.row(
                ui.column(2, ui.p(block)),
                ui.column(5, year1_widget),
                ui.column(5, year2_widget)
            )
            rows.append(new_row)
        return ui.column(12, rows)


    def create_taken_courses_output_ui(courses_df, taken_courses):
        courses_df = filter_taken_courses(courses_df, taken_courses)

        rows  = []
        for block in range(1,7):
            year1 = get_courses(courses_df, year=1, block=block)
            year2 = get_courses(courses_df, year=2, block=block)
            print(year1)
            new_row = ui.row(
                ui.column(2, ui.p(block)),
                ui.column(5, taken_course_to_widget(year1[0]) if len(year1) > 0 else ""),
                ui.column(5, taken_course_to_widget(year2[0]) if len(year2) > 0 else "")
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
                            if course_to_button_id(course,year,block, action=action) ==  button_id]
        return selected_courses[0] if len(selected_courses) > 0 else None

    # tod cleanup two below finctions into something more DRY

    def get_all_inputs_ids( ):
        global courses_objects
        loaded_data = load_data()

        return [   button_id
            for course in loaded_data
            for button_id in course.all_possible_button_ids()
        ]

    
    def get_all_inputs():

        inputs_stuff = get_all_input_info().values()
        print("inputs_stuff")
        print(inputs_stuff)
        return inputs_stuff

    def get_all_input_info():
        all_ids = get_all_inputs_ids( )
        print("all_ids",all_ids)
        input_values_dict = {button_id: getattr(input, button_id) 
                             for button_id in  all_ids}
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

	# [0,0,0,0,0,0,0] 
	# [1,0,0,0,1,0,0]
	
    @reactive.Effect
    @reactive.event(*get_all_inputs())
    def any_course_button_clicked():
        print("CLICKED!1")
        clicked_button = which_input_changed( )
        if clicked_button == None:
            print("--- any_course_button_clicked Isssue, nothing changes")
            return
        this_course = course_data_from_button_id(clicked_button)
        if not (this_course is None):
            # TODO: get the actual block and year selected, if there were choices. for now, grab first letter
            added_course_dict = course_from_button_id(clicked_button)
            if is_this_add_button(clicked_button):
                add_course( added_course_dict )
            else:
                remove_course( added_course_dict )

    @render.ui
    @reactive.calc
    def grid_selected_courses():
        global selected_courses
        global courses_objects
        # print("%%%%%%%%%", selected_courses.get())
        
        return create_taken_courses_output_ui_all_experiment(courses_objects.get(), selected_courses.get())
        # return create_taken_courses_output_ui(courses_df.get(), selected_courses.get())
    
 

app = App(app_ui, server)