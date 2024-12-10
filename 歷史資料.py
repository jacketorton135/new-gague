import pymysql

def fetch_health_data():
    # 連接到數據庫
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='oneokrock12345',
        database='heart rate monitor'
    )

    cursor = conn.cursor()

    # 查詢生成
    query = """
    SELECT 
        時間戳記 as timestamp,
        溫度,
        濕度,
        溫度狀態,
        濕度狀態,
        體溫,
        體溫狀態
    FROM
        dht11
    WHERE
        溫度狀態 != '溫度正常' OR 濕度狀態 != '濕度正常' OR 體溫狀態 != '體溫正常'
    UNION ALL
    SELECT
        時間戳記 as timestamp,
        姓名,
        性別,
        身高,
        體重,
        BMI,
        標準體重,
        檢查結果
    FROM
        bmi
    WHERE
        正常_異常 = 0
    UNION ALL
    SELECT
        時間戳記 as timestamp,
        心跳,
        心跳狀態
    FROM
        heart_rate
    WHERE
        心跳正常 = 0
    ORDER BY timestamp DESC
    """

    # 執行查詢
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    except pymysql.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        # 關閉連接
        cursor.close()
        conn.close()

# 呼叫函式並打印結果
if __name__ == "__main__":
    data = fetch_health_data()
    for row in data:
        print(row)

