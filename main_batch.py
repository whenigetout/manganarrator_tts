import json
from app.tts_runner import TTSRunner
from app.config import TTSConfig

def main():
    # Load config
    config = TTSConfig()

    # Initialize runner
    runner = TTSRunner(config)

    # Path to OCR output JSON
    ocr_path = "input/ocr_output.pretty.json"  # You can change this

    # Run ID returned from OCR module (used in output folder name)
    ocr_runid = "api_batch_20250730_204035_1182d4e1"  # Adjust to match the folder name

    # Load OCR output
    with open(ocr_path, "r", encoding="utf-8") as f:
        ocr_json = json.load(f)

    # Process batch
    result = runner.process_ocr_result(ocr_json, ocr_runid)

    print("✅ Done.")
    print(f"Output folder: {result['output_folder']}")

if __name__ == "__main__":
    main()
