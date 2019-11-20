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


printer = pprint.PrettyPrinter(indent=4)

# Configuration des paramètres d'appel
epilog = "Exemples d'appel :\n" + \
    "./testPythonZimbra.py --conf=ur1-prod-zimbra.json --getMailCount --email=p-salaun@univ-rennes1.fr --folder='/inbox'\n" +\
    "./testPythonZimbra.py --conf=ur1-prod-zimbra.json --getFolder --email=p-salaun@univ-rennes1.fr --folder='/'\n" +\
    "./testPythonZimbra.py --conf=ur1-prod-zimbra.json --grantAccessFolder --email=p-salaun@univ-rennes1.fr --id=2 --for=olivier.salaun@univ-rennes1.fr\n"

parser = argparse.ArgumentParser(description="Exploitation des boîtes mail sur la plateforme Partage", epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--conf', required=True, metavar='ur1-prod-zimbra.json', help="fichier de configuration JSON")
parser.add_argument('--email', metavar='jean.kermarrec@univ-rennes1.fr', help="adrese email de l'utilisateur")
parser.add_argument('--for', metavar='anne.guernic@univ-rennes1.fr', help="adrese email de l'autre utilisateur")
parser.add_argument('--folder', metavar='/inbox', help="dossier de l'utilisateur")
parser.add_argument('--id', metavar='2', help="Identifiant d'un objet (dossier)")
parser.add_argument('--getMailCount', action='store_const', const=True, help="Nombre de mails dans un dossier")
parser.add_argument('--getFolder', action='store_const', const=True, help="Infos sur un dossier mail")
parser.add_argument('--getAccountInfo', action='store_const', const=True, help="Retourne les infos sur un compte")
parser.add_argument('--grantAccessFolder', action='store_const', const=True, help="Donne accès à un dossier")


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
        logger.error("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['for']:
        logger.error("Paramètre manquant : for")
        raise Exception("Paramètre manquant : for")

    if not args['id']:
        logger.error("Paramètre manquant : id")
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


## FIXME getAccountInfo ne fonctionne pas
elif args['getAccountInfo']:

    if not args['email']:
        logger.error("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetAccountRequest',
        {
            'account': {
                'by': 'name',
                '_content': args['email']
            }
        },
        'urn:zimbraAdmin'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)

    printer.pprint(info_response.get_response()['GetAccountResponse'])

elif args['getFolder']:

    if not args['email']:
        logger.error("Paramètre manquant : email")
        raise Exception("Paramètre manquant : email")

    if not args['folder']:
        logger.error("Paramètre manquant : folder")
        raise Exception("Paramètre manquant : folder")

    (comm, usr_token) = zimbra_auth(conf['soap_service_url'], conf['preauth_key'], args['email'])

    info_request = comm.gen_request(token=usr_token)
    info_request.add_request(
        'GetFolderRequest',
        {
            'folder': {
                'path': args['folder']
            }
        },
        'urn:zimbraMail'
    )
    info_response = comm.send_request(info_request)

    if info_response.is_fault():
        print("Erreur %s : %s" % (info_response.is_fault(), info_response.get_fault_message()))
        exit(-1)
    printer.pprint(info_response.get_response()['GetFolderResponse']['folder'])
