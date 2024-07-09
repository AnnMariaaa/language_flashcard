
# Language Flashcard App

## Overview
The Language Flashcard App is a versatile and user-friendly tool for learning new languages. This app allows users to create their own sets of flashcards, select sets for focused study, and learn through an interactive flashcard system. It incorporates text-to-speech technology to help users improve their pronunciation.

## Features
- **Create Flashcard Sets:** Easily create and manage your own sets of flashcards.
- **Select Flashcard Sets:** Choose from your created sets to focus on specific topics or languages.
- **Interactive Learning:** Flip through flashcards and test your knowledge.
- **Text-to-Speech Technology:** Listen to the pronunciation of words and phrases to enhance your learning experience.

## Libraries Used
The app is built using Python and Tkinter, along with the following libraries:

- `sqlite3`: For database management.
- `tkinter`: For creating the graphical user interface.
- `ttk`: Tkinter themed widgets.
- `messagebox`: For displaying message boxes in Tkinter.
- `ttkbootstrap`: For enhanced styling of Tkinter widgets.
- `gTTS`: For text-to-speech conversion.
- `PIL (Pillow)`: For image handling.
- `os`: For operating system interactions.
- `pygame`: For playing audio files.
- `sv_ttk`: For additional styling.

## Usage
1. **Creating a Flashcard Set:**
    - Open the app and navigate to the 'Create Set' section.
    - Enter the title for your set and add your flashcards by providing the word/phrase and its translation.
    - Save your set.

2. **Selecting a Flashcard Set:**
    - Go to the 'Select Set' section.
    - Choose the set you want to study from the list of your created sets.

3. **Learning with Flashcards:**
    - In the 'Learn' section, you can start flipping through your selected set of flashcards.
    - Use the text-to-speech button to hear the pronunciation of the word/phrase.

## Text-to-Speech Integration
The app uses the `gTTS` library for text-to-speech functionality to help you learn the correct pronunciation of words and phrases. Ensure your device has an internet connection to use this feature.

## Contribution
If you encounter any issues or have suggestions for improvement, feel free to contribute by submitting a pull request or opening an issue on the GitHub repository.
