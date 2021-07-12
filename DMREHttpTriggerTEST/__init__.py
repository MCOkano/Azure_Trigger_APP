import logging

import azure.functions as func

#DBアクセス用ライブラリ
import pyodbc

#日付取得用
import datetime

#DB接続
def connectSQL():
    server = 'mcdev001.database.windows.net'
    database = 'DMRE_Demo_1st'
    username = 'mcroot'
    password = 'mlG0klf$3_6r'   
    driver= '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()
    print("SQL Connect OK")
    return conn,cursor

#DB切断
def closeSQL(_cursor,_conn):
    _cursor.close()
    _conn.close()
    print("SQL Close OK")
    return

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    apid = req.params.get('apid')
    logging.info(apid) 

    if apid == "scn":

        id = req.params.get('id')
        kind = req.params.get('kind')
        reg_date = str(datetime.date.today())
        input_data = req.params.get('data')

        logging.info(id) 
        logging.info(kind)
        logging.info(reg_date)
        logging.info(input_data)

        #DB読出し
        cn,cur = connectSQL()
        cur.execute("select * from Table_D_テストテーブル")
        rows = cur.fetchall()
        closeSQL(cur,cn)
        logging.info("【DEB】パス0") 

        if id != "":
            text = "入力された登録ＩＤは" + id + "です。"
            logging.info(text)
            logging.info("【DEB】パス1") 
            for r in rows:
                did = r[4]
                dkind = r[2]
                logging.info(did)
                logging.info(dkind)
                if id == r[4]:
                    logging.info("【DEB】パス2") 
                    if kind == r[2]:
                        text2 ="入力したＩＤ、種別が重複しています。"
                        logging.info(text2)
                        logging.info("【DEB】パス3") 
                        return func.HttpResponse(text2)
                    else:
                        logging.info("【DEB】パス4") 

            text2 ="登録完了 注文番号：" + id + " 種別：" + kind + " 登録日：" + reg_date + " 登録内容：" + input_data  
            logging.info(text2)

            cn,cur = connectSQL()
            cur.execute("""
            INSERT INTO Table_D_テストテーブル (注文番号,日付,種別,内容)
            VALUES (?,?,?,?)""",
            id, reg_date, kind, input_data)
            cur.commit()

            closeSQL(cur,cn)

            logging.info("【DEB】パス6") 

            return func.HttpResponse(text2)

        else:
            logging.info("【DEB】パス7") 
            text = "登録IDが入力されていません。"     
            logging.info(text)
            return func.HttpResponse(text)

    elif apid == "rd":

        rows = []
        rows2 = []
        in_date = req.params.get('date')
        log_text = "【DEB】" + in_date
        logging.info(log_text)
        tmp_data = in_date.translate(str.maketrans('年月','--')) 
        date = tmp_data.replace('日','')
        log_text = "【DEB】" + date
        logging.info(log_text)

        #DB読出し
        cn,cur = connectSQL()
        cur.execute("select * from Table_D_テストテーブル")
        rows = cur.fetchall()
        closeSQL(cur,cn)

        logging.info("【DEB】パス0") 

        if date:
            for r in rows:
                if date == r[1]:
                    logging.info("【DEB】パス1") 
                    rows2.append(r[4])

            if len(rows) == 0:
                logging.info("【DEB】パス2") 
                return func.HttpResponse("該当するデータはありませんでした。")
            else:
                logging.info("【DEB】パス3") 
                logging.info(rows2) 
                return func.HttpResponse(str(rows2))
 
        else:
            logging.info('Dateなし') 
            return func.HttpResponse(
                 "該当するデータはありませんでした。",status_code=200
            )

    else:

        logging.info('該当処理なし') 
        return func.HttpResponse(
            "該当する処理はありません。",status_code=200
        )

