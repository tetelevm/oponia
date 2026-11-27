"""Create initial game schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("image", sa.Text(), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("ascii_art", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "game_enemies",
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_id", sa.Uuid(), nullable=True),
        sa.Column("icon_id", sa.Uuid(), nullable=True),
        sa.Column("health", sa.Integer(), server_default="0", nullable=False),
        sa.Column("damage", sa.Integer(), server_default="0", nullable=False),
        sa.Column("armor", sa.Integer(), server_default="0", nullable=False),
        sa.Column("special_effects", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("btrim(name) <> ''", name="ck_enemies_name_not_blank"),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+([-_][a-z0-9]+)*$'", name="ck_enemies_slug_format"
        ),
        sa.ForeignKeyConstraint(["icon_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        op.f("ix_game_enemies_icon_id"), "game_enemies", ["icon_id"], unique=False
    )
    op.create_index(
        op.f("ix_game_enemies_image_id"), "game_enemies", ["image_id"], unique=False
    )
    op.create_table(
        "game_items",
        sa.Column(
            "type",
            sa.Enum(
                "weapon",
                "secondary_weapon",
                "helmet",
                "armor",
                "gloves",
                "pants",
                "boots",
                "amulet",
                "ring",
                "potion",
                "scroll",
                "enhancement",
                name="game_item_type",
            ),
            nullable=False,
        ),
        sa.Column("price_coins", sa.BigInteger(), nullable=True),
        sa.Column("price_platinum", sa.BigInteger(), nullable=True),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("lifetime", sa.Interval(), nullable=True),
        sa.Column("durability", sa.Integer(), nullable=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_id", sa.Uuid(), nullable=True),
        sa.Column("icon_id", sa.Uuid(), nullable=True),
        sa.Column("health", sa.Integer(), server_default="0", nullable=False),
        sa.Column("damage", sa.Integer(), server_default="0", nullable=False),
        sa.Column("armor", sa.Integer(), server_default="0", nullable=False),
        sa.Column("special_effects", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("btrim(name) <> ''", name="ck_items_name_not_blank"),
        sa.CheckConstraint("lifetime > INTERVAL '0 seconds'", name="ck_items_lifetime"),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+([-_][a-z0-9]+)*$'", name="ck_items_slug_format"
        ),
        sa.CheckConstraint("durability >= 0", name="ck_items_durability"),
        sa.CheckConstraint("price_coins >= 0", name="ck_items_price_coins"),
        sa.CheckConstraint("price_platinum >= 0", name="ck_items_price_platinum"),
        sa.CheckConstraint("quantity >= 1", name="ck_items_quantity"),
        sa.ForeignKeyConstraint(["icon_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        op.f("ix_game_items_icon_id"), "game_items", ["icon_id"], unique=False
    )
    op.create_index(
        op.f("ix_game_items_image_id"), "game_items", ["image_id"], unique=False
    )
    op.create_table(
        "game_locations",
        sa.Column("sell_multiplier", sa.Float(), nullable=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_id", sa.Uuid(), nullable=True),
        sa.Column("icon_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("btrim(name) <> ''", name="ck_locations_name_not_blank"),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+([-_][a-z0-9]+)*$'", name="ck_locations_slug_format"
        ),
        sa.CheckConstraint(
            "sell_multiplier BETWEEN 0 AND 1", name="ck_locations_sell_multiplier"
        ),
        sa.ForeignKeyConstraint(["icon_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        op.f("ix_game_locations_icon_id"), "game_locations", ["icon_id"], unique=False
    )
    op.create_index(
        op.f("ix_game_locations_image_id"), "game_locations", ["image_id"], unique=False
    )
    op.create_table(
        "game_quest_items",
        sa.Column("lifetime", sa.Interval(), nullable=True),
        sa.Column(
            "visible", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_id", sa.Uuid(), nullable=True),
        sa.Column("icon_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("btrim(name) <> ''", name="ck_quest_items_name_not_blank"),
        sa.CheckConstraint(
            "lifetime > INTERVAL '0 seconds'", name="ck_quest_items_lifetime"
        ),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+([-_][a-z0-9]+)*$'", name="ck_quest_items_slug_format"
        ),
        sa.ForeignKeyConstraint(["icon_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        op.f("ix_game_quest_items_icon_id"),
        "game_quest_items",
        ["icon_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_game_quest_items_image_id"),
        "game_quest_items",
        ["image_id"],
        unique=False,
    )
    op.create_table(
        "game_characters",
        sa.Column("nickname", sa.String(length=64), nullable=False),
        sa.Column("level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("experience", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("fame", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("coins", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("platinum", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("coupons", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("image_id", sa.Uuid(), nullable=True),
        sa.Column("location_id", sa.Uuid(), nullable=False),
        sa.Column("health", sa.Integer(), server_default="0", nullable=False),
        sa.Column("damage", sa.Integer(), server_default="0", nullable=False),
        sa.Column("armor", sa.Integer(), server_default="0", nullable=False),
        sa.Column("special_effects", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "btrim(nickname) <> ''", name="ck_characters_nickname_not_blank"
        ),
        sa.CheckConstraint("coins >= 0", name="ck_characters_coins"),
        sa.CheckConstraint("coupons >= 0", name="ck_characters_coupons"),
        sa.CheckConstraint("experience >= 0", name="ck_characters_experience"),
        sa.CheckConstraint("fame >= 0", name="ck_characters_fame"),
        sa.CheckConstraint("level >= 1", name="ck_characters_level"),
        sa.CheckConstraint("platinum >= 0", name="ck_characters_platinum"),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["location_id"], ["game_locations.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_game_characters_image_id"),
        "game_characters",
        ["image_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_game_characters_location_id"),
        "game_characters",
        ["location_id"],
        unique=False,
    )
    op.create_table(
        "game_enemy_locations",
        sa.Column("order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("enemy_id", sa.Uuid(), nullable=False),
        sa.Column("location_id", sa.Uuid(), nullable=False),
        sa.Column(
            "conditions",
            postgresql.ARRAY(sa.String(length=64)),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["enemy_id"], ["game_enemies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["location_id"], ["game_locations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("enemy_id", "location_id", name="uq_enemy_locations_pair"),
    )
    op.create_index(
        op.f("ix_game_enemy_locations_location_id"),
        "game_enemy_locations",
        ["location_id"],
        unique=False,
    )
    op.create_table(
        "game_item_locations",
        sa.Column("order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("location_id", sa.Uuid(), nullable=False),
        sa.Column(
            "conditions",
            postgresql.ARRAY(sa.String(length=64)),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["game_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["location_id"], ["game_locations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id", "location_id", name="uq_item_locations_pair"),
    )
    op.create_index(
        op.f("ix_game_item_locations_location_id"),
        "game_item_locations",
        ["location_id"],
        unique=False,
    )
    op.create_table(
        "game_location_connections",
        sa.Column("order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column(
            "conditions",
            postgresql.ARRAY(sa.String(length=64)),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["source_id"], ["game_locations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["target_id"], ["game_locations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_id", "target_id", name="uq_location_connections_pair"
        ),
    )
    op.create_index(
        op.f("ix_game_location_connections_target_id"),
        "game_location_connections",
        ["target_id"],
        unique=False,
    )
    op.create_table(
        "game_character_items",
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("character_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("durability", sa.Integer(), nullable=True),
        sa.Column(
            "equipped", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("durability >= 0", name="ck_character_items_durability"),
        sa.CheckConstraint("quantity >= 0", name="ck_character_items_quantity"),
        sa.ForeignKeyConstraint(
            ["character_id"], ["game_characters.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["item_id"], ["game_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_game_character_items_character_id"),
        "game_character_items",
        ["character_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_game_character_items_item_id"),
        "game_character_items",
        ["item_id"],
        unique=False,
    )
    op.create_table(
        "game_character_quest_items",
        sa.Column("quest_item_id", sa.Uuid(), nullable=False),
        sa.Column("character_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("quantity >= 0", name="ck_character_quest_items_quantity"),
        sa.ForeignKeyConstraint(
            ["character_id"], ["game_characters.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["quest_item_id"], ["game_quest_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_game_character_quest_items_character_id"),
        "game_character_quest_items",
        ["character_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_game_character_quest_items_quest_item_id"),
        "game_character_quest_items",
        ["quest_item_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_game_character_quest_items_quest_item_id"),
        table_name="game_character_quest_items",
    )
    op.drop_index(
        op.f("ix_game_character_quest_items_character_id"),
        table_name="game_character_quest_items",
    )
    op.drop_table("game_character_quest_items")
    op.drop_index(
        op.f("ix_game_character_items_item_id"), table_name="game_character_items"
    )
    op.drop_index(
        op.f("ix_game_character_items_character_id"), table_name="game_character_items"
    )
    op.drop_table("game_character_items")
    op.drop_index(
        op.f("ix_game_location_connections_target_id"),
        table_name="game_location_connections",
    )
    op.drop_table("game_location_connections")
    op.drop_index(
        op.f("ix_game_item_locations_location_id"), table_name="game_item_locations"
    )
    op.drop_table("game_item_locations")
    op.drop_index(
        op.f("ix_game_enemy_locations_location_id"), table_name="game_enemy_locations"
    )
    op.drop_table("game_enemy_locations")
    op.drop_index(op.f("ix_game_characters_location_id"), table_name="game_characters")
    op.drop_index(op.f("ix_game_characters_image_id"), table_name="game_characters")
    op.drop_table("game_characters")
    op.drop_index(op.f("ix_game_quest_items_image_id"), table_name="game_quest_items")
    op.drop_index(op.f("ix_game_quest_items_icon_id"), table_name="game_quest_items")
    op.drop_table("game_quest_items")
    op.drop_index(op.f("ix_game_locations_image_id"), table_name="game_locations")
    op.drop_index(op.f("ix_game_locations_icon_id"), table_name="game_locations")
    op.drop_table("game_locations")
    op.drop_index(op.f("ix_game_items_image_id"), table_name="game_items")
    op.drop_index(op.f("ix_game_items_icon_id"), table_name="game_items")
    op.drop_table("game_items")
    op.drop_index(op.f("ix_game_enemies_image_id"), table_name="game_enemies")
    op.drop_index(op.f("ix_game_enemies_icon_id"), table_name="game_enemies")
    op.drop_table("game_enemies")
    op.drop_table("images")
    postgresql.ENUM(name="game_item_type").drop(op.get_bind())
