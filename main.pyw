import PySimpleGUI as sg
import json
import requests
import os
import math
from PIL import Image, ImageOps


if not os.path.exists("Results"):
    os.makedirs("Results")

if not os.path.exists("Resources/Texts"):
    os.makedirs("Resources/Texts")

sg.theme('DarkRed2')



RRCHARS = ["Afi and Galu", "Ashani", "Ezzie", "Kidd", "Raymer", "Weishan", "Urdah", "Zhurong", "Seth", "Velora"]
CHARACTERS_ID = ["1756", "1757", "1758", "1759", "1760", "1761", "1762", "1763", "1844", "1875"]
IMG_TYPES = ['Default', 'Poster', "Mini Menu", 'CSS']

disabled_state = False

def get_character_from_id(char_id):
    return RRCHARS[CHARACTERS_ID.index(str(char_id))]

def disable_character_options():
    window['mirror_left'].update(disabled=disabled_state)
    window['mirror_right'].update(disabled=disabled_state)
    window['use_default'].update(disabled=disabled_state)
    window['use_poster'].update(disabled=disabled_state)
    window['use_css'].update(disabled=disabled_state)
    window['use_minimenu'].update(disabled=disabled_state)
    

with open('api_key.txt', 'r') as f:
    API_KEY = f.read()

layout = [  [sg.Text('Smashgg API Key')],
            [sg.InputText(default_text=API_KEY, justification='c', key='api_key', password_char='*')],
            [sg.Text('Set ID')],
            [sg.InputText(justification='c', key='set_id')],
            [],
            # [sg.Text('Characters/Legends')],
            # [sg.Text("Player 1's Character"), sg.Text("Player 2's Character")],
            # [sg.Combo(values=RRCHARS, key='PLAYER1', readonly=True), sg.Combo(values=RRCHARS, key='PLAYER2', readonly=True)],
            [sg.Checkbox("Mirror Left Image", default=True, key='mirror_left'), sg.Checkbox("Mirror Right Image", default=False, key='mirror_right')],
            [sg.Radio('Use Default Images', 'img_types', default=True, key='use_default'), sg.Radio('Use Poster Images', 'img_types', key='use_poster'), sg.Radio('Use Mini Menu Images', 'img_types', key='use_minimenu'), sg.Radio('Use CSS Images', 'img_types', key='use_css')],            
            [sg.Radio('Update Scoreboard/VS Screen and Write Files', group_id='updater', default=True, key='update_all', enable_events=True), sg.Radio('Update Scoreboard/VS Screen Only', group_id='updater', key='update_scoreboard_only', enable_events=True), sg.Radio('Write Files Only', group_id='updater', key='update_files_only', enable_events=True)],
            [sg.Text('Optional ↓')],
            [sg.Text('Caster 1'), sg.Text('Caster 2')],
            [sg.InputText(justification='c', key='caster_1', size=20), sg.InputText(justification='c', key='caster_2', size=20)],
            [sg.Text('Twitter 1'), sg.Text('Twitter 2')],
            [sg.InputText(justification='c', key='twitter_1', size=20), sg.InputText(justification='c', key='twitter_2', size=20)],
            [sg.Text('Twitch 1'), sg.Text('Twitch 2')],
            [sg.InputText(justification='c', key='twitch_1', size=20), sg.InputText(justification='c', key='twitch_2', size=20)],
            [sg.Button('Fetch Results')]]


window = sg.Window('Rushdown Revolt SGG Fetcher v1.1.0', layout, element_justification='c')

def update_chars(char1, char2):

    if values['use_poster']:
        img_type = "Poster"

    elif values['use_minimenu']:
        img_type = "MiniMenu"
    
    elif values['use_css']:
        img_type = "CSS"
    
    elif values['use_default']:
        img_type = "CharSel"
                
    if not values['mirror_left']:
        with open('Results/charleft.png', 'wb') as f:
            if char1 == "Random":
                image_location = "Resources/Characters/Random/Poster.png"
            else:
                image_location = f"Resources/Characters/{char1}/{img_type}.png"
            
            with open(image_location, 'rb') as character:
                f.write(character.read())
    else:
        if char1 == "Random":
            image_location = "Resources/Characters/Random/Poster.png"
        else:
            image_location = f"Resources/Characters/{char1}/{img_type}.png"
        
        im_flip = ImageOps.mirror(Image.open(image_location))
        im_flip.save('Results/charleft.png')

    if not values['mirror_right']:
        with open('Results/charright.png', 'wb') as f:
            if char2 == "Random":
                image_location = "Resources/Characters/Random/Poster.png"
            else:
                image_location = f"Resources/Characters/{char2}/{img_type}.png"
            
            with open(image_location, 'rb') as character:
                f.write(character.read())
    else:
        if char2 == "Random":
            image_location = "Resources/Characters/Random/Poster.png"
        else:
            image_location = f"Resources/Characters/{char2}/{img_type}.png"
        
        im_flip = ImageOps.mirror(Image.open(image_location))
        im_flip.save('Results/charright.png')
            
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    # Disable Character Settings if on scoreboard_only mode
    if values['update_scoreboard_only']:
        disabled_state = True
        disable_character_options()
    
    if values['update_all'] or values['update_files_only']:
        disabled_state = False
        disable_character_options()

    if event == 'Fetch Results':
        if values['set_id'] == '':
            sg.popup_error("Error", "Set ID can't be empty")

        
        if values['set_id'] != '':

            SetID = values['set_id']
                
            query = '''
            query InProgressSet {{
            set(id: {TheID}) {{
                state
                fullRoundText
                event {{
                    tournament {{
                        name
                    }}
                }}
                games {{
                selections {{
                    selectionValue
                }}
                }}
                slots {{
                entrant {{
                    name
                    participants{{
                        gamerTag
                        prefix
                        id
                        user{{
                        location{{
                            country
                        }}
                    }}
                    }}
                }}
                standing {{
                    stats {{
                    score {{
                        value
                    }}
                    }}
                }}
                }}
            }}
            }}
            '''.format(TheID = SetID)

            data = {'query': query}
            headers = {'Authorization': 'Bearer ' + values['api_key']}
            data = requests.post("https://api.smash.gg/gql/alpha", data=data, headers=headers)
            data = json.loads(data.text)

            thejson = json.dumps(data, indent=2)
            print(thejson)

            # Handle Bad API Token
            if 'success' in data:
                if data['success'] == False:
                    sg.popup_error("Error", "Bad API Token", "Get an API token from https://smash.gg/admin/profile/developer")

            else:
                # Handle Bad Set ID
                if data['data']['set'] == None:
                    sg.popup_error("Error", "Bad Set ID", "Review your set ID and try again")

                else:
                    left_full_name = data['data']['set']['slots'][0]['entrant']['name']
                    left_score = data['data']['set']['slots'][0]['standing']['stats']['score']['value']
                    left_gamertag = data['data']['set']['slots'][0]['entrant']['participants'][0]['gamerTag']

                    right_full_name = data['data']['set']['slots'][1]['entrant']['name']
                    right_score = data['data']['set']['slots'][1]['standing']['stats']['score']['value']
                    right_gamertag = data['data']['set']['slots'][1]['entrant']['participants'][0]['gamerTag']
                    
            
                    if data['data']['set']['slots'][0]['entrant']['participants'][0]['prefix'] == None:
                        left_prefix = ""
                    else:
                        left_prefix = data['data']['set']['slots'][0]['entrant']['participants'][0]['prefix']

                    if data['data']['set']['slots'][1]['entrant']['participants'][0]['prefix'] == None:
                        right_prefix = ""
                    else:
                        right_prefix = data['data']['set']['slots'][1]['entrant']['participants'][0]['prefix']
                    
                    set_name = data['data']['set']['fullRoundText']
                    tourney_name = data['data']['set']['event']['tournament']['name']
                    best_of = requests.get(f"https://api.smash.gg/set/{SetID}").json()['entities']['sets']['bestOf']
                   
                    left_country = data['data']['set']['slots'][0]['entrant']['participants'][0]['user']['location']['country']
                    right_country = data['data']['set']['slots'][1]['entrant']['participants'][0]['user']['location']['country']

                    caster_1 = values['caster_1']
                    caster_2 = values['caster_2']
                    twitch_1 = values['twitch_1']
                    twitch_2 = values['twitch_2']
                    twitter_1 = values['twitter_1']
                    twitter_2 = values['twitter_2']
                    
                    if data['data']['set']['games'] != None:
                        left_character = get_character_from_id(data['data']['set']['games'][-1]['selections'][0]['selectionValue'])
                        right_character = get_character_from_id(data['data']['set']['games'][-1]['selections'][1]['selectionValue'])
                    else:
                        left_character, right_character = "Random", "Random"


                    if values['update_all'] or values['update_scoreboard_only']:
                        with open('Resources/Texts/ScoreboardInfo.json', 'w') as f:
                            if set_name == 'Grand Final' or set_name == 'Grand Final Reset':
                                wl_list = [None, 'W', 'L']
                            else:
                                wl_list = [None, 'Nada', 'Nada']

                            if data['data']['set']['games'] == None:
                                if left_score == -1:
                                    left_gamertag = f"{left_gamertag} [DQ]"
                                    left_prefix = ""
                                    right_score = math.ceil(best_of / 2)

                                if right_score == -1:
                                    right_gamertag = f"[DQ] {right_gamertag}"
                                    right_prefix = ""
                                    left_score = math.ceil(best_of / 2)
                            
                            score_list = [None, str(left_score), str(right_score)]

                            overlay_json = {'player': [{}, {'name': left_gamertag.lower(), 'tag': left_prefix, 'character': left_character}, {'name': right_gamertag, 'tag': right_prefix, 'character':right_character}, {'name': '', 'tag': '', 'character': 'Random'}, {'name': '', 'tag': '', 'character': 'Random'}, {'name': '', 'tag': '', 'character': 'Random'}, {'name': '', 'tag': '', 'character': 'Random'}],
                            'teamName': [None, '', ''], 'score': score_list, 'wl': wl_list, 'gamemode': 1, 'bestOf': f'Bo{best_of}', 'round': set_name, 'tournamentName': tourney_name, 'caster': [{}, {'name': caster_1, 'twitter': twitter_1, 'twitch': twitch_1}, {'name': caster_2, 'twitter': twitter_2, 'twitch': twitch_2}], 'allowIntro': False}
                            scoreboard_json = json.dumps(overlay_json, indent=2)
                            f.write(scoreboard_json)

                    if values['update_files_only'] or values['update_all']:
                        with open('countries.json', 'r') as countries:
                            country_dict = json.loads(countries.read())

                            with open('Results/leftflag.png', 'wb') as f:
                                if left_country != None:
                                    f.write(requests.get(f"https://flagcdn.com/256x192/{country_dict[left_country]}.png").content)

                            with open('Results/rightflag.png', 'wb') as f:
                                if right_country != None:
                                    f.write(requests.get(f"https://flagcdn.com/256x192/{country_dict[right_country]}.png").content)
                        
                        with open('Results/leftfullname.txt', 'w') as f:
                            f.write(left_full_name)
                        with open('Results/leftgamertag.txt', 'w') as f:
                            f.write(left_gamertag)
                        with open('Results/leftprefix.txt', 'w') as f:
                            f.write(left_prefix)
                        with open('Results/leftscore.txt', 'w') as f:
                            if left_score == -1:
                                f.write("DQ")
                            else:
                                f.write(str(left_score))
                        
                        with open('Results/rightfullname.txt', 'w') as f:
                            f.write(right_full_name)
                        with open('Results/rightgamertag.txt', 'w') as f:
                            f.write(right_gamertag)
                        with open('Results/rightprefix.txt', 'w') as f:
                            f.write(right_prefix)
                        with open('Results/rightscore.txt', 'w') as f:
                            if right_score == -1:
                                f.write("DQ")
                            else:
                                f.write(str(right_score))
                        
                        with open('Results/setname.txt', 'w') as f:
                            f.write(set_name)
                        with open('Results/tourneyname.txt', 'w') as f:
                            f.write(tourney_name)
                        
                        update_chars(left_character, right_character)

                        with open('Results/caster1.txt', 'w') as f:
                            f.write(caster_1)
                        with open('Results/twitter1.txt', 'w') as f:
                            f.write(twitter_1)
                        with open('Results/twitch1.txt', 'w') as f:
                            f.write(twitch_1)

                        with open('Results/caster2.txt', 'w') as f:
                            f.write(caster_2)
                        with open('Results/twitter2.txt', 'w') as f:
                            f.write(twitter_2)
                        with open('Results/twitch2.txt', 'w') as f:
                            f.write(twitch_2)
                         

                    

window.close()