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
        return "display:flex;"
   
    def style_metainfo_box():
        return "position: absolute; right: 0px; height: 100%; top: 0px ; display:block;"
    
     
    def style_theme_single_size(how_many_themes):
        return f"width: 24px;height: 24px; text-align:center;"
    
         
    def style_theme_single_size_with_count(how_many_themes):
        return f"width: 24px;height: 48px; text-align:center;"

    def style_theme_single(theme):
        return f"padding:1px; text-align:center; vertical-align: middle; color:{StyleService.theme_infos()[theme]['textcolor']};background-color:{StyleService.theme_infos()[theme]['color']};"


    def theme_infos():
        return {
            "all": {"name":"All", "color": "#1E90FF", "textcolor": "white", "emoji": "🍰", "description":"TODO"}, 
            # "code": {"name":"Coding", "color": "#1E90FF", "textcolor": "white", "emoji": "👾", "description":"TODO"},  # Dodger Blue
            "code-r":{ "name":"Coding in R", "color": "#1E90FF", "textcolor": "white", "emoji": "🧩", "description":"TODO"},  # Dodger Blue
            "code-python": { "name":"Coding in Python", "color": "#1E90FF", "textcolor": "white", "emoji": "🐍", "description":"TODO"},  # Dodger Blue
            "code-sql": { "name":"Coding in SQL", "color": "#1E90FF", "textcolor": "white", "emoji": "🗄", "description":"TODO"},  # Dodger Blue
            "context": { "name":"Health and Social Care Context", "color": "#00ff00", "textcolor": "black", "emoji": "🩺", "description":"TODO"},  # Lime
            "data": { "name":"Understanding Data", "color": "#00ffff", "textcolor": "black", "emoji": "🔎", "description":"TODO"},  # Aqua
            "quant": { "name":"Quantitative Methods", "color": "#ff1493", "textcolor": "black", "emoji": "🔢", "description":"TODO"},  # Pink
            "qual": { "name":"Qualitative Methods", "color": "#8B0000", "textcolor": "white", "emoji": "💬", "description":"TODO"},  # Dark Red
            "scholar":{  "name":"Scholarship and Research", "color": "#FFD700", "textcolor": "black", "emoji": "📚", "description":"TODO"},  # Gold 
            "stats": { "name":"Statitstics", "color": "#4682B4", "textcolor": "white", "emoji": "📊", "description":"TODO"},  # Steel Blue
            "ethics":{  "name":"Ethics and Social Issues", "color": "#111111", "textcolor": "white", "emoji": "😇", "description":"TODO"},  # black
            "leader":{  "name":"Leadership Skills", "color": "#8a2be2", "textcolor": "white", "emoji": "🌟", "description":"TODO"},  # violet
            # "?":{  "name":"Unknown", "color": "#B8860B", "textcolor": "black", "emoji": "❓", "description":"TODO"},  # Dark Goldenrod
            "design":{  "name":"Design and Presentation", "color": "#32CD32", "textcolor": "black", "emoji": "🎨", "description":"TODO"}  # Lime Green
        }


    def style_highlighted_link():
        return "background-color: #ffff00; padding: 0px 10px;"
    
    def style_meta_box_half_bottom():
        return "right: 0px; bottom: 0px; position:absolute;"
   
    def single_theme(theme_name, how_many_vertical, text=None):
        if text == None:
            extra_style = StyleService.style_theme_single_size(how_many_vertical)
        else:
            extra_style = StyleService.style_theme_single_size_with_count(how_many_vertical)

        text = text if text  else f"{StyleService.theme_infos()[theme_name]['emoji']}"
        return  ui.div(text, 
                      style=StyleService.style_theme_single(theme_name)+extra_style),
    
    def box_of_course_metainfo(course_info, no_popover = False):
        more_info_card = StyleService.info_card_for_course(course_info) if not no_popover else None
        return ui.popover( 
            ui.div(
                ui.div( 
                    ui.div(
                        icon("circle-info"),
                        # ui.div(f"{course_info.credits} cred"),
                          style="right: 0px; top: 0px; position: absolute;"),
                     ),
                StyleService.box_of_themes(course_info.themes, StyleService.style_meta_box_half_bottom()),
                style= StyleService.style_metainfo_box()
            ), more_info_card )
        

    def one_theme(theme_name, count):
        return ui.div( 
            f"{count} : {StyleService.theme_infos()[theme_name]['emoji']} {StyleService.theme_infos()[theme_name]['name']}",
            # f"{StyleService.theme_infos()[theme_name]['description']}",
            style=f"background-color:{StyleService.theme_infos()[theme_name]['color']}; color:{StyleService.theme_infos()[theme_name]['textcolor']};",
        )
        
    def theme_balance(theme_counts_dict):
        return ui.div( [
            StyleService.one_theme(theme_name, theme_counts_dict[theme_name])
            for theme_name in theme_counts_dict],
        )

    def box_of_themes(themes, extra_styles = ""):
        return ui.div([StyleService.single_theme(theme, len(themes)) 
                       for theme in themes], 
                      style= StyleService.style_theme_box()+extra_styles)


    def name_shorter(long_name):
        shorter_name =  long_name.replace("health and social care", "H&SC").replace("Health and Social Care", "H&SC")
        shorter_name = shorter_name.replace("Introduction", "Intro")
        return shorter_name
    
    def course_as_card(course_info, show = True, buttons = [], dissertation = False):
        name_label = StyleService.name_shorter(course_info.name) #+ " " + self.course_info.id
        
        # credits = f"{self.course_info.credits} cred."
        return ui.div( 
                        ui.div(  name_label,  ),
                        ui.div( 
                            ui.div(  *[button for button in buttons]   ),
                            style = "margin:0px; padding:0px",
                            hidden = (dissertation)
                        ),
                        StyleService.box_of_course_metainfo(course_info),
                        # StyleService.box_of_themes(self.course_info.themes),
                  
                         style= StyleService.style_course_box(),
                         hidden = (not show)
        ).add_class("card-header")



    def info_card_for_course(course_info):
        more_info_card = (ui.div(
                                ui.row(ui.div(
                                    {"style": "font-weight: bold"},
                                    ui.p("Course Information"),
                                ),),
                                ui.div(ui.tags.b("name: "), f"{ course_info.name}"),
                                ui.div(ui.tags.b("id: "), course_info.id),
                                ui.div(ui.tags.b("Credits: "), course_info.credits),
                                ui.div(ui.tags.b("degree_ids: "), course_info.degree_ids),
                                ui.div(ui.tags.b("Notes: "), course_info.notes),
                                ui.div(ui.tags.b("Years: "), course_info.years),
                                ui.div(ui.tags.b("Has prerequisites: "), course_info.has_pre_req_id),
                                ui.div(ui.tags.b("Blocks: "), course_info.blocks),
                                ui.div(ui.tags.b("Themes: "), ", ".join(course_info.themes)),
                                ui.div(ui.tags.b("prog lang: "), course_info.prog_lang),
                                ui.div( StyleService.box_of_themes(course_info.themes, StyleService.style_meta_box_half_bottom())),
                                # ui.row("‣ ","TODO: what other info about the course would we like to have here?"),
                                # ui.row("‣ Themes: ",", ".join(course_info.themes) if len(course_info.themes)>0 else "none"),
                                # ui.row("‣ Programming languages: ", ", ".join(course_info.prog_lang) if len(course_info.prog_lang)>0 else "none"),
                                # ui.row("‣ ",isprereq),
                                # ui.row("‣ ",credits),
                                # ui.row("‣ ",proglang),
                                ui.row(ui.tags.a("View this course on DRPS", href=course_info.link, target="_blank"))
                            ))
        return more_info_card
    
