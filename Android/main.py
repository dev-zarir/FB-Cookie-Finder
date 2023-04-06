from kivy.lang.builder import Builder
from kivymd.app import MDApp

class CookieFinder(MDApp):
    def build(self):
        self.app_title = 'FB Cookie Finder'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Green'
        self.theme_cls.primary_hue = 'A700'
        return Builder.load_file('ui-design.kv')

app = CookieFinder()
app.run()

