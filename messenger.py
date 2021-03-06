# TCP Chat Client
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
repo = "https://github.com/Nytra/messenger"
# Created on 16-03-2016
#

import socket, threading, random, winsound, os, datetime, time, string
from tkinter import *

class App(Frame):
    version = "1.00"
    def __init__(self, master):
        root.withdraw()
        super(App, self).__init__(master)
        servers = self.get_servers()
        if len(servers) >= 1:
            print("Servers you have previously connected to:")
            printed_ip = []
            for ip in servers:
                if ip not in printed_ip:
                    print("\t- " + ip, end = "")
                    printed_ip.append(ip)
            print()
        self.server = ""
        print("Enter an IP address: ", end = "")
        while not self.server:
            self.server = input().strip()
            if not self.server:
                print("You must enter an IP address: ", end = "")
                self.server = ""
        if ":" in self.server:
            parts = self.server.split(":")
            self.server = parts[0]
            if self.server:
                print("Server: {}".format(self.server))
            try:
                self.port = int(parts[1])
                print("Port: {}".format(self.port))
            except ValueError:
                self.port = ""
                print("Enter a port number: ", end = "")
        else:
            self.port = ""
            print("Server: {}".format(self.server))
            print("Enter a port number: ", end = "")
        while not self.port:
            try:
                self.port = int(input())
            except ValueError:
                print("Enter integers only: ", end = "")
                pass
        self.name = ""
        print("Enter your name: ", end = "")
        while not self.name:
            self.name = input().strip()
            if " " in self.name:
                print("Your name cannot contain spaces: ", end = "")
                self.name = ""
                continue
        if not self.name:
            self.name = "Anonymous" + str(random.randrange(1, 10000))
        self.grid()
        self.sound = True
        self.data_buff = 4096
        self.disconnected = False
        self.msg_index = 0
        self.encryption_key = 7
        self.sent_messages = []
        if not self.connect():
            #print("Unable to connect to", self.server, "on port", str(self.port), "\nClosing program...")
            quit()
        root.deiconify()
        if self.server not in self.get_servers():
            with open("servers.txt", "a") as f:
                f.write(self.server + ":" + str(self.port) + "\n")
        nick_msg = "/nick {}".format(self.name)
        nick_msg = self.encrypt(nick_msg, self.encryption_key)
        s.send(nick_msg.encode())
        self.create_widgets()
        t1 = threading.Thread(target = self.get_messages)
        t1.start()

    def get_servers(self):
            with open("servers.txt", "r") as f:
                servers = f.readlines()
            return servers

    def __str__(self):
        try:
            rep = "Chat Instance\nServer: " + self.server + "\nPort: " + str(self.port) + "\nVersion: " + str(App.version)
        except:
            rep = "Chat Instance\nServer: None\nPort: None\nVersion: " + str(App.version)
        return rep

    def create_widgets(self):
        self.nick_lbl = Label(self, text = "Nickname: " + self.name, bg = "black", fg = "white")
        #self.nick_lbl.grid(row = 0, column = 1, sticky = N)
        #self.message_lbl = Label(self, text = "Message: ", bg = "black", fg = "white")
        #self.message_lbl.grid(row = 1, column = 0, sticky = W)
        self.message_output = Text(self, width = 100, height = 40, wrap = WORD)
        self.message_output.grid(row = 0, column = 0, sticky = W)
        self.message_input = Entry(self, width = 50)
        self.message_input.grid(row = 1, column = 0, sticky = W+S+E+N)
        self.submit_bttn = Button(self, text = "Send", command = self.submit_message, bg = "white", fg = "black")
        self.submit_bttn.grid(row = 1, column = 0, sticky = E)
        self.message_output.config(state=DISABLED)
        root.bind('<Return>', self.enter)
        self.mute_button = Button(self, text = "\nNotifications\n", command = self.toggle_sound, bg = "darkgreen", fg = "white")
        self.mute_button.grid(row = 0, column = 1, sticky = N+E+W)
        self.disconnect_bttn = Button(self, text = "\nDisconnect\n", command = self.disconnect, bg = "darkgreen", fg = "white")
        self.disconnect_bttn.grid(row = 0, column = 2, sticky = N+E+W)
        root.bind('<Up>', self.arrow_up)
        root.bind('<Down>', self.arrow_down)

    def arrow_down(self, event):
        try:
            self.msg_index += 1
            msg = self.sent_messages[self.msg_index]
            self.message_input.delete(0, END)
            self.message_input.insert(0, msg)
        except:
            self.msg_index -= 1
            return

    def arrow_up(self, event):
        try:
            self.msg_index -= 1
            if len(self.sent_messages) == 1:
                self.msg_index = 0
            if self.msg_index < 0:
                self.msg_index += 1
                return
            msg = self.sent_messages[self.msg_index]
            self.message_input.delete(0, END)
            self.message_input.insert(0, msg)
        except:
            return
        
    def enter(self, event):
        self.submit_message()

    def change_window_colour(self):
        global song_done
        colours = ["red", "green", "blue", "pink", "black", "white", "purple", "brown", "yellow"]
        while not song_done:
            rand_colour = random.choice(colours)
            root.configure(background = rand_colour)
            app.configure(background = rand_colour)
            time.sleep(0.1)
        app.configure(background = default_bg_colour)
        root.configure(background = default_bg_colour)

    def party(self):
        global song_done
        song_done = False
        t1 = threading.Thread(target=self.song)
        t1.start()
        for i in range(200):
            t2 = threading.Thread(target = self.change_window_colour)
            t2.start()

    def song(self):
        global song_done
        for i in range(200):
            pitch = random.randrange(50, 1000)
            duration = random.randrange(100, 200)
            winsound.Beep(pitch, duration)
        song_done = True

    def toggle_sound(self):
        if self.sound == True:
            #self.mute_button["text"] = "\nEnable Sound\n"
            self.mute_button["bg"] = "red"
            #self.mute_button["fg"] = "white"
            self.sound = False
        else:
            #self.mute_button["text"] = "\nDisable Sound\n"
            self.mute_button["bg"] = "darkgreen"
            #self.mute_button["fg"] = "white"
            self.sound = True

    def submit_message(self):
        if self.disconnected:
            return
        message = self.message_input.get().strip()
        if not message:
            self.message_input.delete(0, END)
            return
        #message = self.name + "> " + message
        if len(self.sent_messages) > 0:
            if message not in self.sent_messages:
                self.sent_messages.append(message)
            self.msg_index = len(self.sent_messages)
        else:
            self.sent_messages.append(message)
        message = self.encrypt(message, self.encryption_key)
        data = message.encode()
        s.send(data)
        self.message_input.delete(0, END)

    def insert_message(self, message):
        global log
        log = self.message_output.get("1.0", END).strip()
        if not log:
            log = message.strip()
        else:
            log = log + "\n" + message
        self.message_output.config(state=NORMAL)
        self.message_output.delete("1.0", END)
        self.message_output.insert("1.0", log)
        self.message_output.config(state=DISABLED)
        self.message_output.yview("moveto", 1)

    def server_command(self, message):
        parts = message.split("%^")
        if parts[0] == "$%server":
            if parts[1] == "mod":
                if parts[2] == "widget":
                    if parts[3] == "nick":
                        if parts[4] == "label":
                            if parts[5] == "text":
                                try:
                                    temp = self.nick_lbl["text"]
                                    self.nick_lbl["text"] = "Nickname: " + " ".join(x for x in parts[6:])
                                except:
                                    temp = self.nick_lbl["text"]
                                    self.nick_lbl["text"] = temp
            elif parts[1] == "do":
                if parts[2] == "party":
                    self.party()
                elif parts[2] == "clear":
                    self.clear_message_output()
                elif parts[2] == "disconnect":
                    self.disconnect()
                elif parts[2] == "beep":
                    if self.sound:
                        tbeep = threading.Thread(target = winsound.Beep, args = (600, 100))
                        tbeep.start()

    def clear_message_output(self):
        self.message_output.config(state=NORMAL)
        self.message_output.delete("1.0", END)
        self.message_output.config(state=DISABLED)
        self.message_output.yview("moveto", 1)
        #log = ""

    def encrypt(self, message, key):
        alphabet = ['x', '$', 'W', 't', 'D', '|', 'd', " ", 'E', 'N', '`', 'n', 'X', 'h', 'V', 'A',
             'Y', '5', 'a', '¦', '2', 'J', 'C', 'b', 'k', 'H', 'I', 'c', 'f', 'K', '1', '9', 'u', ':', '3',
              '#', '%', 'P', 'i', '^', '4', 'O', '(', '[', 'R', '+', 'T', 'o', '@', '&', 'l', 'M', '>', '8',
               '"', 'Q', '<', '=', '*', '7', 'z', 'v', 'p', 's', 'B', '}', 'G', 'y', ')', '?', '0', '~', '/',
                "'", 'j', '6', '-', '_', '¬', '£', ',', 'U', 'F', 'Z', 'S', 'g', 'w', 'L', 'e', 'r', 'q', ';',
                 '.', '\\', '!', 'm', ']', '{', "\n"]
        encrypted = ""
        for char in message:
            index = alphabet.index(char)
            for i in range(key):
                index += 1
                if index > len(alphabet) - 1:
                    index = 0
            encrypted += alphabet[index]
        return encrypted

    def decrypt(self, message, key):
        alphabet = ['x', '$', 'W', 't', 'D', '|', 'd', " ", 'E', 'N', '`', 'n', 'X', 'h', 'V', 'A',
             'Y', '5', 'a', '¦', '2', 'J', 'C', 'b', 'k', 'H', 'I', 'c', 'f', 'K', '1', '9', 'u', ':', '3',
              '#', '%', 'P', 'i', '^', '4', 'O', '(', '[', 'R', '+', 'T', 'o', '@', '&', 'l', 'M', '>', '8',
               '"', 'Q', '<', '=', '*', '7', 'z', 'v', 'p', 's', 'B', '}', 'G', 'y', ')', '?', '0', '~', '/',
                "'", 'j', '6', '-', '_', '¬', '£', ',', 'U', 'F', 'Z', 'S', 'g', 'w', 'L', 'e', 'r', 'q', ';',
                 '.', '\\', '!', 'm', ']', '{', "\n"]
        encrypted = ""
        for char in message:
            index = alphabet.index(char)
            for i in range(key):
                index -= 1
                if index < 0 - len(alphabet): # this might not work correctly
                    index = len(alphabet) - 1
            encrypted += alphabet[index]
        return encrypted

    def get_messages(self):
        while True:
            if self.disconnected:
                break
            data = s.recv(self.data_buff)
            if not data:
                break
            decoded = data.decode("utf-8")
            decoded = self.decrypt(decoded, self.encryption_key)
            try:
                if decoded[:8] != "$%server":
                    self.insert_message(decoded)
                else:
                    self.server_command(decoded)
            except IndexError:
                self.insert_message(decoded)
        s.close()
        time = datetime.datetime.now().strftime('%H:%M:%S')
        self.insert_message("[{}] Disconnected.".format(time))

    def connect(self):
        print("Attempting to connect to", self.server, "on port", self.port)
        try:
            s.connect((self.server, self.port))
            print("Connection established.")
            return True
        except Exception as e:
            print(e)
            return False

    def disconnect(self):
        #print("Window closed.")
        #root.destroy()
        if not self.disconnected:
            self.disconnected = True
            s.close()
            time = datetime.datetime.now().strftime('%H:%M:%S')
            print("[{}] Disconnected.".format(time))
            self.insert_message("[{}] Disconnected.".format(time))

    def on_delete(self):
        print("Window closed.")
        root.destroy()
        s.close()
        print("Disconnected.")
                

try:
    with open("servers.txt", "r") as r:
        r.read()
except IOError:
    with open("servers.txt", "w") as f:
        pass
        
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
root = Tk()
app = App(root)
default_bg_colour = "#4B95A6"
app.configure(background = default_bg_colour)
root.configure(background = default_bg_colour)
root.title("Messenger V{}".format(str(App.version)))
#root.geometry("1280x720")
root.protocol("WM_DELETE_WINDOW", app.on_delete)
try:
    root.iconbitmap(r'{}\icon.ico'.format(os.path.abspath("")))
except:
    print("Unable to load window icon. Please reinstall the program via the updater.")
root.mainloop()
