import subprocess


def listen():
    subprocess.call(['rec rec.wav rate 32k silence 1 0.1 5% 1 1.0 5%'], shell=True)


if __name__ == '__main__':
    print(listen())
