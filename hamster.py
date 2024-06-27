import hyperdiv as hd
from hyperdiv_session import session

from _storage import connect, persist, load, delete
from hamster import *
from hamster import _levelup

from time_plugin import time as thetime




def main():
    # Create a session object with a secret key
    sid = session(secret_key="some very secret")

    with hd.box(padding=8, gap=2):
        if not sid.is_authenticated():
            hd.text("Not authenticated yet.")

            if hd.button("Authenticate").clicked:
                sid.gdpr_flag = True
                sid.create_new()  # create new session
                

                persist(sid.session_id, 
                        create_initial_state(datetime.now()))

        else:
            user_state = load(sid.session_id)

            # View state
            view_state = hd.state(
                energy=user_state.energy,
                max_energy=user_state.max_energy,
                balance=user_state.balance,
                level=user_state.level,
                till_levelup=_levelup(user_state.total_earned)[1] - user_state.balance,
                dummy=1
            )

            hd.text(f"⚡{view_state.energy} / {view_state.max_energy}  🏆{view_state.level}")
            hd.text(view_state.balance)


            if hd.button("CLICKER").clicked:
                new_state = click(user_state, datetime.now())
                
                view_state.energy = user_state.energy
                view_state.max_energy = user_state.max_energy
                view_state.balance = user_state.balance
                view_state.level = user_state.level
                view_state.till_levelup = _levelup(user_state.total_earned)[1] - user_state.balance
                persist(sid.session_id, new_state)

            # if hd.button("Refresh"):
            #     view_state.dummy += 1
                

            if hd.button("Log out").clicked:
                sid.clear()
                delete(sid.session_id)


connect()  # open connection to storage or create a new one

hd.run(main)
