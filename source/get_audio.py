# credit https://github.com/oscie57/tiktok-voice?tab=readme-ov-file
import requests, textwrap, os, base64, re
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = f"https://api16-normal-c-useast2a.tiktokv.com/media/api/text/speech/invoke/"
USER_AGENT = f"com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)"
SESSION_ID = os.getenv('TIKTOK_SESSION_ID')
req_text = open('input_text.txt', 'r').read()

# 'en_us_006',                  # English US - Male 1
# 'en_us_007',                  # English US - Male 2
# 'en_us_009',                  # English US - Male 3
# 'en_us_010',                  # English US - Male 4
# 'en_male_narration'           # narrator
# 'en_male_funny'               # wacky
# 'en_female_emotional'         # peaceful

# divide textx in by 200 chars chunks
chunk_size = 200
textlist = textwrap.wrap(req_text, width=chunk_size, break_long_words=True, break_on_hyphens=False)

batch_dir = os.path.join(os.getcwd(), 'media', 'temp')

# call the api
for i, item in enumerate(textlist):

    item = req_text.replace("+", "plus")
    item = req_text.replace(" ", "+")
    item = req_text.replace("&", "and")
    item = req_text.replace("ä", "ae")
    item = req_text.replace("ö", "oe")
    item = req_text.replace("ü", "ue")
    item = req_text.replace("ß", "ss")

    r = requests.post(
        f"{API_BASE_URL}?text_speaker={'en_us_006'}&req_text={item}&speaker_map_type=0&aid=1233",
        headers={
            'User-Agent': USER_AGENT,
            'Cookie': f'sessionid={SESSION_ID}'
        }
    )

    filename = f'{batch_dir}{i}.mp3'


    if r.json()["message"] == "Couldn't load speech. Try again.":
        raise Exception('Invalid session ID')
    
    vstr = [r.json()["data"]["v_str"]][0]
    b64d = base64.b64decode(vstr)
    with open(filename, "wb") as out:
        out.write(b64d)


def batch_create(filename: str = 'voice.mp3'):
    out = open(filename, 'wb')

    def sorted_alphanumeric(data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(data, key=alphanum_key)

    for item in sorted_alphanumeric(os.listdir('./batch/')):
        filestuff = open('./batch/' + item, 'rb').read()
        out.write(filestuff)

    out.close()


    batch_create(filename)
