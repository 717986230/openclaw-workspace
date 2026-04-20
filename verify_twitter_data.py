import mysql.connector

# 连接到MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root123',
    database='crawler_db'
)

cursor = conn.cursor()

# 查询Twitter推文
cursor.execute('SELECT id, author_name, text, likes, retweets FROM twitter_tweets LIMIT 5')
results = cursor.fetchall()

print('Twitter推文数据:')
print('-' * 80)

for row in results:
    print(f'ID: {row[0]}')
    print(f'作者: {row[1]}')
    print(f'内容: {row[2][:50]}...')
    print(f'点赞: {row[3]}, 转发: {row[4]}')
    print('-' * 80)

# 统计信息
cursor.execute('SELECT COUNT(*) FROM twitter_tweets')
total = cursor.fetchone()[0]

cursor.execute('SELECT SUM(likes), SUM(retweets), SUM(views) FROM twitter_tweets')
metrics = cursor.fetchone()

print(f'总计: {total} 条推文')
print(f'总点赞: {metrics[0]}, 总转发: {metrics[1]}, 总浏览: {metrics[2]}')

conn.close()
