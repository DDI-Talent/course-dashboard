from shiny import App, render, ui, reactive, session
import pandas as pd


version = "0.3.2" # major.sprint.release

global string_to_list
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
# global courses_df # can we move this to server? ui.sidebar("Courses",  would need to be dynamicly generated UI
global load_data
def load_data():
    loaded_df = pd.read_csv(f'./data/example_course_outline.csv')
    loaded_df['year'] = loaded_df['year'].apply(string_to_list)
    loaded_df['block'] = loaded_df['block'].apply(string_to_list)
    
    loaded_df = loaded_df.explode('year').reset_index(drop=True)

    loaded_df['year'] = loaded_df['year'].apply(lambda x: [x[0]])
    loaded_df['block'] = loaded_df['block'].apply(lambda x: x[0][0])

    loaded_df['block'] = loaded_df['block'].apply(lambda x: [x] if isinstance(x, int) else x)

    # new code to combine year and block data in the course id so that when creating buttons from course ids the ids are unique 
    for index, row in loaded_df.iterrows():
        if 2 in row['year']:
            loaded_df.at[index, 'block'] = [x+6 for x in row['block']] # this adds 6 onto any block that is in year 2, so blocks 1-6 represent year 1 blocks and blocks 7-12 represent year 2 blocks

    # create new column 'course_id_with_info' so that each id is unique - will be HEIN0000_1_2 for a course that runs in year 1 block 1 and 2, or HEIN0000_7_8 for a course that runs in year 2 block 1 and 2
    loaded_df['course_id_with_info'] = loaded_df.apply(lambda row: row['course_id'] + '_' + '_'.join(map(str, row['block'])), axis=1)
    return loaded_df

courses_df = load_data()    

def button_for_course(course):
    
    button_label = f"{course['course_name']}"
    course_id = f"{course['course_id']}"

    duplicates = courses_df[courses_df['course_name'].duplicated()]
    if course['course_name'] in duplicates['course_name'].tolist():
        button_uid = [f"button_{course_id_info}" for course_id_info in courses_df[courses_df['course_name'] == course['course_name']]['course_id_with_info'].tolist()]
        choose_button = [
                [ui.input_action_button(button_uid[i], f"➕ YEAR {i+1}") for i in range(len(button_uid))],
                ]
    else:
        button_uid = f"button_{course['course_id_with_info']}"
        if int(button_uid.split('_')[-1]) > 6:
            year = 2
        else:
            year = 1
        choose_button = ui.input_action_button(button_uid, f"➕ YEAR {year}"),

    return ui.card(
        ui.card_header(button_label),
        ui.p("some course description"),
        # here figure out if it can be taken in manu years/blocks and add more buttons
        # should this be server side?
        # ui.layout_columns(*card),
        choose_button,
        ui.card_footer(f"Course id: {course_id}"),
        full_screen=True,
    ),


def get_all_courses_as_buttons(courses_df):
    courses_df = courses_df.drop_duplicates(subset='course_name')

    return [
          button_for_course(course) 
          for _, course in courses_df.iterrows()
        ]
    
app_ui = ui.page_sidebar(
    ui.sidebar("Courses", 
               get_all_courses_as_buttons(courses_df),
               width=400,
               bg = '#579a9f6d',
               ),
    ui.panel_title(f"Course Dashboard v{version}"),
        ui.layout_columns(
            # ui.output_ui('test_card'),
            ui.output_text('block_header'),ui.output_text('y1_header'),ui.output_text('y2_header'),
            ui.output_text('block1'),ui.output_text('block_y1b1'),ui.output_text('block_y2b1'),
            ui.output_text('block2'),ui.output_text('block_y1b2'),ui.output_text('block_y2b2'),
            ui.output_text('block3'),ui.output_text('block_y1b3'),ui.output_text('block_y2b3'),
            ui.output_text('block4'),ui.output_text('block_y1b4'),ui.output_text('block_y2b4'),
            ui.output_text('block5'),ui.output_text('block_y1b5'),ui.output_text('block_y2b5'),
            ui.output_text('block6'),ui.output_text('block_y1b6'),ui.output_text('block_y2b6'),

            # ui.output_table('courses_table'),

            col_widths=[2, 5, 5],
        )   
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

    def add_course( course_id, year, block):
        global selected_courses
        print("selected_courses", selected_courses)
        course_as_dictionary = course_as_dict(course_id, year, block) 
        if course_as_dictionary not in selected_courses.get() : 
            selected_courses.set(selected_courses.get() + [course_as_dictionary])

    def remove_course( course_id, year, block):
        global selected_courses
        one_to_remove = course_as_dict(course_id, year, block) 
        selected_courses = [course 
                            for course in selected_courses
                            if course != one_to_remove]
    
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
                block_taken = block+(year-1)*6 # blocks are now 1-12, so year 1 is 1-6, year 2 is 7-12, so we need to adjust block number according to this, year 1 - number doesn't change, year 2 - just add 6
                courses = get_courses(courses_df, year=year, block=block_taken)
                row[f'Year {year}'] = ', '.join([f'{course[0]} ({course[1]})' for course in courses])
                # row[f'Year {year}'] = ', '.join([ui.card(ui.card_header(course[0])) for course in courses])

                # print(row)
                df_output.loc[block] = row
        df_output = df_output.reset_index().rename(columns={'index': 'Block'})
        return df_output 

    def course_data_with_id(course_id):
        global courses_df
        selected_courses = [course for _, course in courses_df.get().iterrows() if course['course_id_with_info'] ==  course_id]
        return selected_courses[0] if len(selected_courses) > 0 else None

    # tod cleanup two below finctions into something more DRY

    def get_all_inputs( start_string = "button_"):
        # global courses_df
        loaded_data = load_data() #this is not from global for now, because of reactive drama
        button_ids = [f"{start_string}{course_id}" for course_id in loaded_data['course_id_with_info'].tolist() ]
        # button_ids = button_ids + [f"button_{course_id}_2" for course_id in loaded_data['course_id'].tolist()]# if len(course_data_with_id(course_id)['year']) > 1
        
        input_values = [getattr(input, button_id) for button_id in button_ids]
        return input_values

    def get_all_input_info( start_string = "button_"):
        # global courses_df
        loaded_data = load_data() #this is not from global for now, because of reactive drama
        button_ids = [f"{start_string}{course_id}" for course_id in loaded_data['course_id_with_info'].tolist() ]
        # button_ids = button_ids + [f"button_{course_id}_2" for course_id in loaded_data['course_id'].tolist()]# if len(course_data_with_id(course_id)['year']) > 1

        input_values = {button_id: getattr(input, button_id) for button_id in button_ids}
        return input_values

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
        # button_id = button_id.replace("_2","")
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
            course_block = int(this_course['block'][0]) # does this also need to be adjusted for year 2? - block+(year-1)*6?

            add_course( this_course['course_id'],course_year,course_block)

            block_taken = course_block-(course_year-1)*6 # blocks are now 1-12, so we need to adjust block number according to this, year 1 - number doesn't change, year 2 - just minus 6
            print(f"course taken: year {course_year}, block {block_taken}")
            card_selector = f'#block_y{course_year}b{block_taken}'
            ui.insert_ui(
                ui.card(f'{this_course['course_name']}',
                        # to do - make remove button remove_ui from table
                        ui.input_action_button(f'remove_button_{this_course['course_id_with_info']}_{card_selector[1:]}', f"➖")
                        ),
                        
                f'{card_selector}')
                


    # refresh items state at the beginning 


    initialized = reactive.Value(0) # 0 = no context, 1 initialising, 2 initialised
    # Function to initialize the app
    @reactive.Effect
    def init():
        # this is an awful hack to execture something once, once app is initialised, and then never again
        if initialized.get() == 0:
            initialized.set(1)
        elif initialized.get() == 1:
            init_set_input_states()
            initialized.set(2)
        # print("initialized.get()", initialized.get())


    # def init():
    #     # run once the session is created
    #     print("init")
    #     # get_all_input_info() # refresh button press counts
    #     init_set_input_states()
            
    # session.on_flush(init, once=False)


    @render.table
    # def courses_table():
    #     global selected_courses
    #     global courses_df
    #     return create_output_df(courses_df.get(), selected_courses.get())
    def courses_table():
        global selected_courses
        global courses_df
        output_df = create_output_df(courses_df.get(), selected_courses.get())
        output_df.iloc[0,1] = ui.card(ui.card_header(output_df.iloc[0,1]))
        return output_df
    
    @render.text
    def block_header():
        return 'Block'
    @render.text
    def y1_header():
        return 'Year 1'
    @render.text
    def y2_header():
        return 'Year 2'
    @render.text
    def block1():
        return '1'  
    @render.text
    def block_y1b1():
        return ''
    @render.text
    def block_y2b1():
        return ''
    @render.text
    def block2():
        return '2' 
    @render.text
    def block_y1b2():
        return ''
    @render.text
    def block_y2b2():
        return '' 
    @render.text
    def block3():
        return '3'  
    @render.text
    def block_y1b3():
        return ''
    @render.text
    def block_y2b3():
        return '' 
    @render.text
    def block4():
        return '4' 
    @render.text
    def block_y1b4():
        return ''
    @render.text
    def block_y2b4():
        return ''  
    @render.text
    def block5():
        return '5'  
    @render.text
    def block_y1b5():
        return ''
    @render.text
    def block_y2b5():
        return '' 
    @render.text
    def block6():
        return '6'  
    @render.text
    def block_y1b6():
        return ''
    @render.text
    def block_y2b6():
        return ''   
    
    # ui.insert_ui(ui.card('test'), '#block_e1')


app = App(app_ui, server)