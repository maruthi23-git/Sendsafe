import mysql.connector
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
import socket
import os

# MySQL connection setup
def connect_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='open',
            database='send_safe'
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

# Main window configuration
root = Tk()
ttk.Style().theme_use("clam")
root.title("SendSafe")
root.geometry("450x560+500+200")
root.configure(bg="#f4fdfe")
root.resizable(False, False)

#icon
image_icon=PhotoImage(file="Image/icon.png")
root.iconphoto(False,image_icon)

background = PhotoImage(file="Image/background.png")
Label(root,image=background).place(x=-2,y=323)

Label(root,text="File Transfer",font=('Acumin Variable Concept',20,'bold'),bg="#f4fdfe").place(x=20,y=30)
Frame(root,width=400,height=2,bg="#f3f5f6").place(x=25,y=80)

# Track window state to prevent opening multiple times
send_window_open = False
receive_window_open = False

def Send():
    global send_window_open

    if send_window_open:
        return  # Prevent reopening the Send window if it's already open

    send_window_open = True

    def open_send_window():
        Window = Toplevel(root)
        Window.title("Send")
        Window.geometry("450x560+500+200")
        Window.configure(bg="#f4fdfe")
        Window.resizable(False, False)

        filename = None  # Variable to store selected file

        try:
            Sbackground = PhotoImage(file="Image/sender.png")  # Ensure this image exists in the Image folder
        except TclError:
            messagebox.showerror("Error", "Image 'sender.png' not found in the 'Image' folder.")
            return

        Label(Window, image=Sbackground).place(x=0, y=0)
        try:
            Mbackground = PhotoImage(file="Image/id.png")  # Ensure this image exists in the Image folder
        except TclError:
            messagebox.showerror("Error", "Image 'id.png' not found in the 'Image' folder.")
            return

        host_ip = socket.gethostbyname(socket.gethostname())
        Label(Window, image=Mbackground).place(x=100, y=260)
        Label(Window, text=f'ID: {host_ip}', fg='black', font=('arial', 12)).place(x=140, y=290)

        selected_file_label = Label(Window, text="No file selected", bg="#f4fdfe", fg="black", font=('arial', 12), wraplength=300)
        selected_file_label.place(x=160, y=200)

        def select_file():
            nonlocal filename
            filename = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select File', filetypes=(('Text Files', '*.txt'), ('All files', '*.*')))
            if filename:
                selected_file_label.config(text=f'Selected: {os.path.basename(filename)}')  # Display filename

        def sender():
            if not filename:
                messagebox.showerror("Error", "Please select a file first!")
                return
            try:
                s = socket.socket()
                host = socket.gethostname()  # Get the local machine name
                port = 8080
                s.bind((host, port))
                s.listen(1)
                conn, addr = s.accept()
                with open(filename, 'rb') as file:
                    file_data = file.read(1024)
                    while file_data:
                        conn.send(file_data)
                        file_data = file.read(1024)

                db_conn = connect_db()
                if db_conn:
                    cursor = db_conn.cursor()
                    sender_id = host_ip
                    recipient_id = addr[0]
                    cursor.execute("INSERT INTO transfer_history (sender_id, recipient_id, file_name, transfer_status) VALUES (%s, %s, %s, %s)",
                                   (sender_id, recipient_id, os.path.basename(filename), 'Sent'))
                    db_conn.commit()
                    cursor.close()
                    db_conn.close()

                messagebox.showinfo("Success", "File sent successfully!")
                conn.close()
                Window.destroy()  # Close the window after sending the file
                global send_window_open
                send_window_open = False  # Reset window state
            except Exception as e:
                messagebox.showerror("Error", "Failed to send file")

        try:
            image_icon1 = PhotoImage(file="Image/send.png")  # Ensure this image exists in the Image folder
        except TclError:
            messagebox.showerror("Error", "Image 'send.png' not found in the 'Image' folder.")
            return

        Window.iconphoto(False, image_icon1)

        Button(Window, text="+ Select File", width=15, height=2, font='arial 12 bold', bg="#fff", fg="#000", command=select_file).place(x=160, y=150)
        Button(Window, text="SEND", width=10, height=2, font='arial 12 bold', bg='#000', fg="#fff", command=sender).place(x=300, y=150)

        Window.protocol("WM_DELETE_WINDOW", lambda: close_send_window(Window))  # Add close protocol
        Window.mainloop()

    open_send_window()

def close_send_window(Window):
    global send_window_open
    send_window_open = False  # Reset window state when it's closed
    Window.destroy()

def Receive():
    global receive_window_open

    if receive_window_open:
        return  # Prevent reopening the Receive window if it's already open

    receive_window_open = True

    def open_receive_window():
        main = Toplevel(root)
        main.title("Receive")
        main.geometry("450x560+500+200")
        main.configure(bg="#f4fdfe")
        main.resizable(False, False)

        def receiver():
            ID = SenderID.get()
            filename1 = incoming_file.get()

            try:
                s = socket.socket()
                port = 8080
                s.connect((ID, port))
                file = open(filename1, 'wb')
                file_data = s.recv(1024)
                while file_data:
                    file.write(file_data)
                    file_data = s.recv(1024)
                file.close()

                db_conn = connect_db()
                if db_conn:
                    cursor = db_conn.cursor()
                    sender_id = ID
                    recipient_id = socket.gethostbyname(socket.gethostname())  # Receiver's IP
                    cursor.execute("INSERT INTO transfer_history (sender_id, recipient_id, file_name, transfer_status) VALUES (%s, %s, %s, %s)",
                                   (sender_id, recipient_id, os.path.basename(filename1), 'Received'))
                    db_conn.commit()
                    cursor.close()
                    db_conn.close()

                messagebox.showinfo("Success", "File received successfully!")
                s.close()
                main.destroy()  # Close the window after receiving the file
                global receive_window_open
                receive_window_open = False  # Reset window state
            except Exception as e:
                messagebox.showerror("Error", f"Failed to receive file: {e}")

        try:
            Hbackground = PhotoImage(file="Image/receiver.png")  # Ensure this image exists in the Image folder
        except TclError:
            messagebox.showerror("Error", "Image 'receiver.png' not found in the 'Image' folder.")
            return

        Label(main, image=Hbackground).place(x=0, y=0)

        Label(main, text="Input sender ID", font=('arial', 10, 'bold'), bg="#f4fdfe").place(x=20, y=340)
        SenderID = Entry(main, width=25, fg="black", border=2, bg='white', font=('arial', 15))
        SenderID.place(x=20, y=370)
        SenderID.focus()

        Label(main, text="File name for the incoming file: ", font=('arial', 10, 'bold'), bg="#f4fdfe").place(x=20, y=420)
        incoming_file = Entry(main, width=25, fg="black", border=2, bg='white', font=('arial', 15))
        incoming_file.place(x=20, y=450)

        Button(main, text="Receive", width=15, height=2, font='arial 12 bold', bg="#4CAF50", fg="#fff", command=receiver).place(x=150, y=500)

        main.protocol("WM_DELETE_WINDOW", lambda: close_receive_window(main))  # Add close protocol
        main.mainloop()

    open_receive_window()

def close_receive_window(main):
    global receive_window_open
    receive_window_open = False  # Reset window state when it's closed
    main.destroy()

def history():
    history_window = Toplevel(root)
    history_window.title("Transfer History")
    history_window.geometry("450x560+500+200")
    history_window.configure(bg="#f4fdfe")
    history_window.resizable(False, False)

    db_conn = connect_db()
    if db_conn:
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM transfer_history")
        transfers = cursor.fetchall()
        cursor.close()
        db_conn.close()

        # Create treeview with custom column widths and heading alignment
        tree = ttk.Treeview(history_window, columns=("ID", "Sender", "Recipient", "File", "Status"), show="headings")

        tree.heading("ID", text="Transfer ID", anchor="center")
        tree.heading("Sender", text="Sender ID", anchor="center")
        tree.heading("Recipient", text="Recipient ID", anchor="center")
        tree.heading("File", text="File Name", anchor="center")
        tree.heading("Status", text="Transfer Status", anchor="center")

        # Set column widths (optional to fit content)
        tree.column("ID", width=63, anchor="center")
        tree.column("Sender", width=65, anchor="center")
        tree.column("Recipient", width=65, anchor="center")
        tree.column("File", width=100, anchor="center")
        tree.column("Status", width=80, anchor="center")

        # Insert data into treeview
        for transfer in transfers:
            tree.insert("", "end", values=transfer)

        # Scrollbar for Treeview
        scrollbar = Scrollbar(history_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        tree.pack(fill=BOTH, expand=True)

    Button(history_window, text="Close", command=history_window.destroy).pack(pady=10)


send_image=PhotoImage(file="Image/send.png")
send=Button(root,image=send_image,bg="#f4fdfe",bd=0,command=Send)
send.place(x=50,y=100)

Button(root, text="History", width=10, height=2, font='arial 12 bold', bg="#9C27B0", fg="#fff", command=history).place(x=300, y=20)

receive_image = PhotoImage(file="Image/receive.png")
receive = Button(root, image=receive_image, bg="#f4fdfe", bd=0, command=Receive)
receive.place(x=300, y=120)

Label(root, text="Send", font=('Acumin Variable Concept', 17, 'bold'), bg="#f4fdfe").place(x=65, y=200)
Label(root, text="Receive", font=('Acumin Variable Concept', 17, 'bold'), bg="#f4fdfe").place(x=300, y=220)



root.mainloop()
