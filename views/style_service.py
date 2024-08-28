from shiny import  ui
import pandas as pd
from faicons import icon_svg as icon

class StyleService:

    def __init__(self):
        pass

    def style_course_box():
        return "padding: 10px; border: 1px solid black; margin: 2px;"
    
    def style_course_box_not_selected():
        return "padding: 10px; border: 1px dashed grey; margin: 2px;"
    
    def style_section_box():
        return "padding: 10px; border: 1px solid grey;"

    def name_shorter(long_name):
        shorter_name =  long_name.replace("health and social care", "H&SC").replace("Health and Social Care", "H&SC")
        shorter_name = shorter_name.replace("Introduction", "Intro")
        return shorter_name
    
    def info_card_for_course(course_info):
        proglang_footer=[]
        if not pd.isna(course_info.proglang):
            if course_info.proglang == "Python":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("python"))
                proglang = f"Programming language: Python"
            if course_info.proglang == "R":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("r"))
                proglang = f"Programming language: R"
            if course_info.proglang == "R and SQL":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("python"))
                proglang_footer.append("+ SQL")
                proglang = f"Programming language: Python and SQL"
        else:
            proglang = "This is not a programming course"

        
        # if self.course_info.compulsory == True:
        #     compulsory = "This course is compulsory"
        # else:
        #     compulsory = "This course is optional"
        # if not pd.isna(self.course_info.isprereq):
        #     isprereq = f"This course is a prerequisite for {self.course_info.isprereq}"
        # else:
        #     isprereq = "This course is not a prerequisite for any courses"
        # if not pd.isna(self.course_info.hasprereq):
        #     hasprereq = f"This course has prerequisites: {self.course_info.hasprereq}"
        # else:
        #     hasprereq = "This course does not have any prerequsites"
        
        more_info_card = (ui.card(
                                ui.row(ui.div(
                                    {"style": "font-weight: bold"},
                                    ui.p("Course Information"),
                                ),),
                                ui.row("‣ ","TODO: what other info about the course would we like to have here?"),
                                # ui.row("‣ ",hasprereq),
                                # ui.row("‣ ",isprereq),
                                # ui.row("‣ ",credits),
                                ui.row("‣ ",proglang),
                                ui.row(ui.tags.a("View this course on DRPS", href=course_info.link, target="_blank"))
                            ))
        return more_info_card
    
