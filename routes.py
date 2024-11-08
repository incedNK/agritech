from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

import schema
import crud
import config
from models import get_db

base_router = APIRouter(prefix="/base", tags=['Base'], include_in_schema=True)
user_router = APIRouter(prefix="/users", tags=['Users'], include_in_schema=True)
api_router = APIRouter(prefix="/api", tags=["API's"], include_in_schema=True)

""" CREATEROUTES """
""" Create new system, shift, device """
# Create system(s)
@base_router.post("/systems")
def create_new_system(system: schema.SystemCreate, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    owner = crud.get_user(db=db, username=system.owner)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found user in database"
        )
    try:
        system = crud.create_system(db=db, system=system)
        return {"detail": "New system was created successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Create pump(s)
@base_router.post("/pumps")
def create_new_pump(pump: schema.AddPump, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    system = crud.get_system(db=db, system_id=pump.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    try:
        crud.create_pump(db=db, pump=pump)
        return {"detail": "New pump was successfully added to system"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Create valve(s)
@base_router.post("/valves")
def create_new_valve(valve: schema.AddValve, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    system = crud.get_system(db=db, system_id=valve.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    try:
        crud.create_valve(db=db, valve=valve)
        return {"detail": "New valve was successfully added to system"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Create sensor(s)
@base_router.post("/sensors")
def create_new_sensor(sensor: schema.AddSensor, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    system = crud.get_system(db=db, system_id=sensor.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    try:
        crud.create_sensor(db=db, sensor=sensor)
        return {"detail": "New sensor was successfully added to system"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Create shifts
@base_router.post("/shift", response_model=schema.ShiftsWithID)
def create_new_shift(shift: schema.AddShift, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        new_shift = crud.create_shift(db=db, shift=shift)
        return new_shift
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Create shift's section
@base_router.post("/section", response_model=schema.SectionWithID)
def create_new_shift_section(section: schema.SectionCreate, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    shift = crud.get_shift(db=db, shift_id=section.shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found shift in database"
        )
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    available_valves = crud.check_for_valve_in_sections(
        db=db, shift_id=section.shift_id)
    try:
        if section.valve_id in available_valves:
            new_section = crud.create_section(db=db, section=section)
            return new_section
        else:
            return {"detail": "Selected valve is not available. Please try another one."}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Create sensor controler
@base_router.post("/sensorControler", response_model=schema.SControlWithID)
def create_new_sensor_controler(controler: schema.SensorControler, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    sensor_contolers = crud.get_sensor_controlers(
        db=db, section_id=controler.section_id)
    section = crud.get_section(db=db, id=controler.section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found section in database"
        )
    shift = crud.get_shift(db=db, shift_id=section.shift_id)
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    available_sensors = []
    for sensor in system.system_sensors:
        available_sensors.append(sensor.sensor_id)
    sensors = []
    for new_sensor in sensor_contolers:
        sensors.append(new_sensor.sensor_id)
    try:
        if controler.sensor_id in sensors:
            return {"detail": "You have already added this sensor to group."}
        if controler.sensor_id not in available_sensors:
            return {"detail": "There is no such sensor in system. Check device ID."}
        else:
            new_controler = crud.add_new_sensor_controler(
                db=db, scontroler=controler)
            return new_controler
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Create timer controler
@base_router.post("/timer", response_model=schema.TControlWithID)
def create_new_timer(controler: schema.TimerControl, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    check_timers = []
    timers = []
    shift = crud.get_shift(db=db, shift_id=controler.shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found shift in database"
        )
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    system_shifts = []
    for entry in system.system_shifts:
        system_shifts.append(entry)
    for data in system_shifts:
        for timer in data.shift_timers:
            timers.append(timer)
    for timer in timers:
        timer_to_dict = timer.serialize()
        check_timers.append(timer_to_dict)
    else:
        try:
            for timer in check_timers:
                print("Checking available timers....")
                if crud.do_timers_interfere(timer1=timer, timer2=controler.serialize()):
                    return {"detail": "Timers match each other."}
            new_timer = crud.add_new_timer(db=db, tcontroler=controler)
            return new_timer
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Something went wrong with connection to database"
            )


""" UPDATEROUTES """
""" Update user, system and device routes """
# Update user by user
@base_router.put("/user/{username}")
def user_self_update(username: str, user: schema.UserUpdate, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    if current_user.username != username and not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    user_to_update = crud.get_user(db=db, username=username)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found user in database"
        )
    try:
        crud.update_user(username=username, db=db, user=user)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Change password by user
@base_router.patch("/change_password/{username}")
def user_change_password(username: str, password: schema.LostPassword, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    if current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    user_to_update = crud.get_user(db=db, username=username)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found user in database"
        )
    try:
        crud.change_password(db=db, username=username, password=password)
        return {"detail": "Successfully changed password"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Update user by admin
@base_router.put("/admin/{username}")
def user_admin_update(username: str, user: schema.AdminUserUpdate, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    user_to_update = crud.get_user(db=db, username=username)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found user in database"
        )
    try:
        crud.admin_update_user(db=db, username=username, user=user)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Update system
@base_router.put("/system/{system_id}")
def system_update(system_id: int, to_update: schema.SystemUpdate, db: Session = Depends(get_db),
                  current_user: str = Depends(crud.get_current_user)):

    system_to_update = crud.get_system(db=db, system_id=system_id)
    if not system_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    if current_user.username != system_to_update.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.update_system(db=db, system=to_update, system_id=system_id)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Update pump
@base_router.put("/pump/{pump_id}")
def pump_update(pump_id: str, pump_to_update: schema.UpdatePump, db: Session = Depends(get_db),
                current_user: str = Depends(crud.get_current_user)):

    existing_pump = crud.get_pump(db=db, pump_id=pump_id)
    if not existing_pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found pump in database"
        )
    system = crud.get_system(db=db, system_id=existing_pump.system_id)
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.update_pump(db=db, pump=pump_to_update, pump_id=pump_id)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Update valve
@base_router.put("/valve/{valve_id}")
def valve_update(valve_id: str, valve_to_update: schema.UpdateValve, db: Session = Depends(get_db),
                 current_user: str = Depends(crud.get_current_user)):

    existing_valve = crud.get_valve(db=db, valve_id=valve_id)
    if not existing_valve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found valve in database"
        )
    system = crud.get_system(db=db, system_id=existing_valve.system_id)
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.update_valve(db=db, valve=valve_to_update, valve_id=valve_id)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Update sensor
@base_router.put("/sensor/{sensor_id}")
def sensor_update(sensor_id: str, sensor_to_update: schema.UpdateSensor, db: Session = Depends(get_db),
                  current_user: str = Depends(crud.get_current_user)):

    existing_sensor = crud.get_sensor(db=db, sensor_id=sensor_id)
    if not existing_sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found sensor in database"
        )
    system = crud.get_system(db=db, system_id=existing_sensor.system_id)
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.update_sensor(
            db=db, sensor=sensor_to_update, sensor_id=sensor_id)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Update section
@base_router.put("/section/{id}")
def section_update(id: int, section_to_update: schema.SectionUpdate, db: Session = Depends(get_db),
                   current_user: str = Depends(crud.get_current_user)):
    section = crud.get_section(db=db, id=id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found shift in database"
        )
    shift = crud.get_shift(db=db, shift_id=section.shift_id)
    system = crud.get_system(db=db, system_id=shift.system_id)
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    sensor_option = ["AVG", "ONE", "ALL"]
    if section_to_update.stops_at <= section_to_update.starts_at or section_to_update.starts_at < 0 or section_to_update.stops_at > 100:
        return {"detail": "Start values must be less than 100, greater than 0 and start value must be lower than stop value."}
    if section_to_update.sensors_settings not in sensor_option:
        return {"detail": "Select one of options: AVG/ONE/ALL."}
    try:
        crud.change_section(db=db, section=section_to_update, id=id)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Update sensor controler
@base_router.patch("/sensorControler/{controler_id}")
def change_sensor_controler_settings(controler_id: int, controler_to_update: schema.SensorControler, db: Session = Depends(get_db),
                                     current_user: str = Depends(crud.get_current_user)):
    controler = crud.get_sensor_controler(db=db, id=controler_id)
    if not controler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found controler in database"
        )
    sensor_contolers = crud.get_sensor_controlers(
        db=db, section_id=controler.section_id)
    section = crud.get_section(db=db, id=controler.section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found section in database"
        )
    shift = crud.get_shift(db=db, shift_id=section.shift_id)
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    available_sensors = []
    for sensor in system.system_sensors:
        available_sensors.append(sensor.sensor_id)
    sensors = []
    for new_sensor in sensor_contolers:
        sensors.append(new_sensor.sensor_id)
    if controler_to_update.section_id != section.id:
        return {"detail": "Can't update unproper section ID."}
    elif controler_to_update.sensor_id not in available_sensors:
        return {"detail": "There is no such sensor in system. Please check device ID."}
    else:
        try:
            if controler_to_update.sensor_id in sensors:
                return {"detail": "You have already added this sensor to group."}
            else:
                crud.change_sensor_controler(
                    db=db, scontroler=controler_to_update, id=controler_id)
                return {"detail": "Successfully updated database"}
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Something went wrong with connection to database"
            )

# Update timer shift controler
@base_router.patch("/timer/{id}")
def change_timer_controler_settings(id: int, controler_to_update: schema.TimerUpdate, db: Session = Depends(get_db),
                                    current_user: str = Depends(crud.get_current_user)):
    controler = crud.get_timer(db=db, id=id)
    if not controler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found controler in database"
        )
    check_timers = []
    timers = []
    shift = crud.get_shift(db=db, shift_id=controler.shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found shift in database"
        )
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    if current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    system_shifts = []
    for entry in system.system_shifts:
        system_shifts.append(entry)
    for data in system_shifts:
        for timer in data.shift_timers:
            if timer.id != id:
                timers.append(timer)
    for timer in timers:
        timer_to_dict = timer.serialize()
        check_timers.append(timer_to_dict)
    if controler_to_update.starts >= controler_to_update.stops:
        return {"detail": "Start values must be less than stop value."}
    else:
        try:
            for timer in check_timers:
                print("Checking available timers....")
                if crud.do_timers_interfere(timer1=timer, timer2=controler_to_update.serialize()):
                    return {"detail": "Timers match each other."}
            crud.change_timer_settings(
                db=db, tcontroler=controler_to_update, id=id)
            return {"detail": "Successfully updated database"}
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Something went wrong with connection to database"
            )

# Update log route
@base_router.put("/log/{log_id}")
def log_update(log_id: int, log_to_update: schema.UpdateLog, db: Session = Depends(get_db)):
    existing_log = crud.get_log(db=db, log_id=log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found shift in database"
        )
    try:
        crud.update_log(db=db, log_id=log_id, log=log_to_update)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )


""" DELETEROUTES """
# Delete user route
@base_router.delete("/{username}")
def delete_user(username: str, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    user_to_delete = crud.get_user(db=db, username=username)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found user in database"
        )
    try:
        crud.delete_user(username=username, db=db)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete system route
@base_router.delete("/system/{system_id}")
def delete_system(system_id: int, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    system_to_delete = crud.get_system(db=db, system_id=system_id)
    if not system_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found system in database"
        )
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.delete_system(system_id=system_id, db=db)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete pump route
@base_router.delete("/pump/{pump_id}")
def delete_pump(pump_id: str, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    pump_to_delete = crud.get_pump(db=db, pump_id=pump_id)
    if not pump_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found pump in database"
        )
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.delete_pump(pump_id=pump_id, db=db)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete valve route
@base_router.delete("/valve/{valve_id}")
def delete_valve(valve_id: str, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    valve_to_delete = crud.get_valve(db=db, valve_id=valve_id)
    if not valve_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found valve in database"
        )
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.delete_valve(valve_id=valve_id, db=db)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete sensor route
@base_router.delete("/sensor/{sensor_id}")
def delete_sensor(sensor_id: str, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    sensor_to_delete = crud.get_sensor(db=db, sensor_id=sensor_id)
    if not sensor_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found sensor in database"
        )
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.delete_sensor(sensor_id=sensor_id, db=db)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete shift route
@base_router.delete("/shift/{shift_id}")
def delete_shift(shift_id: int, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    shift_to_delete = crud.get_shift(db=db, shift_id=shift_id)
    if not shift_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found shift in database"
        )
    system = crud.get_system(db=db, system_id=shift_to_delete.system_id)
    if not current_user.admin and current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.delete_shift(shift_id=shift_id, db=db)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete Shift section route
@base_router.delete("/section/{id}")
def delete_shift_section(id: int, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    section_to_delete = crud.get_section(db=db, id=id)
    if not section_to_delete:
        return {"detail": f"There is no section with ID: {id}."}
    shift = crud.get_shift(db=db, shift_id=section_to_delete.shift_id)
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not section_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found shift in database"
        )
    if not current_user.admin and current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.delete_section(db=db, id=id)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete sensor controler route
@base_router.delete("/sensorControler/{id}")
def delete_sensor_controler(id: int, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    controler_to_delete = crud.get_sensor_controler(db=db, id=id)
    if not controler_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no controler with ID: {id}."
        )
    section = crud.get_section(db=db, id=controler_to_delete.section_id)
    shift = crud.get_shift(db=db, shift_id=section.shift_id)
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not current_user.admin and current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.delete_sensor_controler(db=db, id=id)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete timer route
@base_router.delete("/timer/{id}")
def delete_timer(id: int, db: Session = Depends(get_db), current_user: str = Depends(crud.get_current_user)):
    timer_to_delete = crud.get_timer(db=db, id=id)
    if not timer_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no timer with ID: {id}."
        )
    shift = crud.get_shift(db=db, shift_id=timer_to_delete.shift_id)
    system = crud.get_system(db=db, system_id=shift.system_id)
    if not current_user.admin and current_user.username != system.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update database"
        )
    try:
        crud.delete_timer(db=db, id=id)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

# Delete log route
@base_router.delete("/log/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    log_to_delete = crud.get_log(db=db, log_id=log_id)
    if not log_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not found log in database"
        )
    try:
        crud.delete_log(log_id=log_id, db=db)
        return {"detail": "Successfully updated database"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Something went wrong with connection to database"
        )

""" User routers """
#Create user
@user_router.post("/register")
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Username already exists")
    user_mail= crud.get_user_email(db, email=user.email)
    if user_mail:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Email already exists")
    user = crud.create_user(user=user, db=db)
    return {"detail": "New user was created successfully"}

#Change password
@user_router.patch("/reset_password/{secret}")
def user_reset_password(password: schema.ResetPassword, db: Session = Depends(get_db)):
    password_to_update = crud.get_user_by_secret(db=db, secret=password.secret)
    if not password_to_update:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Could not found user in database"
        )
    try:
        crud.reset_password(db=db, password=password)
        return {"detail": "Successfully changed password"}
    except:
        raise HTTPException(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "Something went wrong with connection to database"
        )

#Get secret key
@user_router.get("/get_key/{username}")
def get_secret_key(username: str, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, username=username)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Couldn't find user",
        )
    else:
        config.send_key_to_mail(email=user.email, key=user.secret)
        return RedirectResponse("/reset", status_code=status.HTTP_302_FOUND)

#Login user
@user_router.post("/login", response_model=schema.Token)
def log_user(user: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    db_user = crud.validate_user(db=db, user=user)

    if not db_user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = config.create_access_token(
        data={"sub": user.username}
    )
    # return {"access_token": access_token, "token_type": "bearer"}

    token = jsonable_encoder(access_token)
    content = {"detail": "You've successfully logged in. Wellcome back!"}
    response = JSONResponse(content=content)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="Lax",
        secure=False,
    )
    return response

@user_router.get("/users", response_model=List[schema.User])
def read_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    db_users = crud.get_users(db=db, skip=skip, limit=limit)
    return db_users

""" Devices API endpoints """

#Flow date routes
@api_router.post("/flowdata")
def flow_data(flow: schema.AddFlowData, db: Session = Depends(get_db)):
    pump_flow = crud.get_pump(db=db, pump_id=flow.pump_id)
    if not pump_flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such pump. Please check device ID"
        )
    try:
        db_flow = crud.create_flow_data(db=db, flow=flow)
        new_volume = pump_flow.current - flow.flow_rate
        crud.update_pump_data(
            db=db, pump_id=db_flow.pump_id, current=new_volume)
        return {"detail": "Successfully updated pump volume"}
    except:
        return {"detail": "Couldn't find pump in database"}

@api_router.get("/flowdata/{pump_id}", response_model=List[schema.GetFlowData])
def all_flow_data(pump_id: str, db: Session = Depends(get_db)):
    pump = crud.get_pump(db=db, pump_id=pump_id)
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such pump. Please check device ID"
        )
    try:
        db_data = crud.get_all_flow_data(db=db, pump_id=pump_id)
        if not db_data:
            return {"detail": "There is no available data"}
        return db_data.all()
    except:
        return {"detail": "There is problems with database"}

@api_router.get("/lastflowdata/{pump_id}", response_model=schema.GetFlowData)
def last_flow_data(pump_id: str, db: Session = Depends(get_db)):
    pump = crud.get_pump(db=db, pump_id=pump_id)
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such pump. Please check device ID"
        )
    try:
        last_data = crud.get_flow_data(db=db, pump_id=pump_id)
        if not last_data:
            return {"detail": "There is no available data"}
        return last_data
    except:
        return {"detail": "There is problems with database"}

#Sensor data routes
@api_router.post("/sensordata")
def sensor_data(sensor_data: schema.AddSensorData, db: Session = Depends(get_db)):
    try:
        new_data = crud.create_sensor_data(db=db, sensor=sensor_data)
        sensor = crud.get_sensor(db=db, sensor_id=new_data.sensor_id)
        moisture = {"level_1": new_data.level_1,
                "level_2": new_data.level_2, "level_3": new_data.level_3}
        temp = {"level_1": new_data.temp_1,
                "level_2": new_data.temp_2, "level_3": new_data.temp_3}
        settings = {"level_1": sensor.set_lvl_1,
                    "level_2": sensor.set_lvl_2, "level_3": sensor.set_lvl_3}
        user_setup = [f"level_{i}" for i in range(1, 4) if settings[f"level_{i}"]]
        y = len(user_setup)
        new_readings = 0
        for i in user_setup:
            new_readings += moisture[i]/y
        new_temp = 0
        for j in user_setup:
            new_temp += temp[j]/y
        crud.update_sensor_data(
            db=db, sensor_id=new_data.sensor_id, readings=new_readings, temp= new_temp)
        return {"detail": "Successfully updated sensor readings"}
    except:
        return {"detail": "Couldn't find sensor in database"}

@api_router.get("/sensordata/{sensor_id}", response_model=List[schema.SensorData])
def all_sensor_data(sensor_id: str, db: Session = Depends(get_db)):
    sensor = crud.get_sensor(db=db, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such sensor. Please check device ID"
        )
    try:
        db_data = crud.get_all_sensor_data(db=db, sensor_id=sensor_id)
        if not db_data:
            return {"detail": "There is no available data"}
        return db_data.all()
    except:
        return {"detail": "There is problems with database"}

@api_router.get("/lastsensordata/{sensor_id}", response_model=schema.SensorData)
def last_sensor_data(sensor_id: str, db: Session = Depends(get_db)):
    sensor = crud.get_sensor(db=db, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no such sensor. Please check device ID"
        )
    try:
        last_data = crud.get_sensor_data(db=db, sensor_id=sensor_id)
        if not last_data:
            return {"detail": "There is no available data"}
        return last_data
    except:
        return {"detail": "There is problems with database"}

@api_router.get("/sensor_settings/{system_id}")
def sensor_settings(system_id: int, db: Session = Depends(get_db)):
    system = crud.get_system(db=db, system_id=system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please select active system ID"
        )
    system_sensors = crud.get_system_sensors(db=db, system_id=system_id)
    sensors = []
    for sensor in system_sensors:
        sensors.append({"SensorID": sensor.sensor_id, "settings": [
                       {"10 cm": sensor.set_lvl_1, "20 cm": sensor.set_lvl_2, "40 cm": sensor.set_lvl_3}]})
    return sensors

# Valve routes
@api_router.get("/valvestatus/{system_id}")
def get_valve_status(system_id: int, db: Session = Depends(get_db)):
    system = crud.get_system(db=db, system_id=system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please select active system ID"
        )
    try:
        valves = crud.get_system_valves(db=db, system_id=system_id)
        valve_status = []
        for valve in valves:
            valve_status.append({valve.valve_id: valve.status})
        return valve_status
    except:
        return {"detail": "There is problems with database"}

@api_router.patch("/valve/{valve_id}")
def change_valve_status(valve_id: str, valve: schema.UpdateValveStatus, db: Session = Depends(get_db)):
    existing_valve = crud.get_valve(db=db, valve_id=valve_id)
    if not existing_valve:
        return {"detail": "Could not found valve in database"}
    try:
        crud.update_valve_status(db=db, valve=valve, valve_id=valve_id)
        return {"detail": "Successfully updated database"}
    except:
        return {"detail": "Something went wrong with database"}

# Logs of devices events
@api_router.post("/log/{id}")
def create_log(log: schema.LogCreate, id: str, db: Session = Depends(get_db)):
    pump = crud.get_pump(db=db, pump_id=id)
    valve = crud.get_valve(db=db, valve_id=id)
    sensor = crud.get_sensor(db=db, sensor_id=id)
    if not pump and not valve and not sensor:
        return {"detail": "Couldn't find device in database. Check if input is valid!"}
    else:
        crud.create_log(db=db, log=log)
        return {"detail": "Successfully updated log"}

@api_router.get("/systemlogs", response_model=List[List[schema.Logs]])
def get_system_logs(system_id: int, db: Session = Depends(get_db)):
    system = crud.get_system(db=db, system_id=system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please select active system ID"
        )
    pump_logs = []
    valve_logs = []
    sensor_logs = []
    for pump in system.system_pumps:
        pumps_logs = crud.get_dev_logs(db=db, dev_id=pump.pump_id)
        for pump_log in pumps_logs:
            pump_logs.append(pump_log)
    for valve in system.system_valves:
        valves_logs = crud.get_dev_logs(db=db, dev_id=valve.valve_id)
        for valve_log in valves_logs:
            valve_logs.append(valve_log)
    for sensor in system.system_sensors:
        sensors_logs = crud.get_dev_logs(db=db, dev_id=sensor.sensor_id)
        for sensor_log in sensors_logs:
            sensor_logs.append(sensor_log)
    return [pump_logs, valve_logs, sensor_logs]

# API routes for getting setting
@api_router.get("/system_shifts/{system_id}", response_model=List[schema.Shifts])
def get_systems_shifts(system_id: int, db: Session = Depends(get_db)):
    system = crud.get_system(db=db, system_id=system_id)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please select active system ID"
        )
    shifts = crud.get_system_shifts(db=db, system_id=system_id)
    return shifts

# Get current time
@api_router.get("/timestamp", response_model=schema.CurrentTime)
def return_current_time():
    current_timestamp = datetime.now().timestamp()
    return {"current_time": current_timestamp}

# Get string systemID
@api_router.get("/system_str_ID/{systemID}", response_model=schema.SystemID)
def get_systemID_as_str(systemID: str, db: Session = Depends(get_db)):
    system = crud.get_systemID(db=db, systemID=systemID)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coldn't find system. Please select active systemID"
        )
    return system