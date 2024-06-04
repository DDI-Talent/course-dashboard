from shiny import App, render, ui

import pandas as pd

courses_df = pd.read_csv(f'./data/example_course_outline.csv')
					# [   {'id':'HEIN11037', 'year': 1, 'block': 1, ...............},
                    #     {'id':'HEIN11037', 'year': 1, 'block': 2},
                    #     {'id':'HEIN11062', 'year': 2, 'block': 5}
                    #     {'id':'HEIN11062', 'year': 1, 'block': 5},
					# 	]


selected_courses_ids = [ {'course_id':'HEIN11037', 'year': 1, 'block': 1},
                        {'course_id':'HEIN11037', 'year': 1, 'block': 2},
                        {'course_id':'HEIN11062', 'year': 2, 'block': 5}
                    #   {'course_id':'HEIN11062', 'year': 1, 'block': 5},
                        
						]

def add_course(course_id, year, block):
    selected_courses_ids.append( {'id':course_id, 'year': year, 'block': block})

def get_courses(courses_df, year=None, block=None):
    
    if year is not None:
        courses_df = courses_df[courses_df['year'].str.contains(str(year))]
    if block is not None:
        courses_df = courses_df[courses_df['block'].str.contains(str(block))]

    return courses_df[['course_name', 'course_id']].values.tolist()

def filter_taken_courses(courses_df, taken_courses):
    # {'course_id':'HEIN11062', 'year': 2, 'block': 5}

    final_df = pd.DataFrame()
    for course_info in taken_courses:
        print(course_info['year'])
        print(courses_df['year'])

        new_item_df = courses_df.loc[
            		(courses_df['year'].str.contains(str(course_info['year']))) & 
              		(courses_df['block'].str.contains(str(course_info['block']))) &
                  	(courses_df['course_id'].str.contains(str(course_info['course_id'])))]
        new_item_df['year'] = str(course_info['year'])
        new_item_df['block'] = str(course_info['block'])
        final_df = pd.concat([final_df, new_item_df ])
        print(new_item_df)
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
            df_output.loc[block] = row
    df_output = df_output.reset_index().rename(columns={'index': 'Block'})
    return df_output 

app_ui = ui.page_fixed(
    ui.output_table('courses_table')
)

def server(input, output, session):

    @render.table
    def courses_table():
        return create_output_df(courses_df, selected_courses_ids)
    

app = App(app_ui, server)