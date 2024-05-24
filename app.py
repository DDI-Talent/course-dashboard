from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.input_slider("val", "Slider label", min=0, max=100, value=50),
    ui.output_text_verbatim("slider_val")
)

def server(input, output, session):
    @render.text
    def slider_val():
        return f"Slider value: {input.val()}"

app = App(app_ui, server)