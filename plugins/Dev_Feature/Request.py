# This code has been modified by @Safaridev
# Please do not remove this credit

from fuzzywuzzy import process
from imdb import IMDb
from utils import temp
from info import REQ_CHANNEL, GRP_LNK
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import get_search_results, get_all_files

imdb = IMDb()

async def ai_spell_check(chat_id, wrong_name):
    try:
        async def search_movie(wrong_name):
            search_results = imdb.search_movie(wrong_name)
            movie_list = [movie['title'] for movie in search_results]
            return movie_list

        movie_list = await search_movie(wrong_name)

        if not movie_list:
            return None

        for _ in range(5):
            closest_match = process.extractOne(wrong_name, movie_list)

            if not closest_match or closest_match[1] <= 80:
                return None

            movie = closest_match[0]
            files, offset, total_results = await get_search_results(chat_id=chat_id, query=movie)

            if files:
                return movie

            movie_list.remove(movie)

        return None

    except Exception as e:
        print(f"Error in ai_spell_check: {e}")
        return None


@Client.on_message(filters.command(["request", "Request"]) & filters.private | filters.regex("#request") | filters.regex("#Request"))
async def requests(client, message):
    search = message.text
    requested_movie = search.replace("/request", "").replace("/Request", "").strip()
    user_id = message.from_user.id

    if not requested_movie:
        await message.reply_text("🙅 To request a movie, please enter the movie name along with the year, like this 👇\n<code>/request Pushpa 2021</code>")
        return

    files, offset, total_results = await get_search_results(chat_id=message.chat.id, query=requested_movie)

    if files:
        file_name = files[0]['file_name']
        await message.reply_text(f"🎥 {file_name}\n\nThe movie you requested is available in the group.\n\nGroup Link = {GRP_LNK}")
    else:
        closest_movie = await ai_spell_check(chat_id=message.chat.id, wrong_name=requested_movie)
        if closest_movie:
            files, offset, total_results = await get_search_results(chat_id=message.chat.id, query=closest_movie)
            if files:
                file_name = files[0]['file_name']
                await message.reply_text(f"🎥 {file_name}\n\nThe movie you requested is available in the group.\n\nGroup Link = {GRP_LNK}")
            else:
                await message.reply_text(f"✅ Your movie <b>{closest_movie}</b> has been sent to our admin.\n\n🚀 We'll message you as soon as the movie is uploaded.\n\n📌 Note - Admins may be busy, so uploading may take some time.")
                await client.send_message(
                    REQ_CHANNEL,
                    f"☏ #REQUESTED_CONTENT ☎︎\n\nBot - {temp.B_NAME}\nName - {message.from_user.mention} (<code>{message.from_user.id}</code>)\nRequest - <code>{closest_movie}</code>",
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton('Not Released 📅', callback_data=f"not_release:{user_id}:{requested_movie}"),
                            InlineKeyboardButton('Not Available 🙅', callback_data=f"not_available:{user_id}:{requested_movie}")
                        ],[
                            InlineKeyboardButton('Uploaded ✅', callback_data=f"uploaded:{user_id}:{requested_movie}")
                        ],[
                            InlineKeyboardButton('Invalid Format 🙅', callback_data=f"series:{user_id}:{requested_movie}"),
                            InlineKeyboardButton('Spelling Mistake ✍️', callback_data=f"spelling_error:{user_id}:{requested_movie}")
                        ],[
                            InlineKeyboardButton('⦉ Close ⦊', callback_data=f"close_data")]
                        ])
                )
        else:
            await message.reply_text(f"✅ Your movie <b>{requested_movie}</b> has been sent to our admin.\n\n🚀 We'll message you as soon as the movie is uploaded.\n\n📌 Note - Admins may be busy, so uploading may take some time.")
            await client.send_message(
                REQ_CHANNEL,
                f"📝 #REQUESTED_CONTENT 📝\n\nBot - {temp.B_NAME}\nName - {message.from_user.mention} (<code>{message.from_user.id}</code>)\nRequest - <code>{requested_movie}</code>",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton('Not Released 📅', callback_data=f"not_release:{user_id}:{requested_movie}"),
                        InlineKeyboardButton('Not Available 🙅', callback_data=f"not_available:{user_id}:{requested_movie}")
                    ],[
                        InlineKeyboardButton('Uploaded ✅', callback_data=f"uploaded:{user_id}:{requested_movie}")
                    ],[
                        InlineKeyboardButton('Invalid Format 🙅', callback_data=f"series:{user_id}:{requested_movie}"),
                        InlineKeyboardButton('Spelling Mistake ✍️', callback_data=f"spelling_error:{user_id}:{requested_movie}")
                    ],[
                        InlineKeyboardButton('⦉ Close ⦊', callback_data=f"close_data")]
                    ])
            )
