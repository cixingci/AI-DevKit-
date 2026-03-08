import sqlite3

# 连接数据库
conn = sqlite3.connect('devkit.db')
cursor = conn.cursor()

# 查询卡片和类型关联信息
cursor.execute('SELECT c.id, c.title, c.card_type_id, ct.name FROM card c LEFT JOIN cardtype ct ON c.card_type_id = ct.id')
rows = cursor.fetchall()

print('卡片和类型信息:')
for row in rows:
    print(f'卡片ID: {row[0]}, 标题: {row[1]}, 类型ID: {row[2]}, 类型名称: {row[3]}')

# 查询卡片类型信息
cursor.execute('SELECT id, name FROM cardtype')
types = cursor.fetchall()
print('\n所有卡片类型:')
for card_type in types:
    print(f'类型ID: {card_type[0]}, 名称: {card_type[1]}')

conn.close()