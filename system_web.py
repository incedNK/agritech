from nicegui import ui, app, APIRouter, events
import models
import theme
from datetime import datetime, timedelta, timezone
import asyncio
from PIL import Image
import os

system_router = APIRouter()

with open('static/svg_icons/icons8-valve.svg') as f:
    valve_icon = f.read()
with open('static/svg_icons/icons8-sensor.svg') as f:
    sensor_icon = f.read()
with open('static/svg_icons/icons8-stacked-organizational-chart-highlighted-parent-node.svg') as f:
    shift_icon = f.read()
with open('static/svg_icons/icons8-humidity.svg') as f:
    moist_icon = f.read()
with open('static/svg_icons/icons8-temperature.svg') as f:
    temp_icon = f.read()
with open('static/svg_icons/icons8-battery (2).svg') as f:
    half_bat_icon = f.read()
with open('static/svg_icons/icons8-battery (1).svg') as f:
    full_bat_icon = f.read()
with open('static/svg_icons/icons8-battery.svg') as f:
    bat_icon = f.read()

@system_router.page('/system')
def system():
    ui.add_head_html('''
        <style type="text/tailwindcss">
            @layer components {
                .red-circle {
                    @apply bg-[#FF7E86] w-[20px] h-[20px] text-center rounded-full text-white;
                }
                .green-circle {
                    @apply bg-[#70CF97] w-[20px] h-[20px] text-center rounded-full text-white;
                }
                .blue-circle {
                    @apply bg-[#2699FB] w-[20px] h-[20px] text-center rounded-full text-white;
                }
                .big-red-circle {
                    @apply bg-[#FF7E86] w-[28px] h-[28px] text-center text-xl rounded-full text-white;
                }
                .big-green-circle {
                    @apply bg-[#70CF97] w-[28px] h-[28px] text-center text-xl rounded-full text-white;
                }
                .big-blue-circle {
                    @apply bg-[#2699FB] w-[28px] h-[28px] text-center text-xl rounded-full text-white;
                }
            }
        </style>
    ''')
    def moisture_knob(value: int):
        if value < 45:
            knob_color='#FF7E86'
        elif value > 85:
            knob_color='#2699FB'
        else:
            knob_color='#70CF97'
        with ui.column().classes('gap-0 items-center'):
            ui.label('Soil Moisture').classes('text-xs text-gray-400 self-center')
            with ui.knob(value, min=0, max=140, color=knob_color, size='65px').props('angle=230 thickness=0.3 rounded'):
                ui.label(f'{round(value)}%').classes('text-primary text-sm font-bold')
            if value < 45:
                ui.label('Poor').classes('text-sm font-bold text-[#FF6370]/75 self-center')
            elif value > 85:
                ui.label('Flooded').classes('text-sm font-bold text-[#2699FB]/75 self-center')
            else:
                ui.label('Optimal').classes('text-sm font-bold text-[#70CF97]/75 self-center')

    def temperature_knob(value: int):
        if value > 40:
            knob_color='#ff8000'
        elif value < 10:
            knob_color='#2699FB'
        else:
            knob_color='#FF6370'
        with ui.column().classes('gap-0 items-center'):
            ui.label('Soil Temperature').classes('text-xs text-gray-400 self-center')
            with ui.knob(value, min=-20, max=60, color=knob_color, size='65px').props('angle=230 thickness=0.3 rounded'):
                ui.label(f'{round(value)}C').classes('text-primary text-sm font-bold')
            if value < 10:
                ui.label('Cold').classes('text-sm font-bold text-[#2699FB]/75 self-center')
            elif value > 40:
                ui.label('Hot').classes('text-sm font-bold text-[#ff8000]/75 self-center')
            else:
                ui.label('Moderate').classes('text-sm font-bold text-[#FF6370]/75 self-center')
    def create_system_log(id: int):
        db_log = models.Logs(dev_id=id, message=f'SystemID {id} is not responsive. Check if something goes wrong.',
                            disable=False, dev_code=1)
        models.session.add(db_log)
        models.session.commit()

    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    id = app.storage.user['system_id']
    system = models.session.query(models.System).filter(models.System.id == id).first()
    red_sensors = []
    green_sensors = []
    blue_sensors = []
    active_valves = []
    inactive_valves = []
    system_devs = [str(id)]
    system_logs = []
    
    pump_ids = []
    valve_ids = []
    sensor_ids = []
    system_id = str(id)
    for pump in system.system_pumps:
        pump_ids.append(pump.pump_id)
    for valve in system.system_valves:
        valve_ids.append(valve.valve_id)
    for sensor in system.system_sensors:
        sensor_ids.append(sensor.sensor_id)
    system_log = []
    pump_logs = []
    valve_logs = []
    sensor_logs = []
    all_logs = {'pumps':pump_logs, 'valves': valve_logs, 'sensors': sensor_logs, 'system': system_log}
    logs = models.session.query(models.Logs).order_by(models.Logs.date.desc()).all()
    for log in logs:
        if log.dev_id in pump_ids:
            pump_logs.append(log)
        if log.dev_id in valve_ids:
            valve_logs.append(log)
        if log.dev_id in sensor_ids:
            sensor_logs.append(log)
        if log.dev_id == system_id:
            system_log.append(log)
    
    system_last_comm = system.updated_at
    scheduled_system_response = system_last_comm + timedelta(minutes=180)
    if datetime.now().replace(tzinfo=timezone(offset=timedelta())) > scheduled_system_response:
        last_system_log = models.session.query(models.Logs).order_by(models.Logs.dev_id, models.Logs.date.desc()).filter(models.Logs.dev_id == str(id)).first()
        if not last_system_log:
            create_system_log(id=id)
        else:
            if datetime.now().replace(tzinfo=timezone(offset=timedelta())) > (last_system_log.date + timedelta(minutes=1440)):
                create_system_log(id=id)


    for pump in system.system_pumps:
        system_devs.append(pump.pump_id)
    for valve in system.system_valves:
        system_devs.append(valve.valve_id)
    for sensor in system.system_sensors:
        system_devs.append(sensor.sensor_id)
    logs = models.session.query(models.Logs).order_by(models.Logs.date.desc()).all()
    for log in logs:
        if log.dev_id in system_devs:
            system_logs.append(log)
    
    for sensor in system.system_sensors:
        if sensor.readings < 45:
            red_sensors.append(sensor)
        elif sensor.readings >= 45 and sensor.readings < 85:
            green_sensors.append(sensor)
        else:
            blue_sensors.append(sensor)
    for valve in system.system_valves:
        if valve.status:
            active_valves.append(valve)
        else:
            inactive_valves.append(valve)
    if system.owner != current_user.username and not current_user.admin:
        ui.notify('You are not allowed!', position='top', color='negative')
        ui.navigate.to('/')
    def shift_stats():
        active_shifts = []
        for shift in system.system_shifts:
            if shift.id not in active_shifts:
                active_shifts.append(shift.id)
            shift_sensors = []
            if shift.id in active_shifts:
                with ui.row().classes('w-full bg-white justify-center md:justify-between'):
                    with ui.column().classes('gap-0 p-2 items-center md:items-start'):
                        if shift.shift_name:
                            ui.label(f'Shift #{shift.shift_name}').classes('font-bold')
                        else:
                            ui.label(f'Shift #{shift.id}').classes('font-bold')
                        ui.label('Accompanied Valves:').classes('text-xs text-gray-400')

                        with ui.row().classes('no-wrap w-full justify-center md:justify-start'):
                            for section in shift.shifts_sections:
                                for controler in section.section_sensors:
                                    shift_sensors.append(controler.sensor_id)
                                with ui.column().classes('gap-0'):
                                    #ui.image('/static/icons/valve.png')
                                    ui.html(valve_icon)
                                    for valve in system.system_valves:
                                        if valve.valve_id == section.valve_id:
                                            if valve.valve_name:
                                                ui.label(valve.valve_name).classes('text-xs text-gray-400 self-center')
                                            else:
                                                ui.label(valve.valve_id).classes('text-xs text-gray-400 self-center')
                                    
                    with ui.row().classes('w-[450px] no-wrap justify-center'):
                        for sensor in system.system_sensors:
                            if sensor.sensor_id in shift_sensors:
                                with ui.column().classes('gap-0 p-2'):
                                    if sensor.sensor_name:
                                        ui.label(sensor.sensor_name).classes('text-xs text-gray-400 self-center')
                                    else:
                                        ui.label(sensor.sensor_id).classes('text-xs text-gray-400 self-center')
                                    with ui.row():
                                        moisture_knob(sensor.readings)
                                        temperature_knob(sensor.temp)
                    timer_settings = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
                    active_times = timer_settings[datetime.now().weekday()]
                    with ui.column().classes('w-[250px] p-2'):
                        for timer in shift.shift_timers:
                            if timer.Mon:
                                timer_settings[0].append({timer.starts: timer.stops})
                            if timer.Tue:
                                timer_settings[1].append({timer.starts: timer.stops})
                            if timer.Wed:
                                timer_settings[2].append({timer.starts: timer.stops})
                            if timer.Thu:
                                timer_settings[3].append({timer.starts: timer.stops})
                            if timer.Fri:
                                timer_settings[4].append({timer.starts: timer.stops})
                            if timer.Sat:
                                timer_settings[5].append({timer.starts: timer.stops})
                            if timer.Sun:
                                timer_settings[6].append({timer.starts: timer.stops})

                        if not active_times:
                            ui.label('No active timers!').classes('text-xs font-bold self-center')
                        else:
                            with ui.row().classes('w-full wrap justify-between p-2'):
                                ui.label('Start at:').classes('text-xs text-gray-400')
                                ui.label('Ends at:').classes('text-xs text-gray-400')
                            start_time = []
                            stop_time = []
                            for time in active_times:
                                for k,v in time.items():
                                    start_time.append(k)
                                    stop_time.append(v)
                                    if datetime.now().time()<k:
                                        with ui.row().classes('w-full no-wrap justify-between'):
                                            ui.label(k).classes('text-xs font-bold')
                                            ui.label(v).classes('text-xs font-bold')
                                        with ui.row().classes('justify-center'):
                                            ui.label('Starting at:').classes('text-xs text-gray-400')
                                            def timer_update() -> None:
                                                current_time = datetime.strptime(datetime.now().strftime('%H:%M:%S'), '%H:%M:%S')
                                                starting_at = datetime.strptime(k.strftime('%H:%M:%S'), '%H:%M:%S')
                                                x = starting_at - current_time
                                                if clock.text == x:
                                                    return
                                                clock.text = str(x)
                                                if starting_at < current_time:
                                                    ui.navigate.reload()
                                            clock = ui.label().classes('text-xs font-bold')
                                            ui.timer(1.0, callback=timer_update)

                                    if k< datetime.now().time() and datetime.now().time()<v:
                                        with ui.row().classes('w-full no-wrap justify-between'):
                                            ui.label(k).classes('text-xs font-bold')
                                            ui.label(v).classes('text-xs font-bold')
                                        with ui.column().classes('w-full'):
                                            start = k.hour*3600 + k.minute*60 + k.second
                                            stop = v.hour*3600 + v.minute*60 + v.second
                                            current = datetime.now().time().hour*3600 + datetime.now().time().minute*60 + datetime.now().time().second
                                            def update_timer_progress() -> None:
                                                current_time = datetime.strptime(datetime.now().strftime('%H:%M:%S'), '%H:%M:%S')
                                                x = current_time.time()
                                                timestamp = x.hour*3600 + x.minute*60 + x.second
                                                new_value = (1/(stop - start))*(timestamp - start)
                                                slider.set_value(new_value)

                                            ui.timer(1.0, callback=update_timer_progress)
                                            slider = ui.slider(min=start, max=stop, value=current)
                                            slider.visible = False
                                            ui.linear_progress(show_value=False, size='15px', color='#2699FB').bind_value_from(slider, 'value').props('rounded')

                                        with ui.row().classes('self-center'):
                                            ui.label('Time remain:').classes('text-xs text-gray-400')
                                            def timer_update() -> None:
                                                current_time = datetime.strptime(datetime.now().strftime('%H:%M:%S'), '%H:%M:%S')
                                                starting_at = datetime.strptime(v.strftime('%H:%M:%S'), '%H:%M:%S')
                                                x = starting_at - current_time
                                                if clock.text == x:
                                                    return
                                                clock.text = str(x)
                                                if starting_at < current_time:
                                                    ui.navigate.reload()
                                            clock = ui.label().classes('text-xs font-bold')
                                            ui.timer(1.0, callback=timer_update)
                                    if datetime.now().time()>v:
                                        with ui.column().classes('gap-1 w-full'):
                                            with ui.row().classes('w-full no-wrap justify-between'):
                                                ui.label(f'Timer-{timer.id}').classes('text-xs text-gray-400')
                                                ui.label(f'Finished at: {v}').classes('text-xs font-bold')

    with theme.system_frame():
        with ui.column().classes('md:hidden w-full h-[78px] bg-[#D3F9D8] justify-center rounded-lg'):
            with ui.row().classes('self-start'):
                ui.knob(1.0, color='green-400', center_color='green-500', size='48px').props('thickness=0.3').classes('ml-10')
                with ui.column().classes('gap-0'):
                    ui.label("Keep chillin'").classes('font-bold')
                    ui.label('All nodes are running smoothly.').classes('text-sm')
        with ui.column().classes('md:hidden w-full h-[78px] bg-[#D0EBFF] justify-center rounded-lg'):
            with ui.row().classes('justify-between w-full'):
                with ui.column().classes('gap-2 ml-10'):
                    ui.label('Sensor Status:').classes('text-gray-400')
                    with ui.row():
                        ui.label(len(red_sensors)).classes('red-circle')
                        ui.label(len(green_sensors)).classes('green-circle')
                        ui.label(len(blue_sensors)).classes('blue-circle')
                with ui.row().classes('justify-center mr-10'):
                    if not system.system_pumps:
                        ui.label('Water Cons.').classes('text-gray-600')
                        ui.label('No Active Pumps!').classes('font-bold text-red')
                    for pump in system.system_pumps:
                        last_flow = models.session.query(models.FlowData).order_by(
                            models.FlowData.pump_id, models.FlowData.date.desc()).filter(
                            models.FlowData.pump_id == pump.pump_id).first()
                        ui.echart({
                            'series': [{'type': 'pie',
                                        'color': ['#FFF2F3', '#FF6370'],
                                        'data': [
                                            {'value': pump.current, 'label': {'show': False},'labelLine': {'show': False}},
                                            {'value': pump.capacity-pump.current, 'label': {'show': False},'labelLine': {'show': False}}]
                                        }],
                            }).classes('w-[60px] h-[60px]')
                        with ui.column().classes('gap-0'):
                            ui.label('Water Cons.').classes('text-gray-600')
                            ui.label(f'{last_flow.flow_rate} qm').classes('font-bold text-red')
                            ui.label('Spent Today').classes('text-xs text-gray-400')
        with ui.column().classes('md:hidden'):
            shift_stats()
        with ui.row().classes('no-wrap p-2'):
            with ui.column().classes('max-sm:hidden w-[920px] p-2 '):
                with ui.row():
                    with ui.column().classes('w-[130px] h-[160px] gap-0 p-2 bg-white'):
                        ui.label('Sensors').classes('font-bold')
                        ui.label('Soil Moisture Status').classes('text-xs text-gray-400 mb-2')
                        with ui.column().classes('self-center'):
                            ui.label(len(green_sensors)).classes('big-green-circle text-sm self-center content-center')
                            with ui.row():
                                    ui.label(len(red_sensors)).classes('big-red-circle text-sm content-center')
                                    ui.label(len(blue_sensors)).classes('big-blue-circle text-sm content-center')
                    with ui.column().classes('w-[130px] h-[160px] gap-0 p-2 bg-white'):
                        ui.label('Valves').classes('font-bold')
                        ui.label('Activity Status').classes('text-xs text-gray-400 mb-2')
                        with ui.column().classes('self-center'):
                            ui.label(len(active_valves)).classes('big-green-circle text-sm content-center')
                            ui.label(len(inactive_valves)).classes('big-red-circle text-sm content-center')
                    with ui.column().classes('w-[610px] h-[160px] gap-0 bg-white'):
                        with ui.row().classes('w-full'):
                            with ui.column().classes('gap-0 pl-2 pt-2 w-[390px]'):
                                ui.label('Water Consumption').classes('font-bold')
                                ui.label('Daily Consumption').classes('text-xs text-gray-400 mb-2')
                                if system.system_pumps:
                                    dates = []
                                    flows = []
                                    for pump in system.system_pumps:
                                        flow_data = models.session.query(models.FlowData).filter(models.FlowData.pump_id == pump.pump_id).all()
                                        for data in flow_data:
                                            dates.append(data.date.strftime('%d/%m'))
                                            flows.append(data.flow_rate)
                                        ui.echart({
                                            'xAxis':{
                                                'data': dates
                                            },
                                            'yAxis': {},
                                            'series':[
                                                {
                                                    'type': 'bar',
                                                    'data': flows,
                                                    'barWidth': '20%',
                                                    'color': '#FF6370'
                                                }
                                            ]
                                        }).classes('w-[350px] h-[80px]')
                            with ui.column().classes('gap-0 p-2'):
                                ui.label('Currently Available').classes('text-xs text-gray-400')
                                if not system.system_pumps:
                                    ui.label('No active pumps.').classes('text-xs font-bold')
                                else:
                                    for pump in system.system_pumps:
                                        last_flow = models.session.query(models.FlowData).order_by(
                                                models.FlowData.pump_id, models.FlowData.date.desc()).filter(
                                                models.FlowData.pump_id == pump.pump_id).first()
                                        ui.label(f'{pump.capacity} / {pump.current} qubic m').classes('text-xs font-bold')
                                        ui.echart({
                                        'series': [{'type': 'pie',
                                            'color': ['#FFF2F3', '#FF6370'],
                                            'data': [
                                                {'value': pump.current, 'label': {'show': False},'labelLine': {'show': False}},
                                                {'value': pump.capacity-pump.current, 'label': {'show': False},'labelLine': {'show': False}}]
                                            }],
                                        }).classes('w-[80px] h-[80px] self-center')
                                        ui.label(f'{last_flow.flow_rate} qubic m').classes('font-bold text-red self-center')
                                        ui.label('Spent Today').classes('text-xs text-gray-400 self-center')
                ui.label('Irrigation Status').classes('font-bold text-lg ml-2')
                shift_stats()

            with ui.column().classes('max-sm:hidden w-[290px] h-screen bg-white'):
                with ui.row().classes('w-full no-wrap justify-between p-2 items-center'):
                    with ui.column().classes('gap-0'):
                        ui.label('Activity Monitor').classes('font-bold text-xl')
                        ui.label('Report Center').classes('text-xs text-gray-400')
                    ui.icon('more_vert').classes('text-2xl')
                with ui.column().classes('w-[280px] h-[78px] bg-[#D3F9D8] justify-center rounded-lg m-2'):
                    with ui.row().classes('self-start'):
                        ui.knob(1.0, color='green-400', center_color='green-500', size='48px').props('thickness=0.3').classes('ml-2')
                        with ui.column().classes('gap-0'):
                            ui.label("Keep chillin'").classes('font-bold')
                            ui.label('All nodes are running smoothly.').classes('text-sm')
                ui.label('Recent alerts').classes('text-xs text-gray-400 ml-2')
                ui.add_head_html('''
                    <style type="text/tailwindcss">
                        @layer components {
                            .log_red-circle {
                                @apply bg-[#FF6370] w-[30px] h-[30px] text-center rounded-full text-white;
                            }
                            .log_orange-circle {
                                @apply bg-[#FFAA71] w-[30px] h-[30px] text-center rounded-full text-white;
                            }
                            .log_green-circle {
                                @apply bg-[#70CF97] w-[30px] h-[30px] text-center rounded-full text-white;
                            }
                        }
                    </style>
                ''')
                if len(system_logs) >3:
                    log_range = 3
                else:
                    log_range =len(system_logs)
                for i in range(log_range):
                    with ui.column().classes('gap-0 w-full m-2 p-2'):
                        with ui.row().classes('no-wrap'):
                            if system_logs[i] in all_logs['pumps']: 
                                with ui.row().classes('w-[40px]'):   
                                    if system_logs[i].dev_code == 3:
                                        with ui.label().classes('log_green-circle content-center'):
                                            ui.image('/static/icons/pump.png').classes('w-[20px] h-[20px]')
                                    elif system_logs[i].dev_code == 2:
                                        with ui.label().classes('log_orange-circle content-center'):
                                            ui.image('/static/icons/pump.png').classes('w-[20px] h-[20px]')
                                    else:
                                        with ui.label().classes('log_red-circle content-center'):
                                            ui.image('/static/icons/pump.png').classes('w-[20px] h-[20px]')
                                with ui.column().classes('gap-0'):
                                    ui.label(system_logs[i].message).classes('text-xs text-gray-400')
                                    ui.label(f'{system_logs[i].date.strftime("%b %d, %Y")} | {system_logs[i].date.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')
                            if system_logs[i] in all_logs['valves']:
                                with ui.row().classes('w-[40px]'):
                                    if system_logs[i].dev_code == 3:
                                        with ui.label().classes('log_green-circle content-center'):
                                            ui.image('/static/icons/valve-white.png').classes('w-[20px] h-[20px]')
                                    elif system_logs[i].dev_code == 2:
                                        with ui.label().classes('log_orange-circle content-center'):
                                            ui.image('/static/icons/valve-white.png').classes('w-[20px] h-[20px]')
                                    else:
                                        with ui.label().classes('log_red-circle content-center'):
                                            ui.image('/static/icons/valve-white.png').classes('w-[20px] h-[20px]')
                                with ui.column().classes('gap-0'):
                                    ui.label(system_logs[i].message).classes('text-xs text-gray-400')
                                    ui.label(f'{system_logs[i].date.strftime("%b %d, %Y")} | {system_logs[i].date.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')
                            if system_logs[i] in all_logs['sensors']:
                                with ui.row().classes('w-[40px]'):
                                    if system_logs[i].dev_code == 3:
                                        with ui.label().classes('log_green-circle content-center'):
                                            ui.image('/static/icons/sensor-white.png').classes('w-[20px] h-[20px]')
                                    elif system_logs[i].dev_code == 2:
                                        with ui.label().classes('log_orange-circle content-center'):
                                            ui.image('/static/icons/sensor-white.png').classes('w-[20px] h-[20px]')
                                    else:
                                        with ui.label().classes('log_red-circle content-center'):
                                            ui.image('/static/icons/sensor-white.png').classes('w-[20px] h-[20px]')
                                with ui.column().classes('gap-0'):
                                    ui.label(system_logs[i].message).classes('text-xs text-gray-400')
                                    ui.label(f'{system_logs[i].date.strftime("%b %d, %Y")} | {system_logs[i].date.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')
                            if system_logs[i] in all_logs['system']:
                                with ui.row().classes('w-[50px]'):
                                    ui.label('!').classes('log_red-circle content-center font-bold text-lg text-white')
                                with ui.column().classes('gap-0'):
                                    ui.label(system_logs[i].message).classes('text-xs text-gray-400')
                                    ui.label(f'{system_logs[i].date.strftime("%b %d, %Y")} | {system_logs[i].date.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')
                            print(system_logs[i].message)
                            #ui.label(f'{system_logs[i].dev_id} -').classes('font-bold text-xs')
                            #ui.label(system_logs[i].message).classes('text-xs text-gray-400')
                            #ui.label(f'{system_logs[i].date.strftime("%b %d, %Y")} | {system_logs[i].date.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')


@system_router.page('/sensors')
def sensors():
    id = app.storage.user['system_id']
    system = models.session.query(models.System).filter(models.System.id == id).first()
    def moisture_knob(value: int, knob_size: int):
        if value < 45:
            knob_color='#FF7E86'
        elif value > 85:
            knob_color='#2699FB'
        else:
            knob_color='#70CF97'
        with ui.column().classes('gap-0'):
            with ui.knob(value, min=0, max=140, color=knob_color, size=f'{knob_size}px').props('angle=230 thickness=0.3 rounded'):
                ui.label(f'{value}%').classes('text-primary text-sm font-bold')
            if value < 45:
                ui.label('Poor').classes('text-sm font-bold text-[#FF6370]/75 self-center')
            elif value > 85:
                ui.label('Flooded').classes('text-sm font-bold text-[#2699FB]/75 self-center')
            else:
                ui.label('Optimal').classes('text-sm font-bold text-[#70CF97]/75 self-center')

    def temperature_knob(value: int, knob_size: int):
        if value > 40:
            knob_color='#ff8000'
        elif value < 10:
            knob_color='#2699FB'
        else:
            knob_color='#FF6370'
        with ui.column().classes('gap-0'):
            with ui.knob(value, min=-20, max=60, color=knob_color, size=f'{knob_size}px').props('angle=230 thickness=0.3 rounded'):
                ui.label(f'{value} C').classes('text-primary text-sm font-bold')
            if value < 10:
                ui.label('Cold').classes('text-sm font-bold text-[#2699FB]/75 self-center')
            elif value > 40:
                ui.label('Hot').classes('text-sm font-bold text-[#ff8000]/75 self-center')
            else:
                ui.label('Moderate').classes('text-sm font-bold text-[#FF6370]/75 self-center')

    async def edit_sensor(id: str, l1: bool, l2: bool, l3: bool):
        sensor_setting = {
                'set_lvl_1': l1,
                'set_lvl_2': l2,
                'set_lvl_3': l3,
                'updated_at': datetime.now()
                }
        sensor_query = models.session.query(models.Sensor).filter(models.Sensor.sensor_id == id)
        sensor_query.update(sensor_setting)
        models.session.commit()
        data = models.session.query(models.SensorData).order_by(models.SensorData.sensor_id, models.SensorData.date.desc()).filter(
                    models.SensorData.sensor_id == id).first()
        readings = {'level_1': data.level_1, 'level_2': data.level_2, 'level_3': data.level_3}
        temp = {'temp_1': data.temp_1, 'temp_2': data.temp_2, 'temp_3': data.temp_3}
        settings = {'level_1': l1, 'level_2': l2, 'level_3': l3}
        temp_level = {'temp_1': l1, 'temp_2': l2, 'temp_3': l3}
        user_setting = [f'level_{i}' for i in range(1, 4) if settings[f'level_{i}']]
        temp_setting = [f'temp_{i}' for i in range(1, 4) if temp_level[f'temp_{i}']]
        z = len(temp_setting)
        y = len(user_setting)
        new_reading = 0
        new_temp = 0
        for x in user_setting:
            new_reading += readings[x]/y
        for v in temp_setting:
            new_temp += temp[v]/z
        query_readings = models.session.query(models.Sensor).filter(
                    models.Sensor.sensor_id == id)
        query_readings.update({'readings': new_reading, 'temp': new_temp})
        models.session.commit()
        ui.notify('Settings changed succesfully', position='top', color='positive')
        await asyncio.sleep(3)
        ui.navigate.reload()
    
    async def change_sensor(id: str, name: str):
        sensor_query = models.session.query(models.Sensor).filter(models.Sensor.sensor_id == id)
        sensor_query.update({'sensor_name': name})
        models.session.commit()
        sensor_dialog.close()
        ui.notify('Settings changed succesfully', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()

    with theme.system_frame():
        ui.label('Sensors').classes('font-bold md:text-2xl ')
        for sensor in system.system_sensors:
            last_data = models.session.query(models.SensorData).order_by(models.SensorData.sensor_id, models.SensorData.date.desc()).filter(
                    models.SensorData.sensor_id == sensor.sensor_id).first()
            with ui.dialog() as edit_sensor_dialog, ui.card():
                with ui.row().classes('justify-between w-full'):
                    ui.label('Edit Sensor').classes('font-bold md:text-lg')
                    ui.button(icon='close', on_click=edit_sensor_dialog.close).props('outline flat')
                with ui.row().classes('justify-between items-center'):
                    ui.label('Sensor name:').classes('md:text-lg')
                    new_name = ui.input(sensor.sensor_name)
                ui.button(color='#FF6370', text='Save', on_click=lambda my_sensor=sensor, sensor_name=new_name: change_sensor(id=my_sensor.sensor_id, name=sensor_name.value)).props('no-caps rounded-lg').classes('text-white self-center w-full')
           
                
            with ui.dialog().props('persistent') as sensor_setting_dialog, ui.card():
                with ui.column():
                    with ui.row().classes('w-full no-wrap justify-between'):
                        with ui.column().classes('gap-0'):
                            ui.label('Select sensor settings').classes('font-bold md:text-lg')
                            ui.label('Select from the list below:').classes('text-gray-400')
                        ui.icon('more_vert').classes('text-xl p-2')
                    level_1 = ui.checkbox('7 cm', value=sensor.set_lvl_1 ).props('color=red-4')
                    level_2 = ui.checkbox('20 cm', value=sensor.set_lvl_2).props('color=red-4')
                    level_3 = ui.checkbox('40 cm', value=sensor.set_lvl_3).props('color=red-4')
                with ui.row().classes('no-wrap justify-between p-2 w-full'):
                    ui.button('Change settings', color='#FF6370', on_click=lambda my_sensor = sensor, l1 = level_1, l2 = level_2, l3 = level_3:
                            edit_sensor(id=my_sensor.sensor_id, l1=l1.value, l2=l2.value, l3=l3.value)).props('no-caps rounded-lg dense').classes('p-2 text-white')
                    ui.button('Close', on_click=sensor_setting_dialog.close).props('no-caps rounded-lg dense').classes('p-2')
            
            with ui.dialog() as sensor_dialog, ui.card():
                ui.label('Select what should be changed:').classes('font-bold md:text-lg')
                with ui.row().classes('justify-between items-center w-full'):
                    ui.button('Change name', color='#FF6370', on_click=edit_sensor_dialog.open).props('no-caps dense').classes('text-white')
                    ui.button('Change settings', on_click=sensor_setting_dialog.open).props('no-caps dense').classes('text-white')
            
            with ui.dialog().props('persistent maximized') as chart_dialog, ui.card():
                with ui.row().classes('w-full justify-between'):
                    ui.label(f'Sensor {sensor.sensor_id} data chart').classes('font-bold text-xl text-[#FF6370]')
                    ui.button(icon='close', color='#FF6370', on_click=chart_dialog.close).props('dense rounded').classes('text-white')
                x = []
                y_lvl1 = []
                y_lvl2 = []
                y_lvl3 = []
                y_temp1 = []
                y_temp2 = []
                y_temp3 = []
                y_moisture = []
                y_temperature = []
                data = models.session.query(models.SensorData).filter(models.SensorData.sensor_id == sensor.sensor_id).all()
                for date in data:
                    x.append(date.date.strftime('%d-%m-%Y %H:%M'))
                    y_lvl1.append(date.level_1)
                    y_lvl2.append(date.level_2)
                    y_lvl3.append(date.level_3)
                    y_temp1.append(date.temp_1)
                    y_temp2.append(date.temp_2)
                    y_temp3.append(date.temp_3)
                    y_moisture.append(date.moisture)
                    y_temperature.append(date.temperature)
                ui.echart({
                    'xAxis': {'data': x},
                    'yAxis': {},
                    'legend': {
                        'textStyle': {'color': 'gray'},
                        'orient': 'vertical',
                        'right': 10,
                        'top': 'center'
                        },
                    'series': [{
                        'name': 'moist 7 cm',
                        'data': y_lvl1,
                        'type': 'line'
                    },
                    {
                        'name': 'moist 20 cm',
                        'data': y_lvl2,
                        'type': 'line'
                    },
                    {
                        'name': 'moist 40 cm',
                        'data': y_lvl3,
                        'type': 'line'
                    },
                    {
                        'name': 'temp 7 cm',
                        'data': y_temp2,
                        'type': 'line'
                    },
                    {
                        'name': 'temp 20 cm',
                        'data': y_temp2,
                        'type': 'line'
                    },
                    {
                        'name': 'temp 40 cm',
                        'data': y_temp3,
                        'type': 'line'
                    },
                    {
                        'name': 'Moisture',
                        'data': y_moisture,
                        'type': 'line'
                    },
                    {
                        'name': 'Temperature',
                        'data': y_temperature,
                        'type': 'line'
                    },
                    ]
                }).classes('h-full')
            with ui.row().classes('w-full justify-between md:no-wrap bg-white p-2 mb-4'):
                with ui.column().classes('gap-1 p-2 w-full md:w-[200px] items-center md:items-start'):
                    with ui.row().classes('justify-between'):
                        with ui.row().classes('self-start gap-1'):
                            ui.label('Sensor').classes('font-bold md:text-lg')
                            if sensor.sensor_name:
                                ui.label(sensor.sensor_name).classes('font-bold md:text-lg')
                            else:
                                ui.label(sensor.sensor_id).classes('font-bold md:text-lg')
                        ui.button(icon='edit', color='#FF6370', on_click=sensor_dialog.open).props('size=xs rounded-lg').classes('w-[20px] text-white')
                    ui.label('Last Communication:').classes('font-bold text-gray-400')
                    ui.label(f'{sensor.updated_at.strftime("%b %d, %Y")} | {sensor.updated_at.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')
                with ui.column().classes('gap-1 p-2 w-full md:w-[280px] items-center'):
                    ui.label('Soil Moisture Probe').classes('self-center text-gray-400')
                    with ui.row():
                        with ui.column().classes('gap-0 items-center'):
                            ui.label('7 cm').classes('self-center text-gray-400')
                            moisture_knob(round(last_data.level_1), knob_size=65)
                        with ui.column().classes('gap-0'):
                            ui.label('20 cm').classes('self-center text-gray-400')
                            moisture_knob(round(last_data.level_2), knob_size=65)
                        with ui.column().classes('gap-0'):
                            ui.label('40 cm').classes('self-center text-gray-400')
                            moisture_knob(round(last_data.level_3), knob_size=65)
                with ui.column().classes('gap-1 p-2 w-full md:w-[280px] items-center'):
                    ui.label('Soil Temperature Probe').classes('self-center text-gray-400')
                    with ui.row():
                        with ui.column().classes('gap-0 items-center'):
                            ui.label('7 cm').classes('self-center text-gray-400')
                            temperature_knob(round(last_data.temp_1), knob_size=65)
                        with ui.column().classes('gap-0'):
                            ui.label('20 cm').classes('self-center text-gray-400')
                            temperature_knob(round(last_data.temp_2), knob_size=65)
                        with ui.column().classes('gap-0'):
                            ui.label('40 cm').classes('self-center text-gray-400')
                            temperature_knob(round(last_data.temp_3), knob_size=65)
                with ui.column().classes('p-2 w-full md:w-[250px] items-center'):
                    ui.label('Air Humidity & Temperature').classes('self-center text-gray-400')
                    with ui.row().classes('items-center'):
                        with ui.column().classes('self-center p-2'):
                            with ui.row().classes('gap-1 items-center'):
                                #ui.icon('speed', color='gray-500', size='24px')
                                ui.html(moist_icon)
                                ui.label(f'{last_data.moisture} %').classes('font-bold text-gray-500')
                            with ui.row().classes('gap-1 items-center'):
                                #ui.icon('thermostat', color='gray-500', size='24px')
                                ui.html(temp_icon)
                                ui.label(f'{last_data.temperature} C').classes('font-bold text-gray-500')
                        with ui.row().classes('gap-1 p-2 items-center'):
                            #ui.icon('battery_3_bar', color='gray-500', size='24px')
                            if last_data.bat_level > 80:
                                ui.html(full_bat_icon)
                            elif last_data.bat_level < 20:
                                ui.html(bat_icon)
                            else:
                                ui.html(half_bat_icon)
                            ui.label(f'{last_data.bat_level} %').classes('font-bold text-gray-500')
                with ui.row().classes('w-full md:w-[150px] justify-center md:self-center'):
                    ui.button(icon='show_chart', text='See Chart', color='#FF6370', on_click=chart_dialog.open).props('no-caps dense').classes('text-white mr-2')

@system_router.page('/valves')
def valves():
    id = app.storage.user['system_id']
    system = models.session.query(models.System).filter(models.System.id == id).first()
    pumps = system.system_pumps
    all_valves = system.system_valves
    with theme.system_frame():
        ui.label('Pump').classes('font-bold md:text-2xl ')
        for pump in pumps:
            async def update_pump():
                pump_volume = {
                    'current': current.value,
                    'updated_at': datetime.now()
                }
                pump_query = models.session.query(models.Pump).filter(models.Pump.pump_id == pump.pump_id)
                pump_query.update(pump_volume)
                models.session.commit()
                ui.notify('Settings changed succesfully', position='top', color='positive')
                await asyncio.sleep(3)
                ui.navigate.reload()
                
            async def change_pump(id: str, name: str):
                pump_query = models.session.query(models.Pump).filter(models.Pump.pump_id == id)
                pump_query.update({'pump_name': name})
                models.session.commit()
                ui.notify('Settings changed succesfully', position='top', color='positive')
                await asyncio.sleep(2)
                ui.navigate.reload()
            
            async def change_valve(id: str, name: str):
                valve_query = models.session.query(models.Valve).filter(models.Valve.valve_id == id)
                valve_query.update({'valve_name': name})
                models.session.commit()
                ui.notify('Settings changed succesfully', position='top', color='positive')
                await asyncio.sleep(2)
                ui.navigate.reload()

            with ui.dialog().props('persistent') as dialog, ui.card():
                with ui.column():
                    with ui.row().classes('w-full no-wrap justify-between'):
                        with ui.column().classes('gap-0'):
                            ui.label('Change Available Volume').classes('font-bold md:text-lg')
                            ui.label('Update Current Water Quantity:').classes('text-gray-400')
                        ui.icon('more_vert').classes('text-xl p-2')
                    current = ui.number('Current Volume', value=pump.current).classes('w-full')
                    with ui.row().classes('justify-between w-full'):
                        ui.button('Change settings', color='#FF6370', on_click=update_pump).props('no-caps rounded-lg dense').classes('p-2 text-white')
                        ui.button('Close', on_click=dialog.close).props('no-caps rounded-lg dense').classes('p-2')

            with ui.dialog() as edit_pump_dialog, ui.card():
                with ui.row().classes('justify-between w-full'):
                    ui.label('Edit Pump').classes('font-bold md:text-lg')
                    ui.button(icon='close', on_click=edit_pump_dialog.close).props('outline flat')
                with ui.row().classes('justify-between items-center'):
                    ui.label('Pump name:').classes('md:text-lg')
                    new_name = ui.input(pump.pump_name)
                ui.button(color='#FF6370', text='Save', on_click=lambda my_pump=pump, pump_name=new_name: 
                    change_pump(id=my_pump.pump_id, name=pump_name.value)).props('no-caps rounded-lg').classes('text-white self-center w-full')
            
            with ui.row().classes('w-full justify-between md:no-wrap bg-white p-2 mb-4'):
                with ui.column().classes('gap-0 items-center md:items-start w-full md:w-[250px]'):
                    with ui.row():
                        ui.label('System Pump').classes('font-bold md:text-lg')
                        if pump.pump_name:
                            ui.label(pump.pump_name).classes('font-bold md:text-lg')
                        else:
                            ui.label(pump.pump_id).classes('font-bold md:text-lg')
                        ui.button(icon='edit', color='#FF6370', on_click=edit_pump_dialog.open).props('size=xs rounded-lg').classes('w-[20px] text-white')
                    ui.label('Last Communication:').classes('font-bold text-gray-400')
                    ui.label(f'{pump.updated_at.strftime("%b %d, %Y")} | {pump.updated_at.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')
                with ui.column().classes('items-center w-full md:w-[400px]'):
                    ui.echart({
                        'legend': {
                            'orient': 'vertical',
                            'x': 'right',
                        },
                        'series': [{'type': 'pie',
                                    'color': ['#FF6370', '#FFF2F3'],
                                    'data': [
                                        {'name': 'Available', 'value': pump.current, 'label': {'show': False},'labelLine': {'show': False}},
                                        {'name': 'Spent', 'value': pump.capacity-pump.current, 'label': {'show': False},'labelLine': {'show': False}}]
                                            }],
                        }).classes('w-[250px] h-[150px]')
                with ui.column().classes('items-center w-full md:w-[300px] md:items-end gap-1'):
                    with ui.row():
                        ui.label('Available quantity:').classes('text-gray-400')
                        ui.label(f'{pump.current} qm').classes('font-bold text-[#FF6370]')
                    with ui.row():
                        ui.label('Total capacity:').classes('text-gray-400')
                        ui.label(f'{pump.capacity} qm').classes('font-bold')
                    with ui.button(color='#FF6370', on_click=dialog.open).props('no-caps rounded-lg dense').classes('p-2 text-white'):
                        ui.image('static/icons/pump.png').classes('w-[30px] h-[30px] mr-2')
                        ui.label('Change quantity')

        ui.label('Valves').classes('font-bold md:text-2xl ')
        ui.add_head_html('''
            <style type="text/tailwindcss">
                @layer components {
                    .red-circle {
                        @apply bg-[#FF6370] w-[30px] h-[30px] text-center rounded-full text-white;
                    }
                    .green-circle {
                        @apply bg-[#70CF97] w-[30px] h-[30px] text-center rounded-full text-white;
                    }
                }
            </style>
        ''')
        for valve in all_valves:
            with ui.row().classes('w-full bg-white justify-center md:justify-between m-2'):
                with ui.dialog() as edit_valve_dialog, ui.card():
                    with ui.row().classes('justify-between w-full'):
                        ui.label('Edit Valve').classes('font-bold md:text-lg')
                        ui.button(icon='close', on_click=edit_valve_dialog.close).props('outline flat')
                    with ui.row().classes('justify-between items-center'):
                        ui.label('Valve name:').classes('md:text-lg')
                        new_name = ui.input(valve.valve_name)
                    ui.button(color='#FF6370', text='Save', on_click=lambda my_valve=valve, valve_name=new_name: 
                        change_valve(id=my_valve.valve_id, name=valve_name.value)).props('no-caps rounded-lg').classes('text-white self-center w-full')
                # with ui.card().classes('w-[320px] h-[380px] rounded-xl'):
                #     with ui.row().classes('w-full no-wrap justify-between p-2 items-center'):
                #         with ui.avatar():
                #             ui.image('static/logos/Logo Aqua.png').classes('w-[25px] h-[30px] text-white')
                #         ui.icon('more_vert').classes('text-2xl')
                #     with ui.column().classes('w-full items-center pt-2'):
                #         ui.image('static/icons/valve.png').classes('w-[80px] h-[80px] itmes-center rounded-full')
                #         ui.label(valve.valve_id).classes('text-2xl font-bold mb-2')
                #         with ui.row():
                #             ui.label('Current Status:').classes('text-gray-400')
                #             if valve.status:
                #                 ui.label('OPEN').classes('font-bold text-green-500')
                #             else:
                #                 ui.label('CLOSED').classes('font-bold text-red-500')
                #     with ui.row().classes('w-full items-center p-2'):
                #         ui.icon('arrow_circle_right', color='red').classes('text-xl')
                #         with ui.column().classes('p-2 gap-0'):
                #             ui.label('Last communication:').classes('font-bold text-sm')
                #             ui.label(f'{valve.updated_at.strftime("%b %d, %Y")} | {valve.updated_at.strftime("%I:%M:%S %p")}').classes('text-sm')
                with ui.column().classes('gap-0 items-center md:items-start w-full md:w-[250px]'):
                    with ui.row():
                        ui.label('Valve').classes('font-bold md:text-lg')
                        if valve.valve_name:
                            ui.label(valve.valve_name).classes('font-bold md:text-lg')
                        else:
                            ui.label(valve.valve_id).classes('font-bold md:text-lg')
                        ui.button(icon='edit', color='#FF6370', on_click=edit_valve_dialog.open).props('size=xs rounded-lg').classes('w-[20px] text-white')
                    ui.label('Last Communication:').classes('font-bold text-gray-400')
                    ui.label(f'{valve.updated_at.strftime("%b %d, %Y")} | {valve.updated_at.strftime("%I:%M:%S %p")}').classes('text-xs text-gray-400')
                with ui.column().classes('items-center mr-3'):
                    ui.label('Current Status').classes('font-bold text-gray-400')
                    with ui.row().classes('self-center'):
                        if valve.status:
                            ui.label().classes('green-circle')
                            ui.label('Open').classes('font-bold self-center')
                        else:
                            ui.label().classes('red-circle')
                            ui.label('Closed').classes('font-bold self-center')

@system_router.page('/shifts')
def shifts():
    id = app.storage.user['system_id']
    system = models.session.query(models.System).filter(models.System.id == id).first()
    shifts = system.system_shifts
    sections = models.session.query(models.Section).all()
    async def add_new_shift():
        db_shift = models.Shift(system_id=id, created_at=datetime.now(), updated_at=datetime.now())
        models.session.add(db_shift)
        models.session.commit()
        ui.notify('Adding new Shift. Please wait...', position='top', color='positive')
        await asyncio.sleep(3)
        ui.navigate.reload()
    async def delete_shift(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_shift = models.session.query(models.Shift).filter(models.Shift.id == id)
            existing_shift.delete()
            models.session.commit()
            ui.notify('Deleting Shift. Please wait...', position='top', color='negative')
            await asyncio.sleep(3)
            ui.navigate.reload()
    async def add_valve(id: int):
        valve_id = await section_dialoge
        if valve_id.value == None:
            ui.notify('No selected valve!', position='top', color='negative')
        else:
            db_section = models.Section(shift_id=id, valve_id=valve_id.value, updated_at=datetime.now())
            models.session.add(db_section)
            models.session.commit()
            ui.notify('Adding new Valve. Please wait...', position='top', color='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()
    async def add_sensor(id: int):
        sensor_id = await sensor_dialog
        sensors_list = []
        section_sensors = models.session.query(models.SensorControler).filter(
                models.SensorControler.section_id == id).all()
        for dev in section_sensors:
            sensors_list.append(dev.sensor_id)
        if sensor_id.value in sensors_list:
            ui.notify('Sensor already exist!', position='top', color='negative')
        else:
            db_controler = models.SensorControler(section_id=id, sensor_id=sensor_id.value, updated_at=datetime.now())
            models.session.add(db_controler)
            models.session.commit()
            ui.notify('Adding new Sensor. Please wait...', position='top', color='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()
    async def change_settings(id: int, min: float, max: float, sensors_settings: str):
        data = {'id': id, 'starts_at': min, 'stops_at': max, 'sensors_settings': sensors_settings}
        existing_section = models.session.query(models.Section).filter(models.Section.id == id)
        existing_section.update(data)
        models.session.commit()
        ui.notify('Succesfully updated', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def remove_valve(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_section = models.session.query(models.Section).filter(models.Section.id == id)
            existing_section.delete()
            models.session.commit()
            ui.notify('Deleteing Valve. Please wait...', position='top', color='negative')
            await asyncio.sleep(2)
            ui.navigate.reload()
    async def change_shift(id: str, name: str):
        shift_query = models.session.query(models.Shift).filter(models.Shift.id == id)
        shift_query.update({'shift_name': name})
        models.session.commit()
        ui.notify('Changing Settings. Please wait...', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()

    with theme.system_frame():
        ui.add_head_html('''
            <style type="text/tailwindcss">
                @layer components {
                    .light-gray-circle {
                        @apply bg-[#A4A5A6] w-[30px] h-[30px] pl-1.5 pt-1 rounded-full text-white;
                    }
                    .dark-gray-circle {
                        @apply bg-[#5F6165] w-[30px] h-[30px] pl-1.5 pt-1 rounded-full text-white;
                    }
                }
            </style>
        ''')
        ui.label('Shifts').classes('font-bold md:text-2xl ')
        for shift in shifts:
            system_sections = []
            for part in sections:
                system_sections.append(part.valve_id)
            my_shift = shift
            valves = {}
            section_sensors = {}
            for valve in system.system_valves:
                if valve.valve_id not in system_sections:
                    valves.update({valve.valve_id: f'Valve {valve.valve_name}'})
            for sensor in system.system_sensors:
                section_sensors.update({sensor.sensor_id: f'Sensor {sensor.sensor_id}'})
            with ui.dialog() as section_dialoge, ui.card():
                with ui.column().classes('gap-0 p-2'):
                    with ui.row().classes('w-[350px] justify-between'):
                        ui.label('Available Valves').classes('text-xl font-bold')
                        ui.button(icon='close', on_click=section_dialoge.close).props('outline flat')
                    ui.label('Select from the list below:').classes('text-gray-400')
                if valves:
                    valveID = ui.radio(valves).props('color=red unchecked-icon=check_box_outline_blank')
                else:
                    ui.label('There is no available valves').classes('text-gray-400 self-center')
                ui.button(color='#FF6370', text='Save', on_click=lambda: section_dialoge.submit(valveID)).props('no-caps rounded-lg').classes('text-white mt-10 self-center w-[125px]')
            with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
                with ui.column():
                    ui.label('Are you sure you want to delete item?')
                    with ui.row().classes('self-center'):
                        ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                        ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
            
            with ui.dialog() as sensor_dialog, ui.card():
                with ui.column().classes('gap-0 p-2'):
                    with ui.row().classes('w-[350px] justify-between'):
                        ui.label('Available Sensors').classes('text-xl font-bold')
                        ui.button(icon='close', on_click=sensor_dialog.close).props('outline flat')
                    ui.label('Select from the list below:').classes('text-gray-400')
                sensorID = ui.radio(section_sensors).props('color=red unchecked-icon=check_box_outline_blank')
                ui.button(color='#FF6370', text='Save', on_click=lambda: sensor_dialog.submit(sensorID)).props('no-caps rounded-lg').classes('text-white mt-10 self-center w-[125px]')

            with ui.dialog() as edit_shift_dialog, ui.card():
                with ui.row().classes('justify-between w-full'):
                    ui.label('Edit Shift').classes('font-bold md:text-lg')
                    ui.button(icon='close', on_click=edit_shift_dialog.close).props('outline flat')
                with ui.row().classes('justify-between items-center'):
                    ui.label('Shift name:').classes('md:text-lg')
                    new_name = ui.input(shift.shift_name)
                ui.button(color='#FF6370', text='Save', on_click=lambda edit_shift=my_shift, shift_name=new_name: 
                    change_shift(id=edit_shift.id, name=shift_name.value)).props('no-caps rounded-lg').classes('text-white self-center w-full')
            
            with ui.column().classes('w-full gap-0 bg-white'):
                with ui.row().classes('w-full justify-center md:justify-between md:no-wrap bg-white p-2 mb-4'):
                    with ui.column().classes('gap-1 p-2 md:w-[200px] items-center md:items-start'):
                        with ui.row().classes('justify-between'):
                            with ui.row().classes('self-start gap-1'):
                                ui.label('Shift').classes('font-bold md:text-lg')
                                if my_shift.shift_name:
                                    ui.label(my_shift.shift_name).classes('font-bold md:text-lg')
                                else:
                                    ui.label(my_shift.id).classes('font-bold md:text-lg')
                            ui.button(icon='edit', color='#FF6370', on_click=edit_shift_dialog.open).props('size=xs rounded').classes('w-[20px] text-white')
                        ui.label('Accompanied Valves:').classes('font-bold text-gray-400')
                    with ui.button(color='#F8F3FE', on_click=lambda new_shift=my_shift: delete_shift(id=new_shift.id)).props('no-caps flat'):
                        ui.icon('delete', size='25px').classes('mx-2 text-[#FF6370]')
                for section in my_shift.shifts_sections:
                    with ui.row().classes('w-full md:no-wrap justify-center md:justify-around bg-white p-2 mb-4'):
                        with ui.row().classes('md:w-[400px] no-wrap justify-center self-center'):
                            #ui.image('static/icons/valve.png').classes('w-[30px] h-[30px] itmes-center rounded-full')
                            ui.html(valve_icon)
                            for valve in system.system_valves:
                                if valve.valve_id == section.valve_id:
                                    if valve.valve_name:
                                        ui.label(f'Valve #{valve.valve_name}').classes('p-1')
                                    else:
                                        ui.label(f'Valve #{section.valve_id}').classes('p-1')
                            ui.button(icon='delete', color='#FF6370', on_click=lambda id = section.id: remove_valve(id)).props('size=xs rounded').classes('w-[20px] text-white self-center')
                        with ui.row().classes('md:w-[800px] justify-around'):
                            if section:
                                with ui.dialog().props('full-width') as settings_dialog, ui.row(), ui.card().classes('w-[600px] mx-auto'):
                                    setup = models.session.query(models.Section).filter(models.Section.id == section.id).first()
                                    with ui.column().classes('w-full gap-0 p-2'):
                                        with ui.row().classes('w-full justify-between'):
                                            ui.label('Shift Settings').classes('text-xl font-bold')
                                            ui.button(icon='close', on_click=settings_dialog.close).props('outline flat')
                                        ui.label('Set parameters for Autonomous Operation Mode').classes('text-gray-400')
                                        with ui.row().classes('items-center'):
                                            ui.label('Autonomous Operation Mode').classes('bg-gray-600 text-white p-4')
                                            ui.label('Readings').classes('text-gray-400')
                                    with ui.row().classes('w-full justify-between no-wrap'):
                                        with ui.column():
                                            ui.label('Specify Soil Moisture Level for Irrigation Start:').classes('font-bold')
                                            if setup.starts_at == None:
                                                starts = 50
                                            else:
                                                starts = setup.starts_at
                                            if setup.stops_at == None:
                                                stops = 75
                                            else:
                                                stops = setup.stops_at
                                            model = {'range': {'min': starts, 'max': stops}}
                                            with ui.row().classes('items-center justify-center w-full'):
                                                min_value = ui.number(min=0, max=100, on_change=lambda e: model.update(range={'min': e.value, 'max': model['range']['max']})
                                                                      ).bind_value_from(model, 'range', lambda range: range['min']).classes('w-[50px] self-center')
                                                ui.label('%')
                                            ui.label('Specify Soil Moisture Level for Irrigation End:').classes('font-bold')
                                            with ui.row().classes('items-center justify-center w-full'):
                                                max_value = ui.number(min=0, max=100, on_change=lambda e: model.update(range={'min': model['range']['min'], 'max': e.value})
                                                                      ).bind_value_from(model, 'range', lambda range: range['max']).classes('w-[50px] self-center')
                                                ui.label('%')
                                            ui.range(min=0, max=100).props('track-size=15px color=deep-purple-8 label-always label-color="black"').bind_value(model, 'range')
                                        with ui.column():
                                            ui.label('Define Reference Values Thresholds:').classes('font-bold')
                                            section_setting = ui.radio({'AVG': 'Average value among all sensors recorded threshold value',
                                                                        'ONE': 'One sensor among all has been recorded threshold value',
                                                                        'ALL': 'All sensors recorded threshold value'},
                                                                       value=setup.sensors_settings).props('color=red unchecked-icon:check_box_outline_blank'
                                                                            ).classes('text-xs')
                                            with ui.column().classes('gap-0'):
                                                ui.label('Selected sensors:').classes('font-bold mb-2')
                                                contolers = models.session.query(models.SensorControler).filter(models.SensorControler.section_id == setup.id).all()
                                                for controler in contolers:
                                                    with ui.row().classes('pl-4'):
                                                        ui.icon('check_box', color='red').classes('self-center')
                                                        ui.label(f'Sensor {controler.sensor_id}').classes('text-red text-xs')

                                    ui.button(color='#FF6370', text='Save', on_click=lambda id=section.id, min = min_value, max= max_value,
                                              setting=section_setting: change_settings(id=id, min=min.value, max= max.value, sensors_settings= setting.value)).props('no-caps rounded-lg').classes('text-white mt-10 self-end w-[125px]')

                                with ui.row():
                                    controler = None
                                    for controler in section.section_sensors:
                                        with ui.column().classes('gap-0 items-center'):
                                            #ui.icon('o_sensors', size='md')
                                            ui.html(sensor_icon)
                                            for sensor in system.system_sensors:
                                                if sensor.sensor_id == controler.sensor_id:
                                                    if sensor.sensor_name:
                                                        ui.label(sensor.sensor_name)
                                                    else:
                                                        ui.label(controler.sensor_id)
                                    ui.button(icon='add', text='Add Sensor', color='#FF6370', on_click=lambda id=section.id: add_sensor(id)).props('no-caps rounded-lg dense').classes('text-white m-2')
                                with ui.row():
                                    if section.starts_at:
                                        with ui.column().classes('gap-0 items-center'):
                                            ui.label(section.starts_at).classes('light-gray-circle')
                                            ui.label('Min')
                                    if section.stops_at:
                                        with ui.column().classes('gap-0 items-center'):
                                            ui.label(section.stops_at).classes('dark-gray-circle')
                                            ui.label('Max')
                                    if controler != None and controler.section_id == section.id:
                                        ui.button(icon='o_settings', text='Settings', color='#FF6370', on_click=settings_dialog.open).props('no-caps rounded-lg dense').classes('text-white m-2')

                ui.button(icon='add', text='Add Valve', color='#FF6370', 
                          on_click=lambda id=my_shift.id: add_valve(id)).props('no-caps rounded-lg dense').classes('text-white m-2 md:ml-28 self-center md:self-start')
        with ui.button(color='#F8F3FE', on_click=add_new_shift).props('no-caps flat'):
            ui.icon('add_circle', size='50px').classes('mx-2 text-[#FF6370]')
            ui.label('Add Shift')

@system_router.page('/schedules')
def schedules():
    id = app.storage.user['system_id']
    system = models.session.query(models.System).filter(models.System.id == id).first()
    system_shift_ID = []
    shift_dict = {}
    timers = []
    shifts = system.system_shifts
    for shift in shifts:
        shift_dict.update({shift.id: f'Shift ID: {shift.id}'})
        system_shift_ID.append(shift.id)
        for timer in shift.shift_timers:
            timers.append(timer)
    async def add_new_timer():
        add_timer_dialoge.open()
        ID = await add_timer_dialoge
        db_timer = models.Timer(shift_id=ID.value, updated_at=datetime.now())
        models.session.add(db_timer)
        models.session.commit()
        ui.notify('Added new timer', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def change_timer(id: int):
        existing_timer = models.session.query(models.Timer).filter(models.Timer.id == id)
        timer= existing_timer.first()
        with ui.dialog() as change_timer_dialog, ui.card():
            with ui.column().classes('w-full'):
                with ui.row().classes('justify-between w-full'):
                    ui.label('Edit timer').classes('font-bold self-center')
                    ui.button(icon='close', on_click=change_timer_dialog.close).props('outline flat')
                with ui.row().classes('no-wrap w-full justify-between'):
                    with ui.column():
                        ui.label('Mon')
                        if timer.Mon:
                            mon = ui.checkbox(value=timer.Mon).props('color="red"')
                        else:
                            mon = ui.checkbox(value=False).props('color="red"')
                    with ui.column():
                        ui.label('Tue')
                        if timer.Tue:
                            tue = ui.checkbox(value=timer.Tue).props('color="red"')
                        else:
                            tue = ui.checkbox(value=False).props('color="red"')
                    with ui.column():
                        ui.label('Wed')
                        if timer.Wed:
                            wed = ui.checkbox(value=timer.Wed).props('color="red"')
                        else:
                            wed = ui.checkbox(value=False).props('color="red"')
                    with ui.column():
                        ui.label('Thu')
                        if timer.Thu:
                            thu = ui.checkbox(value=timer.Thu).props('color="red"')
                        else:
                            thu = ui.checkbox(value=False).props('color="red"')
                    with ui.column():
                        ui.label('Fri')
                        if timer.Fri:
                            fri = ui.checkbox(value=timer.Fri).props('color="red"')
                        else:
                            fri = ui.checkbox(value=False).props('color="red"')
                    with ui.column():
                        ui.label('Sat')
                        if timer.Sat:
                            sat = ui.checkbox(value=timer.Sat).props('color="red"')
                        else:
                            sat = ui.checkbox(value=False).props('color="red"')
                    with ui.column():
                        ui.label('Sun')
                        if timer.Sun:
                            sun = ui.checkbox(value=timer.Sun).props('color="red"')
                        else:
                            sun = ui.checkbox(value=False).props('color="red"')
                with ui.row().classes('no-wrap justify-between'):
                    with ui.input('Timer starts at:', value=timer.starts) as starts:
                        with ui.menu().props('no-parent-event') as start_menu:
                            with ui.time().props('format24h').bind_value(starts):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=start_menu.close).props('flat')
                        with starts.add_slot('append'):
                            ui.icon('access_time').on('click', start_menu.open).classes('cursor-pointer')
                    with ui.input('Timer stops at:', value=timer.stops) as stops:
                        with ui.menu().props('no-parent-event') as stop_menu:
                            with ui.time().props('format24h').bind_value(stops):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=stop_menu.close).props('flat')
                        with stops.add_slot('append'):
                            ui.icon('access_time').on('click', stop_menu.open).classes('cursor-pointer')
            ui.button(text='Save', color='#FF6370',
                      on_click=lambda: change_timer_dialog.submit({
                          'Mon': mon.value, 'Tue': tue.value, 'Wed': wed.value, 'Thu': thu.value, 'Fri': fri.value,
                          'Sat': sat.value, 'Sun': sun.value, 'starts': starts.value, 'stops': stops.value
                      })).props('no-caps rounded-lg dense').classes('text-white w-full')
        change_timer_dialog.open()
        data = await change_timer_dialog
        existing_timer.update(data)
        models.session.commit()
        ui.notify('Succesfully updated', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()
    async def delete_timer(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_timer = models.session.query(models.Timer).filter(models.Timer.id == id)
            existing_timer.delete()
            models.session.commit()
            ui.notify('Succesfully deleted', position='top', color='negative')
            await asyncio.sleep(2)
            ui.navigate.reload()
    async def change_timer_name(id: str, name: str):
        timer_query = models.session.query(models.Timer).filter(models.Timer.id == id)
        timer_query.update({'timer_name': name})
        models.session.commit()
        ui.notify('Changing Settings. Please wait...', position='top', color='positive')
        await asyncio.sleep(2)
        ui.navigate.reload()

    with theme.system_frame():
        ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />')
        ui.add_head_html('''
            <style type="text/tailwindcss">
                @layer components {
                    .red-circle {
                        @apply bg-[#FF6370] w-[30px] h-[30px] text-center rounded-full text-white;
                    }
                    .green-circle {
                        @apply bg-[#70CF97] w-[30px] h-[30px] text-center rounded-full text-white;
                    }
                }
            </style>
        ''')
        ui.label('Irrigation Schedule').classes('font-bold md:text-2xl ')
        with ui.dialog() as add_timer_dialoge, ui.card():
            with ui.column().classes('gap-0 p-2'):
                with ui.row().classes('w-[350px] justify-between'):
                    ui.label('Available Shifts').classes('text-xl font-bold')
                    ui.button(icon='close', on_click=add_timer_dialoge.close).props('outline flat')
                ui.label('Select from the list below:').classes('text-gray-400')
            shiftID = ui.radio(shift_dict).props('color=red unchecked-icon=check_box_outline_blank')
            ui.button(color='#FF6370', text='Save',
                        on_click=lambda: add_timer_dialoge.submit(shiftID)).props('no-caps rounded-lg').classes(
                            'text-white mt-10 self-center w-[125px]')
        
        with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
            with ui.column():
                ui.label('Are you sure you want to delete item?')
                with ui.row().classes('self-center'):
                    ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                    ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
                
        for timer in timers:
            with ui.dialog() as edit_timer_dialog, ui.card():
                with ui.row().classes('justify-between w-full'):
                    ui.label('Edit Timer').classes('font-bold md:text-lg')
                    ui.button(icon='close', on_click=edit_timer_dialog.close).props('outline flat')
                with ui.row().classes('justify-between items-center'):
                    ui.label('Timer name:').classes('md:text-lg')
                    new_name = ui.input(timer.timer_name)
                ui.button(color='#FF6370', text='Save', on_click=lambda my_timer=timer, timer_name=new_name: 
                    change_timer_name(id=my_timer.id, name=timer_name.value)).props('no-caps rounded-lg').classes('text-white self-center w-full')
                
            with ui.column().classes('w-full gap-0 bg-white'):
                with ui.row().classes('w-full justify-around md:no-wrap bg-white p-2 mb-4'):
                    with ui.row().classes('justify-between w-full'):
                        with ui.row().classes('self-start gap-1'):
                            ui.label('Timer').classes('font-bold md:text-lg')
                            if timer.timer_name:
                                ui.label(timer.timer_name).classes('font-bold md:text-lg')
                            else:
                                ui.label(timer.id).classes('font-bold md:text-lg')
                            ui.button(icon='edit', color='#FF6370', on_click=edit_timer_dialog.open).props('size=xs rounded').classes('w-[20px] ml-2 text-white')
                        with ui.button(color='#F8F3FE', on_click=lambda new_timer=timer: delete_timer(id=new_timer.id)).props('no-caps flat'):
                            ui.icon('delete', size='25px').classes('mx-2 text-[#FF6370]')
                    with ui.column().classes('gap-1 p-2 md:w-[250px] items-center md:items-start'):
                        ui.label('Accompanied Shift:').classes('font-bold text-gray-400')
                        with ui.row().classes('no-wrap'):
                            with ui.column().classes('gap-0 self-center'):
                                #ui.icon('account_tree', size='26px')
                                ui.html(shift_icon)
                                for shift in system.system_shifts:
                                    if shift.id == timer.shift_id:
                                        if shift.shift_name:
                                            ui.label(shift.shift_name).classes('self-center')
                                        else:
                                            ui.label(timer.shift_id).classes('self-center')
                            with ui.button(color='#FF6370', on_click=lambda id=timer.id: change_timer(id)).props('no-caps rounded-lg dense').classes('text-white m-2'):
                                ui.image('static/icons/schedule.png').classes('w-[20px] h-[20px] mr-2')
                                ui.label('Set Days&Time')

                    with ui.row().classes('self-center'):
                        if timer.Mon:
                            ui.label('M').classes('green-circle font-bold content-center')
                        else:
                            ui.label('M').classes('red-circle font-bold content-center')
                        if timer.Tue:
                            ui.label('T').classes('green-circle font-bold content-center')
                        else:
                            ui.label('T').classes('red-circle font-bold content-center')
                        if timer.Wed:
                            ui.label('W').classes('green-circle font-bold content-center')
                        else:
                            ui.label('W').classes('red-circle font-bold content-center')
                        if timer.Thu:
                            ui.label('T').classes('green-circle font-bold content-center')
                        else:
                            ui.label('T').classes('red-circle font-bold content-center')
                        if timer.Fri:
                            ui.label('F').classes('green-circle font-bold content-center')
                        else:
                            ui.label('F').classes('red-circle font-bold content-center')
                        if timer.Sat:
                            ui.label('S').classes('green-circle font-bold content-center')
                        else:
                            ui.label('S').classes('red-circle font-bold content-center')
                        if timer.Sun:
                            ui.label('S').classes('green-circle font-bold content-center')
                        else:
                            ui.label('S').classes('red-circle font-bold content-center')
                    with ui.row().classes('self-center'):
                        with ui.row():
                            if timer.starts:
                                ui.label(timer.starts.strftime('%H:%M')).classes('self-center font-bold')
                            else:
                                ui.label('N/A').classes('self-center font-bold')
                            ui.icon('eva-clock', color='green', size='28px')
                        with ui.row():
                            if timer.stops:
                                ui.label(timer.stops.strftime('%H:%M')).classes('self-center font-bold')
                            else:
                                ui.label('N/A').classes('self-center font-bold')
                            ui.icon('eva-clock', color='red', size='28px')


        with ui.button(color='#F8F3FE', on_click=add_new_timer).props('no-caps flat'):
            ui.icon('add_circle', size='50px').classes('mx-2 text-[#FF6370]')
            ui.label('Add Timer')

@system_router.page('/logs')
def logs():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    id = app.storage.user['system_id']
    system = models.session.query(models.System).filter(models.System.id == id).first()
    pump_ids = []
    valve_ids = []
    sensor_ids = []
    system_id = str(id)
    for pump in system.system_pumps:
        pump_ids.append(pump.pump_id)
    for valve in system.system_valves:
        valve_ids.append(valve.valve_id)
    for sensor in system.system_sensors:
        sensor_ids.append(sensor.sensor_id)
    system_log = []
    pump_logs = []
    valve_logs = []
    sensor_logs = []
    all_logs = {'pumps':pump_logs, 'valves': valve_logs, 'sensors': sensor_logs, 'system': system_log}
    logs = models.session.query(models.Logs).all()
    for log in logs:
        if log.dev_id in pump_ids:
            pump_logs.append(log)
        if log.dev_id in valve_ids:
            valve_logs.append(log)
        if log.dev_id in sensor_ids:
            sensor_logs.append(log)
        if log.dev_id == system_id:
            system_log.append(log)

    async def remove_log(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_log = models.session.query(models.Logs).filter(models.Logs.id == id)
            existing_log.update({'disable': True})
            models.session.commit()
            ui.notify('Succesfully removed', position='top', color='negative')
            await asyncio.sleep(2)
            ui.navigate.reload()
    async def delete_log(id: int):
        confim_delete_dialog.open()
        confirmation = await confim_delete_dialog
        if confirmation:
            existing_log = models.session.query(models.Logs).filter(models.Logs.id == id)
            existing_log.delete()
            models.session.commit()
            ui.notify('Succesfully deleted', position='top', color='negative')
            await asyncio.sleep(2)
            ui.navigate.reload()

    with theme.system_frame():
        ui.add_head_html('''
            <style type="text/tailwindcss">
                @layer components {
                    .red-circle {
                        @apply bg-[#FF6370] w-[50px] h-[50px] text-center rounded-full text-white;
                    }
                    .orange-circle {
                        @apply bg-[#FFAA71] w-[50px] h-[50px] text-center rounded-full text-white;
                    }
                    .green-circle {
                        @apply bg-[#70CF97] w-[50px] h-[50px] text-center rounded-full text-white;
                    }
                }
            </style>
        ''')
        ui.label('Log').classes('font-bold md:text-2xl ')
        with ui.dialog().props('persistent') as confim_delete_dialog, ui.card().classes('mx-auto'):
            with ui.column():
                ui.label('Are you sure you want to delete item?')
                with ui.row().classes('self-center'):
                    ui.button('Delete', color='#FF6370', on_click=lambda: confim_delete_dialog.submit(True)).props('no-caps').classes('text-white')
                    ui.button('Cancel', color='gray', on_click=lambda: confim_delete_dialog.submit(False)).props('no-caps').classes('text-white')
        if not current_user.admin:
            with ui.column().classes('w-full gap-0 bg-white'):
                for item in all_logs['pumps']:
                    if not item.disable:
                        with ui.row().classes('w-full justify-between items-center p-2 m-2'):
                            with ui.row().classes('items-center'):
                                with ui.row().classes('self-start gap-1 self-center md:w-24'):
                                    ui.label(item.dev_id)
                                #ui.icon('water', size='28px', color='red').classes('md:w-24')
                                with ui.row().classes('md:w-24 justify-center'):
                                    if item.dev_code == 3:
                                        with ui.label().classes('green-circle content-center'):
                                            ui.image('/static/icons/pump.png').classes('w-[25px] h-[25px]')
                                    elif item.dev_code == 2:
                                        with ui.label().classes('orange-circle content-center'):
                                            ui.image('/static/icons/pump.png').classes('w-[25px] h-[25px]')
                                    else:
                                        with ui.label().classes('red-circle content-center'):
                                            ui.image('/static/icons/pump.png').classes('w-[25px] h-[25px]')
                                ui.label(item.message).classes('md:w-96')
                            with ui.button(color='#F8F3FE', on_click=lambda new_log=item: remove_log(id=new_log.id)).props('no-caps flat').classes('p-2 m-2'):
                                ui.icon('delete', size='25px').classes('mx-2 text-[#FF6370]')
                for item in all_logs['valves']:
                    if not item.disable:
                        with ui.row().classes('w-full justify-between items-center p-2 m-2'):
                            with ui.row().classes('items-center'):
                                with ui.row().classes('self-start gap-1 self-center md:w-24'):
                                    ui.label(item.dev_id)
                                with ui.row().classes('md:w-24 justify-center'):
                                    if item.dev_code == 3:
                                        with ui.label().classes('green-circle content-center'):
                                            ui.image('/static/icons/valve-white.png').classes('w-[25px] h-[25px]')
                                    elif item.dev_code == 2:
                                        with ui.label().classes('orange-circle content-center'):
                                            ui.image('/static/icons/valve-white.png').classes('w-[25px] h-[25px]')
                                    else:
                                        with ui.label().classes('red-circle content-center'):
                                            ui.image('/static/icons/valve-white.png').classes('w-[25px] h-[25px]')
                                ui.label(item.message).classes('md:w-96')
                            with ui.button(color='#F8F3FE', on_click=lambda new_log=item: remove_log(id=new_log.id)).props('no-caps flat').classes('p-2 m-2'):
                                ui.icon('delete', size='25px').classes('mx-2 text-[#FF6370]')
                for item in all_logs['sensors']:
                    if not item.disable:
                        with ui.row().classes('w-full justify-between items-center p-2 m-2'):
                            with ui.row().classes('items-center'):
                                with ui.row().classes('self-start gap-1 self-center md:w-24'):
                                    ui.label(item.dev_id)
                                #ui.icon('r_sensors', size='28px', color='red').classes('md:w-24')
                                with ui.row().classes('md:w-24 justify-center'):
                                    if item.dev_code == 3:
                                        with ui.label().classes('green-circle content-center'):
                                            ui.image('/static/icons/sensor-white.png').classes('w-[25px] h-[25px]')
                                    elif item.dev_code == 2:
                                        with ui.label().classes('orange-circle content-center'):
                                            ui.image('/static/icons/sensor-white.png').classes('w-[25px] h-[25px]')
                                    else:
                                        with ui.label().classes('red-circle content-center'):
                                            ui.image('/static/icons/sensor-white.png').classes('w-[25px] h-[25px]')
                                ui.label(item.message).classes('md:w-96')
                            with ui.button(color='#F8F3FE', on_click=lambda new_log=item: remove_log(id=new_log.id)).props('no-caps flat').classes('p-2 m-2'):
                                ui.icon('delete', size='25px').classes('mx-2 text-[#FF6370]')
                for item in all_logs['system']:
                    if not item.disable:
                        with ui.row().classes('w-full justify-between no-wrap items-center p-2 m-2'):
                            with ui.row().classes('items-center'):
                                with ui.row().classes('self-start gap-1 self-center md:w-24'):
                                    ui.label(item.dev_id).classes('w-8 md:w-24')
                                #ui.icon('o_info', size='28px', color='red').classes('md:w-24')
                                with ui.row().classes('md:w-24 justify-center'):
                                    ui.label('!').classes('red-circle content-center text-xl font-bold')
                                ui.label(item.message).classes('w-56 md:w-96')
                            with ui.button(color='#F8F3FE', on_click=lambda new_log=item: remove_log(id=new_log.id)).props('no-caps flat').classes('p-2 m-2'):
                                ui.icon('delete', size='25px').classes('mx-2 text-[#FF6370]')

        if current_user.admin:
            with ui.column().classes('w-full gap-0 bg-white'):
                for log in logs:
                    if log.disable:
                        with ui.row().classes('w-full justify-between no-wrap items-center p-2 m-2'):
                            with ui.row().classes('items-center'):
                                with ui.row().classes('self-start gap-1 self-center md:w-24'):
                                    ui.label(log.dev_id).classes('w-8 md:w-24')
                                #ui.icon('info', size='28px', color='red').classes('md:w-24')
                                with ui.row().classes('md:w-24 justify-center'):
                                    ui.label('!').classes('red-circle content-center text-xl font-bold')
                                ui.label(log.message).classes('w-56 md:w-96')
                            with ui.button(color='#F8F3FE', on_click=lambda new_log=log: delete_log(id=new_log.id)).props('no-caps flat'):
                                ui.icon('delete', size='25px').classes('mx-2 text-[#FF6370]')

@system_router.page('/settings')
def settings():
    current_user = models.session.query(models.User).filter(models.User.username == app.storage.user['username']).first()
    id = app.storage.user['system_id']
    system = models.session.query(models.System).filter(models.System.id == id).first()

    async def handle_upload(e: events.UploadEventArguments):
        if not current_user.username == system.owner:
            ui.notify('Not authorized!', position='top', color='negative')
        else:
            with e.content as img:
                uploaded_img = Image.open(img)
                save_path = f"./static/systems/"
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                uploaded_img.save(save_path+f"system_{id}.jpg")
                ui.notify('Image changed', position='top', type='positive')
                await asyncio.sleep(2)
                ui.navigate.reload()
    async def edit_system():
        if not current_user.username == system.owner:
            ui.notify('Not authorized!', position='top', color='negative')
        else:
            existing_system = models.session.query(models.System).filter(models.System.id == id)
            data = {'name': new_name.value, 'area': new_area.value, 'fruit': new_fruit.value, 'location': new_location.value}
            existing_system.update(data)
            models.session.commit()
            ui.notify('Succesfully updated', position='top', color='positive')
            await asyncio.sleep(2)
            ui.navigate.reload()

    with theme.system_frame():
        ui.label('Settings').classes('font-bold text-xl mb-2')
        with ui.row().classes('w-full justify-around'):
            with ui.column().classes('border-2 p-2 m-4'):
                ui.label('System Image').classes('font-bold mb-2')
                image = f'./static/systems/system_{id}.jpg'
                if os.path.isfile(image):
                    ui.image(f'/static/systems/system_{id}.jpg').classes('w-[400px] h-[300px]')
                else:
                    ui.image('https://picsum.photos/640/360').classes('w-[400px] h-[300px]')
                ui.upload(label='Change system image', on_upload=handle_upload).props('accept=.jpg color="info"').classes('w-[400px]')
            with ui.column().classes('p-2 m-4'):
                with ui.column().classes('border-2 w-[400px] p-3'):
                    ui.label('System details').classes('font-bold text-xl mb-2')
                    with ui.row().classes('w-full justify-end'):
                        ui.label('ID:').classes('self-center')
                        ui.input(value=system.id).props('dense filled readonly').classes('w-48')
                    with ui.row().classes('w-full justify-end'):
                        ui.label('SystemID:').classes('self-center')
                        ui.input(value=system.systemID).props('dense filled readonly').classes('w-48')
                    with ui.row().classes('w-full justify-end'):
                        ui.label('System name:').classes('self-center')
                        new_name = ui.input(value=system.name).props('dense filled').classes('w-48')
                    with ui.row().classes('w-full justify-end'):
                        ui.label('Area:').classes('self-center')
                        with ui.row():
                            new_area = ui.number(value=system.area).props('dense filled').classes('w-40')
                            ui.label('ha').classes('self-center')
                    with ui.row().classes('w-full justify-end'):
                        ui.label('Fruit:').classes('self-center')
                        new_fruit = ui.input(value=system.fruit).props('dense filled').classes('w-48')
                    with ui.row().classes('w-full justify-end'):
                        ui.label('Location:').classes('self-center')
                        new_location = ui.input(value=system.location).props('dense filled').classes('w-48')
                with ui.row():
                    ui.button('Save', color='#FF6370', on_click=edit_system).props('no-caps rounded-lg dense').classes('w-24 text-white p-2 m-4')