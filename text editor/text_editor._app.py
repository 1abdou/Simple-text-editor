import customtkinter as ctk
import tkinter as tk
import pyperclip, os, platform
from CTkMenuBar import *
from PIL import Image
from tkinter import filedialog, messagebox

#Vriables for files operations
global file_name, find_file
file_name = False
find_file = False

#Variable for storing selected text
global selected
selected = False

#Variable for detecting changes
global is_modified
is_modified = False

#Check if there is somthing to find/replace
global there_is_text
there_is_text = False

#Font size percentage
global size_persentage
size_persentage = 100

#Customise buttons
btn_fg_color = "#7a1cac"
btn_hover_color = "#7f27ff"
btn_font = ("Alexandria Medium", 14)

"""
Handeling status
"""
"""Counting characters, lines and columns"""
#By keyboard keys and mouse click
def update_status(event):
    global there_is_text
    #Characters counting
    char_count = len(my_text.get("1.0" , "end-1c"))
    stat_bar2.configure(text=f"     {char_count}  characters")
    #Lines counting
    lin_count = int(my_text.index(tk.INSERT).split(".")[0])
    col_count = int(my_text.index(tk.INSERT).split(".")[1])
    stat_bar3.configure(text=f"   {lin_count}  Ln , {col_count} Col  ")
    #Check if there is text(to find/replace it)
    there_is_text = char_count
    update_line_num(None)

#Monitoring changes on text box
def on_text_modified(event):
    global file_name, is_modified
    if not is_modified:
        is_modified = True
        if file_name:
            window.title(f"{os.path.basename(file_name)} - Text Editor")
        else:
            window.title("Untitled - Text Editor")

#Update line number
def update_line_num(event):
    line_num.configure(state="normal")
    line_num.delete(1.0,"end")
    lines = my_text.get(1.0,"end").count("\n") + 1
    total_line_nember = "\n".join(f"   {str(i)}" for i in range(1, lines))
    line_num.insert(1.0, total_line_nember)
    line_num.configure(state="disable")
    line_num.yview_moveto(my_text.yview()[0])

"""
File operations
"""
#Create a new file function
def new_file(event):
    global file_name, find_file, is_modified
    #Asking to save changes
    if is_modified:
        response = messagebox.askyesnocancel("Save changes", "Do you want to save changes before creating a new file?")
        if response is None:
            return
        elif response:
            save_file(None)
    #Delete the previous text
    my_text.delete("1.0", "end")
    #Update status bar
    window.title("New file - Text Editor")
    stat_bar.configure(text="New file        ")
    #To avoid saving problams
    is_modified = False
    file_name = False
    find_file = False
    update_status(None)
    return "break"

#Open a file function
def open_file(event):
    global file_name, find_file, is_modified
    if is_modified:
        response = messagebox.askyesnocancel("Save changes", "Do you want to save changes before opening a new file?")
        if response is None:
            return
        elif response:
            save_file(None)
    #Find file
    find_file = filedialog.askopenfilename(initialdir=os.path.expanduser('~'), title="Open file", filetypes=(("Text Files", "*.txt"), ("Python Files", "*.py"), ("HTML Files", "*.html"), ("C Files", "*.c"), ("All Files", "*.*")))
    #Stor file name and make it global(maybe use it in save)
    if find_file:
        file_name = os.path.basename(find_file)
        #Delete the previous text
        my_text.delete("1.0", "end")
        #Update status bar
        stat_bar.configure(text=f"{file_name}        ")
        window.title(f"{file_name} - Text Editor")
        #Open the file
        read_file = open(find_file, "r")
        #Add text file to textbox
        my_text.insert("end", read_file.read())
        #Close the open file
        read_file.close()
        update_status(None)
        return "break"

#Save file function
def save_file(event):
    global file_name, find_file, is_modified
    if find_file:
        #Save the file
        save_file = open(find_file, "w")
        save_file.write(my_text.get(1.0, "end"))
        #Close the open file
        save_file.close()
        is_modified = False
        #Update status bar
        stat_bar.configure(text=f"Saved: {file_name}        ")
    else:
        save_as_file(None)
    return "break"

#Save As file function
def save_as_file(event):
    global is_modified
    save_file = filedialog.asksaveasfilename(defaultextension=".*", initialdir=os.path.expanduser('~'), title="Save as", filetypes=(("Text Files", "*.txt"), ("Python Files", "*.py"), ("HTML Files", "*.html"), ("C Files", "*.c"), ("All Files", "*.*")))
    if save_file:
        #Updat status bar
        name = os.path.basename(save_file)
        stat_bar.configure(text=f"Saved: {name}        ")
        window.title(f"{name} - Text Editor")
        #Save the file
        save_file = open(save_file, "w")
        save_file.write(my_text.get(1.0, "end"))
        #Close the open file
        save_file.close()
        is_modified = False
        return "break"

#Close window/Exit from menu
def close_window(event=None):
    global is_modified
    if is_modified:
        response = messagebox.askyesnocancel("Save changes", " Do you want to save changes before exit?")
        if response is None:
            return
        elif response:
            save_file(None)
            window.destroy()
        elif response is False:
            window.destroy()
    else:
        window.destroy()

"""
Editing 
"""
#Cut text
def cut_text(event):
    if my_text.selection_get():
        pyperclip.copy(my_text.selection_get())
        my_text.delete("sel.first", "sel.last")
    else:
        return
    return "break"
#Copy text
def copy_text(event):
    if my_text.selection_get():
        pyperclip.copy(my_text.selection_get())
    else:
        return
    return "break"
#Paste text
def paste_text(event):
        position = my_text.index(tk.INSERT)
        my_text.insert(position, pyperclip.paste())
        return "break"

#Find and replace text
def find_and_replace_dialog(event):
    if not there_is_text:
        return
    #Finding text
    def text_search():
        my_text.tag_remove("found","1.0","end")
        search_text = find_entry.get()
        if search_text:
            pos = "1.0"
            first_word_pos = "0.0"
            #Find and select all matches words to search_text
            while True:
                #Stor searched word begining position
                pos = my_text.search(search_text, pos, stopindex="end", nocase=True)
                #Stop if there is no match found
                if not pos:
                    break
                #Get search word ending position
                end_pos = f"{pos}+{len(search_text)}c"
                #Select found word
                my_text.tag_add("found", pos, end_pos)
                #Stor first word ending position (if there is many matches found)
                if first_word_pos == "0.0":
                    first_word_pos = f"{pos}+{len(search_text)}c"
                #Update begining position for searching
                pos = end_pos

            #Customize tag colors
            my_text.tag_config("found", background="#7f27ff", foreground="white")
            #Move text cursor to the first word found to see results
            my_text.mark_set("insert", f"{first_word_pos}")
            my_text.see("insert")
            my_text.focus()
            #Display no result
            if my_text.tag_ranges("found"):
                no_result.place_forget()
            else:
                no_result.place(x=190,y=12)

    #Replacing text
    def replace_text():
        #Replace the selected text
        if my_text.tag_ranges("sel") and not find_entry.get():
            selected_to_replace = my_text.get(my_text.tag_ranges("sel")[0], my_text.tag_ranges("sel")[1])
            find_entry.insert(0, selected_to_replace)

        to_replace = find_entry.get()
        #If there is no selected text(set focus to the entry)
        if not to_replace:
            find_entry.focus_set()
            return
        
        #Replacing
        replacement = replace_entry.get()
        if replacement:
            pos = "1.0"
            while True:
                pos = my_text.search(to_replace, pos, stopindex="end", nocase=True)
                if not pos:
                    break
                end_pos = f"{pos}+{len(to_replace)}c"
                my_text.delete(pos, end_pos)
                my_text.insert(pos, replacement)
                pos = end_pos
        elif replacement == "":
            pos = "1.0"
            while True:
                pos = my_text.search(to_replace, pos, stopindex="end", nocase=True)
                if not pos:
                    break
                end_pos = f"{pos}+{len(to_replace)}c"
                my_text.delete(pos, end_pos)
                pos = end_pos
                
    #Change find button hover and foreground color
    def change_color(event):
        if ctk.get_appearance_mode() == "Light":
            find_btn.configure(hover_color="#F9F9FA", fg_color="#F9F9FA")
        else:
            find_btn.configure(hover_color="#343638", fg_color="#343638")
        #fill find entry by selected text
        if my_text.tag_ranges("sel") and not find_entry.get():
            selected_text = my_text.get(my_text.tag_ranges("sel")[0], my_text.tag_ranges("sel")[1])
            find_entry.insert(0,selected_text)
        elif not find_entry.get():
            find_entry.focus_set()

    #GUI setup
    f_r_window = ctk.CTkToplevel(window)
    f_r_window.title("")
    f_r_window.geometry("280x100")
    f_r_window.iconbitmap("E:/python/Projects/text editor/assets/book.ico")
    f_r_window.resizable(False,False)
    f_r_window.attributes("-topmost", True)

    #Search image
    img = Image.open("E:/python/Projects/text editor/assets/search.png")
    find_img = ctk.CTkImage(light_image=img, dark_image=img, size=(20,20))
    #Widgets
    find_entry = ctk.CTkEntry(f_r_window, placeholder_text="Find", width=160, height=32, border_width=2, corner_radius=5)
    find_entry.place(x=10, y=10)
    replace_entry = ctk.CTkEntry(f_r_window, placeholder_text="Replace", width=160, height=30, border_width=2, corner_radius=5)
    replace_entry.place(x=10, y=55)
    find_btn = ctk.CTkButton(f_r_window, text="",image=find_img, hover_color="#F9F9FA", fg_color="#F9F9FA", width=25, height=25, corner_radius=0, command=text_search)
    find_btn.place(x=140, y=12)
    no_result = ctk.CTkLabel(f_r_window, text="No result", font=ctk.CTkFont("Alexandria", 14))
    no_result.place(x=190,y=12)
    replace_btn = ctk.CTkButton(f_r_window, text="Replace",font=btn_font, hover_color=btn_hover_color, fg_color=btn_fg_color, width=80, height=26, command=replace_text)
    replace_btn.place(x=180, y=55)

    #bind this sub window with focusIn event to make different changes
    f_r_window.bind("<FocusIn>", change_color)
    #Display loop
    f_r_window.mainloop()

#Go to line
def go_to_line(event):
    #Move carret to the required line
    def focus_on_line():
        line = line_num_entry.get()
        if line:
            my_text.mark_set("insert", f"{line}.0")
            my_text.see("insert")
            my_text.focus()
    def cancel():
        go_to.destroy()
    #GUI setup
    go_to = ctk.CTkToplevel(window)
    go_to.title("")
    go_to.geometry("360x100")
    go_to.iconbitmap("E:/python/Projects/text editor/assets/book.ico")
    go_to.resizable(False,False)
    go_to.attributes("-topmost", True)
    #Widgets
    line_num_entry = ctk.CTkEntry(go_to, placeholder_text="Enter line number", width=300, height=28, corner_radius=5)
    line_num_entry.place(x=30, y=15)
    goto_btn = ctk.CTkButton(go_to, text="Go to", font=btn_font, fg_color=btn_fg_color, hover_color=btn_hover_color, width=140, height=30, command=focus_on_line)
    goto_btn.place(x=30, y=55)
    cancel_btn = ctk.CTkButton(go_to, text="Cancel", font=btn_font, fg_color=btn_fg_color, hover_color=btn_hover_color, width=140, height=30, command=cancel)
    cancel_btn.place(x=190, y=55)
    #Display loop
    go_to.mainloop()

#Bold
def bold_font(state):
    if state is True:
        text_font.configure(weight="bold")
    else:
        text_font.configure(weight="normal")

#Italic
def italic_font(state):
    if state is True:
        text_font.configure(slant="italic")
    else:
        text_font.configure(slant="roman")

#Unerline
def underline_font(state):
    if state is True:
        text_font.configure(underline=True)
    else:
        text_font.configure(underline=False)

#Text color
def text_col():
    #Changing tect color
    def apply():
        try:
            if color_name_entry.get() and not my_text.tag_ranges("sel"):
                my_text.configure(text_color=color_name_entry.get())
            else:
                color = color_name_entry.get()
                start, end = my_text.tag_ranges("sel")
                tag_name = "color"
                my_text.tag_add(tag_name,start,end)
                my_text.tag_config(tag_name, foreground=color)
        except Exception as err:
            messagebox.showerror("Error!", f"Error: {err}")
    #GUI setup
    color_window = ctk.CTkToplevel(window)
    color_window.title("")
    color_window.geometry("280x70")
    color_window.iconbitmap("E:/python/Projects/text editor/assets/book.ico")
    color_window.resizable(False,False)
    color_window.attributes("-topmost", True)
    #Widgets
    color_name_entry = ctk.CTkEntry(color_window, placeholder_text="Color name/Hex", width=150, height=30, border_width=2, corner_radius=5)
    color_name_entry.pack(side="left", padx=10)
    apply_btn = ctk.CTkButton(color_window, text="Apply",font=("Alexandria Medium", 14), hover_color=btn_hover_color, fg_color=btn_fg_color, width=100, height=27, command=apply)
    apply_btn.pack(side="left")
    #Display loop
    color_window.mainloop()

#Select all
def sel_all(event):
    my_text.focus_set()
    my_text.tag_add('sel', "1.0", "end-1c")
    return "break"

#Delete all text
def clear_all():
    my_text.delete("1.0", "end")
    update_status()

"""
View
"""
#Zoom in
def zoom_in(event):
    global size_persentage
    current_size = text_font.cget("size")
    current_size = current_size + 2
    if current_size < 32:
        text_font.configure(size=current_size)
        line_num_font.configure(size=current_size)
        size_persentage = size_persentage + 20
        stat_bar4.configure(text=f"{size_persentage}%      ")
    return "break"

#Zoom out
def zoom_out(event):
    global size_persentage
    current_size = text_font.cget("size")
    current_size = current_size - 2
    if current_size > 8:
        text_font.configure(size=current_size)
        line_num_font.configure(size=current_size)
        size_persentage = size_persentage - 20
        stat_bar4.configure(text=f"{size_persentage}%      ")
    return "break"

#Reset zoom
def defualt_zoom(event):
    global size_persentage
    text_font.configure(size=14)
    line_num_font.configure(size=14)
    size_persentage = 100
    stat_bar4.configure(text=f"{size_persentage}%      ")
    return "break"

#Show/hide status bar
def show_hide_status_bar(state):
    if state is False:
        frame_stat.pack_forget()
        stat_bar.pack_forget()
        stat_bar3.pack_forget()
        stat_bar2.pack_forget()
        stat_bar4.pack_forget()
    else:
        frame_stat.pack(side="bottom", fill="x")
        stat_bar.pack(side="right")
        stat_bar3.pack(side="left")
        stat_bar2.pack(side="left")
        stat_bar4.pack(side="right")

#Word wrapping
def word_wrap(state):
    if state is True:
        my_text.configure(wrap="word")
    else:
        my_text.configure(wrap="none")

#Line numbering display
def show_hide_line_num(state):
    if state is False:
        line_num.pack_forget()
    else:    
        line_num.pack(side="left",fill="y", expand=True,  anchor="w")
        my_text.pack_forget()
        my_text.pack( side="left",fill="both", expand=True)

"""
Themes
"""
#Dark mode
def dark_mode():
    if (ctk.get_appearance_mode() == "Light"):
        ctk.set_appearance_mode("dark")
        menu_1.configure(bg_color="#231F1E")
        file_btn.configure(hover_color="#1B2244")
        edit_btn.configure(hover_color="#1B2244")
        view_btn.configure(hover_color="#1B2244")
        theme_btn.configure(hover_color="#1B2244")
        help_btn.configure(hover_color="#1B2244")
        line_num.configure(fg_color="#231F1E", scrollbar_button_color="#231F1E", scrollbar_button_hover_color="#231F1E")
#Liht mode
def light_mode():
    if(ctk.get_appearance_mode() == "Dark"):
        ctk.set_appearance_mode("light")
        menu_1.configure(bg_color="#F9F1F0")
        file_btn.configure(hover_color="white")
        edit_btn.configure(hover_color="white")
        view_btn.configure(hover_color="white")
        theme_btn.configure(hover_color="white")
        help_btn.configure(hover_color="white")
        line_num.configure(fg_color="#F9F1F0", scrollbar_button_color="#F9F1F0", scrollbar_button_hover_color="#F9F1F0")

"""
Help
"""
#User guide
def show_user_guide():
    # Create a new window
    guide_window = ctk.CTkToplevel(window)
    guide_window.title("User Guide")
    guide_window.geometry("800x600")
    guide_window.iconbitmap("E:/python/Projects/text editor/assets/book.ico")
    guide_window.resizable(True, True)

    # Create a text widget to display the guide
    guide_textbox = ctk.CTkTextbox(guide_window, wrap="word", font= ("Alexandria", 16))
    guide_textbox.pack(fill="both", expand=True)

    # Add the user guide text
    user_guide_text = """
   Text Editor User Guide

    Features
    1. File Operations:
       - New File: Create a new, empty file.
       - Open File: Open an existing file from your computer.
       - Save File: Save the current file.
       - Save As: Save the current file with a new name or location.
       - Exit: Exit the application.

    2. Text Editing:
       - Cut: Cut the selected text.
       - Copy: Copy the selected text.
       - Paste: Paste text from the clipboard.
       - Undo: Undo the last action.
       - Redo: Redo the last undone action.
       - Select All: Select all text in the current file.
       - Clear All: Delete all text in the current file.

    3. Find and Replace:
       - Find: Search for specific text in the file.
       - Replace: Replace specific text with new text.

    4. Font Customization:
       - Bold: Make the selected text bold.
       - Italic: Make the selected text italic.
       - Underline: Underline the selected text.
       - Text Color: Change the color of the selected text or all text.

    5. View Options:
       - Zoom In: Increase the text size.
       - Zoom Out: Decrease the text size.
       - Default Zoom: Reset the text size to the default.
       - Line Numbering: Show or hide line numbers.
       - Word Wrap: Enable or disable word wrapping.
       - Status Bar: Show or hide the status bar.

    6. Themes:
       - Dark Mode: Switch to a dark theme.
       - Light Mode: Switch to a light theme.

    Keyboard Shortcuts

     Action ➜ Shortcut          
    --------------------------
     New File ➜ Ctrl + N          
     Open File ➜ Ctrl + O          
     Save File ➜ Ctrl + S          
     Save As ➜ Ctrl + Shift + S  
     Exit ➜ Ctrl + Q          
     Cut ➜ Ctrl + X          
     Copy ➜ Ctrl + C          
     Paste ➜ Ctrl + V          
     Undo ➜ Ctrl + Z          
     Redo ➜ Ctrl + Y          
     Select All ➜ Ctrl + A          
     Clear All  -
     Find ➜ Ctrl + F          
     Replace ➜ Ctrl + R          
     Go to Line ➜ Ctrl + G          
     Bold ➜ Ctrl + B          
     Italic ➜ Ctrl + I          
     Underline ➜ Ctrl + U          
     Zoom In ➜ Ctrl + Plus (+)   
     Zoom Out ➜ Ctrl + Minus (-)  
     Default Zoom ➜ Ctrl + 0
     Exit ➜ Ctrl + Q          
     Toggle Line Numbers  -                 
     Toggle Word Wrap  -                 
     Toggle Status Bar  -                 
     Dark Mode  -                 
     Light Mode  -                 

    How to Use
    1. Creating a New File:
       - Go to File > New or press Ctrl + N.
       - A new tab will open with an empty file.

    2. Opening a File:
       - Go to File > Open or press Ctrl + O.
       - Select the file you want to open from the dialog.

    3. Saving a File:
       - To save the current file, go to File > Save or press Ctrl + S.
       - To save with a new name or location, go to File > Save As or press Ctrl + Shift + S.

    4. Editing Text:
       - Use the Edit menu or keyboard shortcuts to cut, copy, paste, undo, and redo actions.
       - Select text and change it's color from edit menu.(if there is nothing selected will change all text color) 
       - To select all text, press Ctrl + A.

    5. Finding and Replacing Text:
       - Press Ctrl + F to open the Find dialog.
       - Press Ctrl + R to open the Replace dialog.

    6. Changing Font Style:
       - Use the Edit > Font menu to apply bold, italic, underline, or change text color.

    7. Zooming:
       - Use Ctrl + Plus (+) to zoom in, Ctrl + Minus (-) to zoom out, and Ctrl + 0 to reset the zoom.

    8. Switching Themes:
       - Go to Theme > Dark Mode or Theme > Light Mode to switch between themes.

    9. Exiting the Application:
        - Go to File > Exit or press Ctrl + Q to close the application.

    Tips
    - Use Line Numbering to easily navigate through large files.
    - Enable Word Wrap to prevent horizontal scrolling for long lines of text.
    - Use Dark Mode for a more comfortable experience in low-light environments.
    """
    # Insert the guide text into the textbox
    guide_textbox.insert("1.0", user_guide_text)
    guide_textbox.configure(state="disabled")

#About
def about_window():
    # Create a new window
    about_window = ctk.CTkToplevel(window)
    about_window.title("About")
    about_window.geometry("300x200")
    about_window.iconbitmap("E:/python/Projects/text editor/assets/book.ico")
    about_window.resizable(False, False)

    about_text = f"""
 Text Editor
 Version: 1.0.0
 Date: 07/01/2025
 Python: 3.12
 OS: {platform.platform()}
 
    """
    text_box = ctk.CTkLabel(about_window, text=about_text, font=("Alexandria", 14), anchor="center")
    text_box.pack(fill="both", expand=True)


"""
##############################
+------------main------------+
##############################
"""
#GUI set up
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("dark-blue")
window = ctk.CTk()
window.title("Text Editor")
window.iconbitmap("E:/python/Projects/text editor/assets/book.ico")
window.geometry("800x500")
window.protocol("WM_DELETE_WINDOW", close_window)
window.bind("<Control-q>", close_window)
window.bind("<Control-Q>", close_window)

#Create menu
menu_1 = CTkMenuBar(window, bg_color="#F9F1F0")

#Create main frame
main_f = ctk.CTkFrame(window, corner_radius=0)
main_f.pack(side="top", fill="both", expand=True)

#Font
text_font = ctk.CTkFont(family="Alexandria", size=14, weight="normal", slant="roman", underline=False)
line_num_font = ctk.CTkFont(family="Alexandria", size=14)

#Line Numbering
line_num = ctk.CTkTextbox(main_f, font=line_num_font, width=70, height=5, fg_color="#F9F1F0", state="disabled", cursor="arrow", scrollbar_button_color="#F9F1F0", scrollbar_button_hover_color="#F9F1F0")
line_num.pack(side="left",fill="y", expand=True,  anchor="w")

#Create textbox
my_text = ctk.CTkTextbox(main_f, font=text_font, width=1290, height=5, undo=True, wrap="none")
my_text.pack( side="left",fill="both", expand=True)

#Binding events
my_text.bind("<KeyRelease>", update_status)
my_text.bind("<ButtonRelease>", update_status)
my_text.bind("<Control-a>", sel_all)
my_text.bind("<Control-A>", sel_all)
my_text.bind("<Control-plus>", zoom_in)
my_text.bind("<Control-minus>", zoom_out)
my_text.bind("<Control-0>", defualt_zoom)
my_text.bind("<Control-x>", cut_text)
my_text.bind("<Control-X>", cut_text)
my_text.bind("<Control-c>", copy_text)
my_text.bind("<Control-C>", copy_text)
my_text.bind("<Control-v>", paste_text)
my_text.bind("<Control-V>", paste_text)
my_text.bind("<Control-s>", save_file)
my_text.bind("<Control-S>", save_file)
my_text.bind("<Control-n>", new_file)
my_text.bind("<Control-N>", new_file)
my_text.bind("<Control-o>", open_file)
my_text.bind("<Control-O>", open_file)
my_text.bind("<Control-Shift-s>", save_as_file)
my_text.bind("<Control-Shift-S>", save_as_file)
my_text.bind("<Any-KeyRelease>", on_text_modified)
my_text.bind("<Control-F>", find_and_replace_dialog)
my_text.bind("<Control-f>", find_and_replace_dialog)
my_text.bind("<Control-r>", find_and_replace_dialog)
my_text.bind("<Control-R>", find_and_replace_dialog)
my_text.bind("<Control-G>", go_to_line)
my_text.bind("<Control-g>", go_to_line)
my_text.bind("<MouseWheel>", update_line_num)
my_text.bind("<Control-b>", bold_font)
my_text.bind("<Control-B>", bold_font)

#Add file menu
file_btn = menu_1.add_cascade("File", hover_color="white")
file_dropdown = CustomDropdownMenu(file_btn)
file_dropdown.add_option("New                          Ctrl+N", command= lambda: new_file(None))
file_dropdown.add_option("Open                         Ctrl+O", command= lambda: open_file(None))
file_dropdown.add_option("Save                          Ctrl+S", command= lambda: save_file(None))
file_dropdown.add_option("Save as          Ctrl+Shift+S", command= lambda: save_as_file(None))
file_dropdown.add_separator()
file_dropdown.add_option("Exit                            Ctrl+Q", command= close_window)

#Add Edit menu
edit_btn = menu_1.add_cascade("Edit", hover_color="white")
edit_dropdown = CustomDropdownMenu(edit_btn)
edit_dropdown.add_option("Undo                         Ctrl+Z", command=my_text.edit_undo)
edit_dropdown.add_option("Redo                         Ctrl+Y", command=my_text.edit_redo)
edit_dropdown.add_separator()
edit_dropdown.add_option("Cut                             Ctrl+X", command= lambda: cut_text(None))
edit_dropdown.add_option("Copy                          Ctrl+C", command= lambda: copy_text(None))
edit_dropdown.add_option("Past                           Ctrl+V", command= lambda: paste_text(None))
edit_dropdown.add_separator()
edit_dropdown.add_option("Find                            Ctrl+F", command= lambda: find_and_replace_dialog(None))
edit_dropdown.add_option("Replace                    Ctrl+R", command= lambda: find_and_replace_dialog(None))
edit_dropdown.add_option("Go to                          Ctrl+G", command= lambda: go_to_line(None))
edit_dropdown.add_separator()
font_menu = edit_dropdown.add_submenu("Font                                  ⫸", font=text_font)
font_menu.add_checkable_option("Bold", command=bold_font, initial_state=False)
font_menu.add_checkable_option("Italic", command=italic_font, initial_state=False)
font_menu.add_checkable_option("Underline ", command=underline_font, initial_state=False)
font_menu.add_separator()
font_menu.add_option("Color", command= text_col)
edit_dropdown.add_option("Select all                   Ctrl+A", command= lambda: sel_all(None))
edit_dropdown.add_option("Clear all", command= clear_all)

#Add veiw menu
view_btn = menu_1.add_cascade("View", hover_color="white")
view_dropdown = CustomDropdownMenu(view_btn)
zoom_options = view_dropdown.add_submenu("Zoom                                  ⫸")
zoom_options.add_option("Zoom in                        Ctrl+Plus", command= lambda: zoom_in(None))
zoom_options.add_option("Zoom out                   Ctrl+Minus", command= lambda: zoom_out(None))
zoom_options.add_option("Defualt zoom                     Ctrl+0", command= lambda: defualt_zoom(None))
view_dropdown.add_checkable_option("Line numbering",show_hide_line_num, initial_state=True)
view_dropdown.add_checkable_option("Word Wrap", word_wrap, initial_state=False)
view_dropdown.add_checkable_option("Status bar", show_hide_status_bar, initial_state=True)

#Add theme menu
theme_btn = menu_1.add_cascade("Theme", hover_color="white")
theme_dropdown = CustomDropdownMenu(theme_btn)
theme_dropdown.add_option("Dark mode", command=dark_mode)
theme_dropdown.add_option("Light mode", command=light_mode)

#Add help menu
help_btn = menu_1.add_cascade("Help", hover_color = "white")
help_dropdown = CustomDropdownMenu(help_btn)
help_dropdown.add_option("User guide", command= show_user_guide)
help_dropdown.add_option("About", command= about_window)

#Frame status bars
frame_stat = ctk.CTkFrame(window, bg_color="black")
frame_stat.pack(side="bottom", fill="x")

#status bars
stat_bar = ctk.CTkLabel(frame_stat, text="Ready        ", font=("Alexandria Medium", 14))
stat_bar.pack(side="right")
stat_bar3 = ctk.CTkLabel(frame_stat, text="   0  Ln , 0  Col  ", font=("Alexandria Medium", 14))
stat_bar3.pack(side="left")
stat_bar2 = ctk.CTkLabel(frame_stat, text="     0  Characters", font=("Alexandria Medium", 14))
stat_bar2.pack(side="left")
stat_bar4 = ctk.CTkLabel(frame_stat, text="100%      ", font=("Alexandria Medium", 14))
stat_bar4.pack(side="right")

#1 for the first line
update_line_num(None)

#Display loop
window.mainloop()