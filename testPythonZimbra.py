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
def zimbra_auth(url, preauth_key, email):

    comm = Communication(url)

    usr_token = auth.authenticate(
        url,
        email,
        preauth_key
    )

    return (comm, usr_token)


printer = pprint.PrettyPrinter(indent=4, width=500)

# Configuration des paramètres d'appel
epilog = "Exemples d'appel :\n" + \
    "./testPythonZimbra.py --conf=ur1-prod-zimbra.json --getMailCount --email=p-salaun@univ-rennes1.fr --folder='/inbox'\n" +\
    "./testPythonZimbra.py --conf=ur1-prod-zimbra.json --getMsg --email=p-salaun@univ-rennes1.fr --id=12567\n" +\
    "./testPythonZimbra.py --conf=ur1-prod-zimbra.json --getFolder --email=p-salaun@univ-rennes1.fr --folder='/' -depth=0\n" +\
    "./testPythonZimbra.py --conf=ur1-prod-zimbra.json --getRights --email=p-salaun@univ-rennes1.fr --right=sendAs\n" +\
    "./testPythonZimbra.py --conf=ur1-prod-zimbra.json --grantAccessFolder --email=p-salaun@univ-rennes1.fr --id=2 --for=olivier.salaun@univ-rennes1.fr\n"

parser = argparse.ArgumentParser(description="Exploitation des boîtes mail sur la plateforme Partage", epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--conf', required=True, metavar='ur1-prod-zimbra.json', help="fichier de configuration JSON")
parser.add_argument('--email', metavar='jean.kermarrec@univ-rennes1.fr', help="adrese email de l'utilisateur")
parser.add_argument('--domain', metavar='univ-rennes1.fr', help="domaine de messagerie")
parser.add_argument('--for', metavar='anne.guernic@univ-rennes1.fr', help="adrese email de l'autre utilisateur")
parser.add_argument('--folder', metavar='/inbox', help="dossier de l'utilisateur")
parser.add_argument('--type', metavar='dom', help="type de droits")
parser.add_argument('--depth', metavar='0', help="profondeur de la recherche")
parser.add_argument('--id', metavar='2', help="Identifiant d'un objet (dossier)")
parser.add_argument('--display', metavar='2', help="Nom affiché (pour From)")
parser.add_argument('--getMailCount', action='store_const', const=True, help="Nombre de mails dans un dossier")
parser.add_argument('--getMsg', action='store_const', const=True, help="Accès à un message")
parser.add_argument('--getFolder', action='store_const', const=True, help="Infos sur un dossier mail")
parser.add_argument('--getAccountInfo', action='store_const', const=True, help="Retourne les infos sur un compte")
parser.add_argument('--getInfo', action='store_const', const=True, help="Retourne les infos sur un compte")
parser.add_argument('--grantAccessFolder', action='store_const', const=True, help="Donne accès à un dossier")
parser.add_argument('--getPrefs', action='store_const', const=True, help="Consultation des préférences utilisateur")
parser.add_argument('--getRights', action='store_const', const=True, help="Consultation des droits sendAs et sendOnBehalfOf")
parser.add_argument('--grantRights', action='store_const', const=True, help="Modif droits")
parser.add_argument('--right', metavar='sendAs', help="tpe de droit (sendAs ou SendOnBehalfOf)")
parser.add_argument('--createIdentity', action='store_const', const=True, help="Création d'un avatar")
parser.add_argument('--modifyIdentity', action='store_const', const=True, help="Modification d'un avatar")
parser.add_argument('--deleteIdentity', action='store_const', const=True, help="Suppression d'un avatar")
parser.add_argument('--getIdentities', action='store_const', const=True, help="Consultation des avatars")


args = vars(parser.parse_args())

with open(args['conf'], 'r') as conf_file:
    conf = json.load(conf_file)
    #printer.pprint(conf)

if args['getMailCount']:

    if not args['email']:
        logger.error("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetFolderRequest',
        {
            'folder': {
                'path': '/inbox'
            }
        },
        'urn:zimbraMail'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)

    print ("Nombre de mails dans Inbox : %s" % info_response.get_response()['GetFolderResponse']['folder']['n'])

elif args['grantAccessFolder']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['for']:
        print("Paramètre manquant : for")
        raise Exception("Paramètre manquant : for")

    if not args['id']:
        print("Paramètre manquant : id")
        raise Exception("Paramètre manquant : id")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)

    # ID dossier = 1 (mailbox's root folder)
    info_request.add_request(
        'FolderActionRequest',
        {
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
        },
        'urn:zimbraMail'
    )

    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)

    printer.pprint(info_response.get_response()['FolderActionResponse'])

    info_request = comm.gen_request(token=usr_token)

    info_request.add_request(
        'SendShareNotificationRequest',
        {
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
        },
        'urn:zimbraMail'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)

    printer.pprint(info_response.get_response()['SendShareNotificationResponse'])


elif args['getAccountInfo']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetAccountInfoRequest',
        {
            'account': {
                'by': 'name',
                '_content': args['email']
            }
        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)

    printer.pprint(info_response.get_response()['GetAccountInfoResponse'])

elif args['getInfo']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetInfoRequest',
        {

        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)

    printer.pprint(info_response.get_response()['GetInfoResponse'])

elif args['getFolder']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['folder']:
        print("Paramètre manquant : folder")
        raise Exception("Paramètre manquant : folder")

    depth=1
    if args['depth']:
        depth = int(args['depth'])

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetFolderRequest',
        {
            'folder': {
                'path': args['folder']
            },
            'depth': depth
        },
        'urn:zimbraMail'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    print(json.dumps(info_response.get_response()['GetFolderResponse']['folder']))

elif args['getPrefs']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetPrefsRequest',
        {
            'pref': {
                'name': 'zimbraPrefPasswordRecoveryAddress',
            }
        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['GetPrefsResponse'])

elif args['getRights']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['right']:
        print("Paramètre manquant : right")
        raise Exception("Paramètre manquant : right")


    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetRightsRequest',
        {
            'ace': [
                {
                    'right': args['right']
                }
            ]
        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    print(json.dumps(info_response.get_response()['GetRightsResponse']))

elif args['getMsg']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['id']:
        print("Paramètre manquant : id")
        raise Exception("Paramètre manquant : id")


    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetMsgRequest',
        {
            'm': [
                {
                    'id': args['id']
                }
            ]
        },
        'urn:zimbraMail'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['GetMsgResponse'])


elif args['grantRights']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['type']:
        print("Paramètre manquant : type")
        raise Exception("Paramètre manquant : type")

    if not args['right']:
        print("Paramètre manquant : right")
        raise Exception("Paramètre manquant : right")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)

    # On commence par révoquer les droits publics (zid="99999999-9999-9999-9999-999999999999")
    info_request.add_request(
        'RevokeRightsRequest',
        {
            'ace': [
                {
                    'gt': 'pub',
                    'zid': "99999999-9999-9999-9999-999999999999",
                    'right': args['right']
                }
            ]
        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['RevokeRightsResponse'])

    # Ajout droits
    info_request = comm.gen_request(token=usr_token)
    if args['type'] == "usr":
        if not args['for']:
            print("Paramètre manquant : for")
            raise Exception("Paramètre manquant : for")

        info_request.add_request(
            'GrantRightsRequest',
            {
                'ace': [
                    {
                        'gt': args['type'],
                        'd': args['for'],
                        'right': args['right']
                    }
                ]
            },
            'urn:zimbraAccount'
        )
    else:
        if not args['domain']:
            print("Paramètre manquant : domain")
            raise Exception("Paramètre manquant : domain")

        info_request.add_request(
            'GrantRightsRequest',
            {
                'ace': [
                    {
                        'gt': args['type'],
                        'd': args['domain'],
                        'right': args['right']
                    }
                ]
            },
            'urn:zimbraAccount'
        )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['GrantRightsResponse'])

elif args['createIdentity']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['for']:
        print("Paramètre manquant : for")
        raise Exception("Paramètre manquant : for")

    if not args['id']:
        print("Paramètre manquant : id")
        raise Exception("Paramètre manquant : id")

    if not args['display']:
        print("Paramètre manquant : display")
        raise Exception("Paramètre manquant : display")


    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    # On utilise le format XML car ça marche pas en JSON pour createIdentity
    info_request = comm.gen_request(token=usr_token,request_type="xml")

    # On commence par révoquer les droits publics (zid="99999999-9999-9999-9999-999999999999")

    info_request.add_request(
        'CreateIdentityRequest',
        {
            'identity': {
                'name': args['id'],
                'a':
                    [
                        # {
                        #     'name': 'zimbraPrefIdentityName',
                        #     '_content': args['id']
                        # },
                        # {
                        #     'name': 'zimbraPrefFromDisplay',
                        #     '_content': args['display']
                        # },
                        {
                            'name': 'zimbraPrefFromAddress',
                            '_content': args['for']
                        }
                ]
            }
        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)
    #printer.pprint(info_request.get_request())

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['CreateIdentityResponse'])

elif args['modifyIdentity']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['for']:
        print("Paramètre manquant : for")
        raise Exception("Paramètre manquant : for")

    if not args['id']:
        print("Paramètre manquant : id")
        raise Exception("Paramètre manquant : id")

    if not args['display']:
        print("Paramètre manquant : display")
        raise Exception("Paramètre manquant : display")


    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token,request_type="xml")

    info_request.add_request(
        'ModifyIdentityRequest',
        {
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
        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)
    #print(str(info_request))

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['ModifyIdentityResponse'])

elif args['getIdentities']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)

    # On commence par révoquer les droits publics (zid="99999999-9999-9999-9999-999999999999")
    info_request.add_request(
        'GetIdentitiesRequest',
        {

        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)
    #print(str(info_request))

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['GetIdentitiesResponse'])

elif args['deleteIdentity']:

    if not args['email']:
        print("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['id']:
        print("Paramètre manquant : id")
        raise Exception("Paramètre manquant : id")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)

    # On commence par révoquer les droits publics (zid="99999999-9999-9999-9999-999999999999")
    info_request.add_request(
        'DeleteIdentityRequest',
        {
            'identity': {
                'name': args['id']
            }
        },
        'urn:zimbraAccount'
    )
    info_response = comm.send_request(info_request)
    #print(str(info_request))

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['DeleteIdentityResponse'])
