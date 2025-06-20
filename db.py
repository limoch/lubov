import aiosqlite

DB_NAME = "users.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                gender TEXT,
                interests TEXT,
                photo_id TEXT
            )
        ''')
        await db.commit()


async def save_user(user_id: int, name: str, age: int, gender: str, interests: str, photo_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (user_id, name, age, gender, interests, photo_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, age, gender, interests, photo_id))
        await db.commit()



async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT name, age, gender, interests, photo_id FROM users WHERE user_id = ?', (user_id,))
        return await cursor.fetchone()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id, name, age, gender, interests, photo_id FROM users")
        return await cursor.fetchall()



async def delete_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        await db.commit()
