import os
import subprocess


def take_pic():
    process = subprocess.Popen(['bash', 'image_cap.sh'], stdout=open(os.devnull, 'wb'))
    process.communicate()


def take_pics(num, name):
    name_folder = ("./images/train/" + name)
    for i in range(num):
        process = subprocess.Popen(['bash', 'image_cap_norename.sh', name_folder], stdout=open(os.devnull, 'wb'))
        process.communicate()


if __name__ == '__main__':
    take_pic()
