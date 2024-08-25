class StyleService:

    def __init__(self):
        pass

    def style_course_box():
        return "padding: 10px; border: 1px solid black; margin: 2px;"
    
    def name_shorter(long_name):
        shorter_name =  long_name.replace("health and social care", "H&SC").replace("Health and Social Care", "H&SC")
        shorter_name = shorter_name.replace("Introduction", "Intro")
        return shorter_name