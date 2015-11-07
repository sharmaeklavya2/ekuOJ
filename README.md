# ekuOJ

This is an online judge for competitive programming. It is written in python 3.4 and django 1.8. It uses [sharmaeklavya2/OJL3](https://github.com/sharmaeklavya2/OJL3). It can run on Unix-like systems only.

## Setting up

To set up this online judge, you will need

1. Python 3.4 (I might run on lower python 3 versions as well; I haven't tried that)
2. Django 1.8
3. [sharmaeklavya2/OJL3](https://github.com/sharmaeklavya2/OJL3)
4. [ochko/safeexec](https://github.com/ochko/safeexec)

Steps to build:

1. First get safeexec and build it.
2. Then get sharmaeklavya2/OJL3 and set it up by following the instructions in its README.
3. Add a symlink to OJL3 in ekuOJ's root directory.
4. Add a symlink to `OJ_data` (`OJ_data` is explained in OJL3's readme) in ekuOJ's root directory
5. From ekuOJ's root directory, run `python3 manage.py makemigrations` and then `python3 manage.py migrate`

ekuOJ is now set up. Run `python3 manage.py runserver` to run ekuOJ on django's development server.
