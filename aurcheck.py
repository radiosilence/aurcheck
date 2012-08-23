#/usr/bin/env python3
from time import sleep
import json
import smtplib
import requests

INTERVAL = 60*5

ARCH = 'x86_64'

REPO_URL = 'https://www.archlinux.org/packages/{1}/{2}/{0}/json/'
AUR_URL = 'https://aur.archlinux.org/rpc.php?type=info&arg={0}'

packages = (
    (('dmenu', 'community'), 'dmenu-dogs'),
)


def get_ver(package, repo=None):
    if repo:
        return json.loads(requests.get(REPO_URL.format(
            package,
            repo,
            ARCH
        )).content.decode('utf-8'))['pkgver']
    else:
        return json.loads(requests.get(AUR_URL.format(
            package
        )).content.decode('utf-8'))['results']['Version'].split('-')[0]


def ver_greater(a, b):
    a = a.split('.')
    b = b.split('.')
    i = 0
    for point in a:
        try:
            if int(point) > int(b[i]):
                return True
        except IndexError:
            return True
        i += 1
    return False


def send_email(msg):
    s = smtplib.SMTP('localhost', 25)
    sender = 'test@localhost'
    receivers = ['jamescleveland@gmail.com']
    message = ("From: {0}\n"
        + "To: {1}\n"
        + "Subject: {2}\n"
        + "\n"
        + "{2}\n").format(
            sender,
            receivers[0],
            msg
        )

    s.sendmail(sender, receivers, message)


def check(pkg, aurpkg):
    aur_ver = get_ver(aurpkg)
    pkg, repo = pkg
    pkg_ver = get_ver(pkg, repo=repo)
    if ver_greater(pkg_ver, aur_ver):
        return True, '{} version ({}) is > AUR {} version ({})'.format(
            pkg,
            pkg_ver,
            aurpkg,
            aur_ver
        )
    else:
        return False, '{} version ({}) is <= to AUR {} version ({})'.format(
            pkg,
            pkg_ver,
            aurpkg,
            aur_ver
        )

while True:
    print("checking for update")
    for pkg, aurpkg in packages:
        gt, msg = check(pkg, aurpkg)
        print(msg)
        if gt:
            send_email(msg)

    sleep(INTERVAL)
