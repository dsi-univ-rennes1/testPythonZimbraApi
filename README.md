# Tests de l'API Zimbra

Ce projet est prévu pour tester les fonctionnalités de l'API ZImbra.

## Bibliothèque pythonzimbra utilisée

Documentation de python-zimbra : https://github.com/Zimbra-Community/python-zimbra

## D'autres exemples de code utilisant pythonzimbra

* https://github.com/LeandroBP/zimbra/tree/fd69034cce2e8b9353d27409f419c3987d6e6330
* https://github.com/Atheloses/Troverino-droperino/blob/962ecdc0b8989baa7e555d81d73493f76d06453d/src/data/zimbraadmin.py
* https://github.com/Urumasi/Trove/blob/85ffe870fb237819b4e06c39c547d74c254bd2bf/src/data/zimbraadmin.py
* https://github.com/Alespost/zimbra_admin/blob/1245c468a249f926edb841b98dd1c931dfb32bdc/src/data/zimbraadmin.py

## Installation 

```
git clone git@github.com:salaun-urennes1/testPythonZimbraApi.git
cd testPythonZimbraApi
python3.5 -m venv venv
venv/bin/pip install --requirement requirements.txt
cp example-zimbra.json my-conf.json
vim example-zimbra.json
./testPythonZimbra.py --help
```

## Exemples d'appel

```
./testPythonZimbra.py --conf=prod-conf.json --createFolder --email=user@my.dom --folder='Quarantaine_Phishing'
./testPythonZimbra.py --conf=prod-conf.json --createIdentity --email=user@my.dom --for=user2@dom --id=New_Avatar --display='User' | jq .
./testPythonZimbra.py --conf=prod-conf.json --deleteIdentity --email=user@my.dom --id=New_Avatar| jq .
./testPythonZimbra.py --conf=prod-conf.json --getAccountInfo --email=user@my.dom | jq .
./testPythonZimbra.py --conf=prod-conf.json --getFolder --email=user@my.dom --folder='/' -depth=0
./testPythonZimbra.py --conf=prod-conf.json --getMailCount --email=user@my.dom --folder='/inbox'
./testPythonZimbra.py --conf=prod-conf.json --getIdentities --email=user@my.dom | jq .
./testPythonZimbra.py --conf=prod-conf.json --getInfo --email=user@my.dom | jq .
./testPythonZimbra.py --conf=prod-conf.json --getMsg --email=user@my.dom --id=12567
./testPythonZimbra.py --conf=prod-conf.json --getMsg --email=user@my.dom --id=12567 --part=1.2
./testPythonZimbra.py --conf=prod-conf.json --getPrefs --email=user@my.dom | jq .
./testPythonZimbra.py --conf=prod-conf.json --getRights --email=user@my.dom --right=sendAs
./testPythonZimbra.py --conf=prod-conf.json --grantAccessFolder --email=user@my.dom --id=2 --for=user2@dom.fr
./testPythonZimbra.py --conf=prod-conf.json --grantRights --right=viewFreeBusy --type=dom --domain=my.dom --email=user@my.dom | jq .
./testPythonZimbra.py --conf=prod-conf.json --modifyIdentity --email=user@my.dom --for=user2@dom --id=New_Avatar --display='User' | jq .
./testPythonZimbra.py --conf=prod-conf.json --moveMsg --email=user@my.dom --id=963827 --folder=8_Perso
./testPythonZimbra.py --conf=prod-conf.json --search --email=user@my.dom --folder=Inbox
./testPythonZimbra.py --conf=prod-conf.json --search --email=user@my.dom --query='from:user@univ-avignon.fr'
./testPythonZimbra.py --conf=prod-conf.json --search --email=user@my.dom --query='#X-Mailer:"PHPMailer 6.0.2"'
./testPythonZimbra.py --conf=prod-conf.json --search --getMsg --email=user@my.dom --id=962266
```
