from aiogram import F
from aiogram.types import Message

from engine.async_system import AsyncSystem
from engine.aiogram_system import AiogramSystem


class Bot_DetailsHandlersSystem(AsyncSystem):
    async def on_details(self, message: Message) -> None:
        await message.answer(
            "Сенс боту - надати мешканцям селища можливість дізнатись "
            "нового про своє селище. Він дасть відповідь на питання: "
            "\"А де можна сьогодні погуляти?\", запропонувавши цікаві "
            "та популярні локації, в залежності від Ваших потреб. "
            "Більшість локацій має фото або відео, тому Ви можете "
            "одразу побачити, що Вас там буде чекає. Але якщо фото чи "
            "відео немає, ви все одно зможете дізнатись багато "
            "інформації про локацію, бо до кожної з них йде детальний "
            "опис, історичні факти та рейтинг, завдяки якому Ви "
            "можете швидко дізнатись актуальність локації.\n\n"

            "Також Ви можете допомогти боту, запропонувавши свою "
            "локацію. Вона перевіриться модераторами і буде додана "
            "до списку."
        )

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.on_details, F.text == "Детальніше")
