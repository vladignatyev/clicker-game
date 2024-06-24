from copy import copy
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from typing import List

from enum import Enum
import math


@dataclass
class Card:
    price: float
    profit_per_second: float
    energy_per_second: float
    profit_per_click: float
    own_since: datetime


CLICK_COST_ENERGY = 1  # energy cost of a click


@dataclass
class State:
    timestamp: datetime

    energy: float = 1000
    max_energy: float = 1000
    balance: float = 0

    total_earned: float = 0
    level: int = 1

    cards: List[Card] = field(default_factory=list)

    energy_per_second: float = 1
    profit_per_second: float = 0
    profit_per_click: float = 1


def create_initial_state(now: datetime) -> State:
    return State(timestamp=now)


def time_travel(state: State, now: datetime) -> State:
    # TODO: time_travel to the future may skip multiple level ups
    seconds_passed = int((now - state.timestamp).total_seconds())

    energy_credit = seconds_passed * state.energy_per_second
    new_energy = state.energy + energy_credit
    balance_credit = seconds_passed * state.profit_per_second

    new_balance = state.balance + balance_credit  # balance does not change
    new_total_earned = state.total_earned + balance_credit

    new_level, earn_to_next_levelup = _levelup(new_total_earned)

    new_energy_per_second = 1 + sum(card.energy_per_second for card in state.cards)
    new_max_energy = _energy_by_level(new_level)
    new_profit_per_click = 1 + sum(card.profit_per_click for card in state.cards)
    new_profit_per_second = sum(card.profit_per_second for card in state.cards)

    if new_energy > state.max_energy:
        new_energy = state.max_energy

    return State(
        energy=new_energy,
        max_energy=new_max_energy,
        balance=new_balance,
        total_earned=new_total_earned,
        level=new_level,
        cards=state.cards,
        timestamp=now,
        energy_per_second=new_energy_per_second,
        profit_per_second=new_profit_per_second,
        profit_per_click=new_profit_per_click,
    )


def seconds_to_next_levelup(state: State) -> int:
    if state.profit_per_second == 0:
        return None
    new_level, earn_to_next_levelup = _levelup(state.total_earned)
    return round((earn_to_next_levelup - state.balance) / state.profit_per_second)


def time_travel_iterative(state: State, now: datetime) -> State:
    s = state
    t = s.timestamp
    while s.timestamp < now:
        if seconds_to_next_levelup(s) is None:
            return time_travel(s, now)
            
        seconds_to_next = min(seconds_to_next_levelup(s), (now - s.timestamp).total_seconds())

        if seconds_to_next <= 0:
            seconds_to_next = 1
        t2 = t + timedelta(seconds=seconds_to_next)
        s = time_travel(s, t2)
        t = t2
    

    return s


def click(state: State, now: datetime) -> State:
    now_state = time_travel(state, now)

    balance_credit = state.profit_per_click
    energy_debit = CLICK_COST_ENERGY

    new_energy = now_state.energy - energy_debit
    new_balance = now_state.balance + balance_credit
    new_total_earned = state.total_earned + balance_credit

    new_level, earn_to_next_levelup = _levelup(new_total_earned)
    new_max_energy = _energy_by_level(new_level)

    if new_level > state.level:
        new_energy = new_max_energy

    if new_energy < 0:
        return state  # not enough energy
    elif new_energy > state.max_energy:
        new_energy = state.max_energy

    return State(
        energy=new_energy,
        max_energy=new_max_energy,
        balance=new_balance,
        total_earned=new_total_earned,
        level=new_level,
        cards=now_state.cards,
        timestamp=now,
        energy_per_second=now_state.energy_per_second,
        profit_per_second=now_state.profit_per_second,
        profit_per_click=now_state.profit_per_click,
    )


def _levelup(total_earned: float) -> int:
    if total_earned >= 10_000 and total_earned < 20_000:
        return (2, 20_000)
    elif total_earned >= 20_000 and total_earned < 30_000:
        return (3, 30_000)
    elif total_earned >= 30_000 and total_earned < 40_000:
        return (4, 40_000)
    elif total_earned >= 40_000:
        level = round(math.log(total_earned, 2) / 3)
        earn_to_next_levelup = 2 ** (3 * (level + 1))
        return (level, earn_to_next_levelup)
    else:
        return (1, 10_000)

    # level + 1 = log(x, 2) / 3
    # 3 * (level + 1) = log(x, 2)
    # x = 2 ** (3 * (level + 1))


def _energy_by_level(level):
    return 1000 * level


def buy_card(state: State, now: datetime, card: Card) -> State:
    new_balance = state.balance - card.price
    new_card = copy(card)

    new_cards = state.cards + [new_card]

    new_profit_per_click = 1 + sum(card.profit_per_click for card in new_cards)
    new_profit_per_second = sum(card.profit_per_second for card in new_cards)
    new_card.own_since = now

    if new_balance < 0:
        return state

    return State(
        energy=state.energy,
        max_energy=state.max_energy,
        balance=new_balance,
        total_earned=state.total_earned,
        level=state.level,
        cards=state.cards + [card],
        timestamp=now,
        energy_per_second=state.energy_per_second,
        profit_per_second=new_profit_per_second,
        profit_per_click=new_profit_per_click,
    )
