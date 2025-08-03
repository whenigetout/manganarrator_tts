# main.py

from app.config import TTSConfig
from app.tts_runner import TTSRunner
from pathlib import Path

if __name__ == "__main__":
    # Sample input
    test_text = prompt = '''
I’m trying to focus.  
Really, I am.

The screen in front of me is still glowing. My hand’s on the mouse.  
But he’s here. Beneath the desk. And I know exactly what he’s doing.

> “You’re supposed to let me work,” I murmur, barely moving my lips.

No response, of course. Just a soft exhale — warm against the skin of my belly.  
I feel fingers gently sliding up, gathering the folds of my pallu, pushing it out of the way like it’s in his way.  
Like he owns the right to uncover me.

And I just… let him.
'''
    test_gender = "female"
    test_emotion = "aroused"
    speaker_id = "default"  # Optional
    run_id = "test_run"

    # Load config and runner
    config = TTSConfig()
    runner = TTSRunner(config)

    # Run generation
    result = runner.generate_line(
        text=test_text,
        gender=test_gender,
        emotion=test_emotion,
        speaker_id=speaker_id,
        run_id=run_id
    )

    print("\n✅ Audio generated:")
    for k, v in result.items():
        print(f"{k}: {v}")
