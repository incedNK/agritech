from pydantic import BaseModel, EmailStr
from datetime import datetime, time
from typing import Optional, Union, List

''' Schema file is specific for each project -- create new schema that suite project need '''
# Pump's schemas
class Flow(BaseModel):
    pump_id: str
    capacity: Union[float, None] = None
    current: Union[float, None] = None

class AddPump(Flow):
    system_id: int

class UpdatePump(BaseModel):
    current: float

class Pump(Flow):
    system_id: int
    updated_at: datetime
    created_at: datetime
    class Config:
        from_attributes = True

class AddFlowData(BaseModel):
    pump_id: str
    flow_rate: float

class GetFlowData(BaseModel):
    flow_rate: Optional[float]
    date: Optional[datetime]
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

# Valve's schemas
class ValveBase(BaseModel):
    valve_id: str
    status: Union[bool, None] = None

class AddValve(ValveBase):
    system_id: int

class UpdateValve(BaseModel):
    status: Optional[bool]

class UpdateValveStatus(BaseModel):
    status: Optional[bool]

class Valve(ValveBase):
    system_id: int
    updated_at: datetime
    created_at: datetime
    class Config:
        from_attributes = True

# Sensor's schemas
class SensorBase(BaseModel):
    sensor_id: str
    readings: Optional[float] = 50
    temp: Optional[float] = 15
    set_lvl_1: bool = False
    set_lvl_2: bool = True
    set_lvl_3: bool = False

class AddSensor(SensorBase):
    system_id: int

class UpdateSensor(BaseModel):
    set_lvl_1: Optional[bool]
    set_lvl_2: Optional[bool]
    set_lvl_3: Optional[bool]

class Sensor(SensorBase):
    system_id: int
    updated_at: datetime
    created_at: datetime
    class Config:
        from_attributes = True

class AddSensorData(BaseModel):
    sensor_id: str
    bat_level: float
    level_1: float
    level_2: float
    level_3: float
    temp_1: float
    temp_2: float
    temp_3: float
    temperature: float
    moisture: float

class SensorData(BaseModel):
    date: datetime
    bat_level: float
    level_1: float
    level_2: float
    level_3: float
    temp_1: Optional[float]
    temp_2: Optional[float]
    temp_3: Optional[float]
    temperature: float
    moisture: float
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

class SensorControler(BaseModel):
    section_id: int
    sensor_id: Optional[str]

class SControl(BaseModel):
    id: int
    updated_at: datetime
    sensor_id: Union[str, None] = None
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

class SControlWithID(BaseModel):
    detail: str = "New section was successfully added to shift"
    id: int
    class Config:
        from_attributes = True

class SectionCreate(BaseModel):
    shift_id: int
    valve_id: str
    updated_at: datetime = datetime.now()

class SectionUpdate(BaseModel):
    sensors_settings: Optional[str]
    starts_at: Optional[float]
    stops_at: Optional[float]

class Section(BaseModel):
    id: int
    updated_at: datetime
    valve_id: str
    sensors_settings: Optional[str]
    starts_at: Optional[float]
    stops_at: Optional[float]
    section_sensors: List[SControl] = []
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

class SectionWithID(BaseModel):
    detail: str = "New section was successfully added to shift"
    id: int
    class Config:
        from_attributes = True

class TimerControl(BaseModel):
    shift_id: int
    Mon: Optional[bool] = None
    Tue: Optional[bool] = None
    Wed: Optional[bool] = None
    Thu: Optional[bool] = None
    Fri: Optional[bool] = None
    Sat: Optional[bool] = None
    Sun: Optional[bool] = None
    starts: Optional[time] = None
    stops: Optional[time] = None
    updated_at: datetime = datetime.now()
    def serialize(self):
        return {"Mon": self.Mon, "Tue": self.Tue, "Wed": self.Wed, "Thu": self.Thu,
                "Fri": self.Fri, "Sat": self.Sat, "Sun": self.Sun,
                "starts": str(self.starts), "stops": str(self.stops)}

class TimerUpdate(BaseModel):
    Mon: Optional[bool]
    Tue: Optional[bool]
    Wed: Optional[bool]
    Thu: Optional[bool]
    Fri: Optional[bool]
    Sat: Optional[bool]
    Sun: Optional[bool]
    starts: Optional[time]
    stops: Optional[time]
    def serialize(self):
        return {"Mon": self.Mon, "Tue": self.Tue, "Wed": self.Wed, "Thu": self.Thu,
                "Fri": self.Fri, "Sat": self.Sat, "Sun": self.Sun,
                "starts": str(self.starts), "stops": str(self.stops)}

class TControl(BaseModel):
    id: int
    updated_at: datetime
    Mon: Union[bool, None] = None
    Tue: Union[bool, None] = None
    Wed: Union[bool, None] = None
    Thu: Union[bool, None] = None
    Fri: Union[bool, None] = None
    Sat: Union[bool, None] = None
    Sun: Union[bool, None] = None
    starts: Union[time, None] = None
    stops: Union[time, None] = None
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

class TControlWithID(BaseModel):
    detail: str = "New timer was successfully added to shift"
    id: int
    class Config:
        from_attributes = True

class AddShift(BaseModel):
    system_id: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class UpdateShift(BaseModel):
    updated_at: datetime = datetime.now()

class Shifts(BaseModel):
    id: int
    updated_at: datetime
    shifts_sections: List[Section] = []
    shift_timers: List[TControl] = []
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

class ShiftsWithID(BaseModel):
    detail: str = "New shift was successfully added to system"
    id: int
    class Config:
        from_attributes = True

class SystemBase(BaseModel):
    name: str
    location: str
    fruit: str
    area: float

class SystemCreate(SystemBase):
    systemID: str
    owner: str

class SystemUpdate(BaseModel):
    name: Optional[str]
    location: Optional[str]
    area: Optional[float]
    fruit: Optional[str]

class SystemID(BaseModel):
    id: int
    name: str
    location: str
    area: float
    fruit: str
    owner: str
    class Config:
        from_attributes = True

class System(SystemBase):
    id: int
    systemID: str
    owner: str
    created_at: datetime
    updated_at: datetime
    system_pumps: List[Pump] = []
    system_valves: List[Valve] = []
    system_sensors: List[Sensor] = []
    system_shifts: List[Shifts] = []
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

class LogCreate(BaseModel):
    dev_id: str
    message: str
    disable: bool = False
    dev_code: int
class Logs(LogCreate):
    date: datetime
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

class UpdateLog(BaseModel):
    disable: bool = True

class CurrentTime(BaseModel):
    current_time: datetime = datetime.now()
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

# Handle admins notifications to users
class NoteCreate(BaseModel):
    user: str
    read: bool = False
    message: str


class Notifications(BaseModel):
    id: int
    user: str
    message: str
    read: bool
    date: datetime

    class Config:
        from_attributes = True

class UpdateNote(BaseModel):
    read: bool = True

#Subscriptions to services
class SubscriberCreate(BaseModel):
    mail: str

class Subscribtion(SubscriberCreate):
    date: datetime

    class Config:
        from_attributes = True

# Handle users reads and creates
class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    surname: str
    address: str
    admin: bool = False
    premium: bool = False

class UserCreate(UserBase):
    password: str
    delisted: bool = True

class User(UserBase):
    delisted: bool
    updated_at: datetime
    created_at: datetime
    systems: List[System] = []
    alerts: List[Notifications] = []
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    address: Optional[str]
    email: Optional[EmailStr]

class AdminUserUpdate(BaseModel):
    admin: Optional[bool]
    premium: Optional[bool]
    delisted: Optional[bool]

# Deals with authorisation and authentications
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class Login(BaseModel):
    username: str
    password: str

class LostPassword(BaseModel):
    password: str

class ResetPassword(BaseModel):
    secret: str
    password: str