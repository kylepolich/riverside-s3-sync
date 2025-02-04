import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv


load_dotenv()
username = os.getenv("username")
password = os.getenv("password")
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
bucket_name = os.getenv("bucket_name")
bucket_prefix = os.getenv("bucket_prefix")

s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


def get_recordings_raw_data(page):
    recording_elements = page.query_selector_all("div[data-automation-class='recordings recording-container']")
    print(f"Found {len(recording_elements)} recording elements.")
    relem = recording_elements[0]
    download_button = relem.query_selector(download_button_selector)
    if download_button:
        download_button.click()
    track_elements = page.query_selector_all("div[data-automation-class='recording track-container']")
    print(f"Found {len(track_elements)} track container elements.")
    downloaded_files = {}  # Dictionary to store speaker name -> BytesIO
    for index, track in enumerate(track_elements, start=1):
        speaker_element = track.query_selector("span[data-automation-class='recording speaker-name']")
        speaker_name = speaker_element.inner_text().strip() if speaker_element else f"track_{index}"
        print(f"Processing track {index} for speaker '{speaker_name}'...")
        high_quality_button = track.query_selector("button:has-text('High quality')")
        if not high_quality_button:
            print(f"Track {index}: 'High quality' button not found.")
            continue
        high_quality_button.click()
        print(f"Track {index}: Clicked 'High quality' button.")
        try:
            raw_audio_option = page.wait_for_selector("text=Raw audio", timeout=1000)
        except Exception:
            print(f"Track {index}: 'Raw audio' option not found. Skipping.")
            continue
        raw_audio_option = page.query_selector("text=Raw audio")
        if not raw_audio_option:
            print(f"Track {index}: 'Raw audio' option not found.")
            continue
        with page.expect_download() as download_info:
            raw_audio_option.click()
            print(f"Track {index}: Clicked 'Raw audio' option.")
        download = download_info.value
        temp_file_path = download.path()
        with open(temp_file_path, "rb") as f:
            data = f.read()
        import io
        buffer = io.BytesIO(data)
        downloaded_files[speaker_name] = buffer
        print(f"Track {index}: Downloaded 'Raw audio' for speaker '{speaker_name}' into memory.")
        page.wait_for_timeout(2000)
    return downloaded_files

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
context = browser.new_context()
page = context.new_page()
page.goto("https://riverside.fm/login")
page.wait_for_selector("input[name='email']")

page.fill("input[name='email']", username)
page.fill("input[name='password']", password)
page.click("button[type='submit']")


i = 0
project_count = 99
while i < project_count:
    page.goto("https://riverside.fm/dashboard/studios/data-skeptic-podcast/projects")
    time.sleep(5)
    project_cards = page.query_selector_all("div[data-testid='project-grid-card']")
    project_count = len(project_cards)
    print(f"Found {project_count} project grid card elements.")
    project_cards[i].click()
    downloaded_files = get_recordings_raw_data(page)
    #
    for name in downloaded_files.keys():
        bytez = downloaded_files[name]
        dest_key = f'{bucket_prefix}/{name}.wav'
        # TODO: save bytez to dest_key via boto3 in bucket_name
        s3_client.upload_fileobj(bytez, bucket_name, dest_key)
    #
    i += 1











