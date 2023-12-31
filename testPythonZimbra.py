#!venv/bin/python
# This Python file uses the following encoding: utf-8# Script pour faire mes 1er pas en Python
# O.Salaün (Univ Rennes1) : Tests API ZImbra

import pythonzimbra.communication
from pythonzimbra.communication import Communication
import pythonzimbra.tools
from pythonzimbra.tools import auth
import argparse, sys, os, subprocess
import pprint
import json

# Authentification auprès du serveur Zimbra
def zimbra_auth(conf, email):
    url = conf['soap_service_url']
    domain = email.split('@')[1]
    if domain in conf['preauth_key']:
        preauth_key = conf['preauth_key'][domain]
    else:
        raise Exception("Pas de clé configurée pour le domaine " + domain)

    if 'timeout' in conf:
        timeout = conf['timeout']
    else:
        timeout = 5
    comm = Communication(url=url, timeout=timeout)

    usr_token = auth.authenticate(
        url,
        email,
        preauth_key
    )

    # Contexte EPE : si authentification échoue, ça peut être parce que le VRAI domaine de l'utilisateur est en univ-rennes1.fr
    # dans ce cas, on essaie une authentification sur les domaines alternatifs définis dans la conf
    if not usr_token:
        if 'alt_domains' in conf and domain in conf['alt_domains']:
            altdomain = conf['alt_domains'][domain]
            altemail = email.replace('@'+domain, '@'+altdomain)
            (comm, usr_token) = zimbra_auth(conf,altemail)

    return (comm, usr_token)


def zimbra_request(zimbra_action, zimbra_namespace, email, request_data, request_type="json"):
    (comm, usr_token) = zimbra_auth(conf, email)

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        zimbra_action+'Request', request_data, zimbra_namespace)
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)

    return info_response

printer = pprint.PrettyPrinter(indent=4, width=500)

sample_email="user@my.dom"
sample_conf="prod-conf.json"
# Configuration des paramètres d'appel
epilog = "Exemples d'appel :\n" + \
    "./testPythonZimbra.py --conf=%s --createFolder --email=%s --folder='Quarantaine_Phishing'\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --createIdentity --email=%s --for=user2@dom --id=New_Avatar --display='User' | jq .\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --deleteIdentity --email=%s --id=New_Avatar| jq .\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --getAccountInfo --email=%s | jq .\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --getFolder --email=%s --folder='/' -depth=0\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --getMailCount --email=%s --folder='/inbox'\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --getIdentities --email=%s | jq .\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --getInfo --email=%s | jq .\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --getMsg --email=%s --id=12567\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --getMsg --email=%s --id=12567 --part=1.2\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --getPrefs --email=%s | jq .\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --getRights --email=%s --right=sendAs\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --grantAccessFolder --email=%s --id=2 --for=user2@dom.fr\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --grantRights --right=viewFreeBusy --type=dom --domain=my.dom --email=%s | jq .\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --modifyIdentity --email=%s --for=user2@dom --id=New_Avatar --display='User' | jq .\n" % (sample_conf, sample_email) +\
    "./testPythonZimbra.py --conf=%s --moveMsg --email=%s --id=963827 --folder=8_Perso\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --search --email=%s --folder=Inbox\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --search --email=%s --query='from:user@univ-avignon.fr'\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --search --email=%s --query='#X-Mailer:\"PHPMailer 6.0.2\"'\n" % (sample_conf, sample_email)  +\
    "./testPythonZimbra.py --conf=%s --search --getMsg --email=%s --id=962266\n" % (sample_conf, sample_email)


parser = argparse.ArgumentParser(description="Exploitation des boîtes mail sur la plateforme Partage", epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--conf', required=True, metavar=sample_conf, help="fichier de configuration JSON")
parser.add_argument('--createIdentity', action='store_const', const=True, help="Création d'un avatar")
parser.add_argument('--createFolder', action='store_const', const=True, help="Création d'un dossier mail")
parser.add_argument('--deleteIdentity', action='store_const', const=True, help="Suppression d'un avatar")
parser.add_argument('--depth', metavar='0', help="profondeur de la recherche")
parser.add_argument('--display', metavar='2', help="Nom affiché (pour From)")
parser.add_argument('--domain', metavar='univ-rennes1.fr', help="domaine de messagerie")
parser.add_argument('--email', metavar='user@univ-rennes1.fr', help="adrese email de l'utilisateur")
parser.add_argument('--folder', metavar='/inbox', help="dossier de l'utilisateur")
parser.add_argument('--for', metavar='user@univ-rennes1.fr', help="adrese email de l'autre utilisateur")
parser.add_argument('--getAccountInfo', action='store_const', const=True, help="Retourne les infos sur un compte")
parser.add_argument('--getIdentities', action='store_const', const=True, help="Consultation des avatars")
parser.add_argument('--getInfo', action='store_const', const=True, help="Retourne les infos sur un compte")
parser.add_argument('--getFolder', action='store_const', const=True, help="Infos sur un dossier mail")
parser.add_argument('--getMailCount', action='store_const', const=True, help="Nombre de mails dans un dossier")
parser.add_argument('--getMsg', action='store_const', const=True, help="Accès à un message")
parser.add_argument('--getPrefs', action='store_const', const=True, help="Consultation des préférences utilisateur")
parser.add_argument('--getRights', action='store_const', const=True, help="Consultation des droits sendAs et sendOnBehalfOf")
parser.add_argument('--grantAccessFolder', action='store_const', const=True, help="Donne accès à un dossier")
parser.add_argument('--grantRights', action='store_const', const=True, help="Modif droits")
parser.add_argument('--id', metavar='2', help="Identifiant d'un objet (dossier)")
parser.add_argument('--limit', metavar='0', help="Limite (pour recherche)")
parser.add_argument('--modifyIdentity', action='store_const', const=True, help="Modification d'un avatar")
parser.add_argument('--moveMsg', action='store_const', const=True, help="Déplacer un message dans un dossier")
parser.add_argument('--offset', metavar='0', help="Offset (pour recherche)")
parser.add_argument('--part', metavar='2', help="Identifiant d'une partie MIME d'un mail")
parser.add_argument('--query', metavar='0', help="requête (pour recherche)")
parser.add_argument('--right', metavar='sendAs', help="tpe de droit (sendAs ou SendOnBehalfOf)")
parser.add_argument('--search', action='store_const', const=True, help="Liste des mails dans un dossier (si --folder spécifié) ou recherche (si --query spécifié)")
parser.add_argument('--type', metavar='dom', help="type de droits")


args = vars(parser.parse_args())

with open(args['conf'], 'r') as conf_file:
    conf = json.load(conf_file)
    #printer.pprint(conf)

if args['getMailCount']:

    for need in ('email','folder'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    request_data = {
        'folder': {
                'path': args['folder']
            }
    }
    info_response = zimbra_request('GetFolder', 'urn:zimbraMail', args['email'], request_data)

    print ("Nombre de mails dans %s : %s" % (args['folder'], info_response.get_response()['GetFolderResponse']['folder']['n']))

elif args['grantAccessFolder']:

    for need in ('email','for','id'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    # ID dossier = 1 (mailbox's root folder)
    request_data = {
            'account': {
              'by': 'name',
                '_content': args['email']
            },
            'action': {
                'op': 'grant',
                'id': args['id'],
                'grant': {
                    'gt': 'usr',
                    'inh': 1,
                    'd': args['for'],
                    'perm': 'rwidx'
                }
            }
        }
    info_response = zimbra_request('FolderAction', 'urn:zimbraMail', args['email'], request_data)

    printer.pprint(info_response.get_response()['FolderActionResponse'])

    request_data = {
            'account': {
              'by': 'name',
                '_content': args['email']
            },
            'item': {
                'id': args['id'],
                'e': {
                    'a': args['for']
                }
            }
        }
    info_request = zimbra_request('SendShareNotification', 'urn:zimbraMail', args['email'], request_data)

    print(json.dumps(info_response.get_response()['SendShareNotificationResponse']))


elif args['getAccountInfo']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    request_data = {
            'account': {
                'by': 'name',
                '_content': args['email']
            }
        }
    info_response = zimbra_request('GetAccountInfo', 'urn:zimbraAccount', args['email'], request_data)

    print(json.dumps(info_response.get_response()['GetAccountInfoResponse']))

elif args['getInfo']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    request_data = {}
    info_response = zimbra_request('GetInfo', 'urn:zimbraAccount', args['email'], request_data)

    print(json.dumps(info_response.get_response()['GetInfoResponse']))

elif args['getFolder']:

    for need in ('email','folder'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    depth = 1
    if args['depth']:
        depth = int(args['depth'])
    request_data = {
            'folder': {
                'path': args['folder']
            },
            'depth': depth
        }
    info_response = zimbra_request('GetFolder', 'urn:zimbraMail', args['email'], request_data)

    print(json.dumps(info_response.get_response()['GetFolderResponse']['folder']))

elif args['search']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not (args['folder'] or args['query']):
        print("Paramètre manquant : folder ou query")
        raise Exception("Paramètre manquant : folder or query")

    limit=100
    if args['limit']:
        limit = args['limit']

    offset = 0
    if args['offset']:
        offset= args['offset']

    query = ""
    if args['query']:
        query = args['query']
    else:
        query = 'in:"'+args['folder']+'"'

    request_data = {
            'query': query,
            'types': "message",
            'limit': limit,
            'offset': offset
        }
    info_response = zimbra_request('Search', 'urn:zimbraMail', args['email'], request_data)

    print(json.dumps(info_response.get_response()['SearchResponse']))

elif args['getPrefs']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    request_data = {
            'pref': {
                'name': 'zimbraPrefPasswordRecoveryAddress',
            }
        }
    info_response = zimbra_request('GetPrefs', 'urn:zimbraAccount', args['email'], request_data)

    print(json.dumps(info_response.get_response()['GetPrefsResponse']))

elif args['getRights']:

    for need in ('email','right'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    request_data = {
            'ace': [
                {
                    'right': args['right']
                }
            ]
        }
    info_response = zimbra_request('GetRights', 'urn:zimbraAccount', args['email'], request_data)

    print(json.dumps(info_response.get_response()['GetRightsResponse']))

elif args['getMsg']:

    for need in ('email','id'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    request_data = {
            'm': [
                {
                    'id': args['id'],
                    'raw': 0,
                    'wantContent': 'both',
                    'header': [
                        { 'n': 'X-UCE-Type'},
                        { 'n': 'X-Renater-Spam-Status'}
                    ],
                }
            ]
        }
    if args['part']:
        request_data['m'][0]['part'] = args['part']

    info_response = zimbra_request('GetMsg', 'urn:zimbraMail', args['email'], request_data)

    print(json.dumps(info_response.get_response()['GetMsgResponse']))

elif args['moveMsg']:

    for need in ('email','id','folder'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

     # Get folder ID
    request_data = {
        'folder': {
            'path': args['folder']
        }
    }
    info_response = zimbra_request('GetFolder', 'urn:zimbraMail', args['email'], request_data)

    folder_id = info_response.get_response()['GetFolderResponse']['folder']['id']
    #print("Folder "+folder_id)

    # Move message to folder
    request_data = {
            'action': [
                {
                    'op': 'move',
                    'id': args['id'],
                    'l': folder_id
                }
            ]
        }
    info_response = zimbra_request('MsgAction', 'urn:zimbraMail', args['email'], request_data)

    print(json.dumps(info_response.get_response()['MsgActionResponse']))

elif args['grantRights']:

    for need in ('email','type','right'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    # On commence par révoquer les droits publics (zid="99999999-9999-9999-9999-999999999999")
    request_data = {
            'ace': [
                {
                    'gt': 'pub',
                    'zid': "99999999-9999-9999-9999-999999999999",
                    'right': args['right']
                }
            ]
        }

    info_response = zimbra_request('RevokeRights', 'urn:zimbraAccount', args['email'], request_data)

    # Ajout droits
    if args['type'] == "usr":
        if not args['for']:
            print("Paramètre manquant : for")
            raise Exception("Paramètre manquant : for")

        request_data = {
                'ace': [
                    {
                        'gt': args['type'],
                        'd': args['for'],
                        'right': args['right']
                    }
                ]
            }
    else:
        if not args['domain']:
            print("Paramètre manquant : domain")
            raise Exception("Paramètre manquant : domain")

        request_data = {
                'ace': [
                    {
                        'gt': args['type'],
                        'd': args['domain'],
                        'right': args['right']
                    }
                ]
            }

    info_response = zimbra_request('GrantRights', 'urn:zimbraAccount', args['email'], request_data)

    print(json.dumps(info_response.get_response()['GrantRightsResponse']))

elif args['createIdentity']:

    for need in ('email','id','for','display'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    request_data = {
            'identity': {
                'name': args['id'],
                'a':
                    [
                        {
                            'name': 'zimbraPrefIdentityName',
                            '_content': args['id']
                        },
                        {
                            'name': 'zimbraPrefFromDisplay',
                            '_content': args['display']
                        },
                        {
                            'name': 'zimbraPrefFromAddress',
                            '_content': args['for']
                        }
                ]
            }
        }
    info_response = zimbra_request('CreateIdentity', 'urn:zimbraAccount', args['email'], request_data, request_type="xml")

    print(json.dumps(info_response.get_response()['CreateIdentityResponse']))

elif args['modifyIdentity']:

    for need in ('email','id','for','display'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    request_data = {
            'identity': {
                'name': args['id'],
                'a':
                [
                    {
                         'name': 'zimbraPrefIdentityName',
                         '_content': args['id']
                     },
                     {
                         'name': 'zimbraPrefFromDisplay',
                         '_content': args['display']
                     },
                    {
                        'name': 'zimbraPrefFromAddress',
                        '_content': args['for']
                    }
                ]
            }
        }
    info_response = zimbra_request('ModifyIdentity', 'urn:zimbraAccount', args['email'], request_data, request_type="xml")

    print(json.dumps(info_response.get_response()['ModifyIdentityResponse']))

elif args['getIdentities']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    request_data = {}
    info_response = zimbra_request('GetIdentities', 'urn:zimbraAccount', args['email'], request_data)

    print(json.dumps(info_response.get_response()['GetIdentitiesResponse']))

elif args['deleteIdentity']:

    for need in ('email','id'):
        if not args[need]:
            print("Paramètre manquant : "+need)
            raise Exception("Paramètre manquant : "+need)

    request_data = {
            'identity': {
                'name': args['id']
            }
        }
    info_response = zimbra_request('DeleteIdentity', 'urn:zimbraAccount', args['email'], request_data)

    print(json.dumps(info_response.get_response()['DeleteIdentityResponse']))

elif args['createFolder']:

    for need in ('email', 'folder'):
        if not args[need]:
            print("Paramètre manquant : " + need)
            raise Exception("Paramètre manquant : " + need)

    request_data = {
                    'folder': {
                        'name': args['folder'],
                        'view': 'message'
                    }
                }
    info_response = zimbra_request('CreateFolder', 'urn:zimbraMail', args['email'], request_data)

    print(json.dumps(info_response.get_response()['CreateFolderResponse']))
