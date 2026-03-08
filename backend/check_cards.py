import sqlite3

# 连接数据库
conn = sqlite3.connect('devkit.db')
cursor = conn.cursor()

# 查询最近的10个卡片
cursor.execute('SELECT id, title, project_id FROM card ORDER BY id DESC LIMIT 10')
rows = cursor.fetchall()

print('最近10个卡片:')
for row in rows:
    print(f'ID: {row[0]}, 标题: {row[1]}, 项目ID: {row[2]}')

# 查询项目信息
cursor.execute('SELECT id, name FROM project')
projects = cursor.fetchall()
print('\n所有项目:')
for project in projects:
    print(f'项目ID: {project[0]}, 名称: {project[1]}')

# 统计每个项目的卡片数量
cursor.execute('SELECT project_id, COUNT(*) as card_count FROM card GROUP BY project_id ORDER BY project_id')
counts = cursor.fetchall()
print('\n各项目卡片数量:')
for count in counts:
    print(f'项目ID: {count[0]}, 卡片数量: {count[1]}')

conn.close()