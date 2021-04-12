# 스파크 데이터프레임 생성
# 1000개의 행과 1개의 열을 갖는 데이터프레임
# 각 행마다 0~999 값 지정
myRange = spark.range(1000).toDF("number")


# COMMAND ----------

# where 메서드는 좁은 의존성을 갖는 트랜스포메이션
# 트랜스포메이션은 데이터프레임을 변환하게 해주는 메서드들을 일컫음
# 데이터프레임은 불변성을 가지므로 프레임 내의 데이터는 변경 불가능함. 따라서 트랜스포메이션을 통해서만 변경 가능
# 스파크는 분산 클러스터 컴퓨팅 엔진. 따라서 빅데이터를 처리하기 위해 모든 데이터를 읽어오지 않음
# 따라서 데이터프레임의 컬럼명과 일부분에 관한 정보들만 읽어옴 (스키마 추론)
# 트랜스포메이션은 실제로 코드를 실행하는 것이 아닌 '실행 계획'을 만들어둠

# 데이터프레임에서 짝수값을 가지는 행만 찾기
divisBy2 = myRange.where("number % 2 = 0")


# COMMAND ----------

# 데이터프레임 구문을 이용해 데이터 불러오기
# 만약 databricks 에서 작업한다면 csv 경로는 책 참조
# databricks는 웹에서 클라우드 컴퓨팅을 지원해주는 UI 제공 사이트로, 제플린과 더불어 자주 씀 (노트북 형식 IDE 제공)
flightData2015 = spark\
  .read\
  .option("inferSchema", "true")\
  .option("header", "true")\
  .csv("/data/flight-data/csv/2015-summary.csv")

# COMMAND ----------

# 데이터프레임을 SQL 쿼리문을 통해 ETL하기 위해서는 테이블/뷰로 생성/변환이 필요
flightData2015.createOrReplaceTempView("flight_data_2015")


# COMMAND ----------

# SparkSession의 sql 메서드를 통해 SQL 쿼리 작성
sqlWay = spark.sql("""
SELECT DEST_COUNTRY_NAME, count(1)
FROM flight_data_2015
GROUP BY DEST_COUNTRY_NAME
""")

# 데이터프레임 구문을 통해 SQL과 동일한 명령 수행
dataFrameWay = flightData2015\
  .groupBy("DEST_COUNTRY_NAME")\
  .count()

# 실제 실행 계획을 비교해보면 동일함
# explain 메서드는 실제로 실행 계획이 어떠한지 출력하여 보여주는 메서드
sqlWay.explain()
dataFrameWay.explain()


# COMMAND ----------

# pyspark 패키지에서 max 함수 임포트
from pyspark.sql.functions import max

# 테이블에서 count 컬럼의 최대값 조회
# take 메서드는 '액션' 메서드 중 하나로, 액션은 앞서 이야기한 트랜스포메이션을 직접 실행시키는 것을 말함
# take 메서드는 결과값 중 1개만 가져오는 메서드
flightData2015.select(max("count")).take(1)


# COMMAND ----------

# SparkSession의 sql 메서드를 통해 SQL 쿼리 작성
maxSql = spark.sql("""
SELECT DEST_COUNTRY_NAME, sum(count) as destination_total
FROM flight_data_2015
GROUP BY DEST_COUNTRY_NAME
ORDER BY sum(count) DESC
LIMIT 5
""")

maxSql.show()


# COMMAND ----------

# 역순 정렬을 위해 pyspark에서 desc 임포트
from pyspark.sql.functions import desc

# 데이터프레임 구문을 통해 SQL 쿼리문과 동일한 명령 작성
flightData2015\
  .groupBy("DEST_COUNTRY_NAME")\
  .sum("count")\
  .withColumnRenamed("sum(count)", "destination_total")\
  .sort(desc("destination_total"))\
  .limit(5)\
  .show()


# COMMAND ----------

# 앞선 SQL 쿼리문과 왜 동일한지 실행 계획을 조회해보면 알 수 있음
flightData2015\
  .groupBy("DEST_COUNTRY_NAME")\
  .sum("count")\
  .withColumnRenamed("sum(count)", "destination_total")\
  .sort(desc("destination_total"))\
  .limit(5)\
  .explain()


# COMMAND ----------
