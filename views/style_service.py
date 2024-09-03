from shiny import  ui
import pandas as pd
from faicons import icon_svg as icon

class StyleService:

    def __init__(self):
        pass

    def style_course_box():
        return "padding: 10px 22px 10px 10px;;  border: 1px solid black; margin: 2px; position:relative;"
    
    def style_course_box_not_selected():
        return "padding: 10px; border: 1px dashed grey; margin: 2px;"
    
    def style_section_box():
        return "padding: 10px; border: 1px solid grey;"
    
    def style_theme_box():
        return "position: absolute; right: 0px;height: 100%; top: 0px;width: 16px;"
    
    def style_theme_single_size(how_many_themes):
        return f"height: {100/how_many_themes}%;width: 100%;"

    def style_theme_single(theme):
        return f"padding-right:2px; text-align:center; color:{StyleService.theme_infos()[theme]['textcolor']};background-color:{StyleService.theme_infos()[theme]['color']};"


    def theme_infos():
        return {    "code":{"color":"aqua","textcolor":"black", "name":"👾"},
                    "code-r":{"color":"aqua","textcolor":"black", "name":"🧩"},
                    "code-python":{"color":"aqua","textcolor":"black", "name":"🐍"},
                    "code-sql":{"color":"aqua","textcolor":"black", "name":"🗄"},
                    "context":{"color":"chartreuse","textcolor":"black", "name":"🩺"},
                    "data":{"color":"darkviolet","textcolor":"white", "name":"🔎"},
                    "quant":{"color":"fuchsia","textcolor":"black", "name":"🔢"},
                    "qual":{"color":"black","textcolor":"white", "name":"💬"},
                    "scholar":{"color":"#e6308a","textcolor":"black", "name":"📚"},
                    "stats":{"color":"yellow","textcolor":"black", "name":"📊"},
                    "ethics":{"color":"#5ba300","textcolor":"black", "name":"😇"},
                    "leader":{"color":"crimson","textcolor":"black", "name":"🌟"},
                    "?":{"color":"#aa8f00","textcolor":"black", "name":"❓"},
                    "design":{"color":"limegreen","textcolor":"white", "name":"🎨"},}


    def style_highlighted_link():
        return "background-color: #ffff00; margin: 10px;"
   
    def single_theme(theme_name, how_many_vertical, text=None):
        text = text if text  else f"{StyleService.theme_infos()[theme_name]['name']}"
        more_info_card = ui.div(theme_name)
        return ui.popover( ui.div(text, 
                      style=StyleService.style_theme_single(theme_name)+StyleService.style_theme_single_size(how_many_vertical)),
                      more_info_card)
    
    def box_of_themes(themes):
        return ui.div([StyleService.single_theme(theme, len(themes)) 
                       for theme in themes], 
                      style= StyleService.style_theme_box()),

    def name_shorter(long_name):
        shorter_name =  long_name.replace("health and social care", "H&SC").replace("Health and Social Care", "H&SC")
        shorter_name = shorter_name.replace("Introduction", "Intro")
        return shorter_name
    
    def info_card_for_course(course_info):
        # proglang_footer=[]
        # if not pd.isna(course_info.prog_lang):
        #     if course_info.prog_lang == "Python":
        #         # footer_items.append("Programming language: ")
        #         proglang_footer.append(icon("python"))
        #         proglang = f"Programming language: Python"
        #     if course_info.prog_lang == "R":
        #         # footer_items.append("Programming language: ")
        #         proglang_footer.append(icon("r"))
        #         proglang = f"Programming language: R"
        #     if course_info.prog_lang == "R and SQL":
        #         # footer_items.append("Programming language: ")
        #         proglang_footer.append(icon("python"))
        #         proglang_footer.append("+ SQL")
        #         proglang = f"Programming language: Python and SQL"
        # else:
        #     proglang = "This is not a programming course"

        
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
        more_info_card = (ui.div(
                                ui.row(ui.div(
                                    {"style": "font-weight: bold"},
                                    ui.p("Course Information"),
                                ),),
                                # ui.row("‣ ","TODO: what other info about the course would we like to have here?"),
                                # ui.row("‣ Themes: ",", ".join(course_info.themes) if len(course_info.themes)>0 else "none"),
                                # ui.row("‣ Programming languages: ", ", ".join(course_info.prog_lang) if len(course_info.prog_lang)>0 else "none"),
                                # ui.row("‣ ",isprereq),
                                # ui.row("‣ ",credits),
                                # ui.row("‣ ",proglang),
                                ui.row(ui.tags.a("View this course on DRPS", href=course_info.link, target="_blank"))
                            ))
        return more_info_card
    
