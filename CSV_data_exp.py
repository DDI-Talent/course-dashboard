import pandas as pd

courses_df = pd.read_csv('/home/hollie_hindley/Documents/data_internship/course-dashboard/example_course_outline.csv')

# print(courses_df)

def get_courses(courses_df, year=None, block=None):
    if year is not None:
        courses_df = courses_df[courses_df['year'].str.contains(str(year))]
    if block is not None:
        courses_df = courses_df[courses_df['block'].str.contains(str(block))]
    return courses_df[['course_name', 'course_id']].values.tolist()

# print('\n year only:', get_courses(courses_df, year=1), '\n') 
# print('block only:', get_courses(courses_df, block=2), '\n')  
# print('year and block:', get_courses(courses_df, year=1, block=2), '\n')  
# print('no filtering:', get_courses(courses_df), '\n')  

df_output = pd.DataFrame(columns=['Year 1', 'Year 2'])

for block in range(1,7):
    row={}
    for year in range(1,3):
        courses = get_courses(courses_df, year=year, block=block)
        row[f'Year {year}'] = ', '.join([f'{course[0]} ({course[1]})' for course in courses])
        df_output.loc[block] = row
    # print(f'Year {year}, Block {block}:', get_courses(courses_df, year=year, block=block), '\n')

# df_output['Block'] = df_output.index
df_output = df_output.reset_index().rename(columns={'index': 'Block'})

print(df_output)
