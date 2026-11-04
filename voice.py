
import streamlit.components.v1 as components


def female_voice(text, language="en-IN"):
    """
    MyOwnAI ke response ko browser ki
    available female voice mein sunata hai.
    """

    safe_text = (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("$", "\\$")
    )

    components.html(
        f"""
        <script>
        const text = `{safe_text}`;

        function speak() {{
            const speech =
                new SpeechSynthesisUtterance(text);

            speech.lang = "{language}";
            speech.rate = 1;
            speech.pitch = 1.1;

            const voices =
                window.speechSynthesis.getVoices();

            const femaleVoiceNames = [
                "zira", "heera", "hazel", "samantha", "karen",
                "susan", "aria", "jenny", "libby", "sonia",
                "eva", "google uk english female", "google हिन्दी",
                "google hindi"
            ];

            const female = voices.find(v =>
                femaleVoiceNames.some(name =>
                    v.name.toLowerCase().includes(name)
                ) && (
                    v.lang.startsWith("{language}") ||
                    v.lang.startsWith("en") ||
                    v.lang.startsWith("hi")
                )
            ) || voices.find(v =>
                femaleVoiceNames.some(name =>
                    v.name.toLowerCase().includes(name)
                )
            );

            if (!female) {{
                console.warn("No supported female browser voice is available.");
                return;
            }}

            speech.voice = female;
            speech.pitch = 1.25;

            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(speech);
        }}

        if (window.speechSynthesis.getVoices().length) {{
            speak();
        }} else {{
            window.speechSynthesis.onvoiceschanged = speak;
        }}
        </script>
        """,
        height=0
    )