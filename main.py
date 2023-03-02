import logging
import requests
from telegram import InputFile, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import var

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_query = " ".join(context.args)
    scryfall_api = f"https://api.scryfall.com/cards/search?q={search_query}"
    response = requests.get(scryfall_api)
    if response.status_code == 200:
        data = response.json()
        if data['total_cards'] > 0:
            if data['total_cards'] == 1:
                card = data['data'][0]
                name = card['name']
                price = card.get('prices', {}).get('usd', 'Not Available')
                image_url = card.get('image_uris', {}).get('normal', '')
                legalities = card.get('legalities', {})
                commander_legal = legalities.get('commander', 'Not Available')
                message = f"Card name: {name}\nPrice (USD): {price}\nLegality in Commander: {commander_legal}"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                if image_url:
                    image = requests.get(image_url)
                    if image.status_code == 200:
                        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(image.content))
            else:
                suggestions = [card['name'] for card in data['data']]
                message = "What card did you mean?\n" + '\n'.join(suggestions)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Card not found.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Could not get suggestions.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(var.key).build()

    fetch_handler = CommandHandler('fetch', fetch)
    application.add_handler(fetch_handler)

    application.run_polling()
