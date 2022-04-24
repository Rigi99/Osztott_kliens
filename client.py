import socket
import threading
import tkinter
import tkinter.scrolledtext
import time
from tkinter import simpledialog
import pandas as pd

HOST = "127.0.0.1"
PORT = 65432


class Client:
    def __init__(self, host, port):

        message = tkinter.Tk()
        message.withdraw()

        self.nickname = simpledialog.askstring("Chat", "Please choose a nickname(max 13 characters)", parent=message)
        self.win = tkinter.Tk()

        self.textArea = tkinter.scrolledtext.ScrolledText(self.win)

        self.chatLabel = tkinter.Label(self.win, text="Chat", bg="lightgray")

        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((host, port))

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def gui_loop(self):
        self.win.title(f"{self.nickname}")
        self.win.configure(bg="lightgray", width=800, height=400)

        self.chatLabel.config(font=('Arial', 16))
        self.chatLabel.place(x=360, y=10)

        self.textArea.place(x=30, y=40, width=700, height=310)
        self.textArea.config(state="disabled")

        self.gui_done = True
        self.send()

    def stop(self):
        self.running = False
        self.win.destroy()
        self.clientSocket.close()
        exit(0)

    def send(self):
        message = "valami"
        while True:
            self.sendMessage(message)
            time.sleep(5)

    def sendMessage(self, message):
        self.clientSocket.send(message.encode('utf-8'))

    def receive(self):
        while self.running:
            try:
                message = self.clientSocket.recv(1024).decode('utf-8')
                single_data = message.split('#')
                single_data.pop()
                single_data_name = [i.split('|')[0] for i in single_data]
                single_data_vote = [i.split('|')[1] for i in single_data]
                df = pd.DataFrame({'Partok': single_data_name, 'Szavazatok': single_data_vote})
                df = df.sort_values(by=['Szavazatok'], ascending=False)
                df = df.reset_index(drop=True)
                if self.gui_done:
                    self.textArea.config(state='normal')
                    self.textArea.delete('1.0', tkinter.END)
                    self.textArea.insert('end', df)
                    self.textArea.insert('end', '\n')
                    self.textArea.yview('end')
                    self.textArea.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("ERROR")
                self.clientSocket.close()
                break
