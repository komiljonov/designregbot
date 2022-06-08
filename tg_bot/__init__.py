from ast import parse
from telegram import *
from telegram.ext import *
from bot.models import Post, Region, User

from utils import distribute


from .constants import *

NAME, NUMBER, REGION, POST_MEDIA, POST_TEXT, POST_CONFIRM = range(6)

class Bot(Updater):
    def __init__(self):
        super().__init__(TOKEN)
        not_start = ~Filters.regex("^/start")

        self.dispatcher.add_handler(
            ConversationHandler(
                [
                    CommandHandler('start', self.start),
                    CommandHandler("post", self.post)
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
                    ],
                    POST_MEDIA: [
                        MessageHandler(Filters.photo, self.post_media_photo),
                        MessageHandler(Filters.video, self.post_media_video),
                        MessageHandler(Filters.document, self.post_media_document)
                    ],
                    POST_TEXT: [
                        MessageHandler(Filters.text & not_start, self.post_text)
                    ],
                    POST_CONFIRM: [
                        CallbackQueryHandler(self.post_confirm, pattern="post_confirm"),
                        CallbackQueryHandler(self.post, pattern="post_retry")
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
            
            context.user_data['old_message'] = user.send_message("<b>Iltimos ismingizni yozing!</b>", parse_mode="HTML",)
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
        context.user_data['old_message'] = user.send_message("<b>Iltimos joylashgan shahar nomeringizni yozing!</b>", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(
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



    def post(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        context.user_data['post'] = {}
        user.send_message("Iltimos post uchun fayl yuboring!", reply_markup=ReplyKeyboardRemove())
        return POST_MEDIA
    
    def post_media_photo(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        context.user_data['post']['mediatype'] = 1
        context.user_data['post']['file'] = update.message.photo[-1]
        user.send_message("Iltimos post uchun matn yuboring!", reply_markup=ReplyKeyboardRemove())
        return POST_TEXT
    
    def post_media_video(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        context.user_data['post']['mediatype'] = 2
        context.user_data['post']['file'] = update.message.video
        user.send_message("Iltimos post uchun matn yuboring!", reply_markup=ReplyKeyboardRemove())
        return POST_TEXT
    
    def post_media_document(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        context.user_data['post']['mediatype'] = 3
        context.user_data['post']['file'] = update.message.document
        user.send_message("Iltimos post uchun matn yuboring!", reply_markup=ReplyKeyboardRemove())
        return POST_TEXT
    
    def post_text(self, update:Update, context:CallbackContext):
        user = update.message.from_user
        context.user_data['post']['com'] = update.message.text
        context.user_data['post']['entities'] = update.message.entities
        user.send_message("Postingiz tayyor iltimos tekshirib tasdiqlang!", reply_markup=ReplyKeyboardRemove())

        if context.user_data['post']['mediatype'] == 1:
            user.send_photo(context.user_data['post']['file'], caption=context.user_data['post']['com'], caption_entities=context.user_data['post']['entities'], reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Tasdiqlash", callback_data="post_confirm"), InlineKeyboardButton("Qayta yozish", callback_data="post_retry")
                    ]
                ]
            ))
        elif context.user_data['post']['mediatype'] == 2:
            user.send_video(context.user_data['post']['file'], caption=context.user_data['post']['com'], caption_entities=context.user_data['post']['entities'], reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Tasdiqlash", callback_data="post_confirm"), InlineKeyboardButton("Qayta yozish", callback_data="post_retry")
                    ]
                ]
            ))
        elif context.user_data['post']['mediatype'] == 3:
            user.send_document(context.user_data['post']['file'], caption=context.user_data['post']['com'], caption_entities=context.user_data['post']['entities'], reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Tasdiqlash", callback_data="post_confirm"), InlineKeyboardButton("Qayta yozish", callback_data="post_retry")
                    ]
                ]
            ))
        else:
            user.send_message(context.user_data['post']['com'], entities=context.user_data['post']['entities'], reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Tasdiqlash", callback_data="post_confirm"), InlineKeyboardButton("Qayta yozish", callback_data="post_retry")
                    ]
                ]
            ))
        
        return POST_CONFIRM
    
    def post_confirm(self, update:Update, context:CallbackContext):
        admin = update.callback_query.from_user
        unsent_users = []
        sent_users = []
        for user in User.objects.all():
            try:
                if context.user_data['post']['mediatype'] == 1:
                    self.bot.send_photo(chat_id=user.chat_id,photo=context.user_data['post']['file'], caption=context.user_data['post']['com'], caption_entities=context.user_data['post']['entities'], reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("Tasdiqlash", callback_data="post_confirm"), InlineKeyboardButton("Qayta yozish", callback_data="post_retry")
                            ]
                        ]
                    ))
                elif context.user_data['post']['mediatype'] == 2:
                    self.bot.send_video(chat_id=user.chat_id,video=context.user_data['post']['file'], caption=context.user_data['post']['com'], caption_entities=context.user_data['post']['entities'], reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("Tasdiqlash", callback_data="post_confirm"), InlineKeyboardButton("Qayta yozish", callback_data="post_retry")
                            ]
                        ]
                    ))
                elif context.user_data['post']['mediatype'] == 3:
                    self.bot.send_document(chat_id=user.chat_id,document=context.user_data['post']['file'], caption=context.user_data['post']['com'], caption_entities=context.user_data['post']['entities'], reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("Tasdiqlash", callback_data="post_confirm"), InlineKeyboardButton("Qayta yozish", callback_data="post_retry")
                            ]
                        ]
                    ))
                else:
                    self.bot.send_message(chat_id=user.chat_id,text=context.user_data['post']['com'], entities=context.user_data['post']['entities'], reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("Tasdiqlash", callback_data="post_confirm"), InlineKeyboardButton("Qayta yozish", callback_data="post_retry")
                            ]
                        ]
                    ))
                sent_users.append(user)
            except:
                unsent_users.append(user)


        admin.send_message("Foydalanuvchilar {} ta.\nPost {} ta odamga yuborildi.\nPostni {} ta odamga yuborib bo'lmadi!".format( len(sent_users) + len(unsent_users), len(sent_users), len(unsent_users) )  )
        return ConversationHandler.END