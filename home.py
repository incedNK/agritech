from nicegui import ui, app, APIRouter, events
from typing import Optional
from fastapi.responses import  RedirectResponse
from PIL import Image
import config
import models
import theme
import asyncio
import os
from datetime import datetime
import shutil


home_router = APIRouter()

''' Basic login routes -- should be kept for other projects as well '''
@home_router.page('/login')
def login_page() -> Optional[RedirectResponse]:
        def try_login()->None:
            db_user = models.session.query(models.User).filter(models.User.username == username.value).first()
            if not db_user:
                username.value = ''
                password.value = ''
                ui.notify('Wrong username or password', position='top', color='negative')
            if not config.verify_password(plain_password=password.value, hashed_password=db_user.hashed_password):    
                username.value = ''
                password.value = ''
                ui.notify('Wrong username or password', position='top', color='negative')
            else:
                access_token = config.create_access_token(data={"sub": db_user.username})
                app.storage.user.update({'username': username.value, 'auth_token': access_token})
                ui.navigate.to(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go

        if app.storage.user.get('auth_token', None):
            return RedirectResponse('/')
        
        def send_secret_key():
            db_user = models.session.query(models.User).filter(models.User.username == username.value).first()
            if db_user:   
                config.send_key_to_mail(db_email=db_user.username, key=db_user.secret)
        
        ui.query('.nicegui-content').classes('p-0')
        with theme.home_frame():
            with ui.image('static/images/background.jpg').props('no-spinner').classes('w-full h-screen md:h-[735px]'):     
                with ui.card().classes('xl:w-2/6 absolute-center bg-white justify-between'):
                    with ui.grid(columns=2).classes('justify-between w-full p-1 mb-2'):
                        ui.label('Welcome to AGTech').classes('font-bold text-black xl:text-4xl')
                        ui.image('static/logos/logo.png').classes('xl:w-[160px] xl:h-[81px] justify-self-end')
                    with ui.column().classes('w-full p-1 rounded-lg border-2 bg-white mb-2'):
                        ui.label('Username').classes('text-black font-bold')
                        username = ui.input(placeholder='Username').props('rounded-lg outlined dense').classes('w-full').on('keydown.enter', try_login)
                        ui.label('Password').classes('text-black font-bold')
                        password = ui.input(placeholder='************', password=True, 
                            password_toggle_button=True).props('rounded-lg outlined dense').classes('w-full').on('keydown.enter', 
                                                                        try_login)
                    ui.link('Forgot your password?', '/reset_password').classes('text-[#A162F7] self-end').on('click',
                                                                        send_secret_key)
                    ui.button('Sign in', color='#4C4C4C', on_click=try_login).props('no-caps').classes('w-full')

@home_router.page('/reset_password')
def reset_page() -> Optional[RedirectResponse]:
        def change_password():
            user = models.session.query(models.User).filter(models.User.secret == email_code)
            if not user.first():
                ui.notify('Wrong code - try again', position='top', color='negative')
            else:
                new_data = {'secret': config.generate_secret(), 'hashed_password': config.get_hashed_password(password=password.value)}
                user.update(new_data)
                models.session.commit()
            ui.notify('Success', position='top', color='positive')
            return RedirectResponse('/login')
        
        ui.query('.nicegui-content').classes('p-0')    
        with theme.home_frame():
            with ui.image('static/images/background.jpg').props('no-spinner').classes('w-full h-screen md:h-[735px]'):     
                with ui.card().classes('xl:w-2/6 absolute-center bg-white justify-between'):
                    with ui.grid(columns=2).classes('justify-between w-full p-2 mb-2'):
                        ui.label('Welcome to AGTech').classes('font-bold text-black xl:text-4xl')
                        ui.image('static/logos/logo.png').classes('xl:w-[160px] xl:h-[81px] justify-self-end')
                    ui.label('We sent you email with your secret code to reset password...').classes('text-[#A162F7] font-bold')
                    with ui.column().classes('w-full p-4 rounded-lg border-2 bg-white mb-2'):
                        ui.label('Secret email code').classes('text-black font-bold')
                        email_code = ui.input(placeholder='Secret code').props('rounded-lg outlined dense').classes('w-full').on(
                            'keydown.enter', change_password)
                        ui.label('Password').classes('text-black font-bold')
                        password1 = ui.input(placeholder='************', password=True, 
                            password_toggle_button=True).props('rounded-lg outlined dense').classes('w-full').on('keydown.enter', 
                                                                        change_password)
                        ui.label('Confirm password').classes('text-black font-bold')
                        password2 = ui.input(placeholder='************', password=True, 
                            password_toggle_button=True).props('rounded-lg outlined dense').classes('w-full').on('keydown.enter', 
                                                                        change_password)
                        if password1==password2:
                            password = password1
                    ui.button('Reset password', color='#4C4C4C', on_click=change_password).props('no-caps').classes('w-full')        


@home_router.page('/bug_trap')
def bug_trap():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    
    ui.query('.nicegui-content').classes('p-0')
    with theme.home_frame():
        with ui.image('static/images/background.jpg'):     
            with ui.card().classes('xl:w-2/6 h-3/6 absolute-center bg-white justify-around'):
                with ui.grid(columns=2).classes('justify-between w-full p-1 mb-2'):
                    ui.label('Welcome to AGTech').classes('font-bold text-black xl:text-4xl')
                    ui.image('static/logos/logo.png').classes('xl:w-[160px] xl:h-[81px] justify-self-end')
                with ui.column().classes('w-full p-1 rounded-lg border-2 bg-white mb-2'):
                    if current_user.bug_trap:
                        ui.label('Welcome to our service').classes('text-black font-bold text-xl self-center')
                        ui.label('Welcome to this page is currently work in progress.').classes('text-black self-center')
                        ui.label('We will let you know more once it is complete.').classes('text-black self-center')
                    else:
                        ui.label('You do not authorized for this service').classes('text-black font-bold text-xl self-center')
                        ui.label('Please contact our team for more details.').classes('text-black self-center')

@home_router.page('/carpo')
def carpo():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    ui.query('.nicegui-content').classes('p-0')
    with theme.home_frame():
        with ui.image('static/images/background.jpg'):     
            with ui.card().classes('xl:w-2/6 h-3/6 absolute-center bg-white justify-around'):
                with ui.grid(columns=2).classes('justify-between w-full p-1 mb-2'):
                    ui.label('Welcome to AGTech').classes('font-bold text-black xl:text-4xl')
                    ui.image('static/logos/logo.png').classes('xl:w-[160px] xl:h-[81px] justify-self-end')
                with ui.column().classes('w-full p-1 rounded-lg border-2 bg-white mb-2'):
                    if current_user.carpo:
                        ui.label('Welcome to our service').classes('text-black font-bold text-xl self-center')
                        ui.label('Welcome to this page is currently work in progress.').classes('text-black self-center')
                        ui.label('We will let you know more once it is complete.').classes('text-black self-center')
                    else:
                        ui.label('You do not authorized for this service').classes('text-black font-bold text-xl self-center')
                        ui.label('Please contact our team for more details.').classes('text-black self-center')                    

@home_router.page('/')
def home():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user.get('username')).first()
    topics = models.session.query(models.About).order_by(models.About.id.asc()).all()
    abouts = []
    for topic in topics:
        abouts.append(topic)
    async def create_topic():
        db_topic = models.About(header=header.value, text=text.value)
        models.session.add(db_topic)
        models.session.commit()
        add_topic_dialog.close()
        ui.notify('New topic created!', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def change_topic(id: int):
        existing_topic = models.session.query(models.About).filter(models.About.id == id)
        note = existing_topic.first()
        with ui.dialog() as change_topic_dialog, ui.card():
            with ui.column().classes('gap-0 p-2'):
                ui.label('Add new topic').classes('font-bold self-center mb-2')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Topic:').classes('self-center')
                    header = ui.input(value=note.header).props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Text:').classes('self-center')
                    text = ui.textarea(value=note.text).props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.button('Save', color='#FF6370', on_click=lambda: change_topic_dialog.submit({
                        'header': header.value, 'text': text.value, 'date': datetime.now()
                        })).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                    ui.button('Cancel', color='gray', on_click=change_topic_dialog.close).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
        change_topic_dialog.open()
        data = await change_topic_dialog
        existing_topic.update(data)
        models.session.commit()
        ui.notify('Topic has been modified', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def delete_topic(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_topic = models.session.query(models.About).filter(models.About.id == id)
            existing_topic.delete()
            models.session.commit()
            ui.notify('Topic has been removed', position='top', color='negative')
            await asyncio.sleep(2)
            ui.navigate.reload()
    ui.query('.nicegui-content').classes('p-0')
    with theme.home_frame():
        with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
            with ui.column():
                ui.label('Are you sure you want to delete item?')
                with ui.row().classes('self-center'):
                    ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                    ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
        
        with ui.dialog() as add_topic_dialog, ui.card():
            with ui.column().classes('gap-0 p-2'):
                ui.label('Add new topic').classes('font-bold self-center mb-2')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Topic:').classes('self-center')
                    header = ui.input().props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Text:').classes('self-center')
                    text = ui.textarea().props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.button('Save', color='#FF6370', on_click=create_topic).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                    ui.button('Cancel', color='gray', on_click=add_topic_dialog.close).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
        
        def right_text(text1: str, text2: str):
            ui.label(text1).classes('pl-4 pt-2 pb-2 font-bold text-lg text-end w-full bg-white border-1')
            ui.label(text2).classes('pl-2 text-end w-full bg-white border-1')
        def left_text(text1: str, text2: str):
            ui.label(text1).classes('pl-4 pt-2 pb-2 font-bold text-lg text-start w-full bg-white border-1')
            ui.label(text2).classes('pl-2 text-start w-full bg-white border-1')
                
        with ui.column().classes('w-full p-4'):
            ui.label('About Us').classes('font-bold text-xl self-center p-2 m-2')
            for i in range(len(abouts)):
                with ui.column().classes('w-full p-4 m-4 border-2'):
                    if (i%2) == 0:
                        left_text(f'{abouts[i].header}', f'{abouts[i].text}')
                    else:
                        right_text(f'{abouts[i].header}', f'{abouts[i].text}')
                        
                    if app.storage.user.get('username', None):
                        if current_user.admin:
                            with ui.row().classes('w-full justify-end'):
                                ui.button('Edit', color='primary', on_click=lambda topic= abouts[i]: change_topic(topic.id)).props('no-caps outline flat').classes('items-start')
                                ui.button('Delete', color='negative', on_click=lambda topic= abouts[i]: delete_topic(topic.id)).props('no-caps outline flat').classes('items-start')
                    
            if app.storage.user.get('username', None):
                if current_user.admin:
                    with ui.button(color='#F8F3FE', on_click=add_topic_dialog.open).props('no-caps flat'):
                        ui.icon('add_circle', size='50px').classes('mx-2 text-[#FF6370]')
                        ui.label('Add Topic')
                                        
@home_router.page('/forum')
def forum():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user.get('username')).first()
    faqs = models.session.query(models.FAQ).order_by(models.FAQ.id.asc()).all()
    questions = models.session.query(models.Forum).order_by(models.Forum.id.asc()).all()
    async def change_response(id: int):
        existing_faq = models.session.query(models.FAQ).filter(models.FAQ.id == id)
        item = existing_faq.first()
        with ui.dialog() as change_faq_dialog, ui.card():
            with ui.column().classes('gap-0 p-2'):
                ui.label('Add new question').classes('font-bold self-center mb-2')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Question:').classes('self-center')
                    header = ui.input(value=item.header).props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Answer:').classes('self-center')
                    text = ui.textarea(value=item.text).props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.button('Save', color='#FF6370', on_click=lambda: change_faq_dialog.submit({
                        'header': header.value, 'text': text.value, 'date': datetime.now()
                        })).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                    ui.button('Cancel', color='gray', on_click=change_faq_dialog.close).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
        change_faq_dialog.open()
        data = await change_faq_dialog
        existing_faq.update(data)
        models.session.commit()
        ui.notify('Topic has been modified', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def delete_response(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_faq = models.session.query(models.FAQ).filter(models.FAQ.id == id)
            existing_faq.delete()
            models.session.commit()
            ui.notify('Topic has been removed', position='top', color='negative')
            await asyncio.sleep(2)
            ui.navigate.reload()
    async def create_faq():
        db_faq = models.FAQ(header=header.value, text=text.value)
        models.session.add(db_faq)
        models.session.commit()
        add_faq_dialog.close()
        ui.notify('New topic created!', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def create_question():
        db_question = models.Forum(question=new_question.value, is_active=True)
        models.session.add(db_question)
        models.session.commit()
        add_faq_dialog.close()
        ui.notify('New question created!', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def reply_question(id: int):
        with ui.dialog() as reply_dialog, ui.card():
            with ui.column().classes('gap-0 p-2'):
                ui.label('Provide an answer').classes('font-bold self-center mb-2')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Answer:').classes('self-center')
                    answer = ui.textarea().props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.button('Save', color='#FF6370', on_click=lambda: reply_dialog.submit(answer.value)).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                    ui.button('Cancel', color='gray', on_click=lambda: reply_dialog.submit(False)).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
        reply_dialog.open()
        data = await reply_dialog
        if data:
            db_answer = models.UserResponse(user=current_user.username, question=id, answer=data)
        models.session.add(db_answer)
        models.session.commit()
        reply_dialog.close()
        ui.notify('Answer provided', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def deactivate_question(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_answer = models.session.query(models.Forum).filter(models.Forum.id == id)
            existing_answer.update({'is_active': False})
            models.session.commit()
            ui.notify('Question deactivated', position='top', color='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()
    async def delete_question(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_answer = models.session.query(models.Forum).filter(models.Forum.id == id)
            existing_answer.delete()
            models.session.commit()
            ui.notify('Question deleted', position='top', color='negative')
            await asyncio.sleep(2)
            ui.navigate.reload()
    ui.query('.nicegui-content').classes('p-0')
    with theme.home_frame():
        with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
            with ui.column():
                ui.label('Are you sure you want to delete item?')
                with ui.row().classes('self-center'):
                    ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                    ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
        
        ui.label('Help-Desk').classes('font-bold text-xl self-center p-2 m-2')
        with ui.tabs().classes('w-full justify-around') as tabs:
            faq = ui.tab('Frequently Asked Questions')
            forum = ui.tab('Forum - Users Questions') 
        with ui.tab_panels(tabs, value=faq).classes('w-full'):
            with ui.tab_panel(faq):
                with ui.dialog() as add_faq_dialog, ui.card():
                    with ui.column().classes('gap-0 p-2'):
                        ui.label('Add new topic').classes('font-bold self-center mb-2')
                        with ui.row().classes('w-full justify-between'):
                            ui.label('Topic:').classes('self-center')
                            header = ui.input().props('dense filled').classes('w-48')
                        with ui.row().classes('w-full justify-between'):
                            ui.label('Text:').classes('self-center')
                            text = ui.textarea().props('dense filled').classes('w-48')
                        with ui.row().classes('w-full justify-between'):
                            ui.button('Save', color='#FF6370', on_click=create_faq).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                            ui.button('Cancel', color='gray', on_click=add_faq_dialog.close).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
                for faq in faqs:
                    with ui.column().classes('w-full p-4 border-2'):
                        with ui.row().classes('w-full no-wrap justify-between'):
                            ui.label(faq.header).classes('pl-4 pt-2 pb-2 font-bold text-lg text-start w-full bg-white border-1')
                            if app.storage.user.get('username', None):
                                if current_user.admin:
                                    with ui.row().classes('w-full justify-end'):
                                        ui.button('Edit', color='primary', on_click=lambda q= faq: change_response(q.id)).props('no-caps outline flat').classes('items-start')
                                        ui.button('Delete', color='negative', on_click=lambda q= faq: delete_response(q.id)).props('no-caps outline flat').classes('items-start')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label(faq.text).classes('text-end w-full bg-white border-1')
                            ui.label(f'{faq.date.strftime("%b %d, %Y")} | {faq.date.strftime("%I:%M:%S %p")}').classes('md:w-48 text-xs self-center bg-white border-1')
                if app.storage.user.get('username', None):
                    if current_user.admin:
                        with ui.button(color='#F8F3FE', on_click=add_faq_dialog.open).props('no-caps flat'):
                            ui.icon('add_circle', size='50px').classes('mx-2 text-[#FF6370]')
                            ui.label('Add FAQ')
            with ui.tab_panel(forum):
                with ui.dialog() as add_question_dialog, ui.card():
                    with ui.column().classes('gap-0 p-2'):
                        ui.label('Add new topic').classes('font-bold self-center mb-2')
                        with ui.row().classes('w-full justify-between'):
                            ui.label('Question:').classes('self-center')
                            new_question = ui.input().props('dense filled').classes('w-48')
                        with ui.row().classes('w-full justify-between'):
                            ui.button('Save', color='#FF6370', on_click=create_question).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                            ui.button('Cancel', color='gray', on_click=add_question_dialog.close).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
                for question in questions:
                    with ui.expansion(f'{question.question}.... Question raised: {question.date.strftime("%b %d, %Y")} | {question.date.strftime("%I:%M:%S %p")}', 
                                      caption=f'Question is active: {question.is_active}', group='group').classes('w-full md:text-xl'):
                        answers = models.session.query(models.UserResponse).filter(models.UserResponse.question == question.id).all()
                        with ui.column().classes('w-full'):
                            for answer in answers:
                                with ui.row().classes('w-full no-wrap justify-between border-1'):
                                    ui.label(answer.answer).classes('text-start text-xs')
                                    with ui.row().classes('self-center no-wrap'):
                                        ui.label(f'Answered by {answer.user}').classes('md:w-48 text-xs self-center bg-white')
                                        ui.label(f'{answer.date.strftime("%b %d, %Y")} | {answer.date.strftime("%I:%M:%S %p")}').classes('md:w-48 text-xs self-center bg-white')
                    if app.storage.user.get('username', None):
                        with ui.row().classes('w-full justify-between'):
                            if question.is_active:
                                ui.button('Reply', color='primary', on_click=lambda q=question: reply_question(q.id)).props('no-caps outline flat').classes('items-start')
                            if current_user.admin:
                                with ui.row():
                                    if question.is_active:
                                        ui.button('Deactivate', color='primary', on_click=lambda q= question: deactivate_question(q.id)).props('no-caps outline flat').classes('items-start')
                                    ui.button('Delete', color='negative', on_click=lambda q= question: delete_question(q.id)).props('no-caps outline flat').classes('items-start')      
                if app.storage.user.get('username', None):
                    with ui.button(color='#F8F3FE', on_click=add_question_dialog.open).props('no-caps flat'):
                        ui.icon('add_circle', size='50px').classes('mx-2 text-[#FF6370]')
                        ui.label('Ask Question')
        
@home_router.page('/price_lists')
def market():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user.get('username')).first()
    products = models.session.query(models.Product).order_by(models.Product.id.asc()).all()
    async def create_product():
        db_product = models.Product(name=name.value, category=category.value, producer=producer.value, type=type.value, 
                                    dimension=dimension.value, color=color.value, price=price.value, mass=mass.value, used=used.value,
                                    details=details.value)
        models.session.add(db_product)
        models.session.commit()
        add_product_dialog.close()
        ui.notify('Product created', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    with theme.home_frame():
        with ui.dialog() as add_product_dialog, ui.card():
            ui.label('Add new product').classes('font-bold self-center mb-2')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product name:').classes('self-center')
                name = ui.input().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product category:').classes('self-center')
                category = ui.input().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Producer:').classes('self-center')
                producer = ui.input().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product type:').classes('self-center')
                type = ui.input().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product dimensions in mm:').classes('self-center')
                dimension = ui.input().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product color:').classes('self-center')
                color = ui.input().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product price in KM:').classes('self-center')
                price = ui.number().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product mass in grams:').classes('self-center')
                mass = ui.number().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product used/new:').classes('self-center')
                used = ui.checkbox()
            with ui.row().classes('w-full justify-between'):
                ui.label('Product details:').classes('self-center')
                details = ui.textarea().props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.button('Save', color='#FF6370', on_click=create_product).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                ui.button('Cancel', color='gray', on_click=add_product_dialog.close).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
        ui.label('Market').classes('font-bold text-xl self-center p-2 m-2')
        with ui.row().classes('w-full no-wrap'):
            for product in products:
                with ui.card().classes('rounded-xl m-4'):
                    with ui.column().classes('w-full items-center p-1 mb-2'):
                        image = f'./static/products/product_{product.id}/1.jpg'
                        if os.path.isfile(image):
                            ui.image(f'./static/products/product_{product.id}/1.jpg').classes('w-[150px] h-[250px]')
                        else:
                            ui.image(f'./static/products/blank.jpg').classes('w-[150px] h-[250px]')
                        ui.label(product.name).classes('font-bold mb-2 w-full')
                        with ui.row().classes('w-full justify-between'):
                            ui.label(f'{product.date.strftime("%b %d, %Y")} | {product.date.strftime("%I:%M:%S %p")}').classes('text-xs self-center bg-white')
                            ui.label(f'{product.price} KM').classes('font-bold')
                        with ui.link(target=f'/product/{product.id}'):
                            ui.button('View Details', color='negative').props('no-caps outline flat').classes('items-center w-full') 
        if app.storage.user.get('username', None):
            if current_user.admin:
                with ui.button(color='#F8F3FE', on_click=add_product_dialog.open).props('no-caps flat'):
                    ui.icon('add_circle', size='50px').classes('mx-2 text-[#FF6370]')
                    ui.label('Add Product')

@home_router.page('/product/{id}')
def product(id: int):
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user.get('username')).first()
    product = models.session.query(models.Product).filter(models.Product.id == id).first()
    async def delete_product(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_product = models.session.query(models.Product).filter(models.Product.id == id)
            existing_product.delete()
            models.session.commit()
            ui.notify('Product deleted', position='top', color='negative')
            path = f'./static/products/product_{id}/'
            shutil.rmtree(path)
            await asyncio.sleep(2)
            ui.navigate.to('/price_lists')
    async def change_product(id: int):
        existing_product = models.session.query(models.Product).filter(models.Product.id == id)
        data = {'name': name.value, 'category': category.value, 'producer': producer.value, 'type': type.value, 'dimension': dimension.value,
                'color': color.value, 'mass': mass.value, 'used': used.value, 'price': price.value, 'details': details.value}
        existing_product.update(data)
        models.session.commit()
        ui.notify('Product modified', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def handle_upload(e: events.UploadEventArguments):
        with e.content as img:
            uploaded_img = Image.open(img)
            save_path = f"./static/products/product_{id}/"
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            i = len(os.listdir(save_path))
            uploaded_img.save(save_path+f"{i+1}.jpg")
            ui.notify('Picture added', position='top', type='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()
    async def delete_photo(i: int, id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            file_path = f'./static/products/product_{id}/{i}.jpg'
            next_file = f'./static/products/product_{id}/{i+1}.jpg'
            if os.path.exists(file_path):
                os.remove(file_path)
                try:
                    os.rename(next_file, file_path)
                    ui.notify('Photo deleted', position='top', color='negative')
                except FileNotFoundError as e:
                    print(e)
                
                await asyncio.sleep(2)
                ui.navigate.reload()
    with theme.home_frame():
        with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
            with ui.column():
                ui.label('Are you sure you want to delete item?')
                with ui.row().classes('self-center'):
                    ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                    ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
        
        with ui.dialog() as edit_photo_dialog, ui.card():
            ui.label('Modify product data').classes('font-bold self-center mb-2')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product name:').classes('self-center')
                name = ui.input(value=product.name).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product category:').classes('self-center')
                category = ui.input(value=product.category).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Producer:').classes('self-center')
                producer = ui.input(value=product.producer).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product type:').classes('self-center')
                type = ui.input(value=product.type).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product dimensions in mm:').classes('self-center')
                dimension = ui.input(value=product.dimension).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product color:').classes('self-center')
                color = ui.input(value=product.color).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product price in KM:').classes('self-center')
                price = ui.number(value=product.price).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product mass in grams:').classes('self-center')
                mass = ui.number(value=product.mass).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.label('Product used/new:').classes('self-center')
                used = ui.checkbox(value=product.used)
            with ui.row().classes('w-full justify-between'):
                ui.label('Product details:').classes('self-center')
                details = ui.textarea(value=product.details).props('dense filled').classes('w-48')
            with ui.row().classes('w-full justify-between'):
                ui.button('Save', color='#FF6370', on_click=lambda: change_product(id)).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                ui.button('Cancel', color='gray', on_click=edit_photo_dialog.close).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
        with ui.dialog() as add_photo_dialog, ui.card():
            ui.label('Add product photos').classes('font-bold self-center mb-2')
            ui.upload(label='Add new image', on_upload=handle_upload).props('accept=.jpg color="info"').classes('w-[400px]')
        
        with ui.column().classes('w-4/6 self-center p-2 m-2'):
            with ui.column().classes('gap-0'):
                ui.label(f'{product.name}').classes('text-xl md:text-4xl')
                ui.label(f'{product.price} KM').classes('text-xl font-bold md:text-4xl')
            if app.storage.user.get('username', None):
                if current_user.admin:
                    with ui.row().classes('w-full justify-between'):
                        with ui.row().classes('no-wrap'):
                            ui.button('Edit', color='positive', on_click=edit_photo_dialog.open).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                            ui.button('Add photos', color='gray', on_click=add_photo_dialog.open).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4')
                        ui.button('Delete', color='#FF6370', on_click=lambda: delete_product(id)).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4') 
            with ui.carousel(animated=True, navigation=True).props('autoplay=2500').classes('md:h-96 h-48 w-full'):
                try:
                    path = f'./static/products/product_{id}'
                    images = os.listdir(path)
                    for i in range(len(images)):
                        with ui.carousel_slide().classes('w-full h-full'):
                            if app.storage.user.get('username', None):
                                if current_user.admin:
                                    with ui.button(on_click=lambda photo_id=(i+1), prod_id=id: delete_photo(i= photo_id, id=prod_id)).props('outlined flat').classes('self-end'):
                                        ui.icon('delete', color='#FF6370', size='18px')
                            ui.image(f'./static/products/product_{id}/{i+1}.jpg')
                            
                except FileNotFoundError:
                    ui.image(f'./static/products/blank.jpg')
            with ui.row().classes('w-full no-wrap justify-between'):
                with ui.row().classes('no-wrap border-2 p-1 m-2'):
                    ui.icon('o_info').classes('self-center')
                    ui.label(f'PRODUCT ID: {product.id}').classes('text-xs text-gray-400')
                with ui.row().classes('no-wrap border-2 p-1 m-2'):
                    ui.icon('o_schedule').classes('self-center')
                    ui.label(f'{product.date.strftime("%b %d, %Y")} | {product.date.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')
            with ui.row().classes('w-full no-wrap justify-between border-2 p-1 m-2'):
                ui.label('This product can be shipped within 24h.').classes(' self-center text-gray-400')
                ui.button('ORDER NOW', color='negative').props('no-caps outline flat').classes('text-xs items-center')
            with ui.column().classes('w-full justify-between border-2 p-1 m-2'):
                ui.label('PRODUCT BASIC CHARACTERISTICS:').classes('text-xl md:text-4xl')
                with ui.row().classes('w-full justify-around'):
                    with ui.row().classes('w-[400px] justify-between p-1'):
                        ui.label('Producer:').classes('self-center text-gray-400')
                        ui.label(f'{product.producer}').classes(' self-center text-gray-400')
                    with ui.row().classes('w-[400px] justify-between p-1'):
                        ui.label('Product type:').classes(' self-center text-gray-400')
                        ui.label(f'{product.type}').classes(' self-center text-gray-400')
                with ui.row().classes('w-full justify-around'):
                    with ui.row().classes('w-[400px] justify-between p-1'):
                        ui.label('Product dimensions:').classes(' self-center text-gray-400')
                        ui.label(f'{product.dimension} mm').classes(' self-center text-gray-400')
                    with ui.row().classes('w-[400px] justify-between p-1'):
                        ui.label('Product mass:').classes(' self-center text-gray-400')
                        ui.label(f'{product.mass} g').classes(' self-center text-gray-400')
                with ui.row().classes('w-full justify-around'):
                    with ui.row().classes('w-[400px] justify-between p-1'):
                        ui.label('Product color:').classes(' self-center text-gray-400')
                        ui.label(f'{product.color}').classes(' self-center text-gray-400')
                    with ui.row().classes('w-[400px] justify-between p-1'):
                        ui.label('Used product:').classes(' self-center text-gray-400')
                        if product.used:
                            ui.label('USED').classes(' self-center text-gray-400')
                        else:
                            ui.label('NEW').classes(' self-center text-gray-400')
            with ui.column().classes('w-full justify-between border-2 p-1 m-2'):
                ui.label('PRODUCT DETAILS:').classes('text-xl md:text-4xl')
                ui.label(f'{product.details}').classes('w-full border-2 text-lg p-2 text-gray-400')