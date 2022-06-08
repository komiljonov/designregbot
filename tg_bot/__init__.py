from ast import parse
from telegram import *
from telegram.ext import *
from bot.models import Post, Region, User

from utils import distribute


from .constants import *

NAME, NUMBER, REGION = range(3)

class Bot(Updater):
    def __init__(self):
        super().__init__(TOKEN)
        not_start = ~Filters.regex("^/start")

        self.dispatcher.add_handler(
            ConversationHandler(
                [
                    CommandHandler('start', self.start)
                ],
                {
                    NAME: [
                        MessageHandler(Filters.text & not_start, self.name)
                    ],
                    NUMBER: [
                        MessageHandler(Filters.contact & not_start, self.number)
                    ],
                    REGION: [
                        MessageHandler(Filters.text & not_start, self.region)
                    ]

                },
                [
                    CommandHandler('start', self.start)
                ]
            )
        )
        print("salom")

        self.start_polling()
        self.idle()
    
    def delete_old_message(self, context:CallbackContext):
        if 'old_message' in context.user_data:
            try:
                context.user_data['old_message'].delete()
            except:
                pass
            del context.user_data['old_message']
        


    def start(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        dbuser = User.objects.filter(chat_id=user.id).first()
        if not dbuser:
            context.user_data['register'] = {
                "chat_id": user.id
            }
            self.delete_old_message(context)
            
            context.user_data['old_message'] = user.send_message("<b>Iltimos ism va familyangizni yuboring!</b>", parse_mode="HTML",)
            return NAME
        else:
            user.send_message("<b>Siz ro'yxatdan o'tib bo'lgansiz!</b>", parse_mode="HTML")
            return ConversationHandler.END
    

    def name(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        context.user_data["register"]['name'] = update.message.text
        self.delete_old_message(context)
        update.message.delete()
        context.user_data['old_message'] = user.send_message("<b>Iltimos telefon raqamingizni yuboring!</b>", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton("Raqamni yuborish", request_contact=True)
                ]
            ], resize_keyboard=True
        ))

        return NUMBER
    
    def number(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        context.user_data["register"]['number'] = update.message.contact.phone_number
        self.delete_old_message(context)
        update.message.delete()
        context.user_data['old_message'] = user.send_message("<b>Iltimos viloyatingizni tanlang!</b>", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(
            distribute(
                [region.name for region in Region.objects.all()],
                2
            ),resize_keyboard=True
        ))
        return REGION
    
    def region(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        # context.user_data['region'] = update.message.text
        # user.send_message("Iltimos telefon raqamingizni yozing!")
        # return NUMBER

        region = Region.objects.filter(name=update.message.text).first()
        if region:
            User.objects.create(**context.user_data['register'], region=region)
            self.delete_old_message(context)
            update.message.delete()
            context.user_data['old_message'] = user.send_message("<b>Muvaffaqiyatli ro'yxatdan o'tildi!</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
            post: Post = Post.objects.first()
            if post:
                if post.mediatype == 0:
                    user.send_message(post.com, parse_mode="HTML")
                elif post.mediatype == 1:
                    user.send_photo(post.file, caption=post.com, parse_mode="HTML")
                elif post.mediatype == 2:
                    user.send_video(post.file, caption=post.com, parse_mode="HTML")
                
            
        else:
            self.delete_old_message(context)
            update.message.delete()
            context.user_data['old_message'] = user.send_message("<b>Region not found!</b>", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(
            distribute(
                Region.objects.all(),
                2
            )
        ))
        return ConversationHandler.END
