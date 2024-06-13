from aiogram import F, types

from app.handlers.router import router
import app.keyboards as kb

from aiogram.enums.parse_mode import ParseMode

@router.message(F.text == 'Информация')
async def products_keyboard_command(message: types.Message):
    text = 'Выберите интересующий Вас пункт меню'
    await message.answer(text, reply_markup=kb.info)


@router.message(F.text == 'Ваш идентификатор')
async def products_keyboard_command(message: types.Message):
    text = f'Ваш идентификатор: <b>{message.from_user.id}</b>'
    await message.answer(text, reply_markup=kb.orders)
    
def info_text():
    text = '''Добро пожаловать в наш магазин электроники КупиПК! У нас вы найдете широкий ассортимент компьютерных комплектующих, периферийных устройств и других электронных товаров по привлекательным ценам.

Для покупок и отслеживания заказов воспользуйтесь этим ботом. 

Если вам требуется дополнительная информация о взаимодействии с ботом, нажмите на клавиатуре "Информация -> Взаимодействие с ботом", где вы найдете подробные инструкции.

Мы стремимся предоставить вам наилучший сервис и качественные товары. Ждем ваших заказов!'''
    return text

@router.message(F.text == 'О нас')
async def products_keyboard_command(message: types.Message):
    await message.answer(info_text(), reply_markup=kb.info)
    
@router.message(F.text == 'Взаимодействие с ботом')
async def products_keyboard_command(message: types.Message):
    text = 'С помощью данного бота Вы можете совершать покупки в магазине КупиПК.\n'
    text += 'Для взаимодействия с ботом необходимо воспользоваться клавиатурой со списком команд.\n\n'
    
    text += 'Подменю "<b>Товары</b>"\n'
    text += 'Данное меню содержит следующие команды: <i>Каталог</i>, <i>Скидки</i>, <i>Поиск товара</i>, <i>Корзина</i>.\n\n'
    
    text += '<i>Каталог</i>\n'
    text += 'В открывшемся сообщении представлен список категорий в виде кнопок.\n'
    text += 'После выбора категории открывается список товаров в ней.\n'
    text += 'Список содержит краткую информацию о товаре:\n'
    text += 'Номер. [артикул] название - цена.\n'
    text += 'Для выбора товара необходимо нажать на кнопку под сообщением с соответсвующим номером.\n'
    text += 'После открытия товара открывается информация о нем. При необходимости, возможно добавить его в корзину, нажав соответсвующую кнопку.\n\n'
    
    text += '<i>Скидки</i>\n'
    text += 'Данная команда аналогична команде <i>Каталог</i> с той разницей, что отображаются только те товары и категории, на которые предоставлена скидка.\n\n'
    
    text += '<i>Поиск товара</i>\n'
    text += 'После выбора данной команды необходимо ввести название товара в строку сообщения.'
    text += 'После отправки будут выведены найденные товары в формате, аналогичном предыдущим командам.\n\n'
    
    text += '<i>Корзина</i>\n'
    text += 'Выводит список товаров в вашей корзине. Содержит информацию: артикул, название, стоимость единицы, количество, общая стоимость.'
    text += 'При необходимости редактирования, необходимо выбрать товар, нажав на кнопку под сообщением с соотвествующим номером.\n'
    text += 'В открывшемся меню можно увидеть аналогичную информацию о выбранном товаре, с возможностью изменения количества и удаления товара из корзины.\n'
    text += 'После проверки корзины, возможно перейти к оформлению товара, выбрав соответсвующую кнопку под сообщением\n'
    text += 'Необходимо выбрать желаемый пункт выдачи из предложенных.\n'
    text += 'После выбора - заказ будет создан.\n'
    text += 'Корзина может содержать не более 8 наименований товаров.\n\n'
    
    text += 'Подменю "<b>Заказы</b>"\n'
    text += 'Данное меню содержит следующие команды: <i>Текущие заказы</i>, <i>История заказов</i>, <i>Ваш идентификатор</i>.\n\n'
    
    text += '<i>Текущие заказы</i>\n'
    text += 'В открывшемся сообщении представлен список ваших текущих заказов с возможностью открытия подробной информации.\n'
    text += 'Текущим заказом является созданный Вами заказ, который еще не получен и не отменён.т\n'
    text += 'Подробная ифнормация содержит список товаров в заказе, в формате, подобном меню <i>Корзина</i>.\n'
    text += 'При необходимости, возможно отменить данный заказ, выбрав соответсвующую кнопку под сообщением с подробной информацией.\n\n'
    
    text += '<i>История заказов</i>\n'
    text += 'В открывшемся сообщении представлена история ваших заказов с возможностью открытия подробной информации.\n'
    text += 'В истории содержаться заказы, которые уже были получены, или отменены.\n\n'
    
    text += '<i>Ваш идентификатор</i>\n'
    text += 'Данная команда отображает Ваш уникальный идентификатор, необходимый для подтверждения получателя заказа.\n\n'
    
    text += 'Подменю "<b>Информация</b>"\n'
    text += 'Данное меню содержит следующие команды: <i>О нас</i>, <i>Пункты выдачи</i>, <i>Взаимодействие с ботом</i>.\n\n'
    
    text += '<i>О нас</i>\n'
    text += 'Данная команда отображает информацию о нашем магазине.\n\n'
    
    text += '<i>Пункты выдачи</i>\n'
    text += 'Данная команда отображает список пунктов выдачи с информацией о адресе и дополнительной информации о нём.\n\n'
    
    text += '<i>Взаимодействие с ботом</i>\n'
    text += 'Данная команда отображает информацию о способах взаимодействия с данным ботом.\n\n'
    
    text += 'Команда "<b>Уведомления</b>"\n'
    text += 'Данная команда отображает информацию о включенных уведомлениях с возможностью их отключения.\n'
    text += 'Уведомления о заказах: если активны - Вы будете получать уведомления о готовности получения ваших заказов.\n'
    text += 'Уведомления о новостях: если активны - Вы будете получать наши новостные рассылки, содержащие полезную информацию.\n'

    
    await message.answer(text, parse_mode=ParseMode.HTML)
    
# @router.message(F.text == 'Пункты выдачи')
# async def products_keyboard_command(message: types.Message):
#     text = 'Выберите интересующий Вас пункт меню'
#     await message.answer(text, reply_markup=kb.info)