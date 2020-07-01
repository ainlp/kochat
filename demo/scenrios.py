"""
@auther Hyunwoong
@since 7/1/2020
@see https://github.com/gusdnd852
"""

from kocrawl.dust import DustCrawler
from kocrawl.map import MapCrawler
from kocrawl.retaurant import RestaurantCrawler
from kocrawl.weather import WeatherCrawler
from kochat.app import Scenario


weather = Scenario(
    intent='weather',
    api=WeatherCrawler().request,
    scenario_dict={
        'LOCATION': [],
        'DATE': ['오늘']
    }
)

dust = Scenario(
    intent='dust',
    api=DustCrawler().request,
    scenario_dict={
        'LOCATION': [],
        'DATE': ['오늘']
    }
)

travel = Scenario(
    intent='travel',
    api=MapCrawler().request,
    scenario_dict={
        'LOCATION': [],
        'TRAVEL': ['여행지']
    }
)

restaurant = Scenario(
    intent='restaurant',
    api=RestaurantCrawler().request,
    scenario_dict={
        'LOCATION': [],
        'TRAVEL': ['맛집']
    }
)
