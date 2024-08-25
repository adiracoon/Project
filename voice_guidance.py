import pyttsx3


def provide_voice_instruction(direction):
    """
    Provides voice instructions to the user.

    This function uses the pyttsx3 library to convert text into speech. It initializes a text-to-speech engine,
    speaks the provided direction, and waits until the speech is complete.

    Args:
    - direction (str): The instruction or direction to be spoken out loud.

    Example:
        provide_voice_instruction("Move left")
    """
    engine = pyttsx3.init()  # Initialize the text-to-speech engine
    engine.say(direction)  # Convert the direction text to speech
    engine.runAndWait()  # Block while processing all the currently queued commands
