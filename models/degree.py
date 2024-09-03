import pandas as pd
import math 
from shiny import ui, reactive
# import fontawesome as fa 
from faicons import icon_svg as icon
from views.style_service import StyleService



class Degree:

    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']   
        self.years = int(row['years'])   
        self.description = row['description']            
        self.link = row['link']            