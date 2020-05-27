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
    def read_status_lampen():
        sql = "SELECT * from lampen"
        return Database.get_rows(sql)

    @staticmethod
    def read_historiek_by_device_id(id):
        sql = "SELECT * FROM historiek WHERE device_id = %s;"
        params = [id]
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_actuator():
        sql = "SELECT * FROM device WHERE eenheid is null"
        return Database.get_rows(sql)
    
    @staticmethod
    def create_historiek(deviceid,timestamp,waarde=None,status=None):
        sql = "INSERT INTO historiek(device_id, `timestamp`, waarde, `status`) VALUES(%s,%s,%s,%s)"
        params = [deviceid,timestamp,waarde,status] 
        return Database.execute_sql(sql, params)
