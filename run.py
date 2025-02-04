import os
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


playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
context = browser.new_context()
page = context.new_page()
page.goto("https://riverside.fm/login")
page.wait_for_selector("input[name='email']")

page.fill("input[name='email']", username)
page.fill("input[name='password']", password)
page.click("button[type='submit']")

page.goto("https://riverside.fm/dashboard/studios/data-skeptic-podcast/projects")

# Allow time for the page to fully load
time.sleep(1)

html_content = page.content()

project_cards = page.query_selector_all("div[data-testid='project-grid-card']")
print(f"Found {len(project_cards)} project grid card elements.")


i = 0
project_cards[i].click()

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

for name in downloaded_files.keys():
    bytez = downloaded_files[name]
    dest_key = f'{bucket_prefix}/{name}.wav'
    # TODO: save bytez to dest_key via boto3 in bucket_name
    s3_client.upload_fileobj(bytez, bucket_name, dest_key)



for index, track in enumerate(track_elements, start=1):
    print(f"Processing track {index}...")
    # Find the "High quality" button within the current track container
    high_quality_button = track.query_selector("button:has-text('High quality')")
    if not high_quality_button:
        print(f"Track {index}: 'High quality' button not found.")
        continue
    # Click the "High quality" button to reveal download options
    high_quality_button.click()
    print(f"Track {index}: Clicked 'High quality' button.")
    # Wait for the popover to show the "Raw audio" option
    try:
        raw_audio_option = page.wait_for_selector("text=Raw audio", timeout=1000)
    except Exception:
        print(f"Track {index}: 'Raw audio' option not found. Skipping.")
        continue
    raw_audio_option = page.query_selector("text=Raw audio")
    if not raw_audio_option:
        print(f"Track {index}: 'Raw audio' option not found.")
        continue
    # Listen for a download event (if clicking triggers a download)
    with page.expect_download() as download_info:
        raw_audio_option.click()
        print(f"Track {index}: Clicked 'Raw audio' option.")
    download = download_info.value
    # Optionally, save the download to a file (you can choose the path and filename)
    download_path = f"track_{index}_raw_audio.mp3"  # adjust extension if needed
    download.save_as(download_path)
    print(f"Track {index}: Downloaded 'Raw audio' to {download_path}.")
    # Optionally wait a little before processing the next track
    page.wait_for_timeout(2000)










download_button_selector = "button:has-text('Recording Files')"

for i, recording in enumerate(recording_elements, start=1):
    # Try to find the download button within the current recording element
    download_button = recording.query_selector(download_button_selector)
    if download_button:
        download_button.click()
        print(f"Clicked download button for recording {i}.")
        # Optionally wait a bit between clicks if necessary
        page.wait_for_timeout(1000)
    else:
        print(f"Download button not found for recording {i}.")




page.go_back()











prefix = "https://riverside.fm/dashboard/studios/data-skeptic-podcast/projects/"

link_elements = page.query_selector_all("a")

for link in link_elements:
    print(link.get_attribute("href"))

matching_links = [
    link.get_attribute("href")
    for link in link_elements
    if link.get_attribute("href") and link.get_attribute("href").startswith(prefix)
]

print("Found links:")
for href in matching_links:
    print(href)




# Save the page content to temp.html
with open("temp.html", "w", encoding="utf-8") as f:
    f.write(page.content())

print("Page saved to temp.html")
browser.close()
