from shiny import App, render, ui, reactive, session
import inspect
import pandas as pd

# global courses_df # can we move this to server? ui.sidebar("Courses",  would need to be dynamicly generated UI
courses_df = pd.read_csv(f'./data/example_course_outline.csv')

def button_for_course(course):
    button_uid = f"button_{course['course_id']}"
    button_label = f"{course['course_name']}"
    # print("add button ",button_uid)
    return ui.input_action_button(button_uid, button_label, color="yellow")

def get_all_courses_as_buttons(courses_df):
    # print("courses_df",[row['course_id'] for i, row in courses_df.iterrows()])
    return [
          button_for_course(course) for _, course in courses_df.iterrows()# this is possibly more consise
        ]
    

app_ui = ui.page_sidebar(
    ui.sidebar("Courses", 
               get_all_courses_as_buttons(courses_df)
               ),
    "Main content",
    ui.output_table('courses_table')
)


def server(input, output, session):
    global selected_courses
    global courses_df
    global input_states

    courses_df = reactive.value([])
    courses_df = reactive.value(pd.DataFrame({}))
    # courses_df = reactive.value(pd.DataFrame({'course_name':[],'course_id':[],'year':[],'block':[]}))
    selected_courses = reactive.value([])
    input_states = reactive.value({})


    def course_as_dict(course_id, year, block):
        return {'course_id':course_id, 'year': year, 'block': block}

    def add_course( course_id, year, block):
        # TODO: make it so that we can't add the same course many times
        global selected_courses
        print("selected_courses", selected_courses)
        selected_courses.set(selected_courses.get() + [course_as_dict(course_id, year, block) ])

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

        return courses_df[columns_to_keep].values.tolist() if courses_df.shape[0] >0 else  []

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

    def course_data_with_id(course_id):
        global courses_df
        selected_courses = [course for _, course in courses_df.get().iterrows() if course['course_id'] ==  course_id]
        return selected_courses[0] if len(selected_courses) > 0 else None


    def get_all_inputs( start_string = "button_"):
        input_values = []
        for var_name, value_list in inspect.getmembers(input):
            if var_name == "_map":
                # item_ids = [key for key, value in value_list.items() if key.startswith(start_string)]
                input_values = [getattr(input, input_id) for input_id, input_item in value_list.items() if input_id.startswith(start_string)]
                return input_values
        return []

    def get_all_input_info( start_string = "button_"):
        input_values = {}
        # input has lots of objects, but _map inclides all inputs - let's grab those that start with button_
        for var_name, value_list in inspect.getmembers(input):
            if var_name == "_map":
                input_values = {input_id: getattr(input, input_id) for input_id, input_item in value_list.items() if input_id.startswith(start_string)}
                return input_values
        return {}


    def init_set_input_states( ):
        global input_states
        print("old_states")
        new_states = { input_id: input.get() for input_id, input in get_all_input_info().items()}
        input_states.set(new_states)

    def which_input_changed( ):
        global input_states
        print("old_states")
        new_states = { input_id: input.get() for input_id, input in get_all_input_info().items()}
        old_states = input_states.get()
        print("old_states",old_states)
        keys_that_changed = [old_state_key
                            for old_state_key, old_state_value in old_states.items()
                            if old_state_value != new_states[old_state_key]]
        # TODO
        input_states.set(new_states)
        print(new_states)
        print("keys_that_changed", keys_that_changed)
        return keys_that_changed[0]

    def id_button_to_course(button_id):
        return button_id.replace("button_","")

    @reactive.Effect
    @reactive.event(*get_all_inputs(), ignore_init=True) 
    def any_course_button_clicked():
        course_id = id_button_to_course( which_input_changed( ))
        print("CLICKED!", course_id)
        this_course = course_data_with_id(course_id)
        if type(this_course) != None:
            # TODO: get the actual block and year selected, if there were choices. for now, grab first letter
            course_year = int(this_course['year'][0])
            course_block = int(this_course['block'][0])

            add_course( this_course['course_id'],course_year,course_block )
        

    # refresh items state at the beginning 


    initialized = reactive.Value(0) # 0 = no context, 1 initialising, 2 initialised
    # Function to initialize the app
    @reactive.Effect
    def init():
        if initialized.get() == 0:
            initialized.set(1)
        elif initialized.get() == 1:
            init_set_input_states()
            initialized.set(2)
        print("initialized.get()", initialized.get())


    # def init():
    #     # run once the session is created
    #     print("init")
    #     # get_all_input_info() # refresh button press counts
    #     init_set_input_states()
            
    # session.on_flush(init, once=False)


    @render.table
    def courses_table():
        global selected_courses
        global courses_df
        return create_output_df(courses_df.get(), selected_courses.get())
    
app = App(app_ui, server)