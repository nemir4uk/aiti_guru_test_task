from typing import Annotated
from os import getenv
from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.postgres.pg_db import get_async_session
from pydantic import BaseModel, Field
load_dotenv(find_dotenv())


class AddItemRequest(BaseModel):
    client_id: int
    product_id: int
    category_id: int
    quantity: int = Field(gt=0)


app = FastAPI()


@app.get('/add_item')
async def analysis(
        product_id: int,
        category_id: int,
        client_id: int,
        current_quantity: int,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    product_query = await session.execute(text(f"""select quantity from products
        where id = {product_id} and category_id = {category_id}"""))
    product = product_query.fetchone()
    if not product:
        raise HTTPException(404, "Product not found")
    if product[0] <= current_quantity:
        raise HTTPException(400, "Not enough stock")
    upsert_stmt = text(f"""insert into order_items (client_id, product_id, quantity)
        values ({client_id}, {product_id}, 1)
        on conflict (order_id, product_id)
        do update
        set quantity = {current_quantity}""")
    await session.execute(upsert_stmt)
    await session.commit()
    return JSONResponse(content={'status': 'success', 'or': 'whatever'}, status_code=200)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
