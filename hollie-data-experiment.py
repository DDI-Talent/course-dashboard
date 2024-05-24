from shiny import reactive, req
from shiny.express import input, ui, render 
import pandas as pd

course_names = ['Introduction to data science in health and social care', 'Introductory applied machine learning 20 credits', 'Digital technologies in health and social care', 'Data Types & Structures in R & Python', 'Research design for data science in health and social care', 'Systems thinking', 'Data ethics in health and social care', 'Foundations of Software Development in Health and Social Care', 'Applied software development in health and social care (Python 2)']
course_ids = ['HEIN11037', 'HEIN11234', 'HEIN11043', 'HEIN11068', 'HEIN11057', 'HEIN11054', 'HEIN11059', 'HEIN11045', 'HEIN11066']
y1b1 = ['AND','','','','','','','','']
y1b2 = ['AND','','','','','','','','']
y1b3 = ['','AND1','','','','','','','']
y1b4 = ['','AND1','','','','','','','']
y1b5 = ['','','TRUE','','','','','','']
y1b6 = ['','','TRUE','TRUE','','','','','']

y2b1 = ['','','','','AND','','','','']
y2b2 = ['','','','','','TRUE','','','']
y2b3 = ['','AND2','','','','','TRUE','','']
y2b4 = ['','AND2','','','','','','TRUE','']
y2b5 = ['','','','','','','','','TRUE']
y2b6 = ['','','','TRUE','AND','','','','']

# y1b1 AND y1b2 - takes 10 weeks
# y1b6 OR y2b6 - delivered once, but you can take it at many points
# y1b5 - once chance to take it
# (y1b1 AND y1b2) OR (y1b1 AND y1b2 )

df_courses = pd.DataFrame({'course_names':course_names, 'course_ids':course_ids, 'y1b1':y1b1, 'y1b2':y1b2, 'y1b3':y1b3, 'y1b4':y1b4, 'y1b5':y1b5, 'y1b6':y1b6, 'y2b1':y2b1, 'y2b2':y2b2, 'y2b3':y2b3, 'y2b4':y2b4, 'y2b5':y2b5, 'y2b6':y2b6})


def courses_for(year, block, all_courses_df):
    return all_courses_df.loc[ 
                all_courses_df[f'y{year}b{block}'].notnull() & (all_courses_df[f'y{year}b{block}'] != ''),
                ['course_names', 'course_ids']
            ]
    # return all_courses_df.loc[all_courses_df[f'y{year}b{block}'].notnull() & (all_courses_df[f'y{year}b{block}'] != ''), 'course_names'].tolist()

print(courses_for(1,6,df_courses))


# raw_data = [['Introduction to data science in health and social care', 'HEIN11037', ['AND','AND','',  '','','','','','','','','']],
#             ['Introductory applied machine learning 20 credits', 'HEIN11234',     [  '',      '','AND','AND','','','','','','','','']]]

# pd.DataFrame(raw_data, columns=['course_name', 'course_id', 'availability_matrix'])
# course_names = df_courses.courses.values

# yr1 = pd.DataFrame({'Block 1':df_courses.loc[df_courses['y1b1'].notnull() & (df_courses['y1b1'] != ''), 'courses'].tolist(), 'Block 2':df_courses.loc[df_courses['y1b2'].notnull() & (df_courses['y1b2'] != ''), 'courses'].tolist(), 'Block 3':df_courses.loc[df_courses['y1b3'].notnull() & (df_courses['y1b3'] != ''), 'courses'].tolist(), 'Block 4':df_courses.loc[df_courses['y1b4'].notnull() & (df_courses['y1b4'] != ''), 'courses'].tolist(), 'Block 5':df_courses.loc[df_courses['y1b5'].notnull() & (df_courses['y1b5'] != ''), 'courses'].tolist(), 'Block 6':df_courses.loc[df_courses['y1b6'].notnull() & (df_courses['y1b6'] != ''), 'courses'].tolist()})
# yr2 = pd.DataFrame({'Block 1':df_courses.loc[df_courses['y2b1'].notnull() & (df_courses['y2b1'] != ''), 'courses'].tolist(), 'Block 2':df_courses.loc[df_courses['y2b2'].notnull() & (df_courses['y2b2'] != ''), 'courses'].tolist(), 'Block 3':df_courses.loc[df_courses['y2b3'].notnull() & (df_courses['y2b3'] != ''), 'courses'].tolist(), 'Block 4':df_courses.loc[df_courses['y2b4'].notnull() & (df_courses['y2b4'] != ''), 'courses'].tolist(), 'Block 5':df_courses.loc[df_courses['y2b5'].notnull() & (df_courses['y2b5'] != ''), 'courses'].tolist(), 'Block 6':df_courses.loc[df_courses['y2b6'].notnull() & (df_courses['y2b6'] != ''), 'courses'].tolist()})

# "Year 1"
# @render.data_frame
# def render_df1():
#     return render.DataTable(yr1)

# "Year 2"
# @render.data_frame
# def render_df2():
#     return render.DataTable(yr2)