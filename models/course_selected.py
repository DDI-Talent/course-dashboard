import pandas as pd
from shiny import ui
from models.course import Course
from faicons import icon_svg as icon
from views.style_service import StyleService

class CourseSelected:

    def __init__(self, course_info, year, block):
        self.course_info = course_info
        self.year = year
        self.block = block

    def to_selected_button_id(self, action):
        return f"{action}{self.course_info.id}_{self.year}_{self.block}"

    def get_credits(self):
        return self.course_info.credits
    
    def get_colour(self):
        return self.course_info.card_colour.get()

    def as_card_selected(self, show = False):
        button_label = StyleService.name_shorter(self.course_info.name) #+ " " + self.course_info.id
        buttons = []
        button_uid_remove = self.to_selected_button_id( "buttonremove_")
        
        credits = f"Credits: {self.course_info.credits}"
        proglang_footer=[]
        if not pd.isna(self.course_info.proglang):
            if self.course_info.proglang == "Python":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("python"))
                proglang = f"Programming language: Python"
            if self.course_info.proglang == "R":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("r"))
                proglang = f"Programming language: R"
            if self.course_info.proglang == "R and SQL":
                # footer_items.append("Programming language: ")
                proglang_footer.append(icon("python"))
                proglang_footer.append("+ SQL")
                proglang = f"Programming language: Python and SQL"
        else:
            proglang = "This is not a programming course"

        
        if self.course_info.compulsory == True:
            compulsory = "This course is compulsory"
        else:
            compulsory = "This course is optional"
        if not pd.isna(self.course_info.isprereq):
            isprereq = f"This course is a prerequisite for {self.course_info.isprereq}"
        else:
            isprereq = "This course is not a prerequisite for any courses"
        if not pd.isna(self.course_info.hasprereq):
            hasprereq = f"This course has prerequisites: {self.course_info.hasprereq}"
        else:
            hasprereq = "This course does not have any prerequsites"
        
        more_info_card = (ui.card(
                                ui.row(ui.div(
                                    {"style": "font-weight: bold"},
                                    ui.p("Course Information"),
                                ),),
                                ui.row("‣ ",compulsory),
                                ui.row("‣ ",hasprereq),
                                ui.row("‣ ",isprereq),
                                ui.row("‣ ",credits),
                                ui.row("‣ ",proglang),
                                ui.row(ui.tags.a("View this course on DRPS", href=self.course_info.link, target="_blank"))
                            ))
        if len(proglang_footer) > 1:
            footer_cols = [9,3]
        else:
            footer_cols = [11,1]
        
        return ui.div( 
                            ui.div(  button_label),
                            ui.row( 
                                ui.column(1,ui.popover( icon("circle-info"), more_info_card)), 
                                ui.column(8,credits),
                                ui.column(1,      ui.input_action_link(button_uid_remove, f"❌")),
                                style = "margin:0px",
                                # proglang_footer     
                            ),
                        style= StyleService.style_course_box(),
                        hidden = (not show)
                    )


    def as_string(self):
        course_info = f"Course Info: {self.course_info}, Year: {self.year}, Block: {self.block}"
        return course_info   

    def __str__(self):
        return self.as_string()
    
