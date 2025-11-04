from django.core.management.base import BaseCommand
from bridges.models import Bridge, TrafficData

class Command(BaseCommand):
    help = 'Load initial bridge data'

    def handle(self, *args, **kwargs):
        bridges_data = [
            {
                'name': 'Bridge 1',
                'bridge_type': 'BEAM_COMPOSITE',
                'length': 46.158,
                'width': 12.5,
                'lanes': 3,
                'material': 'STEEL_CONCRETE',
                'year_built': 2024,
                'route': 'CITY-MASVINGO ROAD WITH AN UNDERPASS',
                'gps_coordinates': 'X=-1593.793 Y=-1981906.781',
                'deck_rating': 5,
                'girders_rating': 5,
                'piers_rating': 1,
                'abutment_rating': 2,
            },
            {
                'name': 'Bridge 2',
                'bridge_type': 'BEAM_COMPOSITE',
                'length': 60.213,
                'width': 12.5,
                'lanes': 3,
                'material': 'STEEL_CONCRETE',
                'year_built': 2024,
                'route': 'GLEN NORAH-CHITUNGWIZA',
                'gps_coordinates': 'X=-1795.167 Y=-1981782.345',
                'deck_rating': 5,
                'girders_rating': 2,
                'piers_rating': 5,
                'abutment_rating': 3,
            },
            {
                'name': 'Bridge 3',
                'bridge_type': 'BEAM_COMPOSITE',
                'length': 46.179,
                'width': 12,
                'lanes': 3,
                'material': 'STEEL_CONCRETE',
                'year_built': 2024,
                'route': 'CITY-MASVINGO ROAD',
                'gps_coordinates': 'X=-1671.849 Y=-1982017.132',
                'deck_rating': 5,
                'girders_rating': 4,
                'piers_rating': 4,
                'abutment_rating': 5,
            },
        ]

        for data in bridges_data:
            bridge, created = Bridge.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {bridge.name}'))

        # Add traffic data
        traffic_data = [
            {'bridge_name': 'Bridge 1', 'heavy_vehicles': 66, 'small_vehicles': 46},
            {'bridge_name': 'Bridge 2', 'heavy_vehicles': 42, 'small_vehicles': 52},
            {'bridge_name': 'Bridge 3', 'heavy_vehicles': 66, 'small_vehicles': 46},
        ]

        for data in traffic_data:
            bridge = Bridge.objects.get(name=data['bridge_name'])
            TrafficData.objects.get_or_create(
                bridge=bridge,
                defaults={
                    'heavy_vehicles': data['heavy_vehicles'],
                    'small_vehicles': data['small_vehicles']
                }
            )

        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))