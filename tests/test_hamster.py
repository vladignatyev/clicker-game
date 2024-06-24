from datetime import datetime
from hamster import (
    create_initial_state,
    click,
    buy_card,
    State,
    Card,
    seconds_to_next_levelup,
    time_travel,
    time_travel_iterative,
)


def test_initial():
    initial = create_initial_state(datetime(year=2024, month=6, day=22))
    assert type(initial) is State
    assert initial.balance == 0
    assert initial.energy > 0


def test_click():
    initial = create_initial_state(datetime(year=2024, month=6, day=22))
    state = initial
    for _ in range(10):
        state = click(
            state, datetime(year=2024, month=6, day=22, hour=0, minute=0, second=0)
        )

    assert state.balance == 10
    assert state.energy == 990


def test_energy_restore():
    initial = create_initial_state(datetime(year=2024, month=6, day=22))
    state = initial
    for _ in range(1000):
        state = click(
            state, datetime(year=2024, month=6, day=22, hour=0, minute=0, second=0)
        )

    state = click(
        state, datetime(year=2024, month=6, day=22, hour=0, minute=0, second=5)
    )

    assert state.balance == 1001
    assert state.energy == 4


def test_time_travel():
    initial = create_initial_state(datetime(year=2024, month=6, day=22))
    future = time_travel(initial, datetime(year=2025, month=6, day=22))

    assert future.balance == initial.balance
    assert future.energy == initial.energy
    assert future.level == initial.level
    assert future.total_earned == initial.total_earned
    assert future.cards == initial.cards
    assert future.energy_per_second == initial.energy_per_second
    assert future.profit_per_second == initial.profit_per_second
    assert future.profit_per_click == initial.profit_per_click
    assert future.timestamp == datetime(year=2025, month=6, day=22)


def test_cards():
    card = Card(
        price=100,
        profit_per_second=4,
        profit_per_click=1,
        energy_per_second=1,
        own_since=datetime(year=2024, month=6, day=22),
    )
    initial = create_initial_state(datetime(year=2024, month=6, day=22))
    initial.balance = 1000
    state = buy_card(initial, initial.timestamp, card)

    assert state.balance == 900
    assert state.energy == 1000
    assert state.profit_per_second == 4


def test_year_travel():
    t1 = datetime(year=2024, month=6, day=22)
    t2 = datetime(year=2025, month=6, day=22)

    initial = create_initial_state(t1)
    card = Card(
        price=100,
        profit_per_second=4,
        profit_per_click=1,
        energy_per_second=1,
        own_since=datetime(year=2024, month=6, day=22),
    )
    initial.balance = 1000
    state = buy_card(initial, initial.timestamp, card)

    assert state.profit_per_second == 4

    future = time_travel_iterative(state, t2)

    assert future.balance == 126144900


def test_seconds_to_next_levelup():
    initial = create_initial_state(datetime(year=2024, month=6, day=22))
    card = Card(
        price=100,
        profit_per_second=4,
        profit_per_click=1,
        energy_per_second=1,
        own_since=datetime(year=2024, month=6, day=22),
    )
    initial.balance = 1000
    initial.total_earned = 1000
    state = buy_card(initial, initial.timestamp, card)

    assert state.total_earned == 1000

    # so remained to earn 2nd level is 9100

    assert seconds_to_next_levelup(state) == 2275
