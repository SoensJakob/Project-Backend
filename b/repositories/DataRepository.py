from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_latest_data():
        
        sql = "SELECT d.afkorting, d.eenheid, h.device_id, `timestamp` as timestamp, waarde FROM historiek h JOIN device d ON d.device_id = h.device_id WHERE `timestamp` = (SELECT max(timestamp) FROM historiek where device_id < 5) GROUP BY device_id HAVING h.waarde is not null ORDER BY device_id DESC"

        return Database.get_rows(sql)

    @staticmethod
    def read_historiek_by_device_id(id):
        sql = "SELECT * FROM historiek WHERE device_id = %s"
        params = [id]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_historiek_by_device_id_and_day(id,date):
        sql = "SELECT * FROM historiek WHERE device_id = %s and date(`timestamp`) = %s"
        params = [id,date]
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_historiek_by_device_id_and_month(id,date):
        sql = "SELECT * FROM historiek WHERE device_id = %s and month(`timestamp`) = month(%s) GROUP BY UNIX_TIMESTAMP(timestamp) DIV 300"
        params = [id,date]
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_historiek_by_device_id_and_3month(id,date):
        sql = "SELECT * FROM historiek WHERE device_id = %s and month(`timestamp`)-1 <= month(%s)+1 GROUP BY UNIX_TIMESTAMP(timestamp) DIV 300"
        
        params = [id,date]
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_actuators():
        sql = "SELECT * FROM device WHERE eenheid is null"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_AP_action():
        sql = "SELECT device_id, `status` from historiek h where `timestamp` = (SELECT max(timestamp) FROM historiek where device_id = 5) and device_id = 5"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_AH_action():
        sql = "SELECT device_id, `status` from historiek h where `timestamp` = (SELECT max(timestamp) FROM historiek where device_id = 6) and device_id = 6"
        return Database.get_rows(sql)

    @staticmethod
    def read_sensors():
        sql = "SELECT * FROM device WHERE eenheid is not null"
        return Database.get_rows(sql)
    
    @staticmethod
    def create_historiek(deviceid,timestamp,waarde=None,status=None):
        sql = "INSERT INTO historiek(device_id, `timestamp`, waarde, `status`) VALUES(%s,%s,%s,%s)"
        params = [deviceid,timestamp,waarde,status] 
        return Database.execute_sql(sql, params)

    