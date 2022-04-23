import PySimpleGUI as sg
import json
import requests
import os
from PIL import Image, ImageOps
  

if not os.path.exists("Results"):
    os.makedirs("Results")

sg.theme('DarkRed2')


RRCHARS = ['Afi and Galu', 'Ashani', 'Ezzie', 'Kidd', 'Raymer', 'Seth', 'Urdah', 'Velora', 'Weishan', 'Zhurong']
IMG_TYPES = ['Default', 'Poster', "Mini Menu", 'CSS']

with open('api_key.txt', 'r') as f:
    API_KEY = f.read()

layout = [  [sg.Text('Smashgg API Key')],
            [sg.InputText(default_text=API_KEY, justification='c', key='api_key', password_char='*')],
            [sg.Text('Set ID')],
            [sg.InputText(justification='c', key='set_id')],
            [],
            [sg.Text('Characters/Legends')],
            [sg.Text("Player 1's Character"), sg.Text("Player 2's Character")],
            [sg.Combo(values=RRCHARS, key='PLAYER1', readonly=True), sg.Combo(values=RRCHARS, key='PLAYER2', readonly=True)],
            [sg.Checkbox("Mirror Left Image", default=True, key='mirror_left'), sg.Checkbox("Mirror Right Image", default=False, key='mirror_right')],
            [sg.Radio('Use Default Images', 'img_types', default=True, key='use_default'), sg.Radio('Use Poster Images', 'img_types', key='use_poster'), sg.Radio('Use Mini Menu Images', 'img_types', key='use_minimenu'), sg.Radio('Use CSS Images', 'img_types', key='use_css')],            
            [sg.Button('Fetch Results'), sg.Button('Update Characters Only')]]


window = sg.Window('Rushdown Revolt SGG Fetcher', layout, element_justification='c')

def update_chars():

    if values['use_poster']:
        img_type = "Poster"

    elif values['use_minimenu']:
        img_type = "MiniMenu"
    
    elif values['use_css']:
        img_type = "CSS"
    
    elif values['use_default']:
        img_type = "CharSel"

    if values['PLAYER1'] == '':
        sg.popup_error("Error", "Player 1 Character can't be empty", "Image won't be changed")

    if values['PLAYER2'] == '':
        sg.popup_error("Error", "Player 2 Character can't be empty", "Image won't be changed")
                
    if values['PLAYER1'] != '':
        if not values['mirror_left']:
            with open('Results/charleft.png', 'wb') as f:
                with open(f'Characters/{values["PLAYER1"]}/{img_type}.png', 'rb') as character:
                    f.write(character.read())
        else:
            im_flip = ImageOps.mirror(Image.open(f'Characters/{values["PLAYER1"]}/{img_type}.png'))
            im_flip.save('Results/charleft.png')
            
    if values['PLAYER2'] != '':
        if not values['mirror_right']:
            with open('Results/charright.png', 'wb') as f:
                with open(f'Characters/{values["PLAYER2"]}/{img_type}.png', 'rb') as character:
                    f.write(character.read())
        else:
            im_flip = ImageOps.mirror(Image.open(f'Characters/{values["PLAYER2"]}/{img_type}.png'))
            im_flip.save('Results/charright.png')

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Fetch Results':
        print('You entered ', values['api_key'])

        if values['set_id'] == '':
            sg.popup_error("Error", "Set ID can't be empty")

        
        if values['set_id'] != '':

            SetID = values['set_id']
            
            update_chars()
                

            query = '''
            query InProgressSet {{
            set(id: {TheID}) {{
                state
                fullRoundText
                games {{
                selections {{
                    selectionValue
                }}
                }}
                slots {{
                entrant {{
                    name
                    id
                    participants{{
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
            headers = {'Authorization': 'Bearer ' + API_KEY}
            data = requests.post("https://api.smash.gg/gql/alpha", data=data ,headers=headers)
            data = json.loads(data.text)
            thejson = json.dumps(data, indent=2)

            left_name = data['data']['set']['slots'][0]['entrant']['name']
            left_score = data['data']['set']['slots'][0]['standing']['stats']['score']['value']
            right_name = data['data']['set']['slots'][1]['entrant']['name']
            right_score = data['data']['set']['slots'][1]['standing']['stats']['score']['value']

            left_country = data['data']['set']['slots'][0]['entrant']['participants'][0]['user']['location']['country']
            right_country = data['data']['set']['slots'][1]['entrant']['participants'][0]['user']['location']['country']

            with open('countries.json', 'r') as countries:
                country_dict = json.loads(countries.read())

                with open('Results/leftflag.png', 'wb') as f:
                    f.write(requests.get(f"https://flagcdn.com/256x192/{country_dict[left_country]}.png").content)

                with open('Results/rightflag.png', 'wb') as f:
                    f.write(requests.get(f"https://flagcdn.com/256x192/{country_dict[right_country]}.png").content)

            with open('Results/leftname.txt', 'w') as f:
                f.write(left_name)
            with open('Results/leftscore.txt', 'w') as f:
                f.write(str(left_score))
            with open('Results/rightname.txt', 'w') as f:
                f.write(right_name)
            with open('Results/rightscore.txt', 'w') as f:
                f.write(str(right_score))

    if event == 'Update Characters Only':
        update_chars()

window.close()
