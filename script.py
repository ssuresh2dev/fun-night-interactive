import random
import copy
from time import sleep

#######################################
# Possible Roles:
# Werewolf Team:
# Werewolf, Minion
#
# Villager Team:
# Troublemaker, Robber, Seer, Insomniac, Devil's Advocate, Stoner, 
# Rationalist, Podcaster, Inexplicable, Nut Job, Mason, Villager
#
# Flexible Team:
# Dog Whisperer, Tanner, Boy Nextdoor, Agent of Chaos 

ALL_ROLES_IN_GAME = []
CENTER_ROLES = []
ORIGINAL_ROLE_MAPPING = {} # Maps each role to a list of players with that role at the beginning of the game
CURRENT_ASSIGNMENTS = {} # Maps each player to their current role at any given point
INEXPLICABLE_MODE = False

##################
# Helper Functions
##################

def handled_print(msg):
    # Don't narrate role commands when executed by the inexplicable.
    if not INEXPLICABLE_MODE:
        print(msg)

def format_for_reveal(role):
    # Sometimes we update roles that can potentially change in meaning, but anyone who
    # inspects someone's card should only be able to see the original role.
    if '->' in role:
        return role.split(' ->')[0]
    else:
        return role

def get_eligible_inexplicable_roles():
    eligible_roles = []
    for r in set(ALL_ROLES_IN_GAME):
        if r not in ['Devil\'s Advocate', 'Dog Whisperer', 'Mason']:
            eligible_roles.append(r)
    return eligible_roles

##################
# Role Specific Functions
##################

def do_werewolf_turn():
    werewolves = ORIGINAL_ROLE_MAPPING['Werewolf']
    if 'Dog Whisperer' in ALL_ROLES_IN_GAME:
        print('Werewolves, wake up, and look for other werewolves. Choose one of yourselves to be revealed to the dog whisperer. If there is only one werewolf, you may look at a card from the center, and you must reveal yourself to the dog whisperer.')
    else:
        print('Werewolves, wake up, and look for other werewolves. If there is only one werewolf, you may look at a card from the center.')

    if werewolves and len(werewolves) == 1:
        card_to_reveal = random.sample(CENTER_ROLES, 1)
        print(f'[ACTION] Reveal center card to werewolf: {card_to_reveal}')

    sleep(15)
    print('Werewolves, close your eyes.')

def do_minion_turn():
    handled_print('Minion, wake up. Werewolves, stick out your thumbs, so that the minion can see who you are.')
    sleep(10)
    handled_print('Werewolves, put your thumbs down. Minion, close your eyes.')

def do_devils_advocate_turn():
    print('Devil\'s Advocate, wake up. Werewolves, stick out your thumbs, so that the Devil\'s Advocate can see who you are.')
    sleep(10)
    print('Werewolves, put your thumbs down. Devil\'s Advocate, close your eyes.')

def do_mason_turn():
    print('Masons, wake up and look for the other mason.')
    sleep(10)
    print('Masons, close your eyes.')

def do_dog_whisperer_turn():
    print('Dog Whisperer, wake up. Designated werewolf, wake up, and identify each other. If you are the only werewolf, stick out your thumb.')
    if ORIGINAL_ROLE_MAPPING['Dog Whisperer']:
        dog_whisperer = ORIGINAL_ROLE_MAPPING['Dog Whisperer'][0]
        werewolves = ORIGINAL_ROLE_MAPPING['Werewolf']
        if werewolves and len(werewolves) < 2:
            CURRENT_ASSIGNMENTS[dog_whisperer] = 'Dog Whisperer -> Werewolf'

    sleep(10)
    print('Dog Whisperer and designated werewolf, close your eyes.')

def do_stoner_turn():
    handled_print('Stoner, wake up. Choose two players cards to shuffle, and then choose who to assign the revealed card to.')
    if ORIGINAL_ROLE_MAPPING['Stoner']:     
        p1 = input('[ACTION] Enter a player\'s name: ')
        p2 = input('[ACTION] Enter a player\'s name: ')
        revealed = p1 if random.random() < 0.5 else p2
        card_to_reveal = CURRENT_ASSIGNMENTS[revealed]
        print(f'[ACTION] Reveal card to stoner: {format_for_reveal(card_to_reveal)}')
        assigned = input('[ACTION] Enter assignee of revealed card\'s name: ')
        if assigned != revealed:
            CURRENT_ASSIGNMENTS[p1], CURRENT_ASSIGNMENTS[p2] = CURRENT_ASSIGNMENTS[p2], CURRENT_ASSIGNMENTS[p1]
        sleep(5)
    else:
        sleep(15)
    handled_print('Stoner, close your eyes.')

def do_seer_turn():
    handled_print('Seer, wake up. You may look at another player’s card, or two of the center cards.')
    if ORIGINAL_ROLE_MAPPING['Seer']:
        choice = input('[ACTION] Enter a player\'s name, or the word center: ')
        if choice == 'center':
            cards_to_reveal = random.sample(CENTER_ROLES, 2)
            print(f'[ACTION] Reveal center cards to seer: {cards_to_reveal}')
        else:
            card_to_reveal = CURRENT_ASSIGNMENTS[choice]
            print(f'[ACTION] Reveal {choice}\'s role to seer: {format_for_reveal(card_to_reveal)}')
        sleep(5)
    else:
        sleep(12)
    handled_print('Seer, close your eyes.')

def do_rationalist_turn(player=None):
    if player:
        handled_print('Rationalist, wake up, and once again check the role of the player you previously checked.')
    else:
        handled_print('Rationalist, wake up, and inspect a player\'s card of your choosing.')

    if ORIGINAL_ROLE_MAPPING['Rationalist']:
        rationalist = ORIGINAL_ROLE_MAPPING['Rationalist'][-1]
        if not player:
            player = input('[ACTION] Enter a player\'s name: ')
        if rationalist == player:
            print(f'[ACTION] Reveal {player}\'s role to rationalist: {CURRENT_ASSIGNMENTS[player]}')
        else:
            print(f'[ACTION] Reveal {player}\'s role to rationalist: {format_for_reveal(CURRENT_ASSIGNMENTS[player])}')
        sleep(5)
    else:
        sleep(12)
    handled_print('Rationalist, close your eyes.')
    return player

def do_aoc_turn():
    handled_print('Agent of Chaos, wake up. Choose another player to exchange your card with, and then view your new card.')
    if ORIGINAL_ROLE_MAPPING['Agent of Chaos']:
        aoc = ORIGINAL_ROLE_MAPPING['Agent of Chaos'][-1]
        swapped_player = input('[ACTION] Enter a player\'s name: ')
        print(f'[ACTION] Reveal card to Agent of Chaos: {CURRENT_ASSIGNMENTS[swapped_player]}')
        tmp = CURRENT_ASSIGNMENTS[aoc]
        CURRENT_ASSIGNMENTS[aoc] = CURRENT_ASSIGNMENTS[swapped_player]
        if CURRENT_ASSIGNMENTS[swapped_player] in ['Werewolf', 'Minion', 'Dog Whisperer -> Werewolf']:
            CURRENT_ASSIGNMENTS[swapped_player] = f'{tmp} -> Villager'
        elif 'Agent of Chaos' in CURRENT_ASSIGNMENTS[swapped_player]:
            # This happens if the inexplicable is executing this turn and chooses to swap with the person
            # who actually has the AOC card. We once again flip their role 
            if 'Villager' in CURRENT_ASSIGNMENTS[swapped_player]:
                CURRENT_ASSIGNMENTS[swapped_player] = f'{tmp} -> Werewolf'
            else:
                CURRENT_ASSIGNMENTS[swapped_player] = f'{tmp} -> Villager'
        elif CURRENT_ASSIGNMENTS[swapped_player] in ['Tanner', 'Boy Nextdoor']:
            # These roles stay unchanged but we still note the fact that they technically possess the AOC version
            # of their card now instead.
            CURRENT_ASSIGNMENTS[swapped_player] = f'{tmp} -> {CURRENT_ASSIGNMENTS[swapped_player]}'
        else:
            CURRENT_ASSIGNMENTS[swapped_player] = f'{tmp} -> Werewolf'
        sleep(5)
    else:
        sleep(12)
    handled_print('Agent of Chaos, close your eyes.')

def do_robber_turn():
    handled_print('Robber, wake up. Choose another player to exchange your card with, and then view your new card.')
    if ORIGINAL_ROLE_MAPPING['Robber']:
        robber = ORIGINAL_ROLE_MAPPING['Robber'][-1]
        swapped_player = input('[ACTION] Enter a player\'s name: ')
        print(f'[ACTION] Reveal card to Robber: {CURRENT_ASSIGNMENTS[swapped_player]}')
        CURRENT_ASSIGNMENTS[robber], CURRENT_ASSIGNMENTS[swapped_player] = CURRENT_ASSIGNMENTS[swapped_player], CURRENT_ASSIGNMENTS[robber]
        sleep(5)
    else:
        sleep(15)
    handled_print('Robber, close your eyes.')

def do_troublemaker_turn():
    handled_print('Troublemaker, wake up. Choose two players to exchange cards between.')
    if ORIGINAL_ROLE_MAPPING['Troublemaker']:
        p1 = input('[ACTION] Enter a player\'s name: ')
        p2 = input('[ACTION] Enter a player\'s name: ')
        CURRENT_ASSIGNMENTS[p1], CURRENT_ASSIGNMENTS[p2] = CURRENT_ASSIGNMENTS[p2], CURRENT_ASSIGNMENTS[p1]
        sleep(3)
    else:
        sleep(12)
    handled_print('Troublemaker, close your eyes.')

def do_insomniac_turn():
    handled_print('Insomniac, wake up, and look at your card')
    if ORIGINAL_ROLE_MAPPING['Insomniac']:
        insomniac = ORIGINAL_ROLE_MAPPING['Insomniac'][-1]
        print(f'[ACTION] Reveal card to Insomniac: {CURRENT_ASSIGNMENTS[insomniac]}')
        sleep(5)
    else:
        sleep(12)
    handled_print('Insomniac, close your eyes.')

def do_inexplicable_turn():
    print('Inexplicable, wake up. This is the result of your coin flip. If it is heads, you may choose a new role, and perform the action for that role now.')
    if ORIGINAL_ROLE_MAPPING['Inexplicable']:
        inexplicable = ORIGINAL_ROLE_MAPPING['Inexplicable'][0]
        rand_val = random.random()
        coin_flip_result = 'Heads' if rand_val < 0.5 else 'Tails'
        print(f'[ACTION] Reveal coin flip result: {coin_flip_result}')
        if coin_flip_result == 'Heads':
            print(f'[ACTION] Verify new role selection is in: {get_eligible_inexplicable_roles()}')
            new_role = input('[ACTION] Enter new role for inexplicable: ')
            if CURRENT_ASSIGNMENTS[inexplicable] == 'Inexplicable':
                CURRENT_ASSIGNMENTS[inexplicable] = f'Inexplicable -> {new_role}'

            ORIGINAL_ROLE_MAPPING.setdefault(new_role, []).append(inexplicable)
            INEXPLICABLE_MODE = True
            if new_role == 'Minion':
                do_minion_turn()
            elif new_role == 'Stoner':
                do_stoner_turn()
            elif new_role == 'Seer':
                do_seer_turn()
            elif new_role == 'Rationalist':
                do_rationalist_turn()
            elif new_role == 'Robber':
                do_robber_turn()
            elif new_role == 'Troublemaker':
                do_troublemaker_turn()
            elif new_role == 'Insomniac':
                do_insomniac_turn()
            elif new_role == 'Agent of Chaos':
                do_aoc_turn()
        else:
            sleep(12)
    else:
        sleep(15)
    print('Inexplicable, close your eyes.')


if __name__ == '__main__':

    num_players = int(input('Please Enter the Number of Players: '))
    players = []
    for _ in range(num_players):
        players.append(input('Please Enter a Player Name: '))

    for _ in range(num_players + 3):
        role = input('Please Enter a Role in Play: ')
        ALL_ROLES_IN_GAME.append(role)

    random.shuffle(ALL_ROLES_IN_GAME)

    print("Player Assignments: ")

    for i in range(num_players + 3):
        if i < num_players:
            CURRENT_ASSIGNMENTS[players[i]] = ALL_ROLES_IN_GAME[i]
            print(f'{players[i]}: {CURRENT_ASSIGNMENTS[players[i]]}')
            ORIGINAL_ROLE_MAPPING.setdefault(ALL_ROLES_IN_GAME[i], []).append(players[i])
        else:
            CENTER_ROLES.append(ALL_ROLES_IN_GAME[i])

    print('Starting Game...Enter to Confirm')
    input()

    rationalist_selected_player = None

    if 'Werewolf' in ALL_ROLES_IN_GAME:
        print(f"[WEREWOLVES]: {ORIGINAL_ROLE_MAPPING.setdefault('Werewolf', [])}")
        do_werewolf_turn()

    if 'Minion' in ALL_ROLES_IN_GAME:
        print(f"[MINION]: {ORIGINAL_ROLE_MAPPING.setdefault('Minion', [])}")
        do_minion_turn()

    if 'Devil\'s Advocate' in ALL_ROLES_IN_GAME:
        da = ORIGINAL_ROLE_MAPPING.setdefault('Devil\'s Advocate', [])
        print(f"[DEVILS ADVOCATE]: {da}")
        do_devils_advocate_turn()

    if 'Dog Whisperer' in ALL_ROLES_IN_GAME:
        print(f"[DOG WHISPERER]: {ORIGINAL_ROLE_MAPPING.setdefault('Dog Whisperer', [])}")
        do_dog_whisperer_turn()

    if 'Mason' in ALL_ROLES_IN_GAME:
        print(f"[MASONS]: {ORIGINAL_ROLE_MAPPING.setdefault('Mason', [])}")
        do_mason_turn()

    if 'Seer' in ALL_ROLES_IN_GAME:
        print(f"[SEER]: {ORIGINAL_ROLE_MAPPING.setdefault('Seer', [])}")
        do_seer_turn()

    if 'Agent of Chaos' in ALL_ROLES_IN_GAME:
        print(f"[AGENT OF CHAOS]: {ORIGINAL_ROLE_MAPPING.setdefault('Agent of Chaos', [])}")
        do_aoc_turn()
        if 'Rationalist' in ALL_ROLES_IN_GAME:
            print(f"[RATIONALIST]: {ORIGINAL_ROLE_MAPPING.setdefault('Rationalist', [])}")
            rationalist_selected_player = do_rationalist_turn(rationalist_selected_player)

    if 'Stoner' in ALL_ROLES_IN_GAME:
        print(f"[STONER]: {ORIGINAL_ROLE_MAPPING.setdefault('Stoner', [])}")
        do_stoner_turn()
        if 'Rationalist' in ALL_ROLES_IN_GAME:
            print(f"[RATIONALIST]: {ORIGINAL_ROLE_MAPPING.setdefault('Rationalist', [])}")
            rationalist_selected_player = do_rationalist_turn(rationalist_selected_player)

    if 'Robber' in ALL_ROLES_IN_GAME:
        print(f"[ROBBER]: {ORIGINAL_ROLE_MAPPING.setdefault('Robber', [])}")
        do_robber_turn()
        if 'Rationalist' in ALL_ROLES_IN_GAME:
            print(f"[RATIONALIST]: {ORIGINAL_ROLE_MAPPING.setdefault('Rationalist', [])}")
            rationalist_selected_player = do_rationalist_turn(rationalist_selected_player)

    if 'Troublemaker' in ALL_ROLES_IN_GAME:
        print(f"[TROUBLEMAKER]: {ORIGINAL_ROLE_MAPPING.setdefault('Troublemaker', [])}")
        do_troublemaker_turn()
        if 'Rationalist' in ALL_ROLES_IN_GAME:
            print(f"[RATIONALIST]: {ORIGINAL_ROLE_MAPPING.setdefault('Rationalist', [])}")
            rationalist_selected_player = do_rationalist_turn(rationalist_selected_player)

    if 'Insomniac' in ALL_ROLES_IN_GAME:
        print(f"[INSOMNIAC]: {ORIGINAL_ROLE_MAPPING.setdefault('Insomniac', [])}")
        do_insomniac_turn()

    if 'Inexplicable' in ALL_ROLES_IN_GAME:
        print(f"[INEXPLICABLE]: {ORIGINAL_ROLE_MAPPING.setdefault('Inexplicable', [])}")
        do_inexplicable_turn()

    print('Everyone, wake up!')
    print('#######################')
    print('Current Assignments:')
    print(CURRENT_ASSIGNMENTS)
    print('#######################')








