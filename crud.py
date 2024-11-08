from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import Depends, HTTPException, status
import models
import schema
import config
from models import get_db

# Handle system
def get_systems(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.System).offset(skip).limit(limit).all()

def get_system(db: Session, system_id:  int):
    return db.query(models.System).filter(models.System.id == system_id).first()

def get_systemID(db: Session, systemID: str):
    return db.query(models.System).filter(models.System.systemID == systemID).first()

def create_system(db: Session, system: schema.SystemCreate):
    db_system = models.System(**system.dict())
    db.add(db_system)
    db.commit()
    db.refresh(db_system)
    return db_system

def update_system(db: Session, system: schema.SystemUpdate, system_id: int):
    system_query = db.query(models.System).filter(
        models.System.id == system_id)
    if not system_query.first():
        return False
    entry = system.dict()
    entry['updated_at'] = datetime.now()
    system_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def delete_system(system_id: int, db: Session):
    existing_system = db.query(models.System).filter(
        models.System.id == system_id)
    if not existing_system.first():
        return False
    existing_system.delete(synchronize_session=False)
    db.commit()
    return True

# Handle pumps
def get_pumps(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Pump).offset(skip).limit(limit).all()

def get_pump(db: Session, pump_id: str):
    return db.query(models.Pump).filter(models.Pump.pump_id == pump_id).first()

def get_system_pumps(db: Session, system_id: int):
    return db.query(models.Pump).filter(models.Pump.system_id == system_id).all()

def create_pump(db: Session, pump: schema.AddPump):
    db_pump = models.Pump(**pump.dict())
    db.add(db_pump)
    db.commit()
    db.refresh(db_pump)
    return db_pump

def update_pump(db: Session, pump: schema.UpdatePump, pump_id: str):
    pump_query = db.query(models.Pump).filter(models.Pump.pump_id == pump_id)
    if not pump_query.first():
        return False
    entry = pump.dict()
    entry['updated_at'] = datetime.now()
    pump_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def delete_pump(pump_id: str, db: Session):
    existing_pump = db.query(models.Pump).filter(
        models.Pump.pump_id == pump_id)
    if not existing_pump.first():
        return False
    existing_pump.delete(synchronize_session=False)
    db.commit()
    return True

# Handle Valves
def get_valves(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Valve).offset(skip).limit(limit).all()

def get_valve(db: Session, valve_id: str):
    return db.query(models.Valve).filter(models.Valve.valve_id == valve_id).first()

def get_system_valves(db: Session, system_id: int):
    return db.query(models.Valve).filter(models.Valve.system_id == system_id).all()

def create_valve(db: Session, valve: schema.AddValve):
    db_valve = models.Valve(**valve.dict())
    db.add(db_valve)
    db.commit()
    db.refresh(db_valve)
    return db_valve

def update_valve(db: Session, valve: schema.UpdateValve, valve_id: str):
    valve_query = db.query(models.Valve).filter(
        models.Valve.valve_id == valve_id)
    if not valve_query.first():
        return False
    entry = valve.dict()
    entry['updated_at'] = datetime.now()
    valve_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def update_valve_status(db: Session, valve: schema.UpdateValveStatus, valve_id: str):
    valve_query = db.query(models.Valve).filter(
        models.Valve.valve_id == valve_id)
    if not valve_query.first():
        return False
    entry = valve.dict()
    entry['updated_at'] = datetime.now()
    valve_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def delete_valve(valve_id: str, db: Session):
    existing_valve = db.query(models.Valve).filter(
        models.Valve.valve_id == valve_id)
    if not existing_valve.first():
        return False
    existing_valve.delete(synchronize_session=False)
    db.commit()
    print(f"Valve {valve_id} was deleted.")
    existing_section = db.query(models.Section).filter(
        models.Section.valve_id == valve_id)
    while existing_section.first():
        existing_section.delete(synchronize_session=False)
        db.commit()
        print(f"Deleting shift section with valveID: {valve_id}...")
    return True

# Handle sensors
def get_sensors(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Sensor).offset(skip).limit(limit).all()

def get_sensor(db: Session, sensor_id: str):
    return db.query(models.Sensor).filter(models.Sensor.sensor_id == sensor_id).first()

def get_system_sensors(db: Session, system_id: int):
    return db.query(models.Sensor).filter(models.Sensor.system_id == system_id).all()

def create_sensor(db: Session, sensor: schema.AddSensor):
    db_sensor = models.Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def update_sensor(db: Session, sensor: schema.UpdateSensor, sensor_id: str):
    sensor_query = db.query(models.Sensor).filter(
        models.Sensor.sensor_id == sensor_id)
    if not sensor_query.first():
        return False
    entry = sensor.dict()
    entry['updated_at'] = datetime.now()
    sensor_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def delete_sensor(sensor_id: str, db: Session):
    existing_sensor = db.query(models.Sensor).filter(
        models.Sensor.sensor_id == sensor_id)
    if not existing_sensor.first():
        return False
    existing_sensor.delete(synchronize_session=False)
    db.commit()
    return True

# Handle shifts
def get_shifts(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Shift).offset(skip).limit(limit).all()

def get_shift(db: Session, shift_id: int):
    return db.query(models.Shift).filter(models.Shift.id == shift_id).first()

def get_system_shifts(db: Session, system_id: int):
    return db.query(models.Shift).filter(models.Shift.system_id == system_id).all()

def create_shift(db: Session, shift: schema.AddShift):
    db_shift = models.Shift(**shift.dict())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift

def delete_shift(shift_id: int, db: Session):
    existing_shift = db.query(models.Shift).filter(models.Shift.id == shift_id)
    if not existing_shift.first():
        print("No shift found!")
        return False
    existing_shift.delete(synchronize_session=False)
    db.commit()
    print(f"Shift {shift_id} was deleted.")
    existing_timer_controler = db.query(models.Timer).filter(
        models.Timer.shift_id == shift_id)
    while existing_timer_controler.first():
        existing_timer_controler.delete(synchronize_session=False)
        db.commit()
        print(f"Deleting timer for shift {shift_id}...")
    return True

def update_shift(db: Session, shift: schema.UpdateShift, shift_id: int):
    shift_query = db.query(models.Shift).filter(models.Shift.id == shift_id)
    if not shift_query.first():
        return False
    shift_query.update(shift.dict(), synchronize_session=False)
    db.commit()
    print(f"Updating shift ID:{shift_id}....")
    return True

# Handle shift's sections and controls
def get_shift_sections(shift_id: int, db: Session):
    return db.query(models.Section).filter(models.Section.shift_id == shift_id).all()

def get_sections(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Section).offset(skip).limit(limit).all()

def get_section(id: int, db: Session):
    return db.query(models.Section).filter(models.Section.id == id).first()

def check_for_valve_in_sections(db: Session, shift_id: int):
    available_valves = []
    system_id = get_shift(db=db, shift_id=shift_id)
    system_valves = get_system_valves(db=db, system_id=system_id.system_id)
    for valve in system_valves:
        available_valves.append(valve.valve_id)
    section_valves = []
    for valve_id in available_valves:
        section_valve = db.query(models.Section).filter(
            models.Section.valve_id == valve_id).first()
        if section_valve:
            section_valves.append(section_valve.valve_id)
    ready_valves = []
    for valve in available_valves:
        if valve not in section_valves:
            ready_valves.append(valve)
    return ready_valves

def create_section(db: Session, section: schema.SectionCreate):
    db_section = models.Section(**section.dict())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

def change_section(db: Session, section: schema.SectionUpdate, id: int):
    section_query = db.query(models.Section).filter(
        models.Section.id == id)
    if not section_query.first():
        return False
    entry = section.dict()
    entry['updated_at'] = datetime.now()
    section_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def delete_section(id: int, db: Session):
    existing_section = db.query(models.Section).filter(models.Section.id == id)
    if not existing_section.first():
        print(f"No section with ID:{id} has found!")
        return False
    existing_section.delete(synchronize_session=False)
    db.commit()
    print(f"Deleting section ID:{id}...")
    existing_sesor_controler = db.query(models.SensorControler).filter(
        models.SensorControler.section_id == id)
    while existing_sesor_controler.first():
        existing_sesor_controler.delete(synchronize_session=False)
        db.commit()
        print(f"Deleting sensor controlers for section ID:{id}....")
    return True

def get_sensor_controler(id: int, db: Session):
    return db.query(models.SensorControler).filter(
        models.SensorControler.id == id).first()

def get_sensor_controlers(section_id: int, db: Session):
    return db.query(models.SensorControler).filter(
        models.SensorControler.section_id == section_id).all()

def add_new_sensor_controler(db: Session, scontroler: schema.SensorControler):
    db_controler = models.SensorControler(**scontroler.dict())
    db.add(db_controler)
    db.commit()
    db.refresh(db_controler)
    return db_controler

def change_sensor_controler(db: Session, scontroler: schema.SensorControler, id: int):
    controler_query = db.query(models.SensorControler).filter(
        models.SensorControler.id == id)
    if not controler_query.first():
        return False
    entry = scontroler.dict()
    entry['updated_at'] = datetime.now()
    controler_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def delete_sensor_controler(id: int, db: Session):
    existing_controler = db.query(models.SensorControler).filter(
        models.SensorControler.id == id)
    if not existing_controler.first():
        return False
    existing_controler.delete(synchronize_session=False)
    db.commit()
    return True

def get_timer(db: Session, id: int):
    return db.query(models.Timer).filter(
        models.Timer.id == id).first()

def get_timers(db: Session, shift_id: int):
    return db.query(models.Timer).filter(models.Timer.shift_id == shift_id).all()

def get_all_timers(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Timer).offset(skip).limit(limit).all()

def add_new_timer(db: Session, tcontroler: schema.TimerControl):
    db_controler = models.Timer(**tcontroler.dict())
    db.add(db_controler)
    db.commit()
    db.refresh(db_controler)
    return db_controler

def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M:%S").time()

def do_timers_interfere(timer1, timer2):
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Check if any of the days in timer1 overlap with timer2
    for day in days_of_week:
        if timer1[day] and timer2[day]:
            start_time1 = parse_time(timer1["starts"])
            stop_time1 = parse_time(timer1["stops"])
            start_time2 = parse_time(timer2["starts"])
            stop_time2 = parse_time(timer2["stops"])

            # Check if the time ranges overlap (taking into account start time equals end time)
            if (
                (start_time1 < stop_time1 and start_time2 < stop_time2 and
                 ((start_time1 <= start_time2 < stop_time1) or
                  (start_time1 < stop_time2 <= stop_time1) or
                  (start_time2 <= start_time1 < stop_time2) or
                  (start_time2 < stop_time1 <= stop_time2))) or
                (start_time1 == stop_time1 and start_time2 == stop_time2 and
                 start_time1 == start_time2)
            ):
                return True
            else:
                return False

def change_timer_settings(db: Session, tcontroler: schema.TimerUpdate, id: int):
    controler_query = db.query(models.Timer).filter(
        models.Timer.id == id)
    if not controler_query.first():
        return False
    entry = tcontroler.dict()
    entry['updated_at'] = datetime.now()
    controler_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def delete_timer(id: int, db: Session):
    existing_timer = db.query(models.Timer).filter(models.Timer.id == id)
    if not existing_timer.first():
        return False
    existing_timer.delete(synchronize_session=False)
    db.commit()
    return True

# Handle logs
def get_logs(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Logs).offset(skip).limit(limit).all()

def get_dev_logs(db: Session, dev_id: str):
    return db.query(models.Logs).filter(models.Logs.dev_id == dev_id).all()

def get_log(db: Session, log_id: int):
    return db.query(models.Logs).filter(models.Logs.id == log_id).first()

def create_log(db: Session, log: schema.LogCreate):
    db_log = models.Logs(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def update_log(db: Session, log: schema.UpdateLog, log_id: int):
    log_query = db.query(models.Logs).filter(models.Logs.id == log_id)
    if not log_query.first():
        return False
    log_query.update(log.dict(), synchronize_session=False)
    db.commit()
    return True

def delete_log(log_id: int, db: Session):
    existing_log = db.query(models.Logs).filter(models.Logs.id == log_id)
    if not existing_log.first():
        return False
    existing_log.delete(synchronize_session=False)
    db.commit()
    return True

# Handle flow data
def get_flow_data(db: Session, pump_id: str):
    return db.query(models.FlowData).order_by(models.FlowData.pump_id, models.FlowData.date.desc()).filter(
        models.FlowData.pump_id == pump_id).first()

def get_all_flow_data(db: Session, pump_id: str):
    return db.query(models.FlowData).filter(models.FlowData.pump_id == pump_id)

def create_flow_data(db: Session, flow: schema.AddFlowData):
    db_data = models.FlowData(**flow.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def update_pump_data(db: Session, pump_id: str, current: float):
    query_pump = db.query(models.Pump).filter(models.Pump.pump_id == pump_id)
    if not query_pump.first():
        return False
    query_pump.update({models.Pump.current: current},
                      synchronize_session=False)
    db.commit()
    return True

# Handle sensor data
def get_sensor_data(db: Session, sensor_id: str):
    return db.query(models.SensorData).order_by(models.SensorData.sensor_id, models.SensorData.date.desc()).filter(
        models.SensorData.sensor_id == sensor_id).first()

def get_all_sensor_data(db: Session, sensor_id: str):
    return db.query(models.SensorData).filter(models.SensorData.sensor_id == sensor_id)

def create_sensor_data(db: Session, sensor: schema.AddSensorData):
    db_data = models.SensorData(**sensor.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def update_sensor_data(db: Session, sensor_id: str, readings: float, temp: float):
    query_readings = db.query(models.Sensor).filter(
        models.Sensor.sensor_id == sensor_id)
    if not query_readings.first():
        return False
    query_readings.update(
        {models.Sensor.readings: readings, models.Sensor.temp: temp}, synchronize_session=False)
    db.commit()
    return True

# Handling users
def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    return user

def get_user_email(db: Session, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    return user

def get_user_by_secret(db: Session, secret: str):
    user = db.query(models.User).filter(models.User.secret == secret).first()
    return user

def get_users(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schema.UserCreate):
    db_user = models.User(email=user.email, username = user.username, hashed_password=config.get_hashed_password(user.password),
        name=user.name, surname=user.surname, address=user.address, admin=user.admin, premium=user.premium, delisted=user.delisted,
        secret=config.generate_secret())
    if db_user.username == "admin":
        db_user.delisted = False
        db_user.admin = True
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def change_password(db: Session, username: str, password: schema.LostPassword):
    pwd_query = db.query(models.User).filter(models.User.username == username)
    if not pwd_query.first():
        return False
    hashed_pwd = config.get_hashed_password(password.password)
    pwd_query.update({models.User.hashed_password: hashed_pwd}, synchronize_session=False)
    db.commit()
    return True

def reset_password(db: Session, password: schema.ResetPassword):
    reset_query = db.query(models.User).filter(models.User.secret == password.secret)
    if not reset_query.first():
        return False
    hashed_pwd = config.get_hashed_password(password.password)
    reset_query.update(
        {
            models.User.hashed_password: hashed_pwd,
            models.User.secret: config.generate_secret()
        },
        synchronize_session=False)
    db.commit()
    return True

def update_user(db: Session, username: str, user: schema.UserUpdate):
    user_query = db.query(models.User).filter(models.User.username == username)
    if not user_query.first():
        return False
    entry = user.dict()
    entry['updated_at'] = datetime.now()
    user_query.update(entry, synchronize_session=False)
    db.commit()
    return True

def admin_update_user(db: Session, username: str, user: schema.AdminUserUpdate):
    user_query = db.query(models.User).filter(models.User.username == username)
    if not user_query.first():
        return False
    user_query.update(user.dict(), synchronize_session=False)
    db.commit()
    return True

def delete_user(username: str , db: Session):
    existing_user = db.query(models.User).filter(models.User.username == username)
    if not existing_user.first():
        return False
    existing_user.delete(synchronize_session=False)
    db.commit()
    return True

#Handle login
def get_current_user(db: Session = Depends(get_db), token: str=Depends(config.security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = config.get_token(token)
    current_user = get_user(db, username=token_data)
    if current_user is None:
        raise credentials_exception
    return current_user

def validate_user(db: Session, user: schema.Login):
    db_user = get_user(db=db, username=user.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not config.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return db_user