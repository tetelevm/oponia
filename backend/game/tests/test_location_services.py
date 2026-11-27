from database_case import DatabaseTestCase
from models import Location, LocationConnection
from services.locations import get_available_locations


class AvailableLocationTests(DatabaseTestCase):
    def test_outgoing_destinations_are_sorted_and_conditions_are_ignored(self) -> None:
        locations = {
            slug: Location(slug=slug, name=slug.title())
            for slug in ("village", "cave", "forest", "tower", "lake", "incoming")
        }
        self.session.add_all(locations.values())
        for slug, order in (
            ("cave", 2),
            ("forest", -1),
            ("tower", 0),
            ("lake", 0),
        ):
            self.session.add(
                LocationConnection(
                    source=locations["village"],
                    target=locations[slug],
                    order=order,
                    conditions=["requires-key"],
                )
            )
        self.session.add(
            LocationConnection(
                source=locations["incoming"],
                target=locations["village"],
                order=-2,
            )
        )
        self.session.commit()

        destinations = get_available_locations(self.session, locations["village"].id)
        self.assertEqual(
            [location.slug for location in destinations],
            ["forest", "lake", "tower", "cave"],
        )
        self.assertEqual(
            get_available_locations(self.session, locations["cave"].id),
            [],
        )
