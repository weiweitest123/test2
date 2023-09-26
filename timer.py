from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from plyer import notification
import socket
import threading
import time
Window.size = (350, 550)


class MessageReceiver(threading.Thread):
    def __init__(self, app):
        super(MessageReceiver, self).__init__()
        self.app = app
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 8090))
        self.server_socket.listen(1)

    def run(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                message = client_socket.recv(1024).decode()
                if message == "EMERGENCY":
                    self.app.start_ring()
                    self.app.show.notification()
                client_socket.close()
            except Exception as e:
                pass


class RingingApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.start_button = Button(text='Start Ringing', on_release=self.start_ringing)
        self.stop_button = Button(text='Stop Ringing', on_release=self.stop_ringing)
        self.layout.add_widget(self.start_button)
        self.layout.add_widget(self.stop_button)
        self.ringing = False
        self.message_receiver = MessageReceiver(self)
        self.message_receiver.start()
        self.sound = SoundLoader.load('alert.mp3')  # Replace with your ringtone file
        self.volume_increase_rate = 0.1
        self.max_volume = 1.3
        return self.layout


    def start_ringing(self, instance):
        self.ringing = True
        self.sound.loop = True
        self.sound.volume = 0.0
        self.sound.play()
        self.increase_volume()

    def stop_ringing(self, instance):
        self.ringing = False
        self.sound.stop()

    def start_ring(self):
        if self.ringing:
            self.stop_ringing(None)
        self.start_ringing(None)

    def on_stop(self):
        self.message_receiver.running = False
        self.message_receiver.server_socket.close()
        super(RingingApp, self).on_stop()


    def show_notification(self):
        notification_title = 'Emergency Alert'
        notification_text = 'Emergency message received!'
        notification.notify(
            title=notification_title,
            message=notification_text,
            app_name='RingingApp'
        )


    def increase_volume(self):
        while self.ringing and self.sound.volume < self.max_volume:
            self.sound.volume += self.volume_increase_rate
            time.sleep(0.5)
        if self.sound.volume >= self.max_volume:
            self.sound.volume = self.max_volume


if __name__ == '__main__':
    RingingApp().run()
