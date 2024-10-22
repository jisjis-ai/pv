import asyncio
import logging
import random
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont
from colorama import Fore, Style

# Configuração do logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

class TelegramBot:
    def __init__(self, token, channel_id):
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).arbitrary_callback_data(True).build()
        self.channel_id = channel_id
        self.operation_count = 0
        self.button_clicks = {
            "Apostar": 0,
            "Criar Conta": 0
        }
        self.view_count = 0

        # Configurando os handlers
        start_handler = CommandHandler('start', self.start)
        self.application.add_handler(start_handler)

        # Handler para comandos desconhecidos
        unknown_handler = CommandHandler(['start'], self.unknown_command)
        self.application.add_handler(unknown_handler)

    async def start(self, update, context: ContextTypes.DEFAULT_TYPE):
        print(Fore.CYAN + f"Comando recebido: {update.message.text}" + Style.RESET_ALL)

        await context.bot.send_message(
            chat_id=self.channel_id,
            text="Preparem as bancas! As operações vão começar em breve. Fiquem atentos! 🔥"
        )
        self.log_message("Preparem as bancas! As operações vão começar em breve.")

        # Agendar a sequência de operações
        context.job_queue.run_once(self.send_first_image, 10, data=self.channel_id)

    async def unknown_command(self, update, context: ContextTypes.DEFAULT_TYPE):
        print(Fore.RED + f"Comando inválido recebido: {update.message.text}" + Style.RESET_ALL)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Comando não reconhecido. Por favor, use /start para iniciar.")

    async def send_first_image(self, context: ContextTypes.DEFAULT_TYPE):
        image_path = self.generate_image()
        
        # Obter a hora atual e adicionar 2 minutos
        now = datetime.now() + timedelta(minutes=2)
        time_str = now.strftime("%H:%M")  # Formata a hora como HH:MM
        caption = f"Saia antes do resultado abaixo! <b>aposte as: {time_str}:00</b> Prepare-se!"  # Usando HTML

        keyboard = [
            [InlineKeyboardButton("Apostar", url="https://www.megagamelive.com/affiliates/?btag=2059497")],
            [InlineKeyboardButton("Criar Conta", url="https://www.megagamelive.com/affiliates/?btag=2059497")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=context.job.data,
            photo=open(image_path, 'rb'),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'  # Habilitando o HTML
        )

        self.operation_count += 1
        self.log_message(f"Imagem enviada: {image_path}")

        # Agendar a mensagem de resultado após 2 minutos
        context.job_queue.run_once(self.send_result, 180)

    async def send_result(self, context: ContextTypes.DEFAULT_TYPE):
        result_type = random.choice(["success", "failure", "success", "success"])  # Aumenta as chances de sucesso

        if result_type == "success":
            message = "✅✅ Operação bem-sucedida! GREEN! Vamos manter o foco e continuar nas próximas!"
        else:
            if random.random() < 0.1:  # 10% de chance de enviar a mensagem de falha
                message = "❌❌ Saímos perdendo nessa operação. Vamos entrar com força na próxima! Aumentem suas bancas!"
            else:
                return  # Não envia nada se não for a mensagem de falha

        await context.bot.send_message(chat_id=self.channel_id, text=message)
        self.log_message(message)

        # Agendar a próxima imagem após 1 minuto
        context.job_queue.run_once(self.send_next_image, 120, data=self.channel_id)

    async def send_next_image(self, context: ContextTypes.DEFAULT_TYPE):
        image_path = self.generate_image()
        
        # Obter a hora atual e adicionar 2 minutos
        now = datetime.now() + timedelta(minutes=2)
        time_str = now.strftime("%H:%M")  # Formata a hora como HH:MM
        caption = f"Saia antes do resultado abaixo! <b>Hora atual: {time_str}</b> Prepare-se!"  # Usando HTML

        keyboard = [
            [InlineKeyboardButton("Apostar", url="https://www.megagamelive.com/affiliates/?btag=2059497")],
            [InlineKeyboardButton("Criar Conta", url="https://www.megagamelive.com/affiliates/?btag=2059497")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=context.job.data,
            photo=open(image_path, 'rb'),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'  # Habilitando o HTML
        )

        self.operation_count += 1
        self.log_message(f"Imagem enviada: {image_path}")

        context.job_queue.run_once(self.send_result, 120)

    def generate_image(self):
        width, height = 800, 400
        background_color = "black"
        text_color_red = "red"
        text_color_white = "white"

        image = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(image)
        font_large = ImageFont.truetype("arial.ttf", 80)
        font_small = ImageFont.truetype("arial.ttf", 100)

        text_flew_way = "Flew AWAY!"
        random_number = f"{random.uniform(1.00, 6.99):.2f}x"

        draw.text((width/2, height/4), text_flew_way, fill=text_color_red, font=font_large, anchor="ms")
        draw.text((width/2, 3*height/4), random_number, fill=text_color_white, font=font_small, anchor="ms")

        image_path = "flew_way_image.png"
        image.save(image_path)
        return image_path

    def log_message(self, message):
        print(Fore.GREEN + f"Mensagem: {message}" + Style.RESET_ALL)
        print(Fore.CYAN + f"Operações enviadas: {self.operation_count}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Clicks no botão: {self.button_clicks}" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"Visualizações: {self.view_count}" + Style.RESET_ALL)
        print(Fore.RED + f"Ping: {self.get_ping()}" + Style.RESET_ALL)

    def get_ping(self):
        return random.randint(50, 150)  # Simula o ping do bot

    def start_polling(self):
        self.application.run_polling()

if __name__ == '__main__':
    TOKEN = '5847731188:AAF2vTmLyBHvdBYY4LSgJYQFqdbBL5IrSMY'
    CHANNEL_ID = -1002372625511  # ID do canal fornecido
    bot = TelegramBot(token=TOKEN, channel_id=CHANNEL_ID)
    bot.start_polling()
