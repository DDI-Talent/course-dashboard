import pandas as pd
import math 
from shiny import ui, reactive
# import fontawesome as fa 
from faicons import icon_svg as icon
from views.style_service import StyleService



class Persona:

    def __init__(self, row):
        self.name = row['name']
        self.emoji = row['emoji']
        self.degree_id = row['degree_id']
        self.description = row['description']
        self.course_ids_plus_separated = row['course_ids_plus_separated']
    
    
    def sharable_link(self, session):
            
        site_protocol = session.input[".clientdata_url_protocol"]()
        site_port = session.input[".clientdata_url_port"]()
        site_url = session.input[".clientdata_url_hostname"]()
        pathname = session.input[".clientdata_url_pathname"]()

        link_to_share = f"{site_protocol}//{site_url}"
        if len(str(site_port)) > 1: # eg. ignore just "/"
            link_to_share += f":{site_port}"
        if len(pathname) > 1: # eg. ignore just "/"
            link_to_share += f"{pathname}"
        link_to_share += f"?degree_id={self.degree_id}&courses={self.course_ids_plus_separated}"

        more_info_card = ui.div(
                                ui.h3(f"{self.name}"),
                                ui.p(f"{self.description}")
                            )

        return ui.div(ui.a(f"{self.emoji} {self.name} ",  href=link_to_share), ui.popover( icon("circle-info"), more_info_card))