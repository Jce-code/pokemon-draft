import random
import requests
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import DraftState, DraftPokemon, Player
EVOLUTION_CHAIN_CACHE = {}
ALL_POKEMON = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1025").json()["results"]

LEGENDARIES = {
    "articuno", "zapdos", "moltres", "mewtwo", "raikou", "entei", "suicune",
    "lugia", "ho-oh", "regirock", "regice", "registeel", "latias", "latios",
    "kyogre", "groudon", "rayquaza", "uxie", "mesprit", "azelf", "dialga",
    "palkia", "heatran", "regigigas", "giratina", "cresselia", "cobalion",
    "terrakion", "virizion", "tornadus", "thundurus", "landorus", "reshiram",
    "zekrom", "kyurem", "xerneas", "yveltal", "zygarde", "type-null",
    "silvally", "tapu-koko", "tapu-lele", "tapu-bulu", "tapu-fini",
    "cosmog", "cosmoem", "solgaleo", "lunala", "necrozma", "zacian",
    "zamazenta", "eternatus", "kubfu", "urshifu", "regieleki", "regidrago",
    "glastrier", "spectrier", "calyrex", "wo-chien", "chien-pao",
    "ting-lu", "chi-yu", "koraidon", "miraidon", "okidogi", "munkidori",
    "fezandipiti", "ogerpon", "terapagos"
}

MYTHICALS = {
    "mew", "celebi", "jirachi", "deoxys", "phione", "manaphy", "darkrai",
    "shaymin", "arceus", "victini", "keldeo", "meloetta", "genesect",
    "diancie", "hoopa", "volcanion", "magearna", "marshadow", "zeraora",
    "meltan", "melmetal", "zarude", "pecharunt"
}

ULTRA_BEASTS = {
    "nihilego", "buzzwole", "pheromosa", "xurkitree", "celesteela",
    "kartana", "guzzlord", "poipole", "naganadel", "stakataka", "blacephalon"
}

PARADOX = {
    "great-tusk", "scream-tail", "brute-bonnet", "flutter-mane",
    "slither-wing", "sandy-shocks", "roaring-moon", "walking-wake",
    "gouging-fire", "raging-bolt", "iron-treads", "iron-bundle",
    "iron-hands", "iron-jugulis", "iron-moth", "iron-thorns",
    "iron-valiant", "iron-leaves", "iron-crown", "iron-boulder"
}


def get_category(name):
    base_name = name.split("-")[0]

    if base_name in LEGENDARIES:
        return "Legendary"
    if base_name in MYTHICALS:
        return "Mythical"
    if name in ULTRA_BEASTS:
        return "Ultra Beast"
    if name in PARADOX:
        return "Paradox"

    return "Normal"


def build_pokemon_card(pokemon):
    poke_id = pokemon["url"].split("/")[-2]

    return {
        "name": pokemon["name"].replace("-", " ").title(),
        "image": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{poke_id}.png",
        "category": get_category(pokemon["name"]),
    }


def get_evolution_chain_id(pokemon):
    poke_id = pokemon["url"].split("/")[-2]

    if poke_id in EVOLUTION_CHAIN_CACHE:
        return EVOLUTION_CHAIN_CACHE[poke_id]

    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{poke_id}/"
    species_data = requests.get(species_url).json()

    evolution_chain_url = species_data["evolution_chain"]["url"]
    evolution_chain_id = evolution_chain_url.strip("/").split("/")[-1]

    EVOLUTION_CHAIN_CACHE[poke_id] = evolution_chain_id

    return evolution_chain_id


def choose_unique_evolution_lines(pool, count, used_evolution_chains):
    chosen = []
    shuffled_pool = pool[:]
    random.shuffle(shuffled_pool)

    for pokemon in shuffled_pool:
        if len(chosen) >= count:
            break

        evolution_chain_id = get_evolution_chain_id(pokemon)

        if evolution_chain_id in used_evolution_chains:
            continue

        used_evolution_chains.add(evolution_chain_id)
        chosen.append(pokemon)

    return chosen


def generate_pokemon(request):
    selected_pokemon = {}
    error_message = ""

    if request.method == "POST":
        total_count = int(request.POST.get("total_count", 0))
        legendary_count = int(request.POST.get("legendary_count", 0))
        mythical_count = int(request.POST.get("mythical_count", 0))
        paradox_count = int(request.POST.get("paradox_count", 0))
        ultra_beast_count = int(request.POST.get("ultra_beast_count", 0))

        max_legendaries = int(request.POST.get("max_legendaries", 1))
        max_mythicals = int(request.POST.get("max_mythicals", 0))
        max_paradox = int(request.POST.get("max_paradox", 1))
        max_ultra_beasts = int(request.POST.get("max_ultra_beasts", 1))
        pick_timer_seconds = int(request.POST.get("pick_timer_seconds", 90))

        players_text = request.POST.get("players", "")
        player_names = [name.strip() for name in players_text.splitlines() if name.strip()]

        special_total = legendary_count + mythical_count + paradox_count + ultra_beast_count

        if len(player_names) < 2:
            error_message = "Please enter at least 2 players."
        elif special_total > total_count:
            error_message = "Your special category counts are higher than the total bank size."
        else:
            legendary_pool = [p for p in ALL_POKEMON if get_category(p["name"]) == "Legendary"]
            mythical_pool = [p for p in ALL_POKEMON if get_category(p["name"]) == "Mythical"]
            paradox_pool = [p for p in ALL_POKEMON if get_category(p["name"]) == "Paradox"]
            ultra_beast_pool = [p for p in ALL_POKEMON if get_category(p["name"]) == "Ultra Beast"]
            normal_pool = [p for p in ALL_POKEMON if get_category(p["name"]) == "Normal"]

            if legendary_count > len(legendary_pool):
                error_message = "You requested more legendaries than exist."
            elif mythical_count > len(mythical_pool):
                error_message = "You requested more mythicals than exist."
            elif paradox_count > len(paradox_pool):
                error_message = "You requested more paradox Pokémon than exist."
            elif ultra_beast_count > len(ultra_beast_pool):
                error_message = "You requested more Ultra Beasts than exist."
            else:
                normal_count = total_count - special_total
                used_evolution_chains = set()

                chosen = []
                chosen += choose_unique_evolution_lines(legendary_pool, legendary_count, used_evolution_chains)
                chosen += choose_unique_evolution_lines(mythical_pool, mythical_count, used_evolution_chains)
                chosen += choose_unique_evolution_lines(paradox_pool, paradox_count, used_evolution_chains)
                chosen += choose_unique_evolution_lines(ultra_beast_pool, ultra_beast_count, used_evolution_chains)
                chosen += choose_unique_evolution_lines(normal_pool, normal_count, used_evolution_chains)

                random.shuffle(chosen)

                categorized = {
                    "Legendary": [],
                    "Mythical": [],
                    "Paradox": [],
                    "Ultra Beast": [],
                    "Normal": [],
                }

                for pokemon in chosen:
                    card = build_pokemon_card(pokemon)
                    categorized[card["category"]].append(card)

                DraftPokemon.objects.all().delete()
                DraftState.objects.all().delete()
                Player.objects.all().delete()

                DraftState.objects.create(
                    started=False,
                    current_pick_number=1,
                    turn_started_at=timezone.now(),
                    max_legendaries=max_legendaries,
                    max_mythicals=max_mythicals,
                    max_paradox=max_paradox,
                    max_ultra_beasts=max_ultra_beasts,
                    pick_timer_seconds=pick_timer_seconds,
                )

                for index, player_name in enumerate(player_names):
                    Player.objects.create(
                        name=player_name,
                        draft_position=index + 1,
                    )

                for category_name, pokemon_list in categorized.items():
                    for pokemon in pokemon_list:
                        DraftPokemon.objects.create(
                            name=pokemon["name"],
                            image=pokemon["image"],
                            category=pokemon["category"],
                        )

                selected_pokemon = categorized

    return render(request, "draft/generate.html", {
        "selected_pokemon": selected_pokemon,
        "error_message": error_message,
    })


def start_draft(request):
    return redirect("/join/")


def begin_draft(request):
    draft_state = DraftState.objects.first()

    if request.method == "POST" and draft_state:
        draft_state.started = True
        draft_state.current_pick_number = 1
        draft_state.turn_started_at = timezone.now()
        draft_state.save()

    return redirect("/draft-board/")


def get_current_player():
    players = list(Player.objects.order_by("draft_position"))
    draft_state = DraftState.objects.first()

    if not players or not draft_state:
        return None

    pick_index = draft_state.current_pick_number - 1
    round_number = pick_index // len(players)
    position_in_round = pick_index % len(players)

    if round_number % 2 == 0:
        draft_order = players
    else:
        draft_order = list(reversed(players))

    return draft_order[position_in_round]


def is_pick_legal(player, pokemon, draft_state):
    current_count = DraftPokemon.objects.filter(
        picked_by=player,
        category=pokemon.category
    ).count()

    if pokemon.category == "Legendary" and current_count >= draft_state.max_legendaries:
        return False
    if pokemon.category == "Mythical" and current_count >= draft_state.max_mythicals:
        return False
    if pokemon.category == "Paradox" and current_count >= draft_state.max_paradox:
        return False
    if pokemon.category == "Ultra Beast" and current_count >= draft_state.max_ultra_beasts:
        return False

    return True


def draft_board(request):
    draft_state = DraftState.objects.first()
    current_player = get_current_player()

    available_pokemon = DraftPokemon.objects.filter(picked_by__isnull=True)

    categorized = {
        "Legendary": [],
        "Mythical": [],
        "Paradox": [],
        "Ultra Beast": [],
        "Normal": [],
    }

    for pokemon in available_pokemon:
        categorized[pokemon.category].append(pokemon)

    players = Player.objects.order_by("draft_position")

    for player in players:
        player.picks = DraftPokemon.objects.filter(picked_by=player).order_by("pick_number")

    session_player_id = request.session.get("player_id")
    session_player = None

    if session_player_id:
        session_player = Player.objects.filter(id=session_player_id).first()

    time_remaining = 0

    if draft_state and draft_state.turn_started_at:
        elapsed = (timezone.now() - draft_state.turn_started_at).total_seconds()
        time_remaining = max(0, draft_state.pick_timer_seconds - int(elapsed))

    return render(request, "draft/draft_board.html", {
        "draft_state": draft_state,
        "current_player": current_player,
        "categorized_pokemon": categorized,
        "players": players,
        "session_player": session_player,
        "time_remaining": time_remaining,
    })


def pick_pokemon(request, pokemon_id):
    draft_state = DraftState.objects.first()
    current_player = get_current_player()
    pokemon = DraftPokemon.objects.get(id=pokemon_id)

    session_player_id = request.session.get("player_id")
    expected_pick_number = int(request.POST.get("expected_pick_number", 0))

    if (
        request.method == "POST"
        and draft_state
        and current_player
        and pokemon.picked_by is None
        and session_player_id == current_player.id
        and expected_pick_number == draft_state.current_pick_number
        and is_pick_legal(current_player, pokemon, draft_state)
    ):
        pokemon.picked_by = current_player
        pokemon.pick_number = draft_state.current_pick_number
        pokemon.save()

        draft_state.current_pick_number += 1
        draft_state.turn_started_at = timezone.now()
        draft_state.save()

    return redirect("/draft-board/")


def auto_pick(request):
    draft_state = DraftState.objects.first()
    current_player = get_current_player()
    expected_pick_number = int(request.POST.get("expected_pick_number", 0))

    if (
        request.method == "POST"
        and draft_state
        and current_player
        and expected_pick_number == draft_state.current_pick_number
    ):
        available_pokemon = DraftPokemon.objects.filter(picked_by__isnull=True)

        legal_pokemon = [
            pokemon for pokemon in available_pokemon
            if is_pick_legal(current_player, pokemon, draft_state)
        ]

        if legal_pokemon:
            pokemon = random.choice(legal_pokemon)

            pokemon.picked_by = current_player
            pokemon.pick_number = draft_state.current_pick_number
            pokemon.save()

            draft_state.current_pick_number += 1
            draft_state.turn_started_at = timezone.now()
            draft_state.save()

    return redirect("/draft-board/")


def join_draft(request):
    players = Player.objects.order_by("draft_position")

    if request.method == "POST":
        player_id = request.POST.get("player_id")
        request.session["player_id"] = int(player_id)
        return redirect("/draft-board/")

    return render(request, "draft/join_draft.html", {
        "players": players
    })