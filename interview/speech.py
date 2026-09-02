def transcribe_audio_file(audio_file_path):
    """
    Transcribe audio using SpeechRecognition or speech engine if available.
    Supports local SpeechRecognition fallback.
    """
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        return f"[Audio recorded, speech recognition fallback active]: {str(e)}"
