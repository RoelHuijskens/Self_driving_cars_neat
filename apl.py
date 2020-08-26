import string


x = string.ascii_lowercase*2

z = 'aoepctqihjgfkbrylvdznxuwms'

dictionairy = {}


for q in range(0,26):

    print(q)

    for i in range(0,26):
        dictionairy[z[i]] = x[i-q]




    message = 'nvwmvo kjuyba wu eajvn vr mawgnbxo obb vxlwrr je gbelnblbx'
    message_2 = 'gibriv apxslp qiepbzd fsw ap jkbxk ic rlbagpf tb db vpnpk kpxobfbk'

    encrypted = ''

    for a in message_2:

        if a == ' ':
            encrypted = encrypted + ' '
        else:
            encrypted = encrypted + dictionairy[a]

    print(encrypted)

    print('/')