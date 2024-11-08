from nicegui import ui, app, APIRouter, events
from PIL import Image
import os
import models
import theme
import config
import asyncio

aquaterrius_router = APIRouter(prefix="/aquaterrius")

@aquaterrius_router.page('/')
def home():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    systems = []
    if current_user.admin:
        async def remove_system(id: int):
            confim_delete_dialog.open()
            confirmation = await confim_delete_dialog
            if confirmation:
                existing_system = models.session.query(models.System).filter(models.System.id == id)
                existing_system.delete()
                models.session.commit()
                ui.notify('Succesfully deleted', position='top', color='negative')
                await asyncio.sleep(2)
                ui.navigate.reload()

        def get_system(id: int):
            ui.navigate.to('/system')
            app.storage.user.update({'system_id': id})

        all_systems = models.session.query(models.System).all()
        for system in all_systems:
            systems.append(system)
        with theme.main_frame():
            with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
                with ui.column():
                    ui.label('Are you sure you want to delete item?')
                    with ui.row().classes('self-center'):
                        ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                        ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
            ui.label('Systems').classes('text-xl font-bold p-2')
            columns = [{'name': 'owner', 'label': 'Owner', 'field': 'owner', 'align': 'left'},
                        {'name': 'systemID', 'label': 'System ID', 'field': 'systemID', 'align': 'left'},
                        {'name': 'name', 'label': 'System name', 'field': 'name', 'align': 'left'},
                        {"name": "area", "label": 'Area in ha', "field": "area", "align": "left"},
                        {"name": "fruit", "label": 'Planted fruit', "field": "fruit", "align": "left"},
                        {"name": "location", "label": 'Location', "field": "location", "align": "left"},
                        {"name": "created_at", "label": 'Created', "field": "created_at", "align": "left"},
                        {"name": "action", "label": "", "field": "id", "align": "center"}]
            rows = []
            for system in systems:
                values = {}
                values.update({'owner': system.owner, 'systemID': system.systemID, 'name': system.name, 'area': system.area, 'fruit': system.fruit,
                               'location': system.location, 'created_at': system.created_at.strftime('%d-%m-%Y %H:%M'),'id': system.id})
                rows.append(values)
            with ui.table(title='Aquaterrius Systems', columns=columns, rows=rows, pagination=8).classes(
                        'justify-items-center').classes('bordered w-full') as systems_table:
                with systems_table.add_slot('top-right'):
                    with ui.input(placeholder='Search').props('type=search').bind_value(systems_table, 'filter').add_slot('append'):
                        ui.icon('search')
                systems_table.add_slot(f'body-cell-action', """
                    <q-td :props="props">
                        <q-btn @click="$parent.$emit('info', props)" icon="info" flat dense color='blue'/>
                    </q-td>
                    <q-td :props="props">
                        <q-btn @click="$parent.$emit('update', props)" icon="delete" flat dense color='red'/>
                    </q-td>
                    """)
                systems_table.on('info', lambda e: get_system(e.args["row"]["id"]))
                systems_table.on('update', lambda e: remove_system(e.args["row"]["id"]))

    else:
        for system in current_user.systems:
            systems.append(system)
        with theme.main_frame():
            ui.label('Systems').classes('text-xl font-bold p-2')
            with ui.row().classes('justify-center'):
                for system in systems:
                    with ui.card().classes('w-[393px] h-[580px] rounded-xl'):
                        my_system = system
                        with ui.row().classes('w-full no-wrap justify-between p-2 items-center'):
                            with ui.avatar():
                                ui.image('static/logos/Logo Aqua.png').classes('w-[25px] h-[30px] text-white')
                            ui.icon('more_vert').classes('text-2xl')
                        with ui.column().classes('w-full items-center pt-3 mb-10'):
                            image = f'./static/systems/system_{system.id}.jpg'
                            if os.path.isfile(image):
                                ui.image(f'/static/systems/system_{system.id}.jpg').classes('w-[107px] h-[107px] itmes-center rounded-full')
                            else:
                                ui.image('https://picsum.photos/640/360').classes('w-[107px] h-[107px] itmes-center rounded-full')
                            ui.label(my_system.name).classes('text-2xl font-bold mb-2')
                            with ui.column().classes('gap-0'):
                                with ui.row().classes('items-center mb-0'):
                                    ui.label(f'{my_system.area} ha of').classes('text-xs')
                                    ui.label(my_system.fruit).classes('text-xs')
                                ui.label(f'at {my_system.location}').classes('font-bold self-center')
                        with ui.row().classes('w-full items-center p-2'):
                            ui.icon('arrow_circle_right', color='red').classes('text-xl')
                            with ui.column().classes('p-2 gap-0'):
                                ui.label('Last communication:').classes('font-bold text-sm')
                                ui.label(f'{my_system.updated_at.strftime("%b %d, %Y")} | {my_system.updated_at.strftime("%I:%M:%S %p")}').classes('text-sm')
                        with ui.link(target='/system').classes('mx-auto'):
                            ui.button(text='Enter', on_click=lambda system=my_system: app.storage.user.update({'system_id': system.id})).props('rounded').classes('w-[224px] h-[60px] mx-auto')

@aquaterrius_router.page('/profile')
def profile():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    users = models.session.query(models.User).all()
    if current_user.admin:
        async def change_user(username: str):
            existing_user = models.session.query(models.User).filter(models.User.username == username)
            user = existing_user.first()
            with ui.dialog() as change_user_dialog, ui.card():
                with ui.column().classes('w-full'):
                    ui.label('Edit user settings').classes('font-bold self-center')
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label('Admin user:')
                        admin = ui.switch(value=user.admin)
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label('Premium user:')
                        premium = ui.switch(value=user.premium)
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label('Inactive user:')
                        inactive = ui.switch(value=user.delisted)
                    ui.label('Active serices').classes('font-bold self-center')
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label('Aquaterrius user:')
                        aquaterrius = ui.switch(value=user.aquaterrius)
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label('Bug trap user:')
                        bug_trap = ui.switch(value=user.bug_trap)
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label('Carpo user:')
                        carpo = ui.switch(value=user.carpo)
                    ui.button(text='Save', color='#FF6370',
                      on_click=lambda: change_user_dialog.submit({
                          'admin': admin.value, 'premium': premium.value, 'delisted': inactive.value, 'aquaterrius': aquaterrius.value,
                          'bug_trap': bug_trap.value, 'carpo': carpo.value
                      })).props('no-caps rounded-lg dense').classes('text-white w-full')
            change_user_dialog.open()
            data = await change_user_dialog
            existing_user.update(data)
            models.session.commit()
            ui.notify('Settings changed', position='top', color='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()

        async def handle_upload(e: events.UploadEventArguments):
            with e.content as img:
                uploaded_img = Image.open(img)
                save_path = f"./static/profiles/"
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                uploaded_img.save(save_path+f"avatar_{current_user.username}.jpg")
                ui.notify('Avatar added', position='top', type='positive')
                await asyncio.sleep(2)
                ui.navigate.reload()

        async def edit_user():
            user = current_user.username
            existing_user = models.session.query(models.User).filter(models.User.username == user)
            data = {'name': new_name.value, 'surname': new_surname.value, 'email': new_email.value, 'address': new_address.value}
            existing_user.update(data)
            models.session.commit()
            ui.notify('Succesfully updated', position='top', color='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()

        async def remove_user(username: str):
            confim_delete_dialog.open()
            confirmation = await confim_delete_dialog
            if confirmation:
                existing_user = models.session.query(models.User).filter(models.User.username == username)
                existing_user.delete()
                models.session.commit()
                ui.notify('Succesfully deleted', position='top', color='negative')
                await asyncio.sleep(2)
                ui.navigate.reload()
        async def add_new_user():
            db_user = models.User(username=username.value, name=name.value, surname=surname.value, email=email.value, address=address.value,
                                  admin=admin.value, premium=premium.value, delisted=delisted.value, aquaterrius=aquaterrius.value,
                                  bug_trap=bug_trap.value,carpo=carpo.value, hashed_password=config.get_hashed_password(user_password.value),
                                  secret=config.generate_secret())
            models.session.add(db_user)
            models.session.commit()
            ui.notify('Succesfully created', position='top', color='positive')
            await asyncio.sleep(3)
            ui.navigate.reload()
        async def change_password():
            get_user = current_user.username
            existing_user = models.session.query(models.User).filter(models.User.username == get_user)
            user = existing_user.first()
            if not config.verify_password(old_password.value, user.hashed_password):
                ui.notify('Wrong Password', position='top', color='negative')
            elif not new_password.value == retype_password.value:
                ui.notify('Passwords must match', position='top', color='negative')
            else:
                data = {'hashed_password': config.get_hashed_password(new_password.value)}
                existing_user.update(data)
                models.session.commit()
                ui.notify('Password changed', position='top', color='positive')
                await asyncio.sleep(2)
                ui.navigate.reload()


        with theme.main_frame():
            with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
                with ui.column():
                    ui.label('Are you sure you want to delete item?')
                    with ui.row().classes('self-center'):
                        ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                        ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
            with ui.dialog() as add_user_dialog, ui.card():
                with ui.column().classes('gap-0 p-2'):
                    ui.label('Add new user').classes('font-bold self-center mb-2')
                    with ui.row().classes('w-full justify-between items-center mb-2'):
                        username = ui.input('Username')
                        user_password = ui.input('Password', password=True,
                            password_toggle_button=True)
                    with ui.row().classes('w-full justify-between items-center no-wrap mb-2'):
                        name = ui.input('First name:')
                        surname = ui.input('Last name:')
                    with ui.row().classes('w-full justify-between no-wrap mb-2'):
                        email = ui.input('Email')
                        address = ui.input('Address:')
                    ui.label('Basic settings').classes('font-bold self-center mb-2')
                    with ui.row().classes('w-full justify-between items-center mb-2'):
                        with ui.row().classes('justify-between items-center'):
                            ui.label('Is Admin:')
                            admin = ui.switch()
                        with ui.row().classes('justify-between items-center'):
                            ui.label('Premium User:')
                            premium = ui.switch()
                        with ui.row().classes('justify-between items-center'):
                            ui.label('Active User:')
                            delisted = ui.switch()
                    ui.label('Active services').classes('font-bold self-center mb-2')
                    with ui.row().classes('w-full justify-between items-center mb-2'):
                        with ui.row().classes('justify-between items-center'):
                            ui.label('Aquaterrius:')
                            aquaterrius = ui.switch()
                        with ui.row().classes('justify-between items-center'):
                            ui.label('Bug trap:')
                            bug_trap = ui.switch()
                        with ui.row().classes('justify-between items-center'):
                            ui.label('Carpo:')
                            carpo = ui.switch()
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.button('Save', color='#FF6370', on_click=add_new_user).props('no-caps rounded-lg dense').classes('w-24 text-white')
                        ui.button('Cancel', on_click=add_user_dialog.close).props('no-caps rounded-lg dense').classes('w-24 text-white')

            with ui.dialog() as profile_dialog, ui.card():
                ui.label('My account').classes('font-bold text-xl mb-2')
                with ui.row().classes('w-full justify-around'):
                    with ui.column().classes('border-2 p-2 m-4'):
                        ui.label('Avatar').classes('mb-2')
                        image = f'./static/profiles/avatar_{current_user.username}.jpg'
                        if os.path.isfile(image):
                            ui.image(f'/static/profiles/avatar_{current_user.username}.jpg').classes('w-[400px] h-[300px]')
                        else:
                            ui.image('https://picsum.photos/640/360').classes('w-[400px] h-[300px]')
                        ui.upload(label='Change your Avatar', on_upload=handle_upload).props('accept=.jpg color="info"').classes('w-[400px]')
                    with ui.column().classes('p-2 m-4'):
                        with ui.column().classes('border-2 w-[400px]'):
                            ui.label('Information').classes('mb-2')
                            with ui.row().classes('w-full justify-end'):
                                ui.label('Username:').classes('self-center')
                                ui.input(value=current_user.username).props('dense filled readonly').classes('w-48')
                            with ui.row().classes('w-full justify-end'):
                                ui.label('FIrst name:').classes('self-center')
                                new_name = ui.input(value=current_user.name).props('dense filled').classes('w-48')
                            with ui.row().classes('w-full justify-end'):
                                ui.label('Last name:').classes('self-center')
                                new_surname = ui.input(value=current_user.surname).props('dense filled').classes('w-48')
                            with ui.row().classes('w-full justify-end'):
                                ui.label('Email:').classes('self-center')
                                new_email = ui.input(value=current_user.email).props('dense filled').classes('w-48')
                            with ui.row().classes('w-full justify-end'):
                                ui.label('Address:').classes('self-center')
                                new_address = ui.input(value=current_user.address).props('dense filled').classes('w-48')
                        ui.button('Save', color='#FF6370', on_click=edit_user).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')

            with ui.dialog() as password_dialog, ui.card():
                ui.label('Change Password').classes('font-bold text-xl mb-2')
                with ui.row().classes('w-full justify-end'):
                    ui.label('Old Password:').classes('self-center')
                    old_password = ui.input(placeholder='************', password=True,
                            password_toggle_button=True).props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-end'):
                    ui.label('New Password:').classes('self-center')
                    new_password = ui.input(placeholder='************', password=True,
                            password_toggle_button=True).props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-end'):
                    ui.label('Retyped Password:').classes('self-center')
                    retype_password = ui.input(placeholder='************', password=True,
                            password_toggle_button=True).props('dense filled').classes('w-48')
                ui.button('Save', color='#FF6370', on_click=change_password).props('no-caps rounded-lg dense').classes('w-64 self-center text-white p-2 m-4')

            with ui.row().classes('w-full justify-between'):
                ui.label('Users').classes('text-xl font-bold p-2')
                with ui.row().classes('self-center'):
                    ui.button(text='Change Profile', on_click=profile_dialog.open).props('no-caps outline flat').classes('items-start')
                    ui.button(text='Change Password', on_click=password_dialog.open).props('no-caps outline flat').classes('items-start')
            columns = [{'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
                        {'name': 'name', 'label': 'First name', 'field': 'name', 'align': 'left'},
                        {"name": "surname", "label": 'Last name', "field": "surname", "align": "left"},
                        {"name": "address", "label": 'Address', "field": "address", "align": "left"},
                        {"name": "created_at", "label": 'Created', "field": "created_at", "align": "left"},
                        {"name": "action", "label": "", "field": "username", "align": "center"}]
            rows = []
            for user in users:
                values = {}
                values.update({'email': user.email, 'name': user.name, 'surname': user.surname, 'address': user.address,
                               'created_at': user.created_at.strftime('%d-%m-%Y %H:%M'),'username': user.username})
                rows.append(values)
            with ui.table(title='Active Users', columns=columns, rows=rows, pagination=8).classes(
                        'justify-items-center').classes('bordered w-full') as users_table:
                with users_table.add_slot('top-right'):
                    with ui.input(placeholder='Search').props('type=search').bind_value(users_table, 'filter').add_slot('append'):
                        ui.icon('search')
                users_table.add_slot(f'body-cell-action', """
                    <q-td :props="props">
                        <q-btn @click="$parent.$emit('update', props)" icon="edit" flat dense color='green'/>
                    </q-td>
                    <q-td :props="props">
                        <q-btn @click="$parent.$emit('delete', props)" icon="delete" flat dense color='red'/>
                    </q-td>
                    """)
                users_table.on('update', lambda e: change_user(e.args["row"]["username"]))
                users_table.on('delete', lambda e: remove_user(e.args["row"]["username"]))

            with ui.button(color='#F8F3FE', on_click=add_user_dialog.open).props('no-caps flat'):
                ui.icon('add_circle', size='50px').classes('mx-2 text-[#FF6370]')
                ui.label('Add User')
    else:
        async def handle_upload(e: events.UploadEventArguments):
            with e.content as img:
                uploaded_img = Image.open(img)
                save_path = f"./static/profiles/"
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                uploaded_img.save(save_path+f"avatar_{current_user.username}.jpg")
                ui.notify('Avatar added', position='top', type='positive')
                await asyncio.sleep(2)
                ui.navigate.reload()

        async def edit_user():
            user = current_user.username
            existing_user = models.session.query(models.User).filter(models.User.username == user)
            data = {'name': new_name.value, 'surname': new_surname.value, 'email': new_email.value, 'address': new_address.value}
            existing_user.update(data)
            models.session.commit()
            ui.notify('Succesfully updated', position='top', color='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()

        async def change_password():
            get_user = current_user.username
            existing_user = models.session.query(models.User).filter(models.User.username == get_user)
            user = existing_user.first()
            if not config.verify_password(old_password.value, user.hashed_password):
                ui.notify('Wrong Password', position='top', color='negative')
            elif not new_password.value == retype_password.value:
                ui.notify('Passwords must match', position='top', color='negative')
            else:
                data = {'hashed_password': config.get_hashed_password(new_password.value)}
                existing_user.update(data)
                models.session.commit()
                ui.notify('Password changed', position='top', color='positive')
                await asyncio.sleep(2)
                ui.navigate.reload()

        ui.query('.nicegui-content').classes('p-0')
        with theme.main_frame():
            with ui.dialog() as password_dialog, ui.card():
                ui.label('Change Password').classes('font-bold text-xl mb-2')
                with ui.row().classes('w-full justify-end'):
                    ui.label('Old Password:').classes('self-center')
                    old_password = ui.input(placeholder='************', password=True,
                            password_toggle_button=True).props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-end'):
                    ui.label('New Password:').classes('self-center')
                    new_password = ui.input(placeholder='************', password=True,
                            password_toggle_button=True).props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-end'):
                    ui.label('Retyped Password:').classes('self-center')
                    retype_password = ui.input(placeholder='************', password=True,
                            password_toggle_button=True).props('dense filled').classes('w-48')
                ui.button('Save', color='#FF6370', on_click=change_password).props('no-caps rounded-lg dense').classes('w-64 self-center text-white p-2 m-4')

            ui.label('My account').classes('font-bold text-xl mb-2')
            with ui.row().classes('w-full justify-around'):
                with ui.column().classes('border-2 p-2 m-4'):
                    ui.label('Avatar').classes('mb-2')
                    image = f'./static/profiles/avatar_{current_user.username}.jpg'
                    if os.path.isfile(image):
                        ui.image(f'/static/profiles/avatar_{current_user.username}.jpg').classes('w-[400px] h-[300px]')
                    else:
                        ui.image('https://picsum.photos/640/360').classes('w-[400px] h-[300px]')
                    ui.upload(label='Change your Avatar', on_upload=handle_upload).props('accept=.jpg color="info"').classes('w-[400px]')
                with ui.column().classes('p-2 m-4'):
                    with ui.column().classes('border-2 w-[400px]'):
                        ui.label('Information').classes('mb-2')
                        with ui.row().classes('w-full justify-end'):
                            ui.label('Username:').classes('self-center')
                            ui.input(value=current_user.username).props('dense filled readonly').classes('w-48')
                        with ui.row().classes('w-full justify-end'):
                            ui.label('FIrst name:').classes('self-center')
                            new_name = ui.input(value=current_user.name).props('dense filled').classes('w-48')
                        with ui.row().classes('w-full justify-end'):
                            ui.label('Last name:').classes('self-center')
                            new_surname = ui.input(value=current_user.surname).props('dense filled').classes('w-48')
                        with ui.row().classes('w-full justify-end'):
                            ui.label('Email:').classes('self-center')
                            new_email = ui.input(value=current_user.email).props('dense filled').classes('w-48')
                        with ui.row().classes('w-full justify-end'):
                            ui.label('Address:').classes('self-center')
                            new_address = ui.input(value=current_user.address).props('dense filled').classes('w-48')
                    with ui.row():
                        ui.button('Save', color='#FF6370', on_click=edit_user).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                        ui.button('Change Password', color='gray', on_click=password_dialog.open).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4')

@aquaterrius_router.page('/messages')
def messages():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    users = models.session.query(models.User).all()
    active_alerts = models.session.query(models.Notification).filter(models.Notification.read == False).all()
    inactive_alerts = models.session.query(models.Notification).filter(models.Notification.read == True).all()
    user_dict = {}
    for user in users:
        if user.username != current_user.username:
            user_dict.update({user.username : user.email})
    if current_user.admin:
        async def remove_inactive_alert(id: int):
            confim_delete_dialog.open()
            confirmation = await confim_delete_dialog
            if confirmation:
                notification = models.session.query(models.Notification).filter(models.Notification.id == id)
                notification.delete()
                models.session.commit()
                ui.notify('Succesfully removed', position='top', color='negative')
                await asyncio.sleep(2)
                ui.navigate.reload()
        async def send_alert():
            data = models.Notification(user=to_user.value, sender=current_user.username, topic=topic.value, message=message.value, read=False)
            models.session.add(data)
            models.session.commit()
            create_alert_dialog.close()
            ui.notify('Message sent!', position='top', color='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()

        ui.query('.nicegui-content').classes('p-0')
        with theme.main_frame():
            with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
                with ui.column():
                    ui.label('Are you sure you want to delete item?')
                    with ui.row().classes('self-center'):
                        ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                        ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
            with ui.dialog() as create_alert_dialog, ui.card():
                ui.label('Create Message').classes('font-bold self-center')
                with ui.row().classes('w-full justify-between'):
                    ui.label('To:').classes('self-center')
                    to_user = ui.select(user_dict).classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Subject:').classes('self-center')
                    topic = ui.input().props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.label('Message:').classes('self-center')
                    message = ui.textarea().props('dense filled').classes('w-48')
                with ui.row().classes('w-full justify-between'):
                    ui.button('Send', color='#FF6370', on_click=send_alert).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')
                    ui.button('Cancel', color='gray', on_click=create_alert_dialog.close).props('no-caps rounded-lg dense').classes('w-48 text-white p-2 m-4')

            ui.label('List of messages').classes('font-bold text-xl mb-2')
            with ui.tabs().classes('w-full justify-around') as tabs:
                active = ui.tab('Active Notifications')
                inactive = ui.tab('Read Notifications')
            with ui.tab_panels(tabs, value=active).classes('w-full'):
                with ui.tab_panel(active):
                    columns = [{'name': 'date', 'label': 'Date', 'field': 'date', 'align': 'left'},
                                {'name': 'sender', 'label': 'From:', 'field': 'sender', 'align': 'left'},
                                {"name": "user", "label": 'To:', "field": "user", "align": "left"},
                                {"name": "topic", "label": 'Subject:', "field": "topic", "align": "left"},
                                {"name": "message", "label": 'Message', "field": "message", "align": "left"}]
                    rows = []
                    for alert in active_alerts:
                        values = {}
                        values.update({'date': alert.date.strftime('%d-%m-%Y %H:%M'), 'sender': alert.sender, 'user': alert.user,
                                    'topic': alert.topic, 'message': alert.message})
                        rows.append(values)
                    with ui.table(title='Active Notifications', columns=columns, rows=rows, pagination=8).classes(
                                'justify-items-center').classes('bordered w-full') as active_alerts_table:
                        with active_alerts_table.add_slot('top-right'):
                            with ui.input(placeholder='Search').props('type=search').bind_value(active_alerts_table, 'filter').add_slot('append'):
                                ui.icon('search')

                    with ui.button(color='#F8F3FE', on_click=create_alert_dialog.open).props('no-caps flat'):
                        ui.icon('add_circle', size='50px').classes('mx-2 text-[#FF6370]')
                        ui.label('New Alert')
                with ui.tab_panel(inactive):
                    columns = [{'name': 'date', 'label': 'Date', 'field': 'date', 'align': 'left'},
                                {'name': 'sender', 'label': 'From:', 'field': 'sender', 'align': 'left'},
                                {"name": "user", "label": 'To:', "field": "user", "align": "left"},
                                {"name": "topic", "label": 'Subject:', "field": "topic", "align": "left"},
                                {"name": "message", "label": 'Message', "field": "message", "align": "left"},
                                {"name": "action", "label": "", "field": "id", "align": "center"}]
                    rows = []
                    for alert in inactive_alerts:
                        values = {}
                        values.update({'date': alert.date.strftime('%d-%m-%Y %H:%M'), 'sender': alert.sender, 'user': alert.user,
                                    'topic': alert.topic, 'message': alert.message, 'id': alert.id})
                        rows.append(values)
                    with ui.table(title='Read Notifications', columns=columns, rows=rows, pagination=8).classes(
                                'justify-items-center').classes('bordered w-full') as inactive_alerts_table:
                        with inactive_alerts_table.add_slot('top-right'):
                            with ui.input(placeholder='Search').props('type=search').bind_value(inactive_alerts_table, 'filter').add_slot('append'):
                                ui.icon('search')
                        inactive_alerts_table.add_slot(f'body-cell-action', """
                            <q-td :props="props">
                                <q-btn @click="$parent.$emit('delete', props)" icon="delete" flat dense color='red'/>
                            </q-td>
                            """)
                        inactive_alerts_table.on('delete', lambda e: remove_inactive_alert(e.args["row"]["id"]))

    else:
        async def remove_alert(id: int):
            confim_delete_dialog.open()
            confirmation = await confim_delete_dialog
            if confirmation:
                existing_alert = models.session.query(models.Notification).filter(models.Notification.id == id)
                data = {'read': True}
                existing_alert.update(data)
                models.session.commit()
                ui.notify('Succesfully removed', position='top', color='negative')
                await asyncio.sleep(2)
                ui.navigate.reload()

        ui.query('.nicegui-content').classes('p-0')
        with theme.main_frame():
            ui.label('Messages').classes('font-bold text-xl mb-2')
            with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
                with ui.column():
                    ui.label('Are you sure you want to delete item?')
                    with ui.row().classes('self-center'):
                        ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                        ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
            for alert in current_user.alerts:
                if not alert.read:
                    with ui.row().classes('w-full justify-between no-wrap bg-white items-center p-2 m-2'):
                        with ui.row().classes('no-wrap justify-around mr-2'):
                            with ui.avatar():
                                image = f'./static/profiles/avatar_{alert.sender}.jpg'
                                if os.path.isfile(image):
                                    ui.image(f'/static/profiles/avatar_{alert.sender}.jpg').props('no-spinner fit=scale-down')
                                else:
                                    ui.image('https://i.pravatar.cc/300').props('no-spinner fit=scale-down')
                            ui.label(alert.sender).classes('self-center')
                        ui.label(alert.topic).classes('font-bold mr-2')
                        ui.label(alert.message).classes('md:w-[600px]')
                        with ui.button(color='#F8F3FE', on_click=lambda new_alert=alert: remove_alert(id=new_alert.id)).props('no-caps flat').classes('mr-2'):
                                ui.icon('delete', size='25px').classes('mx-2 text-[#FF6370]')