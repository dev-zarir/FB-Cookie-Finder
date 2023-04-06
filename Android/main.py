from kivymd.uix.behaviors import CommonElevationBehavior, BackgroundColorBehavior
from urllib.error import URLError as Urllib_Error_URLError
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.boxlayout import BoxLayout
from kivy.core.clipboard import Clipboard
from kivymd.uix.dialog import MDDialog
from kivy.lang.builder import Builder
from kivymd.uix.label import MDLabel
from kivy.base import EventLoop
from kivymd.toast import toast
from mechanize import Browser
from threading import Thread
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.core.window import Window
from requests import get
import webbrowser, re
import ssl

# Disable SSL Check for mechanize.Browser.open()
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Splash Color #003b6f

Window.keyboard_anim_args = {'d': 0.2, 't': 'in_out_expo'}
Window.softinput_mode = 'below_target'

class CustomToolBar(BoxLayout, BackgroundColorBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = '60dp'
        self.padding = '15dp'
        self.spacing = '0dp'
        self._title = ''
        self._left_action_items = []
        self._left_action_items_widget = []
        self.title_widget = MDLabel(text=self._title, font_style='H6', theme_text_color='Primary')
        self.add_widget(self.title_widget, index=2)
    
    def add_left_action_items(self):
        for widget in self._left_action_items_widget:
            self.remove_widget(widget)
        self._left_action_items_widget = []
        for icon, func in self._left_action_items:
            widget = MDIconButton(icon=icon, on_release=func, pos_hint={'center_y': 0.5})
            self.add_widget(widget, index=1)
            self._left_action_items_widget.append(widget)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.remove_widget(self.title_widget)
        self.title_widget.text = value
        self.add_widget(self.title_widget, index=2)
    
    @property
    def left_action_items(self):
        return self._left_action_items
    
    @left_action_items.setter
    def left_action_items(self, value):
        self._left_action_items = value
        self._left_action_items.reverse()
        self.add_left_action_items()

class CookieFinder(MDApp):
    def build(self):
        self.app_title = 'FB Cookie Finder'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Green'
        self.theme_cls.primary_hue = 'A700'
        return Builder.load_file('ui-design.kv')
    
    def on_start(self):
        self.root.ids.copyright_text.bind(on_ref_press = self.ref_link_callback)
        EventLoop.window.bind(on_keyboard=self.key_press_event)
        return super().on_start()

    def key_press_event(self, window, key, *args):
        if key == 27:
            if self.root.ids.screenmanager.current == 'resultscreen':
                self.resetState()
                return True
    
    def resetState(self):
        self.root.ids.cookie_input.text = self.root.ids.email_input.text = self.root.ids.pass_input.text = ''
        self.changeScreen('homescreen')
    
    def copyCookieThread(self):
        t=Thread(target=self.copyCookie)
        t.daemon=True
        t.start()

    def copyCookie(self):
        cookie = self.root.ids.cookie_input.text
        Clipboard.copy(cookie)
        Clock.schedule_once(lambda x: toast('Cookie Copied'))

    def ref_link_callback(self, instance, value):
        webbrowser.open(value)
    
    def open_fbactive(self):
        webbrowser.open('https://programsmart.xyz/services/fb-24h-active/')
    
    def changeScreen(self, screen_name):
        if screen_name == 'homescreen':
            self.root.ids.toolbar.title = self.app_title
            self.root.ids.toolbar.left_action_items = []
        elif screen_name == 'resultscreen':
            self.root.ids.toolbar.title = 'Your FB Cookie'
            self.root.ids.toolbar.left_action_items = [['arrow-left', lambda x: self.resetState()]]
        self.root.ids.screenmanager.current = screen_name
    
    def show_msg_dialog(self, title, text):
        self.err_dialog = MDDialog(
            title = title,
            text = str(text),
            elevation = 0,
            buttons = [
                MDFlatButton(
                    text = 'Ok',
                    text_color = '#00cc66',
                    on_release = lambda x: self.err_dialog.dismiss()
                )
            ],
        )
        self.err_dialog.open()

    def getCookieThread(self):
        t=Thread(target=self.getCookieFunc)
        t.daemon = True
        t.start()
    
    def getCookieFunc(self):
        def set_cookie(cookie):
            self.root.ids.cookie_input.text = cookie
        def disable_btn():
            self.root.ids.submit_btn.text = 'Working...'
            self.root.ids.submit_btn.disabled = True
        def reset_btn():
            self.root.ids.submit_btn.disabled = False
            self.root.ids.submit_btn.text = 'Get Cookie'
            
        email = self.root.ids.email_input.text
        password = self.root.ids.pass_input.text
        if email == '' or password == '':
            Clock.schedule_once(lambda x: self.show_msg_dialog('Error', 'The fields cannot be empty'))
            return
        Clock.schedule_once(lambda x: disable_btn())
        try:
            has_cookie = True
            cookie = get_cookie_from_email_pass(email, password)
        except Exception as err:
            has_cookie = False
            Clock.schedule_once(lambda x, err=err: self.show_msg_dialog('Error', err))
        Clock.schedule_once(lambda x: reset_btn())
        if has_cookie:
            Clock.schedule_once(lambda x, cookie=cookie: set_cookie(cookie))
            Clock.schedule_once(lambda x: self.changeScreen('resultscreen'))


def get_cookie_from_email_pass(email, password):
    br = Browser()
    br.set_handle_robots(False)
    try:
        br.open('https://mbasic.facebook.com')
    except Urllib_Error_URLError:
        raise Exception('Please check your internet connection and try again.')
    br._factory.is_html = True
    br.select_form(nr=0)
    br.form['email'] = email
    br.form['pass'] = password
    br.submit()
    br._factory.is_html = True
    cookie_dict = {}
    for item in br.cookiejar:
        cookie_dict[item.name] = item.value
    acc_id = get_profile_id(cookie_dict)
    if acc_id:
        cookie_string = ''
        for name, value in cookie_dict.items():
            cookie_string += f'{name}={value};'
        return cookie_string
    else:
        raise Exception('Could not get facebook cookie. Possible reasons can be:\n1. Invalid Email or Phone number\n2. Invalid Password\n3. Account is disabled, locked or suspended\n4. Poor Internet Connection\n5. Could not login due to 2FA Auth\nTip: Login to your local browser and if it works then come here and login with the same credentials.')


def get_profile_id(cookie_dict: str):
    try:
        resp = get('https://mbasic.facebook.com/me',
                   cookies=cookie_dict)
        html = resp.text
        match = re.findall(r'profile_id=\d+', html)
        if not match:
            match = re.findall(r'owner_id=\d+', html)
        if not match:
            match = re.findall(r'confirm/\?bid=\d+', html)
        if not match:
            match = re.findall(r'subscribe.php\?id=\d+', html)
        if not match:
            match = re.findall(r'subject_id=\d+', html)
        if not match:
            match = re.findall(r'poke_target=\d+', html)
        if not match:
            return None
        fb_id = match[0].split('=')[1]
        return fb_id
    except:
        return None
    

app = CookieFinder()
app.run()

