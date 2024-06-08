from shiny import App, render, ui

import pandas as pd

version = "0.3.0" # major.sprint.release

app_ui = ui.page_fixed(
	ui.panel_title(f"Course Dashbaord v{version}"),
    ui.output_table('courses_table')
)

def server(input, output, session):


    def course_as_dict(course_id, year, block):
        return {'course_id':course_id, 'year': year, 'block': block}

    def add_course(selected_courses, course_id, year, block):
        # for now we can add the same course many times
        selected_courses.append(course_as_dict(course_id, year, block) )
        return selected_courses

    def remove_course(selected_courses, course_id, year, block):
        one_to_remove = course_as_dict(course_id, year, block) 
        selected_courses = [course 
                            for course in selected_courses
                            if course != one_to_remove]
        return selected_courses
    
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
        selected_courses = [ {'course_id':'HEIN11037', 'year': 1, 'block': 1},
                                {'course_id':'HEIN11037', 'year': 1, 'block': 2},
                                #   {'course_id':'HEIN11062', 'year': 2, 'block': 5},
                                {'course_id':'HEIN11062', 'year': 1, 'block': 5}
                                ]
    
        # testing
        selected_courses = add_course(selected_courses, 'HEIN11062',2,5)
        selected_courses = add_course(selected_courses, 'HEIN11062',1,5)
        # selected_courses = remove_course(selected_courses, 'HEIN11062',1,5)
        return selected_courses

    courses_df = load_data()
    selected_courses = load_selected_courses()




    def get_courses(courses_df, year=None, block=None, columns_to_keep = ['course_name', 'course_id']):
        if year is not None:
            courses_df = courses_df[courses_df['year'].eq(year)]
        if block is not None:
            courses_df = courses_df[courses_df['block'].eq(block)]

        return courses_df[columns_to_keep].values.tolist()

    def filter_taken_courses(courses_df, taken_courses):
        final_df = pd.DataFrame()
        for course_info in taken_courses:
            new_item_df = courses_df.loc[
                        (courses_df['year'].apply(lambda items: course_info['year'] in items)) &
                        (courses_df['block'].apply(lambda items: course_info['block'] in items)) &
                        (courses_df['course_id'].eq(course_info['course_id']))]
            # once we know course is being taken, modify it in output to only include desired year and block
            new_item_df['year'] = course_info['year']
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
                df_output.loc[block] = row
        df_output = df_output.reset_index().rename(columns={'index': 'Block'})
        return df_output 

    @render.table
    def courses_table():
        return create_output_df(courses_df, selected_courses)
    

app = App(app_ui, server)