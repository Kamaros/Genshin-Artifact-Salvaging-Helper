from datetime import datetime
import json
import re

from bs4 import BeautifulSoup
from curl_cffi import requests

def extract_page_source(url: str):
    response = requests.get(url, impersonate='chrome110')
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')

    print(f'Failed to retrieve page source; received status code {response.status_code}')
    return None

def inline_2pc_set_bonuses(build_str: str):
    replacement_for_placeholders = {
        '+80 EM set': "Wanderer's Troupe, Gilded Dreams, Flower of Paradise Lost, Aubade of Morningstar and Moon, Instructor",
        '+18% ATK set': "Gladiator's Finale, Shimenawa's Reminiscence, Vermillion Hereafter, Echoes of an Offering, Nighttime Whispers in the Echoing Woods, Fragment of Harmonic Whimsy, Unfinished Reverie, A Day Carved From Rising Winds, Disenchantment in Deep Shadow, Scarlet Proof, Heart of the Furnace",
        '+20% HP set': "Tenacity of the Millelith, Vourukasha's Glow",
        '+20% ER set': "Emblem of Severed Fate, Silken Moon's Serenade, Celestial Gift, The Exile",
        '+15% Healing Bonus set': "Maiden Beloved, Ocean-Hued Clam, Song of Days Past",
        '+30% DEF set': "Husk of Opulent Dreams",
        '+25% Physical DMG Bonus set': "Bloodstained Chivalry, Pale Flame",
        '+15% Anemo DMG Bonus set': "Viridescent Venerer, Desert Pavilion Chronicle",
        '+15% Cryo DMG Bonus set': "Blizzard Strayer, Finale of the Deep Galleries",
        '+15% Dendro DMG Bonus set': "Deepwood Memories",
        '+15% Electro DMG Bonus set': "Thundering Fury",
        '+15% Geo DMG Bonus set': "Archaic Petra",
        '+15% Hydro DMG Bonus set': "Heart of Depth, Nymph's Dream",
        '+15% Pyro DMG Bonus set': "Crimson Witch of Flames"
    }
    for key, value in replacement_for_placeholders.items():
        build_str = build_str.replace(key, value)
    return build_str

def get_stat_row_text(element):
    stat_text = element.get_text().replace('ⓘ', '').replace('≈', ' ≈ ')
    stat_text = re.sub('\\d+', '', stat_text)
    return stat_text

def scrape_builds(version: str):
    base_url = 'https://genshin-impact-helper-team.github.io/'
    characters_url = 'https://genshin-impact-helper-team.github.io/genshin-builds/en/'

    content = extract_page_source(characters_url)

    start_timestamp = datetime.now()

    print(f'{start_timestamp}: Started processing')

    character_url_list = []

    # Extract links to each character's page
    character_cards = content.find_all('a', class_='roster-character')
    if character_cards:
        for character_card in character_cards:
            relative_character_url = character_card['href']
            character_url_list.append(f'{base_url}{relative_character_url}')
    else:
        print('Could not find character cards. `/genshin-builds/en` list format must have changed')

    # # List of test characters. Replace previous block with the commented-out code to extract builds from a limited subset
    # # of characters
    # character_url_list = ['https://genshin-impact-helper-team.github.io/genshin-builds/en/yoimiya/', # normal character
    #                       'https://genshin-impact-helper-team.github.io/genshin-builds/en/ganyu/', # character with multiple builds
    #                       'https://genshin-impact-helper-team.github.io/genshin-builds/en/furina/'] # character with stat notes

    builds = []

    for character_url in character_url_list:
        print(f'Now processing: {character_url}')

        character_content = extract_page_source(character_url)

        # Extract character name and element
        character_name_element = character_content.find('h1', id='character-title')
        character_name = character_name_element.string
        page_body = character_content.find('body')
        character_element = page_body['data-element']

        # Extract builds
        build_buttons = character_content.find_all('button', class_='build-switcher-button')
        if build_buttons:
            for build_button in build_buttons:
                build_name_element = build_button.find('span', class_='build-switcher-name')
                build_name = build_name_element.string

                is_priority_build = 0

                # Check for the presence of the 'Best Role' badge and append a star to the build name if present
                build_badge = build_button.find('span', class_='build-badge')
                if build_badge:
                    build_name = build_name + ' ✩'
                    is_priority_build = 1

                # Find corresponding build
                build_id = build_button['data-id']
                build_section = character_content.find('section', class_='build-card', attrs={'data-id': build_id})

                if build_section:
                    artifacts = {}
                    main_stats = {}
                    substats = {}

                    artifacts_section = build_section.find('div', class_='artifact-sets-card')
                    if artifacts_section:

                        # Extract rank groups, each corresponding to a set of set options of comparable power, which we
                        # separate using `≈` characters in the final build string
                        artifact_rank_groups = artifacts_section.find_all('div', class_='rank-group')
                        for i, artifact_rank_group in enumerate(artifact_rank_groups):
                            rank_set_options = []

                            # Each set option can consist of either a 4pc set, or some combination of 2pc sets. As the
                            # HTML element hierarchy is not consistent between 4pc sets and 2pc set combinations, we
                            # extract all set names and artifact count suffixes, then associate them by index. We
                            # separate different set options at this level using `/` characters in the final build
                            # string
                            artifact_rank_rows = artifact_rank_group.find_all('div', class_='rank-row')
                            for artifact_rank_row in artifact_rank_rows:
                                set_options = []

                                set_name_elements = artifact_rank_row.find_all('span', class_='inline-note-label-emphasized')
                                artifact_count_suffixes = artifact_rank_row.find_all('span', class_='artifact-piece-suffix')
                                for j, set_name_element in enumerate(set_name_elements):
                                    set_name = set_name_element.string
                                    artifact_count_suffix = artifact_count_suffixes[j].string
                                    set_options.append(set_name + artifact_count_suffix)
                                rank_set_options.append(' / '.join(set_options))

                            build_string = ' ≈ '.join(rank_set_options)
                            build_string = inline_2pc_set_bonuses(build_string)
                            artifacts[i] = build_string
                    else:
                        print('Could not find Artifact Sets section')

                    stats_section = build_section.find('div', class_='artifact-stats-card')
                    if stats_section:
                        # There's no unique class or other attribute differentiating the Main Stats and Substats
                        # sections, so we assume that there are always two sections, corresponding to Main Stats and
                        # Substats, respectively
                        stat_sections = stats_section.find_all('div', class_='recommendation-section')
                        main_stats_section = stat_sections[0]
                        substats_section = stat_sections[1]

                        # There is similarly no attribute differentiating Sands/Goblet/Circlet, so we assume there are
                        # always three rows, corresponding to Sands/Goblet/Circlet, respectively. We search for the
                        # first `span` in each row to exclude the Sands/Goblet/Circlet header from the text.
                        artifact_slots = main_stats_section.find_all('div', class_='stat-row')
                        main_stats['Sands'] = get_stat_row_text(artifact_slots[0].find('span'))
                        main_stats['Goblet'] = get_stat_row_text(artifact_slots[1].find('span'))
                        main_stats['Circlet'] = get_stat_row_text(artifact_slots[2].find('span'))

                        substat_rows = substats_section.find_all('div', class_='rank-group')
                        for j, substat_row in enumerate(substat_rows):
                            substats[j] = get_stat_row_text(substat_row)

                    else:
                        print('Could not find Artifact Stats section')

                    builds.append({
                        'character_name': character_name,
                        'element': character_element,
                        'build_name':  build_name,
                        'is_priority_build': is_priority_build,
                        'artifacts': artifacts,
                        'main_stats': main_stats,
                        'substats': substats
                    })
                else:
                    print('Could not find build section')
        else:
            print('Could not find build switcher buttons')

    file_path = f"builds_output_{version}.json"

    with open(file_path, 'w') as json_file:
        json.dump(builds, json_file)

    print(f"The builds have been saved to {file_path}.")

    end_timestamp = datetime.now()
    print(f"{end_timestamp}: Completed processing")
    print(f"Took {(end_timestamp - start_timestamp).total_seconds()} seconds")