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

    def as_card_nothing_selected( year, block, show = False):
            button_label = "Nothing selected yet"
            
            return ui.div( 
                                ui.div(  button_label),
                                ui.row( 
                                          ui.input_action_link(f"buttonfilter_{year}_{block}", f"🔎 filter courses for this block (TODO)"),
                                    style = "margin:0px"
                                ),
                            style= StyleService.style_course_box_not_selected(),
                                                    hidden = (not show)

                        )




    def as_card_selected(self, show = False):
        button_label = StyleService.name_shorter(self.course_info.name) #+ " " + self.course_info.id
        buttons = []
        button_uid_remove = self.to_selected_button_id( "buttonremove_")
        
        credits = f"Credits: {self.course_info.credits}"
        more_info_card = StyleService.info_card_for_course(self.course_info)

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
    
