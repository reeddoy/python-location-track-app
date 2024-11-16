from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from plyer import gps
import requests
import threading
import time
import os
import uuid
import platform
from datetime import datetime
import random
from android.permissions import request_permissions, Permission

kivy.require('2.0.0')

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=[20, 200, 20, 200], spacing=10)

        self.username_input = TextInput(hint_text='Username')
        self.password_input = TextInput(hint_text='Password', password=True)
        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)

        self.login_button = Button(text='Login', on_press=self.login)
        self.layout.add_widget(self.login_button)

        self.message_label = Label()
        self.layout.add_widget(self.message_label)

        self.add_widget(self.layout)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        device_id = self.get_device_id()

        response = requests.post('http://127.0.0.1:8000/login/', json={
            'username': username,
            'password': password,
            'device_id': device_id
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.message_label.text = 'Login successful!'
            self.manager.current = 'dashboard'
            self.manager.get_screen('dashboard').set_username(username, self.token)
        else:
            self.message_label.text = 'Login failed!'

    def get_device_id(self):
        if platform.system() == 'Windows':
            file_path = os.path.join(os.path.expanduser("~"), 'Documents', 'device_id.txt')
        else:
            file_path = os.path.join(self.user_data_dir, 'device_id.txt')

        if not os.path.exists(file_path):
            device_id = str(uuid.uuid4())
            with open(file_path, 'w') as f:
                f.write(device_id)
            return device_id
        else:
            with open(file_path, 'r') as f:
                return f.read().strip()

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=[20, 200, 20, 200], spacing=10)
        self.welcome_label = Label(font_size='20sp')
        self.layout.add_widget(self.welcome_label)

        self.response_label = Label(font_size='16sp', color=(0, 1, 0, 1))
        self.layout.add_widget(self.response_label)

        self.countdown_label = Label(font_size='16sp', color=(0, 0, 1, 1))
        self.layout.add_widget(self.countdown_label)

        self.start_button = Button(text='Start Tracking', on_press=self.start_location_tracking)
        self.layout.add_widget(self.start_button)

        self.close_button = Button(text='Close', on_press=self.close_app)
        self.layout.add_widget(self.close_button)

        self.add_widget(self.layout)

        self.token = None
        self.is_running = False
        self.last_update_time = 0

    def set_username(self, username, token):
        self.welcome_label.text = f'Welcome, {username}!'
        self.token = token

    def start_location_tracking(self, instance):
        if self.is_running:
            return

        # Request necessary permissions for GPS, file access, and internet
        request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION, 
                             Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE,
                             Permission.INTERNET])

        self.is_running = True
        self.start_button.disabled = True

        if platform == 'android':
            gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
            gps.start(minTime=10000, minDistance=0)  # 10 seconds update interval, 0 meters
        else:
            threading.Thread(target=self.track_location, daemon=True).start()

    def on_gps_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat is not None and lon is not None:
            self.send_location(lat, lon)

    def on_gps_status(self, stype, status):
        if stype == 'provider-enabled' and status == 'gps':
            self.response_label.text = 'GPS enabled and tracking location...'
        elif stype == 'provider-disabled' and status == 'gps':
            self.response_label.text = 'GPS disabled. Please enable GPS.'

    def track_location(self):
        while self.is_running:
            current_time = time.time()
            if current_time - self.last_update_time >= 10:
                lat = random.uniform(-90, 90)
                lon = random.uniform(-180, 180)
                self.send_location(lat, lon)
                self.last_update_time = current_time

            self.countdown_label.text = f"Next update in: {10 - int(current_time - self.last_update_time)} seconds"
            time.sleep(1)

    def send_location(self, lat, lon):
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.post('http://127.0.0.1:8000/check_location/', json={
            'latitude': lat,
            'longitude': lon
        }, headers=headers)

        if response.status_code == 200:
            self.response_label.color = (0, 1, 0, 1)
            self.response_label.text = f"Location verified at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        else:
            self.response_label.color = (1, 0, 0, 1)
            self.response_label.text = f"Failed to verify location at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."

    def close_app(self, instance):
        self.is_running = False
        self.start_button.disabled = False
        self.response_label.text = ''
        self.countdown_label.text = ''

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    MyApp().run()
