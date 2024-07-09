import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ttkbootstrap as tb
from gtts import gTTS
from PIL import ImageTk, Image
import os
import pygame
import sv_ttk

# Create database tables if they don't exist
def create_tables(conn):
    cursor = conn.cursor()
   
    # Create flashcard_sets table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS flashcard_sets (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL
                       )
    ''')
    
    # Create flashcards table with foreign key reference to flashcard_sets
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS flashcards (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           set_id INTEGER NOT NULL,
                           word TEXT NOT NULL,
                           definition TEXT NOT NULL,
                           FOREIGN KEY (set_id) REFERENCES flashcard_sets(id)
                       )
    ''')
    
# Add a new flashcard set to the database
def add_set(conn, name):
    cursor = conn.cursor()
    
    # Insert the set name into flashcard_sets table
    cursor.execute('''
                   INSERT INTO flashcard_sets(name)
                   VALUES (?)
    ''', (name,))
    
    set_id = cursor.lastrowid
    conn.commit()
    
    return set_id

# Function to add a flashcard to the database
def add_card(conn, set_id, word, definition):
    cursor = conn.cursor()
    
    # Execute SQL query to insert a new flashcard into the database
    cursor.execute('''
                   INSERT INTO flashcards (set_id, word, definition)
                   VALUES (?, ?, ?)
                   ''', (set_id, word, definition))

    # Get the ID of the newly inserted card
    card_id = cursor.lastrowid
    conn.commit()
    
    return card_id

# Function to retrieve all flashcard sets from the database 
def get_sets(conn):
    cursor = conn.cursor()
    
    # Execute SQL query to fetch all flashcard sets 
    cursor.execute('''
                   SELECT id, name FROM flashcard_sets
                   ''')
    rows = cursor.fetchall()
    sets = {row[1]: row[0] for row in rows} # Create a dictionary of sets (name: id)
    return sets

# Function to retrieve all flashcards of a specific set
def get_cards (conn, set_id):
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT word, definition FROM flashcards
                   WHERE set_id = ? 
                   ''', (set_id,))
    rows = cursor.fetchall()
    cards = [(row[0], row[1]) for row in rows] # Create a list of cards (word, definition)
    return cards

# Function to delete a flashcard set from the database 
def delete_set(conn, set_id):
    cursor = conn.cursor()
    # Execute SQL query to delete a flashcard set 
    cursor.execute('''
                   DELETE FROM flashcard_sets
                   WHERE id = ?
                   ''', (set_id,))
    conn.commit()
    sets_combobox.set('')
    clear_flashcard_display()
    populate_sets_combobox()
    
    # Clear the current_cards list and reset card index
    global current_cards, card_index
    current_cards = []
    card_index = 0

# Function to create a new flashcard set 
def create_set():
    set_name = set_name_var.get()
    if set_name:
        if set_name not in get_sets (conn):
            set_id = add_set(conn, set_name) 
            populate_sets_combobox() 
            set_name_var.set('')
            
            # Clear the input fields set_name_var.set('')
            word_var.set('')
            definition_var.set('')

def add_word():
    set_name = set_name_var.get() 
    word = word_var.get()
    definition = definition_var.get()

    if set_name and word and definition: 
        if set_name not in get_sets (conn): 
            set_id = add_set(conn, set_name)
        else:
            set_id = get_sets (conn) [set_name]

        add_card (conn, set_id, word, definition)
        word_var.set('')
        definition_var.set('')
        populate_sets_combobox()
    
def populate_sets_combobox():
    sets_combobox['values'] = tuple(get_sets(conn).keys())
    
def delete_selected_set():
    set_name = sets_combobox.get()
    
    if set_name:
        result = messagebox.askyesno(
            'Confirmation', f'Are you sure you want to delete the "{set_name}" set?'
            )
        if result == tk.YES:
            set_id = get_sets(conn)[set_name]
            delete_set(conn, set_id)
            populate_sets_combobox()
            clear_flashcard_display()

def select_set():
    global current_cards
    set_name = sets_combobox.get()
    if set_name:
        set_id = get_sets (conn) [set_name]
        cards = get_cards (conn, set_id)
        if cards:
            display_flashcards (cards)
            progressbar['value'] = 100/len(current_cards)
        else:
            word_label.config(text="No cards in this set") 
    else:
        # Clear the current cards list and reset card index
        global current_card, card_index
        current_cards = []
        card_index = 0
        clear_flashcard_display()

def display_flashcards (cards): 
    global card_index
    global current_cards

    card_index = 0
    current_cards = cards

    # Clear the display
    if not cards:
        clear_flashcard_display()
    else:
        show_card()
    show_card()

def clear_flashcard_display():
    word_label.config(text = '')

# Function to display the current flashcards
def show_card():
    global card_index
    global current_cards
    
    if current_cards:
        if 0 <= card_index < len(current_cards): 
            word, _ = current_cards [card_index] 
            word_label.config(text=word) 
            progress_label.config(text = f'{card_index + 1} out of {len(current_cards)}')
        else:
            clear_flashcard_display()
    else:
        clear_flashcard_display()

# Function to flip the current card and display its definition
def flip_card():
    global card_index
    global current_cards
    
    try:
        if current_cards:
            word, definition = current_cards[card_index]
            if word_label["text"] == word:
                word_label.config(text=definition)
            elif word_label["text"] == definition:
                word_label.config(text=word)
    except NameError:
        pass
            
# Function to move to the next card
def next_card():
    global card_index
    global current_cards
    try:
        if current_cards:
            card_index = min(card_index + 1, len(current_cards) -1) 
            progressbar['value'] = min(progressbar['value'] + 100/len(current_cards), 100)
            show_card()
    except NameError:
        pass

def prev_card():
    global card_index
    global current_cards
    
    try:
        if current_cards:
            card_index = max(card_index - 1, 0) 
            progressbar['value'] = max(progressbar['value'] - 100/len(current_cards), 100/len(current_cards))
            show_card() 
    except NameError:
        pass

# Function for text to speech
def volume_clicked():
    global card_index
    global current_cards
    pygame.mixer.init()
    
    try:
        if current_cards:
            word, definition = current_cards[card_index]
            if not os.path.isfile(f'{word_label["text"]}.mp3'):
                if word_label["text"] == word:
                    myobj = gTTS(text=word, lang='it', slow=False)
                elif word_label["text"] == definition:
                    myobj = gTTS(text=definition, lang='en', slow=False)
                myobj.save(f'{word_label["text"]}.mp3')
            pygame.mixer.music.load(f"./{word_label['text']}.mp3")
            pygame.mixer.music.play()
    except NameError:
        pass

def changeMode():
    if switch.cget('text') == 'dark mode':
        sv_ttk.set_theme("dark")
        switch['text'] = 'light mode'
    else:
        sv_ttk.set_theme("light")
        switch['text'] = 'dark mode'
    pass

if __name__ == "__main__":
    # Connect to the SQLite database and create tables
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    create_tables(conn)
    
    # Create the main GUI window
    root = tb.Window()
    root.title('Flashcards App')
    root.geometry('900x450')
    
    # Set up the variables for storing user input
    set_name_var = tk.StringVar()
    word_var = tk.StringVar()
    definition_var = tk.StringVar()
    
    # Create a notebook widget to manage tabs
    notebook = tb.Notebook(root, bootstyle = 'dark')
    notebook.pack(fill = 'both', expand = True)
    
    # Create the "Create Set" tab and its content
    create_set_frame = tb.Frame(notebook)
    notebook.add(create_set_frame, text = 'Create Set')
    
    # Label and Entry widgets for entering set name, word and definition
    ttk.Label(create_set_frame, text = 'Set Name:').pack(padx = 5, pady = 5)
    ttk.Entry(create_set_frame, textvariable = set_name_var, width = 30).pack(padx = 5, pady = 5)
    
    ttk.Label(create_set_frame, text = 'Word:').pack(padx = 5, pady = 5)
    ttk.Entry(create_set_frame, textvariable = word_var, width = 30).pack(padx = 5, pady = 5)

    ttk.Label(create_set_frame, text='Definition:').pack(padx = 5, pady = 5)
    ttk.Entry(create_set_frame, textvariable = definition_var, width = 30).pack(padx = 5, pady = 5)
    
    # Button to add a word to the set 
    ttk.Button(create_set_frame, text = 'Add word', command=add_word).pack(padx = 5, pady = 10)
    
    # Button to save the set
    ttk.Button(create_set_frame, text = 'Save Set', command=create_set).pack(padx = 5, pady = 10)
    
    # Create the "Select Set" tab and its content
    select_set_frame = tb.Frame(notebook)
    notebook.add(select_set_frame, text = "Select Set")
    
    # Combobox widget for selecting existing flashcard sets
    sets_combobox = ttk.Combobox(select_set_frame, state='readonly')
    sets_combobox.pack(padx = 5, pady = 5)
    
    # Button to select a set 
    ttk.Button(select_set_frame, text = 'Select Set', command = select_set).pack(padx = 5, pady = 5)
    
    # Button to delete a set
    ttk.Button(select_set_frame, text = 'Delete Set', command = delete_selected_set).pack(padx = 5, pady = 5)

    # Create the "Learn mode" tab and its content
    flashcards_frame = tb.Frame(notebook)
    notebook.add(flashcards_frame, text='Learn Mode')
    
    # Initialize variables for tracking card index and current cards
    card_index = 0
    current_tabs= []
    
    # Label to display the word on the flashcards
    word_label = tk.Label(flashcards_frame, text = '', font = ('TkDefaultFont', 24), borderwidth=2, relief="raised", width=20, height=6)
    word_label.pack(padx = 5, pady = 40)
    
    # Button to flip the flashcard
    ttk.Button(flashcards_frame, text = 'Flip', command = flip_card).pack(side = 'left', padx = 5, pady = 5)
    
    # Button to view the next flashcard
    ttk.Button(flashcards_frame, text = 'Next', command = next_card).pack(side = 'right', padx = 5, pady = 5)
    
    # Button to view the previous flashcard
    ttk.Button(flashcards_frame, text = 'Previous', command = prev_card).pack(side = 'right', padx = 5, pady = 5)
    
    # Progress meter
    global progressbar
    progressbar = ttk.Progressbar(flashcards_frame, orient = 'horizontal', mode = 'determinate', length = 400)
    progressbar.pack(side = 'left')
    
    global progress_label
    progress_label = ttk.Label(flashcards_frame, font = ('TkDefaultFont', 10))
    progress_label.pack(side = 'left')
    
    # Text to speech button
    image = Image.open("./volume.png")
    resize_image = image.resize((30,30))
    volume_img = ImageTk.PhotoImage(resize_image)
    volume_button = ttk.Button(word_label, image = volume_img, command = volume_clicked)
    volume_button.place(relx=1.0, y=0, anchor="ne")
    
    populate_sets_combobox()
    
    # Using a button to set light/dark mode
    global switch
    switch = ttk.Button(select_set_frame, text = "dark mode", style='Padded.TButton', command = changeMode)
    switch.place(relx=1.0, y=0, anchor="ne")
    switch = ttk.Button(create_set_frame, text = "dark mode", style='Padded.TButton', command = changeMode)
    switch.place(relx=1.0, y=0, anchor="ne")
    switch = ttk.Button(flashcards_frame, text = "dark mode", style='Padded.TButton', command = changeMode)
    switch.place(relx=1.0, y=0, anchor="ne")
     
    # Default light mode
    sv_ttk.set_theme("light")
    
    root.mainloop()