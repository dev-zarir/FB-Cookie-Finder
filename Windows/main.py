import io
import sys
sys.stderr = sys.stdout = io.StringIO()
import os
import re
import pyperclip
import webbrowser
from time import sleep
from requests import get
from customtkinter import *
from threading import Thread
from mechanize import Browser
from tkinter import messagebox

def close_splash():
    if getattr(sys, 'frozen', False):
        import pyi_splash
        pyi_splash.close()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


set_appearance_mode('dark')
set_default_color_theme('green')

app = CTk()
app.title('FB Cookie Finder')
app.geometry('400x400')
app.iconbitmap(resource_path('icon.ico'))
app.resizable(False, False)
app.bind_all("<Button-1>", lambda event: event.widget.focus_set())

# Widgets
heading_label = CTkLabel(app, text="FB Cookie Finder", font=('', 24))
email_entry = CTkEntry(
    app, placeholder_text='Email address or Phone Number', height=38, font=('', 18))
pass_entry = CTkEntry(app, placeholder_text='Password',
                      show='*', height=38, font=('', 18))
submit_btn = CTkButton(app, text='Get Cookie', height=34, text_color='#f2f2f2', font=(
    '', 16, 'bold'), fg_color="#0c6", hover_color='#00b359', text_color_disabled="#e6e6e6", command=lambda: run_get_cookie_thread())
cookie_label = CTkLabel(app, text="Your FB Cookie", font=('', 18))
cookie_textbox = CTkTextbox(app, font=('', 16), height=150)
cookie_copy_btn = CTkButton(app, text='Copy Cookie', text_color='#f2f2f2',
                            fg_color='#0c6', hover_color="#00b359", font=('', 16, 'bold'), height=34, text_color_disabled="#e6e6e6", command=lambda: copy_cookie_func())
reset_btn = CTkButton(app, text='Reset', text_color='#fff',
                      fg_color='#0d6efd', hover_color='#0b5ed7', command=lambda: reset_state())
copyright_text = CTkLabel(app, text='Made by ZARIR on behalf of Programs Mart')
copyright_link1 = CTkLabel(
    app, text='ZARIR', text_color='#0c6', cursor='hand2')
copyright_link2 = CTkLabel(app, text='Programs Mart',
                           text_color='#0c6', cursor='hand2')

# Placing
heading_label.place(relx=0.5, rely=0.1, anchor="center")
copyright_text.place(relx=0.5, rely=1, anchor='s')
copyright_link1.place(relx=0.368, rely=1, anchor='s')
copyright_link2.place(relx=0.708, rely=1, anchor='s')


def place_form_widget():
    email_entry.place(relx=0.5, rely=0.28, relwidth=0.9, anchor='center')
    pass_entry.place(relx=0.5, rely=0.4, relwidth=0.9, anchor='center')
    submit_btn.place(relx=0.5, rely=0.52, relwidth=0.9, anchor='center')


def place_cookie_widget():
    cookie_label.place(relx=0.5, rely=0.2, relwidth=0.9, anchor='center')
    cookie_textbox.place(relx=0.5, rely=0.45, relwidth=0.9, anchor='center')
    cookie_copy_btn.place(relx=0.5, rely=0.7, relwidth=0.9, anchor='center')
    reset_btn.place(relx=0.5, rely=0.805, relwidth=0.9, anchor='center')


def unplace_cookie_widget():
    cookie_label.place_forget()
    cookie_textbox.place_forget()
    cookie_copy_btn.place_forget()
    reset_btn.place_forget()


def unplace_form_widget():
    email_entry.place_forget()
    pass_entry.place_forget()
    submit_btn.place_forget()


place_form_widget()

# Binding
copyright_link1.bind(
    '<Button-1>', lambda x: webbrowser.open('https://facebook.com/100075924800901'))
copyright_link2.bind(
    '<Button-1>', lambda x: webbrowser.open('https://programsmart.xyz/'))

# Functions


def reset_state():
    email_entry.delete(0, 'end')
    pass_entry.delete(0, 'end')
    cookie_textbox.configure(state='normal')
    cookie_textbox.delete('1.0', 'end')
    cookie_textbox.configure(state='disabled')
    unplace_cookie_widget()
    place_form_widget()
    app.focus_force()


def copy_cookie_func():
    cookie_textbox.configure(state='normal')
    sanitized_cookie = cookie_textbox.get('1.0', 'end').replace('\n', '')
    cookie_textbox.configure(state='disabled')
    pyperclip.copy(sanitized_cookie)
    cookie_copy_btn.configure(text='Copied', state="disabled")

    def copy_btn_reset_func():
        sleep(2)
        cookie_copy_btn.configure(text='Copy Cookie', state="normal")
    t = Thread(target=copy_btn_reset_func)
    t.daemon = True
    t.start()


def run_get_cookie_thread():
    t = Thread(target=get_cookie)
    t.daemon = True
    t.start()


def get_cookie():
    email = email_entry.get()
    password = pass_entry.get()
    submit_btn.configure(state='disabled', text="Working...")

    try:
        has_cookie = True
        cookie = get_cookie_from_email_pass(email, password)
    except Exception as err:
        has_cookie = False
        messagebox.showerror('Error: Could not get cookie', err)

    submit_btn.configure(state='normal', text="Get Cookie")
    if has_cookie:
        cookie_textbox.configure(state='normal')
        cookie_textbox.insert('1.0', cookie)
        cookie_textbox.configure(state='disabled')
        unplace_form_widget()
        place_cookie_widget()


def get_cookie_from_email_pass(email, password):
    br = Browser()
    br.set_handle_robots(False)
    try:
        br.open('https://mbasic.facebook.com')
    except:
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
        raise Exception('Could not get facebook cookie. Possible reasons can be:\n\t1. Invalid Email or Phone number\n\t2. Invalid Password\n\t3. Account is disabled, locked or suspended\n\t4. Poor Internet Connection\n\t5. Could not login due to 2FA Auth\nTip: Login to your local browser and if it works then come here and login with the same credentials.')


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

close_splash()
app.mainloop()
