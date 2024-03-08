import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time

api_id = 20583486
api_hash = '0ed7a019c011e7848c146f9379acde32'
TOKEN = '6148264758:AAHCAU_v3P9SAkCZLPuS6sStZ9Fhbjskp_w'

# Create the Pyrogram client
bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=TOKEN)

# Global variables
token = ""
user_data = {}
user_pic_counts = {}  # Dictionary to store user-wise pic counts
user_settings = {}   # Dictionary to store user settings

# Styles options
styles = [
    "Surrealistic",
    "Pixar Characters",
    "B-W Tattoo",
    "Midjourney",
    "No Style",
    "Magical Portrait",
    "Creepy",
    "Van Gogh",
    "Dark Tarots",
    "Latex",
    "Horoscope",
    "Funkopops",
    "Prophecy",
    "Tattoo Art",
    "Tattooed Love",
    "Portrait Tattoo",
    "Creepy Tattoo",
    "Pixar Couples",
    "Carnivals In Rio",
    "Logo",
    "Spooky Cartoonish",
    "Neon Jungle",
    "Psychedelic Entities",
    "Halloween",
    "Religious Medieval",
    "Magical",
    "Grinchified Celebrities",
    "Cartoon Caricatures",
    "Japanese Tattoo",
    "Realistic Portraits",
    "Epic 3D Anime",
    "GTA Avatar",
    "Forest Characters",
    "Mario Universe",
    "Portrait Character",
    "B-W Marble",
    "Melting Surreal",
    "Fiber Optic",
    "Game Characters",
    "Lego Characters",
    "Car Toon",
    "Vaporwave Photographs",
    "Hyperreality",
    "Colored Tattoo",
    "T-shirt Design",
    "Gothic",
    "Cyberpunk Portrait",
    "Medieval Portrait",
    "Miniature Histories",
    "Cyberpunk",
    "Illustration",
    "Pop Art",
    "Sketch",
    "Futuristic",
    "Realistic Food",
    "Wicked Illustration",
    "Medieval",
    "Fantasy Portrait",
    "Illumination",
    "Dark Fantasy",
    "Photo Realistic",
    "SDXL 1.0",
    "Acrylic Painting",
    "Crazy T-Shirts",
    "Halloween Wallpaper",
    "Elegant Logo",
    "Psychedelic T-shirt Designs",
    "LOTR",
    "Steampunk",
    "Kawaii",
    "Psychedelic",
    "Fine Art",
    "Fantasy",
    "Holographic",
    "Low Poly",
    "Matte Drawing",
    "Seapunk",
    "Pixel Art",
    "Watercolor",
    "Hyper detailed",
    "3D Render",
    "Depth of Field",
    "Dark Comic",
    "Animal Avatar",
    "Egypt Art",
    "Comics",
    "Futurism",
    "Art Nouveau Portrait",
    "Marble",
    "Dark Art",
    "Halloween Costume",
    "Halloween Makeup",
    "Cinematic",
    "Sneakers Design",
    "Tattoos Around Eye",
    "Food Design",
    "Christmas Postcards",
    "Pixar Christmas",
    "Portrait",
    "Realistic Christmas",
    "Nebula Christmas",
]

# Default size and quality
default_size = "square"
default_quality = "default"

# Owner's chat ID (replace with your own chat ID)
owner_chat_id = 5865178079

# Function to create image
async def create_image(chat_id, prompt, style, quality_cfg=11, quality_step=30):
    global token, user_pic_counts, user_settings
    # Get or refresh token
    await get_token()
    if token:
        if chat_id not in user_pic_counts:
            user_pic_counts[chat_id] = 0
        
        # Check if user is the owner and allow unlimited pics
        if chat_id == owner_chat_id:
            pass
        else:
            # Check if user has exceeded the daily limit
            if user_pic_counts[chat_id] >= 6:
                await bot.send_message(chat_id, "You have reached the daily limit for generating pictures.")
                return
        
        aspect_ratio = default_size  # Default aspect ratio
        quality = default_quality  # Default quality

        # Check if user has set size and quality
        if chat_id in user_settings:
            if 'size' in user_settings[chat_id]:
                aspect_ratio = user_settings[chat_id]["size"]
            if 'quality' in user_settings[chat_id]:
                quality = user_settings[chat_id]["quality"]

        # Determine API URL based on quality_cfg
        if quality == "high":
            quality_cfg = 20
            quality_step = 50
        elif quality == "ultra":
            quality_cfg = 100
            quality_step = 100

        url_process = f"https://api.davinci.ai/publisher/v2/process/?prompt={prompt}&aspect={aspect_ratio}&style={style}&cfg={quality_cfg}&seed=2132150324&step={quality_step}&variant=A"

        headers_process = {
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
            "x-platform": "android",
            "x-userid": "a67f835d636d05b27c4dddc29eac00b9",
            "payment": "1",
            "variant": "E",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.12.0"
        }

        response_process = requests.post(url_process, headers=headers_process)
        if response_process.status_code == 200:
            data_process = response_process.json()
            if data_process["success"]:
                process_id = data_process["data"]["id"]
                print(f"Process started with ID: {process_id}")
                print(f"API URL: {url_process}")  # Print API URL after sending the request
                
                # Increment user's pic count
                user_pic_counts[chat_id] += 1

                # Request to check the status and fetch image URLs for 20 seconds
                start_time = time.time()
                while time.time() - start_time < 20:
                    url_status = f"https://api.davinci.ai/result/v2/status?id={process_id}"
                    headers_status = {
                        "islikedoperation": "true",
                        "authorization": f"Bearer {token}",
                        "x-platform": "android",
                        "x-userid": "a67f835d636d05b27c4dddc29eac00b9",
                        "payment": "1",
                        "variant": "E",
                        "accept-encoding": "gzip",
                        "user-agent": "okhttp/4.12.0",
                        "if-none-match": 'W/"165-QzfJRpmlvyFVq5aHXKouZMf6UGU"'
                    }
                    response_status = requests.get(url_status, headers=headers_status)
                    if response_status.status_code == 200:
                        data_status = response_status.json()
                        if data_status["success"] and "url" in data_status["data"]:
                            image_urls = data_status["data"]["url"]
                            if image_urls:
                                for index, image_url in enumerate(image_urls):
                                    await bot.send_photo(chat_id, image_url)
                                    print(f"Image {index + 1} sent successfully.")
                                return
                            else:
                                print("No image URLs found in the response.")
                        else:
                            print("Failed to retrieve image URL.")
                    else:
                        print(f"Failed to retrieve status. Status code: {response_status.status_code}")
                    await asyncio.sleep(1)

                # If no image URLs found within 20 seconds
                await bot.send_message(chat_id, "Failed to retrieve image URL after 20 seconds. Please try again.")
            else:
                print("Failed to start the process.")
        else:
            print(f"Failed to start the process. Status code: {response_process.status_code}")
    else:
        print("Failed to get token.")

# Function to get new token
async def get_token():
    global token
    url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=AIzaSyAHucoGlwj2y6Agj1z71v1zfrS9jYeP0pk"
    headers = {
        "Content-Type": "application/json",
        "X-Android-Package": "com.hubx.imaginatioo",
        "X-Android-Cert": "YOUR_CERT",
        "Accept-Language": "en-IN, en-US",
        "X-Client-Version": "Android/Fallback/X21000005/FirebaseCore-Android",
        "X-Firebase-GMPID": "1:374146794183:android:3cc0425f6b6431066874e2",
        "X-Firebase-Client": "H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-J610F Build/PPR1.180610.011)",
        "Host": "www.googleapis.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = "{}"

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        response_json = response.json()
        token = response_json.get('idToken')
        print("New Token:", token)
    else:
        print("Failed to get token. Response Status Code:", response.status_code)

# Handler to handle '/genpic' command
@bot.on_message(filters.command('genpic'))
async def genpic_command(client, message):
    chat_id = message.chat.id
    user_input = message.text.split(' ', 1)
    
    if len(user_input) > 1:
        prompt = user_input[1]
        user_data[chat_id] = {"prompt": prompt}
        
        # Send styles as inline keyboard
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(style, callback_data=style) for style in styles[i:i+3]
                ] for i in range(0, len(styles), 3)
            ]
        )
        await message.reply("Choose a style:", reply_markup=markup)
    else:
        await message.reply("Please provide a valid prompt with the command.")

# Handler to handle '/changes' command
@bot.on_message(filters.command('changes'))
async def changes_command(client, message):
    chat_id = message.chat.id
    if chat_id == chat_id:
        # Owner settings change page
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("ʜɪɢʜ sǫᴜᴀʀᴇ", callback_data="high square"),
                    InlineKeyboardButton("ʜɪɢʜ ʜᴏʀɪᴢᴏɴᴛᴀʟ", callback_data="high horizontal"),
                    InlineKeyboardButton("ʜɪɢʜ ʜᴏʀɪᴢᴏɴᴛᴀʟ 𝟺.𝟹", callback_data="high horizontal_4_3")
                ],
                [
                    InlineKeyboardButton("ʜɪɢʜ ʜᴏʀɪᴢᴏɴᴛᴀʟ 𝟷𝟼.𝟿", callback_data="high horizontal_16_9"),
                    InlineKeyboardButton("ʜɪɢʜ ᴠᴇʀᴛɪᴄᴀʟ 𝟹.𝟺", callback_data="high vertical_3_4"),
                    InlineKeyboardButton("ʜɪɢʜ ᴠᴇʀᴛɪᴄᴀʟ 𝟿.𝟷𝟼", callback_data="high vertical_9_16")
                ],
                [
                    InlineKeyboardButton("ᴜʟᴛʀᴀ sǫᴜᴀʀᴇ", callback_data="ultra square"),
                    InlineKeyboardButton("ᴜʟᴛʀᴀ ʜᴏʀɪᴢᴏɴᴛᴀʟ", callback_data="ultra horizontal"),
                    InlineKeyboardButton("ᴜʟᴛʀᴀ ʜᴏʀɪᴢᴏɴᴛᴀʟ 𝟺.𝟹", callback_data="ultra horizontal_4_3")
                ],
                [
                    InlineKeyboardButton("ᴜʟᴛʀᴀ ʜᴏʀɪᴢᴏɴᴛᴀʟ 𝟷𝟼.𝟿", callback_data="ultra horizontal_16_9"),
                    InlineKeyboardButton("ᴜʟᴛʀᴀ ᴠᴇʀᴛɪᴄᴀʟ 𝟹.𝟺", callback_data="ultra vertical_3_4"),
                    InlineKeyboardButton("ᴜʟᴛʀᴀ ᴠᴇʀᴛɪᴄᴀʟ 𝟿.𝟷𝟼", callback_data="ultra vertical_9_16")
                ],
                [
                    InlineKeyboardButton("sᴇᴛ ᴛᴏ ᴅᴇғᴀᴜʟᴛ", callback_data="set_default")
                ]
            ]
        )
        await message.reply("~          𝗖𝗛𝗢𝗢𝗦𝗘 𝗔 𝗤𝗨𝗔𝗟𝗜𝗧𝗬 & 𝗦𝗜𝗭𝗘           ~", reply_markup=markup)
    else:
        await message.reply("𝗯𝗵𝗮𝗴")

# Handler to handle inline keyboard button clicks for '/genpic' command
@bot.on_callback_query()
async def genpic_callback_handler(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    
    if data in styles:  # Check if the clicked button data is a valid style
        prompt = user_data[chat_id]["prompt"]
        
        # Delete the style buttons
        await bot.delete_messages(chat_id, callback_query.message.id)
        
        # Send "YOUR PIC IS GENERATING" message
        sent_message = await bot.send_message(chat_id, "🖌ʏᴏᴜʀ ᴘɪᴄ ɪs ɢᴇɴᴇʀᴀᴛɪɴɢ...")
        
        # Create the image
        await create_image(chat_id, prompt, data)
        
        # Delete the "YOUR PIC IS GENERATING" message
        await sent_message.delete()
        
    elif data.startswith("high") or data.startswith("ultra"):
        quality = data.split()[0]
        size = data.split()[1]
        user_settings[chat_id] = {"quality": quality, "size": size}
        
        # Send confirmation message for quality and size settings
        rent_message = await bot.send_message(chat_id, f"ʏᴏᴜʀ sɪᴢᴇ ᴀɴᴅ ǫᴜᴀʟɪᴛʏ sᴇᴛ ᴛᴏ ~ {size} {quality}.")
        
        # Delete the confirmation message after a brief delay
        await asyncio.sleep(1)
        await rent_message.delete()
        
        # Delete the inline keyboard message
        await bot.delete_messages(chat_id, callback_query.message.id)
    
    elif data == "set_default":
        user_settings[chat_id] = {"quality": default_quality, "size": default_size}
        
        # Send confirmation message for default settings
        rent_message = await bot.send_message(chat_id, "ᴅᴇғᴀᴜʟᴛ")
        
        # Delete the confirmation message after a brief delay
        await asyncio.sleep(0)
        await rent_message.delete()
        
        # Delete the inline keyboard message
        await bot.delete_messages(chat_id, callback_query.message.id)

# Start the bot
bot.run()
