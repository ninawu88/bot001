from marshmallow import Schema, fields

# mashamallow
ModemSchema_750 = Schema.from_dict(
    {'id': fields.Int(),
    'transactionId': fields.Str(), 
    'messageEncoding': fields.Str(), 
    'messageType': fields.Str(), 
    'modemId': fields.Str(), 
    'messageId': fields.Str(), 
    'dataLength': fields.Str(), 
    'gpsTime': fields.DateTime(),
    'latitude': fields.Float(), 
    'longitude': fields.Float(), 
    'altitude': fields.Float(), 
    'speed': fields.Float(), 
    'direction': fields.Float(), 
    'odometer': fields.Int(), 
    'hdop': fields.Float(), 
    'satellites': fields.Int(), 
    'ioStatus': fields.Str(), 
    'reserved': fields.Str(), 
    'mainPowerVoltage': fields.Float(), 
    'backupBatteryVoltage': fields.Float(),
    'rtcTime': fields.DateTime(),
    'posTime': fields.DateTime(),
    'csq': fields.Str(),
    'mcuMotorRpm': fields.Int(),
    'obdSpeed': fields.Int(),
    'bmsBatterySoc': fields.Int(),
    'mtrOdoData': fields.Str(),
    'keyStatus': fields.Str(),
    'chargingStatus': fields.Str()
    }
)
