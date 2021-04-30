from tortoise import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=128, null=True)
    last_name = fields.CharField(max_length=128)
    first_name = fields.CharField(max_length=128)
    chat_id = fields.IntField()
    created = fields.DatetimeField(auto_now=True)


class Package(Model):
    id = fields.CharField(max_length=13, pk=True)
    description = fields.TextField()
    created = fields.DatetimeField(auto_now=True)
    done = fields.BooleanField(default=False)
    user = fields.ForeignKeyField('diff_models.User', 'packages', on_delete='CASCADE')


class Action(Model):
    id = fields.IntField(pk=True)
    date = fields.DateField()
    action = fields.TextField()
    office = fields.TextField()
    order_num = fields.SmallIntField(null=True)
    created = fields.DatetimeField(auto_now=True)
    package = fields.ForeignKeyField('diff_models.Package', 'actions', on_delete='CASCADE')
from tortoise import Model, fields


class Aerich(Model):
    version = fields.CharField(max_length=50)
    app = fields.CharField(max_length=20)

    class Meta:
        ordering = ["-id"]
