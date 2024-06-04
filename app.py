from shiny import App, render, ui

import pandas as pd

courses_df = pd.read_csv(f'./data/example_course_outline.csv')

def get_courses(courses_df, year=None, block=None):
    if year is not None:
        courses_df = courses_df[courses_df['year'].str.contains(str(year))]
    if block is not None:
        courses_df = courses_df[courses_df['block'].str.contains(str(block))]
    return courses_df[['course_name', 'course_id']].values.tolist()

def create_output_df(courses_df):
    df_output = pd.DataFrame(columns=['Year 1', 'Year 2'])
    for block in range(1,7):
        row={}
        for year in range(1,3):
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
        return create_output_df(courses_df)
    

app = App(app_ui, server)