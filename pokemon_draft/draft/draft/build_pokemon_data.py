import json
import requests
from pathlib import Path

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


def main():
    all_pokemon = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1025").json()["results"]

    final_data = []

    for index, pokemon in enumerate(all_pokemon, start=1):
        name = pokemon["name"]
        poke_id = pokemon["url"].strip("/").split("/")[-1]

        print(f"{index}/1025 Loading {name}")

        species_url = f"https://pokeapi.co/api/v2/pokemon-species/{poke_id}/"
        species_data = requests.get(species_url).json()

        evolution_chain_url = species_data["evolution_chain"]["url"]
        evolution_chain_id = evolution_chain_url.strip("/").split("/")[-1]

        final_data.append({
            "name": name,
            "display_name": name.replace("-", " ").title(),
            "image": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{poke_id}.png",
            "category": get_category(name),
            "evolution_chain_id": evolution_chain_id,
        })

    output_path = Path(__file__).parent / "pokemon_data.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(final_data, file, indent=2)

    print(f"Saved {len(final_data)} Pokemon to {output_path}")


if __name__ == "__main__":
    main()