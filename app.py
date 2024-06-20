from shiny import App, render, ui, reactive, session
import pandas as pd


version = "0.3.2" # major.sprint.release
    
app_ui = ui.page_sidebar(
    ui.sidebar("Courses", 
               ui.output_ui("buttons_course_add"),
               ),
    ui.panel_title(f"Course Dashbaord v{version}"),
    ui.output_table('courses_table')
    )




def server(input, output, session):
    global selected_courses
    global courses_df
    global input_states

    courses_df = reactive.value([]) 
    selected_courses = reactive.value([])
    input_states = reactive.value({})

    def course_as_dict(course_id, year, block):
        return {'course_id':course_id, 'year': year, 'block': block}

    def course_to_button_id(course):
        year = "".join([f"{year}" for year in course['year']]) # turn [1] into "1" and [1,2] into "12"
        block = "".join([f"{block}" for block in course['block']]) # turn [1] into "1" and [1,2] into "12"
        return f"button_{course['course_id']}_{year}_{block[0]}"

    def course_from_button_id(button_id):
        button_id = button_id.replace("button_","")#"button_{course['course_id']}_{year}_{block}"
        course_id, year, block = button_id.split("_")
        return {'course_id':course_id, 'year': int(year), 'block': int(block)}


    def button_for_course(course):
        button_uid = course_to_button_id(course)
        button_label = f"{course['course_name']}"
        return ui.card(
                ui.card_header(button_label),
                ui.p("some course description"),
                # here figure out if it can be taken in manu years/blocks and add more buttons
                # should this be server side?
                ui.input_action_button(button_uid, "+ YEAR 1"),
                ui.card_footer(f"Course id: {button_uid}"),
                full_screen=True,
            )

    @output
    @render.ui
    def buttons_course_add():
        global courses_df
        return [
          button_for_course(course) 
          for _, course in courses_df.get().iterrows()
        ]

    def add_course( course_as_dictionary):
        global selected_courses
        if course_as_dictionary not in selected_courses.get() : 
            selected_courses.set(selected_courses.get() + [course_as_dictionary])
            print("selected_courses.get()",selected_courses.get())

    def remove_course( course_id, year, block):
        global selected_courses
        one_to_remove = course_as_dict(course_id, year, block) 
        selected_courses = [course 
                            for course in selected_courses
                            if course != one_to_remove]
    
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
        loaded_df['year'] = loaded_df['year'].apply(string_to_list)
        loaded_df['block'] = loaded_df['block'].apply(string_to_list)
        
        loaded_df = loaded_df.explode('year').reset_index(drop=True)

        loaded_df['year'] = loaded_df['year'].apply(lambda x: [x[0]])
        loaded_df['block'] = loaded_df['block'].apply(lambda x: x[0][0])

        loaded_df['block'] = loaded_df['block'].apply(lambda x: [x] if isinstance(x, int) else x)
        print("loaded_df")

        return loaded_df

    def load_selected_courses():
           # for testing 
        selected_courses = [ 
            # {'course_id':'HEIN11037', 'year': 1, 'block': 1},
            #                     {'course_id':'HEIN11037', 'year': 1, 'block': 2},
                                #   {'course_id':'HEIN11062', 'year': 2, 'block': 5},
                                # {'course_id':'HEIN11062', 'year': 1, 'block': 5}
                                ]
        # testing
        # selected_courses = add_course(selected_courses, 'HEIN11062',2,5)
        # selected_courses = add_course(selected_courses, 'HEIN11062',1,5)
        # selected_courses = remove_course(selected_courses, 'HEIN11062',1,5)
        return selected_courses


    courses_df.set(load_data())
    selected_courses.set(load_selected_courses())


    def get_courses(courses_df, year=None, block=None, columns_to_keep = ['course_name', 'course_id']):
        if "year" in courses_df.columns and  year is not None:
            courses_df = courses_df[courses_df['year'].eq(year)]
        if  "block" in courses_df.columns  and block is not None:
            courses_df = courses_df[courses_df['block'].eq(block)]
        return courses_df[columns_to_keep].values.tolist() if courses_df.shape[0] > 0 else  []

    def filter_taken_courses(courses_df, taken_courses):
        final_df = pd.DataFrame()
        for course_info in taken_courses:
            new_item_df = courses_df.loc[
                        (courses_df['year'].apply(lambda items: course_info['year'] in items)) &
                        (courses_df['block'].apply(lambda items: course_info['block'] in items)) &
                        (courses_df['course_id'].eq(course_info['course_id']))].copy()
            # once we know course is being taken, modify it in output to only include desired year and block
            new_item_df['year'] = int(course_info['year'])
            new_item_df['block'] = course_info['block']
            final_df = pd.concat([final_df, new_item_df ])
        return final_df

    def create_output_df(courses_df, taken_courses):
        courses_df = filter_taken_courses(courses_df, taken_courses)

        df_output = pd.DataFrame(columns=['Year 1', 'Year 2'])
        for block in range(1,7):
            row={}
            for year in range(1,3):
                # filter just selected 
                # taken_courses = courses_df[ courses_df.course_id.isin(selected_courses_ids) ]
                courses = get_courses(courses_df, year=year, block=block)
                row[f'Year {year}'] = ', '.join([f'{course[0]} ({course[1]})' for course in courses])
                # print(row)
                df_output.loc[block] = row
        df_output = df_output.reset_index().rename(columns={'index': 'Block'})
        return df_output 

    def course_data_from_button_id(button_id):
        global courses_df
        selected_courses = [course for _, course in courses_df.get().iterrows() if course_to_button_id(course) ==  button_id]
        return selected_courses[0] if len(selected_courses) > 0 else None

    # tod cleanup two below finctions into something more DRY

    
    def get_all_inputs( start_string = "button_"):
        # global courses_df
        print("get_all_inputs")
        loaded_data = load_data() #this is not from global for now, because of reactive drama
        # WARNINNG: if any buttin id is wrong everything stips working
        button_ids = [course_to_button_id(course) for _, course in loaded_data.iterrows()]
        input_values = [getattr(input, button_id) for button_id in button_ids]
    
        return input_values

    def get_all_input_info( start_string = "button_"):
        # global courses_df
        print("get_all_input_info")
        loaded_data = load_data() #this is not from global for now, because of reactive drama

        button_ids = [course_to_button_id(course) for _, course in loaded_data.iterrows()]
        input_values_dict = {button_id: getattr(input, button_id) for button_id in button_ids}



        # button_ids = [f"{start_string}{course_id}" for course_id in loaded_data['course_id'].tolist() ]
        # input_values = {button_id: getattr(input, button_id) 
		# 				for button_id in button_ids}
        # print("get_all_input_info2", input_values_dict)
        
        return input_values_dict

    # def init_set_input_states( ):
    #     global input_states
    #     print("init states - this should happen only")
    #     new_states = { input_id: input_object.get() 
	# 					for input_id, input_object in get_all_input_info().items()}
    #     input_states.set(new_states)

    def which_input_changed( ):
        global input_states
        print("which_input_changed1")

        new_states = {}
        all_inputs = get_all_input_info()
        # print("which_input_changed+",all_inputs,len(all_inputs.items()))
        for input_id, input_object in all_inputs.items():
            new_states[input_id] = input_object()

        print("---input_id DONE")
        # new_states = { 
		# 				input_id: 0  # value of a button is a number of times it was clicked
		# 				# input_id: input_object.get()  # value of a button is a number of times it was clicked
		# 				for input_id, input_object in get_all_input_info().items()
		# 				}
        # print("which_input_changed+",list(get_all_input_info().values())[0].get())
        # print("which_input_changed+",list(get_all_input_info().values()))
        # print("which_input_changed2",new_states)

		# {"but_45678": button_oibject} # turn those into
		# {"but_45678": 2}  # those. where number is how many times I was clicked
		
		# old [0,0,1]
		# new [0,0,2]
        print("input_states.get()",input_states.get())
        if (len(input_states.get().keys()) == 0):
            old_states = {new_state_key: 0
                for new_state_key, new_state_value in new_states.items()}
        else:
            old_states = input_states.get()

        print("old_states??",old_states)
        keys_that_changed = [old_state_key
                            for old_state_key, old_state_value in old_states.items()
                            if old_state_value != new_states[old_state_key]]
        
        input_states.set(new_states)
        print(new_states)
        print("keys_that_changed", keys_that_changed)
		# "but_45678"
        return keys_that_changed[0] if len(keys_that_changed) > 0 else None

    def id_button_to_course(button_id):
        return button_id.replace("button_","")

	# [0,0,0,0,0,0,0] 
	# [1,0,0,0,1,0,0]
	
    @reactive.Effect
    @reactive.event(*get_all_inputs()) 
    # @reactive.event(*get_all_inputs(), ignore_init=True) 
    # @reactive.event(input.button_HEIN11037, ignore_init=True) 
    def any_course_button_clicked():
        print("CLICKED!1")
        clicked_button = which_input_changed( )
        if clicked_button == None:
            print("--- any_course_button_clicked Isssue, nothing changes")
            return
        this_course = course_data_from_button_id(clicked_button)
        print("this_course",this_course, type(this_course),"@")
        if not (this_course is None):
            print("this_course",this_course)
            # TODO: get the actual block and year selected, if there were choices. for now, grab first letter
            # course_year = int(this_course['year'][0]) # "1 or 2" --> "1"
            # course_block = int(this_course['block'][0])
            added_course_dict = course_from_button_id(clicked_button)
            add_course( added_course_dict )

    @render.table
    @reactive.calc
    def courses_table():
        global selected_courses
        global courses_df
        print("%%%%%%%%%", selected_courses.get())
        return create_output_df(courses_df.get(), selected_courses.get())
    
 

app = App(app_ui, server)