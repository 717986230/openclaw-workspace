import sqlite3

# 连接到SQLite
conn = sqlite3.connect('twitter_crawler.db')
cursor = conn.cursor()

# 查询Twitter推文
cursor.execute('SELECT COUNT(*) FROM twitter_tweets')
total = cursor.fetchone()[0]

print(f'SQLite数据库: {total} 条推文')

if total > 0:
    print('推文示例:')
    print('-' * 80)

    cursor.execute('SELECT id, author_name, text, likes FROM twitter_tweets LIMIT 3')
    results = cursor.fetchall()

    for row in results:
        print(f'ID: {row[0]}')
        print(f'作者: {row[1]}')
        print(f'内容: {row[2][:50]}...')
        print(f'点赞: {row[3]}')
        print('-' * 80)

conn.close()
