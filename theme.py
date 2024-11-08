from nicegui import ui, app
from contextlib import contextmanager
import models
import os

with open('static/svg_icons/icons8-shop.svg') as f:
    market_icon = f.read()
with open('static/svg_icons/icons8-message.svg') as f:
    message_icon = f.read()
with open('static/svg_icons/icons8-information.svg') as f:
    info_icon = f.read()
with open('static/svg_icons/icons8-timeline-week.svg') as f:
    alert_icon = f.read()
with open('static/svg_icons/icons8-four-squares.svg') as f:
    dash_icon = f.read()
with open('static/svg_icons/icons8-sensor.svg') as f:
    sensor_icon = f.read()
with open('static/svg_icons/icons8-valve.svg') as f:
    valve_icon = f.read()
with open('static/svg_icons/icons8-stacked-organizational-chart-highlighted-parent-node.svg') as f:
    shift_icon = f.read()
with open('static/svg_icons/icons8-task-planning (1).svg') as f:
    schedule_icon = f.read()
with open('static/svg_icons/icons8-book.svg') as f:
    log_icon = f.read()
with open('static/svg_icons/icons8-settings.svg') as f:
    setting_icon = f.read()


def header():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    with ui.row().classes('pt-2 pr-3'):
        if not current_user.admin:
            active_alerts = []
            notifications = current_user.alerts
            with ui.button(icon='o_notifications', color='grey-7').props('outline round dense flat'):
                for alert in notifications:
                    if alert not in active_alerts:
                        if alert.read == False:
                            active_alerts.append(alert)
                if active_alerts:
                    ui.badge(len(active_alerts), color='red').props('floting rounded').classes('self-start')
                else:
                    ui.badge(color='blue').props('floting rounded').classes('self-start')
                with ui.menu() as menu:
                    if not active_alerts:
                        ui.menu_item('There is no new alerts!')
                    else:
                        ui.menu_item('You got new message!')

            with ui.avatar():
                image = f'./static/profiles/avatar_{current_user.username}.jpg'
                if os.path.isfile(image):
                    ui.image(f'/static/profiles/avatar_{current_user.username}.jpg').props('no-spinner fit=scale-down')
                else:
                    ui.image('https://i.pravatar.cc/300').props('no-spinner fit=scale-down')



def aquaterrius_menu():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    if current_user.admin:
        with ui.link(target='/aquaterrius'):
            #ui.button(icon='grid_view', text='Systems').props('no-caps outline flat').classes('w-[174px] items-start')
            with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
                ui.html(dash_icon)
                ui.label('Systems').classes('pl-2')
    else:
        with ui.link(target='/aquaterrius'):
            #ui.button(icon='grid_view', text='Dashboard').props('no-caps outline flat').classes('w-[174px] items-start')
            with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
                ui.html(dash_icon)
                ui.label('Dashboard').classes('pl-2')
    if current_user.admin:
        with ui.link(target='/aquaterrius/profile'):
            ui.button(icon='o_group', text='Users').props('no-caps outline flat').classes('w-[174px] items-start')
    else:
        with ui.link(target='/aquaterrius/profile'):
            ui.button(icon='o_person', text='Profile').props('no-caps outline flat').classes('w-[174px] items-start')
    with ui.link(target='/aquaterrius/messages'):
        #ui.button(icon='event_note', text='Messages').props('no-caps outline flat').classes('w-[174px] items-start')
        with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
            ui.html(alert_icon)
            ui.label('Messages').classes('pl-2')



def system_menu():
    with ui.link(target='/system'):
        #ui.button(icon='grid_view', text='Dashboard').props('no-caps outline flat').classes('w-[174px] items-start')
        with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
            ui.html(dash_icon)
            ui.label('Dashboard').classes('pl-2')
    with ui.link(target='/sensors'):
            #ui.button(icon='o_sensors', text='Sensors').props('no-caps outline flat').classes('w-[174px] items-start')
            with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
                ui.html(sensor_icon)
                ui.label('Sensors').classes('pl-2')
    with ui.link(target='/valves'):
        with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
            ui.html(valve_icon)
            #ui.image('/static/icons/valve.png').classes('w-[22px] h-[22px] rounded-full mr-3')
            ui.label('Valves').classes('pl-2')
    with ui.link(target='/shifts'):
        #ui.button(icon='account_tree', text='Shifts').props('no-caps outline flat').classes('w-[174px] items-start')
        with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
            ui.html(shift_icon)
            ui.label('Shifts').classes('pl-2')
    with ui.link(target='/schedules'):
        #ui.button(icon='pending_actions', text='Schedules').props('no-caps outline flat').classes('w-[174px] items-start')
        with ui.button().props('no-caps outline flat').classes('w-[200px] items-start'):
            ui.html(schedule_icon)
            ui.label('Irrigation Schedule').classes('pl-2')
    with ui.link(target='/logs'):
        #ui.button(icon='o_receipt_long', text='Devices Logs').props('no-caps outline flat').classes('w-[174px] items-start')
        with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
            ui.html(log_icon)
            ui.label('Logs').classes('pl-2')
    with ui.link(target='/settings'):
        #ui.button(icon='o_settings', text='Settings').props('no-caps outline flat').classes('w-[174px] items-start')
        with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
            ui.html(setting_icon)
            ui.label('Settings').classes('pl-2')

@contextmanager
def main_frame():
    ui.query('.nicegui-content').classes('p-0')
    ui.colors(primary='#4C4C4C', secondary='#53B689', accent='#111B1E', positive='#53B689', info='#FF6370')
    with ui.header().classes('md:justify-end justify-between bg-[#F8F3FE] p-0'):
        ui.button(on_click=lambda: left_drawer.toggle(),
                  icon='menu', color='grey-7').props('flat').classes('md:hidden mt-2')
        header()
    with ui.left_drawer(top_corner=True).props('width=254').classes('justify-between') as left_drawer:
        with ui.column().classes('mx-auto md:mt-4 w-[174px]'):
            ui.image('static/logos/logo.png').classes('h-[66px] w-[105px] mx-auto mb-8')
            aquaterrius_menu()
        with ui.column().classes('mx-auto w-[174px]'):
            with ui.link(target='/'):
                ui.button(icon='o_info', text='Home').props('no-caps outline flat').classes('w-[174px] items-start')
            with ui.link(target='/bug_trap'):
                ui.button(icon='o_bug_report', text='Bug Traps').props('no-caps outline flat').classes('w-[174px] items-start')
            with ui.link(target='/carpo'):
                ui.button(icon='o_cloud', text='Carpo').props('no-caps outline flat').classes('w-[174px] items-start')
            with ui.link(target='/'):
                ui.button(icon='logout', text='Logout', on_click=lambda: (app.storage.user.clear())).props('no-caps outline flat').classes('w-[174px] items-start')
    with ui.column().classes('p-4 items-center md:items-start w-full bg-[#F8F3FE]'):
        yield

@contextmanager
def home_frame():
    ui.query('.nicegui-content').classes('p-0')
    ui.colors(primary='#4C4C4C', secondary='#53B689', accent='#111B1E', positive='#53B689',info='#FF6370')
    with ui.header().classes('md:justify-end justify-between bg-[#F8F3FE] p-0'):
        ui.button(on_click=lambda: left_drawer.toggle(),
                  icon='menu', color='grey-7').props('flat').classes('md:hidden mt-2')
        #header()
    with ui.left_drawer(top_corner=True).props('width=254').classes('justify-between') as left_drawer:
        with ui.column().classes('mx-auto md:mt-4 w-[174px]'):
            ui.image('static/logos/logo.png').classes('h-[66px] w-[105px] mx-auto mb-8')
            with ui.link(target='/'):
                #ui.button(icon='o_info', text='Home').props('no-caps outline flat').classes('w-[174px] items-start')
                with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
                    ui.html(info_icon)
                    ui.label('Home').classes('pl-2')
            with ui.link(target='/price_lists'):
                #ui.button(icon='o_sell', text='Price Lists').props('no-caps outline flat').classes('w-[174px] items-start')
                with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
                    ui.html(market_icon)
                    ui.label('Marketplace').classes('pl-2')
            with ui.link(target='/forum'):
                #ui.button(icon='o_chat', text='Help').props('no-caps outline flat').classes('w-[174px] items-start')
                with ui.button().props('no-caps outline flat').classes('w-[174px] items-start'):
                    ui.html(message_icon)
                    ui.label('Help').classes('pl-2')
        with ui.column().classes('mx-auto w-[174px]'):
            with ui.link(target='/aquaterrius'):
                ui.button(icon='o_water', text='Aquaterrius').props('no-caps outline flat').classes('w-[174px] items-start')
            with ui.link(target='/bug_trap'):
                ui.button(icon='o_bug_report', text='Bug Traps').props('no-caps outline flat').classes('w-[174px] items-start')
            with ui.link(target='/carpo'):
                ui.button(icon='o_cloud', text='Carpo').props('no-caps outline flat').classes('w-[174px] items-start')
            if not app.storage.user.get('username', None):
                with ui.link(target='/login'):
                    ui.button(icon='login', text='Login', on_click=lambda: (app.storage.user.clear())).props('no-caps outline flat').classes('w-[174px] items-start')
            else:
                with ui.link(target='/'):
                    ui.button(icon='logout', text='Logout', on_click=lambda: (app.storage.user.clear())).props('no-caps outline flat').classes('w-[174px] items-start')
    with ui.column().classes('w-full bg-[#F8F3FE]'):
        yield

@contextmanager
def system_frame():
    ui.query('.nicegui-content').classes('p-0')
    ui.colors(primary='#4C4C4C', secondary='#53B689', accent='#111B1E', positive='#53B689', info='#FF6370')
    with ui.header().classes('md:justify-end justify-between bg-[#F8F3FE] p-0'):
        ui.button(on_click=lambda: left_drawer.toggle(),
                  icon='menu', color='grey-7').props('flat').classes('md:hidden mt-2')
        header()
    with ui.left_drawer(top_corner=True).props('width=254').classes('justify-between') as left_drawer:
        with ui.column().classes('mx-auto md:mt-4 w-[174px]'):
            ui.image('static/logos/Logo Aqua.png').classes('h-[66px] w-[51px] mx-auto mb-8')
            system_menu()
        with ui.column().classes('mx-auto md:mt-14 w-[174px]'):
            with ui.link(target='/aquaterrius'):
                ui.button(icon='login', text='Main Page', on_click=lambda: (app.storage.user.update({'system_id': None}))).props('no-caps outline flat').classes('w-[174px] items-start')
    with ui.column().classes('p-4 items-center md:items-start w-full bg-[#F8F3FE]'):
        yield