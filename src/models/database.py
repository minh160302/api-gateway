from tortoise.models import Model
from tortoise import fields, Tortoise


class Registration(Model):
    email = fields.CharField(max_length=255, primary_key=True)
    api_key = fields.CharField(max_length=255)


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['models.database']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()
    # Insert test value
    reg = await Registration.filter(api_key='your-secret-token')
    if not reg:
        registration = Registration(
            api_key='your-secret-token', email='test@email.com')
        await registration.save()


async def destroy():
    await Tortoise.close_connections()
