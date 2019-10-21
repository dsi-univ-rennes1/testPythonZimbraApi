# Tests de l'API Zimbra

Ce projet est prévu pour tester les fonctionnalités de l'API ZImbra.

## Bibliothèque pythonzimbra utilisée

La documentation : https://github.com/Zimbra-Community/python-zimbra

## D'autres exemples de code utilisant pythonzimbra

* https://github.com/LeandroBP/zimbra/tree/fd69034cce2e8b9353d27409f419c3987d6e6330
* https://github.com/Atheloses/Troverino-droperino/blob/962ecdc0b8989baa7e555d81d73493f76d06453d/src/data/zimbraadmin.py
* https://github.com/Urumasi/Trove/blob/85ffe870fb237819b4e06c39c547d74c254bd2bf/src/data/zimbraadmin.py
* https://github.com/Alespost/zimbra_admin/blob/1245c468a249f926edb841b98dd1c931dfb32bdc/src/data/zimbraadmin.py

## Exemples d'appel

Partage le dossier Inbos avec un autre compte : `./testPythonZimbra.py --conf=ur1-prod-zimbra.json --grantAccessFolder --email=p-salaun@univ-rennes1.fr --id=2 --for=olivier.salaun@univ-rennes1.fr`