#!/usr/bin/env python3
import csv
import io
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POKE_URL = 'https://raw.githubusercontent.com/tinoxo/PokeCalc/main/data/champions-data.json'
LEG_URL = 'https://raw.githubusercontent.com/tinoxo/PokeCalc/main/data/champions-legality.json'
LAB_URL = 'https://raw.githubusercontent.com/joshuamatalon/champions-lab/main/data/dex.json'
CSV_BASE = 'https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/'

def norm(value):
    return re.sub(r'[^a-z0-9]', '', str(value or '').lower())

def fetch(url):
    last_error = None
    for attempt in range(5):
        request = urllib.request.Request(url, headers={'User-Agent': 'champions-data-updater/1.0'})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except Exception as error:
            last_error = error
            time.sleep(1 + attempt * 2)
    raise last_error

def fetch_json(url):
    return json.loads(fetch(url).decode('utf-8'))

def fetch_csv(name):
    text = fetch(CSV_BASE + name).decode('utf-8-sig')
    return list(csv.DictReader(io.StringIO(text)))

def load_js_json(relative):
    path = ROOT / relative
    if not path.exists():
        return {}
    text = path.read_text(encoding='utf-8')
    start = text.index('{')
    end = text.rstrip().rstrip(';').rindex('}') + 1
    return json.loads(text[start:end])

def main():
    p = fetch_json(POKE_URL)
    legality = fetch_json(LEG_URL)
    lab = fetch_json(LAB_URL)
    old_zh = load_js_json('data/champions-zh.js')

    pokemon_rows = fetch_csv('pokemon.csv')
    species_names = fetch_csv('pokemon_species_names.csv')
    moves_rows = fetch_csv('moves.csv')
    move_names = fetch_csv('move_names.csv')
    ability_rows = fetch_csv('abilities.csv')
    ability_names = fetch_csv('ability_names.csv')
    ability_prose = fetch_csv('ability_prose.csv')
    move_effect_prose = fetch_csv('move_effect_prose.csv')

    lab_species = {norm(s['id']): s for s in lab['species']}
    lab_moves = {norm(m['id']): m for m in lab['moves']}
    lab_abilities = {norm(a['name']): a for a in lab['abilities']}

    poke_by_key = {norm(r['identifier']): r for r in pokemon_rows}
    species_zh = {int(r['pokemon_species_id']): r['name'] for r in species_names if r['local_language_id'] == '12' and r.get('name')}
    move_by_key = {norm(r['identifier']): r for r in moves_rows}
    move_zh = {int(r['move_id']): r['name'] for r in move_names if r['local_language_id'] == '12' and r.get('name')}
    ability_by_key = {norm(r['identifier']): r for r in ability_rows}
    ability_zh = {int(r['ability_id']): r['name'] for r in ability_names if r['local_language_id'] == '12' and r.get('name')}
    ability_effect_zh = {}
    for row in ability_prose:
        if row['local_language_id'] == '12':
            text = (row.get('short_effect') or row.get('effect') or '').strip()
            ability_id = int(row['ability_id'])
            if text and ability_id not in ability_effect_zh:
                ability_effect_zh[ability_id] = text
    move_effect_zh = {}
    for row in move_effect_prose:
        if row['local_language_id'] == '12':
            text = (row.get('short_effect') or row.get('effect') or '').strip()
            effect_id = int(row['move_effect_id'])
            if text and effect_id not in move_effect_zh:
                move_effect_zh[effect_id] = text

    def base_zh(species):
        row = poke_by_key.get(norm(species.get('baseSpecies') or species.get('name')))
        return species_zh.get(int(row['species_id'])) if row else None

    def zh_species(species):
        if species.get('name') in old_zh.get('pokemon', {}):
            return old_zh['pokemon'][species['name']]
        manual = {
            'rotomheat': '加热洛托姆', 'rotomwash': '清洗洛托姆', 'rotomfrost': '结冰洛托姆',
            'rotomfan': '旋转洛托姆', 'rotommow': '切割洛托姆', 'meowsticf': '超能妙喵（雌性）',
            'gourgeistsmall': '南瓜怪人（小尺寸）', 'gourgeistlarge': '南瓜怪人（大尺寸）',
            'gourgeistsuper': '南瓜怪人（超大尺寸）', 'lycanrocmidnight': '鬃岩狼人（黑夜的样子）',
            'lycanrocdusk': '鬃岩狼人（黄昏的样子）', 'toxtricitylowkey': '颤弦蝾螈（低调）',
            'indeedeef': '爱管侍（雌性）', 'basculegionf': '幽尾玄鱼（雌性）',
            'squawkabillyyellow': '下石鸟（黄羽毛）'
        }
        key = norm(species.get('id'))
        if key in manual:
            return manual[key]
        name = species.get('name', '')
        base = base_zh(species) or species.get('baseSpecies') or name
        if species.get('isMega') or species.get('kind') == 'mega':
            tail = re.search(r'mega-([xyz])$', name, re.I)
            return '超级' + base + (tail.group(1).upper() if tail else '')
        low = name.lower()
        if 'alola' in low:
            return '阿罗拉' + base
        if 'galar' in low:
            return '伽勒尔' + base
        if 'hisui' in low:
            return '洗翠' + base
        if 'paldea' in low:
            if '-Combat' in name:
                return '帕底亚' + base + '（斗战种）'
            if '-Blaze' in name:
                return '帕底亚' + base + '（火种）'
            if '-Aqua' in name:
                return '帕底亚' + base + '（水种）'
            return '帕底亚' + base
        return base or name

    def zh_move(move):
        if move['name'] in old_zh.get('moves', {}):
            return old_zh['moves'][move['name']]
        row = move_by_key.get(norm(move['name']))
        return move_zh.get(int(row['id']), move['name']) if row else move['name']

    def zh_ability(ability):
        if ability['name'] in old_zh.get('abilities', {}):
            return old_zh['abilities'][ability['name']]
        row = ability_by_key.get(norm(ability['name']))
        return ability_zh.get(int(row['id']), ability['name']) if row else ability['name']

    def move_effect(move):
        if move['name'] in old_zh.get('moveEffects', {}):
            return old_zh['moveEffects'][move['name']]
        row = move_by_key.get(norm(move['name']))
        if row and row.get('effect_id'):
            try:
                if int(row['effect_id']) in move_effect_zh:
                    return move_effect_zh[int(row['effect_id'])]
            except ValueError:
                pass
        return move.get('shortDesc') or move.get('desc') or '无追加效果。'

    def ability_effect(ability):
        if ability['name'] in old_zh.get('abilityEffects', {}):
            return old_zh['abilityEffects'][ability['name']]
        row = ability_by_key.get(norm(ability['name']))
        if row and int(row['id']) in ability_effect_zh:
            return ability_effect_zh[int(row['id'])]
        return ability.get('shortDesc') or ability.get('desc') or '该特性效果暂未收录。'

    def from_poke_species(key, source):
        stats = source.get('stats') or [0, 0, 0, 0, 0, 0]
        abilities = {('0' if i == 0 else '1' if i == 1 else 'H'): value for i, value in enumerate(source.get('abilities') or [])}
        return {
            'id': key, 'name': source['name'], 'baseSpecies': source.get('name'), 'forme': '',
            'num': source.get('ndex', 0), 'types': source.get('types', []),
            'baseStats': dict(zip(('hp', 'atk', 'def', 'spa', 'spd', 'spe'), stats)),
            'abilities': abilities, 'learnset': source.get('moves', []),
            'isMega': source.get('kind') == 'mega'
        }

    legal_ids = {norm(x) for x in legality.get('legalSpecies', [])}
    legal_ids |= {norm(x) for x in legality.get('previousLegalSpecies', [])}
    legal_ids |= {'pawmot', 'vivillonhighplains'}
    species_list = []
    for key in sorted(legal_ids):
        species = lab_species.get(key)
        if not species:
            source = p.get('species', {}).get(key)
            if not source:
                continue
            species = from_poke_species(key, source)
        species_list.append(species)

    roster, base_stats, learnsets, pokemon_map, pokemon_order = [], [], {}, {}, []
    used_move_ids, used_abilities = set(), []
    for species in species_list:
        name = species['name']
        dex = species.get('num', 0)
        is_mega = species.get('isMega') or species.get('kind') == 'mega'
        name_low = name.lower()
        if is_mega:
            form = 'Mega'
        elif any(x in name_low for x in ('alola', 'galar', 'hisui', 'paldea')):
            form = 'Regional'
        elif species.get('forme'):
            form = 'Other'
        else:
            form = 'Base'
        stats = species.get('baseStats', {})
        abilities = species.get('abilities', {}) or {}
        roster.append({'name': name, 'dexNumber': dex, 'types': species.get('types', []), 'form': form, 'abilities': abilities, 'championsVerified': True})
        base_stats.append({'name': name, 'dexNumber': dex, 'form': form, 'hp': stats.get('hp', 0), 'atk': stats.get('atk', 0), 'def': stats.get('def', 0), 'spa': stats.get('spa', 0), 'spd': stats.get('spd', 0), 'spe': stats.get('spe', 0), 'total': species.get('bst', sum(stats.values())), 'championsVerified': True})
        move_names_list = []
        for move_id in species.get('learnset', []):
            move = lab_moves.get(norm(move_id))
            if not move:
                continue
            used_move_ids.add(norm(move_id))
            move_names_list.append({'name': move['name']})
        learnsets[name] = {'dexNumber': dex, 'form': form, 'championsVerified': True, 'source': 'pokemon-champions-reg-m-c', 'moves': move_names_list, 'moveCount': len(move_names_list)}
        cn = zh_species(species)
        pokemon_map[name] = cn
        pokemon_order.append({'en': name, 'zh': cn, 'dex': dex, 'form': form})
        for ability in abilities.values():
            if ability not in used_abilities:
                used_abilities.append(ability)

    moves = []
    move_effect_map = {}
    for move_id in sorted(used_move_ids, key=lambda x: lab_moves[x]['name']):
        move = lab_moves[move_id]
        effect = move_effect(move)
        moves.append({'name': move['name'], 'type': move.get('type', 'Normal'), 'category': move.get('category', 'Status'), 'description': effect, 'target': move.get('target', 'normal'), 'inChampions': True, 'championsVerified': True, 'power': move.get('basePower', 0), 'accuracy': None if move.get('accuracy') is True else move.get('accuracy'), 'pp': move.get('pp', 0), 'priority': move.get('priority', 0)})
        move_effect_map[move['name']] = effect

    abilities = []
    ability_map, ability_effect_map = {}, {}
    for name in sorted(used_abilities, key=str.lower):
        ability = lab_abilities.get(norm(name)) or {'name': name, 'shortDesc': '', 'desc': ''}
        cn = zh_ability(ability)
        effect = ability_effect(ability)
        abilities.append({'name': ability['name'], 'description': effect, 'championsVerified': True})
        ability_map[ability['name']] = cn
        ability_effect_map[ability['name']] = effect

    chart = {k: dict(v) for k, v in lab['typeChart'].items() if k != 'Stellar'}
    data = {'roster': roster, 'baseStats': base_stats, 'moves': moves, 'abilities': abilities, 'learnsets': learnsets, 'effectiveness': {'types': list(chart.keys()), 'chart': chart}}
    zh = {'pokemon': pokemon_map, 'abilities': ability_map, 'abilityEffects': ability_effect_map, 'moveEffects': move_effect_map, 'moves': {m['name']: zh_move(m) for m in moves}, 'pokemonOrder': sorted(pokemon_order, key=lambda x: (x['dex'], 0 if x['form'] == 'Base' else 1 if x['form'] == 'Regional' else 2 if x['form'] == 'Mega' else 3, x['en']))}
    (ROOT / 'data' / 'champions-data.js').write_text('window.CHAMPIONS_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    (ROOT / 'data' / 'champions-zh.js').write_text('window.CHAMPIONS_ZH = ' + json.dumps(zh, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({'species': len(roster), 'moves': len(moves), 'abilities': len(abilities)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
