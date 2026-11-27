from secrets import compare_digest

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqladmin.filters import AllUniqueStringValuesFilter
from sqlalchemy import Engine
from starlette.requests import Request
from wtforms import DecimalField
from wtforms.validators import NumberRange, Optional

from models import (
    Character,
    CharacterItem,
    CharacterQuestItem,
    Enemy,
    EnemyLocation,
    Image,
    Item,
    ItemLocation,
    Location,
    LocationConnection,
    QuestItem,
)
from settings import Settings


class AdminAuth(AuthenticationBackend):
    def __init__(self, settings: Settings) -> None:
        super().__init__(
            secret_key=settings.admin_secret_key.get_secret_value(),
            session_cookie="oponia_admin",
            same_site="strict",
            max_age=3600,
        )
        self.username = settings.admin_username
        self.password = settings.admin_password.get_secret_value()

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", "")).encode()
        password = str(form.get("password", "")).encode()
        valid_username = compare_digest(username, self.username.encode())
        valid_password = compare_digest(password, self.password.encode())
        request.session.clear()
        if not (valid_username and valid_password):
            return False
        request.session["user_id"] = self.username
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("user_id") == self.username


class ImageAdmin(ModelView, model=Image):
    column_list = [Image.label, Image.image]
    column_searchable_list = [Image.label, Image.image]
    column_default_sort = "label"
    form_widget_args = {"ascii_art": {"rows": 12}}


class DisplayAdmin(ModelView):
    column_list = ["name", "slug"]
    column_searchable_list = ["name", "slug"]
    column_sortable_list = ["name", "slug"]
    column_default_sort = "name"
    category = "World"


class LocationAdmin(DisplayAdmin, model=Location):
    form_overrides = {"sell_multiplier": DecimalField}
    form_args = {
        "sell_multiplier": {
            "places": None,
            "validators": [Optional(), NumberRange(min=0, max=1)],
        },
    }
    form_excluded_columns = [
        "characters", "enemy_links", "item_links", "outgoing_connections",
    ]


class EnemyAdmin(DisplayAdmin, model=Enemy):
    form_excluded_columns = ["location_links"]


class ItemAdmin(DisplayAdmin, model=Item):
    column_list = [Item.name, Item.slug, Item.type, Item.price_coins]
    column_filters = [AllUniqueStringValuesFilter(Item.type)]
    form_excluded_columns = ["character_links", "location_links"]


class QuestItemAdmin(DisplayAdmin, model=QuestItem):
    name = "Quest item"
    name_plural = "Quest items"
    form_excluded_columns = ["character_links"]


class CharacterAdmin(ModelView, model=Character):
    category = "Characters"
    column_list = [Character.nickname, Character.level, Character.location]
    column_searchable_list = [Character.nickname]
    column_sortable_list = [Character.nickname, Character.level]
    column_default_sort = "nickname"
    form_excluded_columns = ["item_links", "quest_item_links"]


class LocationConnectionAdmin(ModelView, model=LocationConnection):
    name = "Location connection"
    name_plural = "Location connections"
    category = "World links"
    column_list = ["source", "target", "order", "conditions"]


class EnemyLocationAdmin(ModelView, model=EnemyLocation):
    name = "Enemy placement"
    name_plural = "Enemy placements"
    category = "World links"
    column_list = ["enemy", "location", "order", "conditions"]


class ItemLocationAdmin(ModelView, model=ItemLocation):
    name = "Shop item"
    name_plural = "Shop items"
    category = "World links"
    column_list = ["item", "location", "order", "conditions"]


class CharacterItemAdmin(ModelView, model=CharacterItem):
    name = "Inventory item"
    name_plural = "Inventory items"
    category = "Characters"
    column_list = ["character", "item", "quantity", "equipped"]


class CharacterQuestItemAdmin(ModelView, model=CharacterQuestItem):
    name = "Quest inventory item"
    name_plural = "Quest inventory items"
    category = "Characters"
    column_list = ["character", "quest_item", "quantity"]


def setup_admin(app: FastAPI, engine: Engine, settings: Settings) -> Admin:
    admin = Admin(
        app,
        engine,
        title="Oponia Game",
        authentication_backend=AdminAuth(settings),
    )
    admin.add_view(ImageAdmin)
    admin.add_view(LocationAdmin)
    admin.add_view(EnemyAdmin)
    admin.add_view(ItemAdmin)
    admin.add_view(QuestItemAdmin)
    admin.add_view(CharacterAdmin)
    admin.add_view(LocationConnectionAdmin)
    admin.add_view(EnemyLocationAdmin)
    admin.add_view(ItemLocationAdmin)
    admin.add_view(CharacterItemAdmin)
    admin.add_view(CharacterQuestItemAdmin)

    return admin
