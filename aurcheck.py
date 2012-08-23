#/usr/bin/env python3
from time import sleep
import smtplib
import requests

packages = (
    (('dmenu', 'community'), 'dmenu-dogs'),
)


def pkgbuild_ver(pkgbuild):
    lines = pkgbuild.decode('utf-8').split("\n")
    ver = None
    for line in lines:
        if line.startswith('pkgver'):
            _, ver = line.split('=')
    return ver


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
    aur_url = 'https://aur.archlinux.org/packages/{}/{}/PKGBUILD'.format(
        aurpkg[:2],
        aurpkg
    )
    aur_ver = pkgbuild_ver(requests.get(aur_url).content)
    pkg, repo = pkg
    pkg_url = ('https://projects.archlinux.org/svntogit/{}.git/plain/trunk/PKG'
        + 'BUILD?h=packages/{}').format(repo, pkg)

    pkg_ver = pkgbuild_ver(requests.get(pkg_url).content)
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

    sleep(5)
