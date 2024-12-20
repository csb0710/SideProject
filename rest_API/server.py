import hashlib
import random
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import aiomysql

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "0000",
    "db": "black_friday",  
}

cache = {}

async def create_database_if_not_exists():
    conn = await aiomysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    async with conn.cursor() as cur:
        await cur.execute("CREATE DATABASE IF NOT EXISTS black_friday")
        await conn.commit()
    conn.close()

async def initialize_products():
    endpoint = "/products"
    cache_key = endpoint
    cache[cache_key] = {
            "last_updated": None,
            "etag": None
        }
    async with aiomysql.connect(**DB_CONFIG) as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                original_price INT,
                discount_price INT,
                discount_rate INT
            )
            """)
            await cur.execute("DELETE FROM products")

            products = []
            for i in range(100):
                name = f"Product {i+1}"
                original_price = random.randint(100, 1000)
                discount_rate = random.randint(10, 50)
                discount_price = int(original_price * (1 - discount_rate / 100))
                products.append((name, original_price, discount_price, discount_rate))

            await cur.executemany(
                "INSERT INTO products (name, original_price, discount_price, discount_rate) VALUES (%s, %s, %s, %s)",
                products,
            )
            await conn.commit()

async def fetch_and_update_cache():
    async with aiomysql.connect(**DB_CONFIG) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, name, original_price, discount_price, discount_rate FROM products ORDER BY discount_rate DESC LIMIT 10")
            products = await cur.fetchall()
            return products

async def update_discount_rate_and_price_periodically():
    cache_key = "/products"
    while True:
        async with aiomysql.connect(**DB_CONFIG) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    UPDATE products
                    SET discount_rate = ROUND(RAND() * 50 + 10),
                        discount_price = original_price * (1 - discount_rate / 100)
                """)
                await conn.commit()

        current_time = datetime.utcnow()
        etag = hashlib.sha256(str(current_time).encode()).hexdigest()

        cache[cache_key] = {
            "last_updated": current_time,
            "etag": etag
        }

        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    await create_database_if_not_exists()
    await initialize_products()
    asyncio.create_task(update_discount_rate_and_price_periodically())

@app.get("/products")
async def get_products(request: Request):
    cache_key = "/products"
    
    cache_etag = cache[cache_key]["etag"]
    if_none_match = request.headers.get("If-None-Match")

    if cache_etag is None or if_none_match != cache_etag:
        products = await fetch_and_update_cache()

        response = JSONResponse(content={"products": products})
        response.headers["Last-Modified"] = cache[cache_key]["last_updated"].strftime("%a, %d %b %Y %H:%M:%S GMT")
        response.headers["ETag"] = cache[cache_key]["etag"]
        return response
    
    return JSONResponse(status_code=304, content={})
