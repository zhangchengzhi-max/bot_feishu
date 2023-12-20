import pymysql

def dbUtil():
    conn = pymysql.connect(host='devdb57-mgr-mysql-dev.chj.cloud', user='vfsc_DevCaseManage_rw',
                           password='ROttfnDkh0D6aZ1g', port=37013, database='vfsc_DevCaseManage')
    cursor = conn.cursor()
    cursor.execute("select * from bus_baseline_strategy where baseline_grade = 3")
    resut = cursor.fetchall()
    return resut