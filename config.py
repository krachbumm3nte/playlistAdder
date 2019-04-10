# appearance
window_width = 35
image_size = 300
backgroundcolor = 'grey'
textcolor = 'white'
selected_text_color = 'blue'

# keymap
key_escape = '<Escape>'
key_confirm = '<Return>'
key_movelistup = '<Up>'
key_movelistdown = '<Down>'
key_confirm_selection = '<Shift_R>'

# userdata
scope = 'playlist-modify-private playlist-modify user-read-currently-playing'
user = 'krachbumm3nte'
c_id = '83ec14d049604028b6e78c5fa0cba697'
c_secret = '6a918e609e2f4fea9aa672d2dbe74e59'
redirect = 'http://localhost:8080'

'''

config = configparser.ConfigParser()
config.read('config.ini')

appearance = config['appearance']

window_width = int(appearance['window_width'])
image_size = int(appearance['image_size'])
backgroundcolor = appearance['backgroundcolor']
textcolor = appearance['textcolor']
selected_text_color = appearance['selected_text_color']

keymap = config['keymap']

key_escape = keymap['key_escape']
key_confirm = keymap['key_confirm']
key_movelistup = keymap['key_movelistup']
key_movelistdown = keymap['key_movelistdown']
key_confirm_selection = keymap['key_confirm_selection']

userdata = config['userdata']

scope = userdata['scope']
user = userdata['user'] #TODO

c_id = userdata['c_id']
c_secret = userdata['c_secret']
redirect = userdata['redirect']
'''


