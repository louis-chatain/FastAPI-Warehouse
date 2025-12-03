from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv
import os

app = FastAPI()

origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

# Access-Control-Allow-Origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

redis_password = os.environ.get("REDIS_PASSWORD")

if redis_password is None:
    raise Exception("No redis password found.")

redis = get_redis_connection(
    host="redis-11913.c321.us-east-1-2.ec2.cloud.redislabs.com",
    port=11913,
    password=redis_password,
    decode_responses=True,
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


def format(pk: str):
    product = Product.get(pk)
    return {
        "product_id": product.pk,
        "product_name": product.name,
        "product_price": product.price,
        "product_quantity": product.quantity,
    }


@app.post("/product")
def create(product: Product):
    return product.save()


@app.get("/product/read_all")
def read_all():
    product = Product.all_pks()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Product pk not found. database empty boy.")
    return [format(pk) for pk in product]


@app.get("/product/{pk}")
def read(pk: str):
    product = Product.get(pk)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product pk {pk} not found.")
    return product


@app.delete("/product/delete")
def delete(pk: str):
    product = Product.delete(pk)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product pk {pk} not found.")
    return product
