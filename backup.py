#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
# ====================================================
# TITLE           : Mysql Database Save Manager
# DESCRIPTION     : 
# - Sauvegarde de l'ensemble des bases de données présentes sur le serveur
# - Restauration de la sauvegarde
# - Gérer la rétention des sauvegardes (fichier de config)
# - BONUS : Restaurer un backup précis avec une base de données précise
# - BONUS : Chiffrement de la sauvegarde
# AUTHORS		  : Benjamin GIRALT & Guillaume HANOTEL
# DATE            : 26/02/2018
# ====================================================

"""
QUESTIONS / INTERROGATIONS :

- tester en premier lieu si mysql est installé ?
- Laisser la possibilité de faire des saves zippés ?

"""

import subprocess
import os
import sys
import datetime
import colors
import yaml
from os.path import expanduser


# Databases are stored in : /var/lib/mysql





'''
 ==== Functions ====
'''


def alter_db():
    os.system("mysql -u root -perty appli_web -e 'UPDATE user SET user_pseudo = \"satan\" WHERE user_id = 1'")


def select_user():
    os.system("mysql -u root -perty appli_web -e 'SELECT * from user'")


def touch(path) -> None:
    """
    Crée le fichier dont le chemin est passé est paramètre
    """
    with open(path, 'a'):
        os.utime(path, None)


def clear_screen() -> None:
    """
    Efface la console
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def load_config(config_file):
    """
    Prend en paramètre le chemin du fichier de configuration ;
        si il n'existe pas, il le crée et le rempli avec des valeurs par défaut
        si il existe, test si tous les attributs sont bien remplis
    Si tout va bien, la configuration est chargée, sinon dire qu'il faut bien remplir la conf
    """
    if not os.path.exists(config_file):
        print(colors.RED + "File" + config_file + " not found"+ colors.ESCAPE)
        print(colors.CYAN + "Creating " + colors.ESCAPE + config_file + colors.CYAN + " now...\n\n" + colors.ESCAPE)
        touch(config_file)
        fill_default_config_file(config_file)
    else:
        check_config_file(config_file)

    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)
    return config


def check_config_file(config_file):
    """
    Prend en paramètre le fichier de configuration, et vérifie si les infos sont bien remplis, sinon exit
    """
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    param_to_test = [config['mysql']['user'], config['mysql']['host'], config['backup']['backup_folder']]

    # si l'un des param est vide ou si le chemin du backup folder n'existe pas
    if check_emptiness(param_to_test) or not os.path.exists(config['backup']['backup_folder']):
        print("The configuration file is incomplete or the backup folder doesn't exist, please check your parameter in " + config_file)
        sys.exit(0)


def check_emptiness(list):
    for val in list:
        if val == "" or val is None:
            return True
    return False


def fill_default_config_file(config_file) -> None:
    """
    Ouvre le fichier de configuration et le rempli avec une config par défaut
    """
    with open(config_file, 'a') as ymlfile:
        ymlfile.write("mysql:\n")
        ymlfile.write("    host: localhost\n")
        ymlfile.write("    user: root\n")
        ymlfile.write("    passwd: erty\n")
        ymlfile.write("backup:\n")
        ymlfile.write("    backup_folder: /home/vagrant/Documents/\n")


def get_date() -> str:
    """
    Fonction retournant la date du jour
    :return: formatted_date
    """
    date_now = datetime.datetime.now()
    formatted_date = str(date_now.year) + reformat_number(str(date_now.month)) + reformat_number(str(date_now.day)) + reformat_number(str(date_now.hour)) + reformat_number(str(date_now.minute)) + reformat_number(str(date_now.second))
    return formatted_date


def reformat_number(str_number) -> str:
    """
    Prend en paramètre un nombre (str), si il est inférieur à 10
    rajoute un 0 au début du str
    """
    if int(str_number) < 10:
        str_number = "0" + str_number
    return str_number


def get_list_db_names() -> list:
    """
    Retourne la liste des base de données MySQL
    """

    command = "mysql -u " + MYSQL_USER + " -p" + MYSQL_PASSWORD + " -h " + MYSQL_HOST + " -e 'show databases;'"

    # output bash to python variable
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (out, err) = process.communicate()
    output = out.decode(encoding='utf-8')

    output_db_list_raw = output.split("\n")
    output_db_list = list(filter(None, output_db_list_raw))

    unwanted_values = ['Database']
    db_name = [x for x in output_db_list if x not in unwanted_values]

    return db_name


def get_list_own_db() -> list:
    """
    Retourne la liste des base de données MySQL sans celles par défaut
    """
    full_list_db = get_list_db_names()
    unwanted_values = ['information_schema', 'mysql', 'performance_schema', 'phpmyadmin']
    list_db = [x for x in full_list_db if x not in unwanted_values]

    return list_db


def print_list_db(list_db) -> None:
    colors.print_cyan("Your databases are: \n")
    print('\t - %s' % '\n\t - '.join(map(str, list_db)))
    print("\n")


def print_versions_db(db_versions_array) -> None:
    print("The available versions for this db are :\n")
    for index in range(len(db_versions_array)):
        print('\t' + str(index) + " - " + db_versions_array[index] + '\t' + " saved at " + timestamp_to_date((db_versions_array[index])[0:14]))


def print_choice_db(db_list) -> None:
    for index in range(len(db_list)):
        print('\t' + str(index) + " - " + db_list[index])


def timestamp_to_date(date) -> str:
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    hour = date[8:10]
    minute = date[10:12]
    second = date[12:14]

    return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second


def save_db(db_name) -> None:
    """
    Sauvegarde de la base de données passée en paramètre
    """
    current_date = get_date()
    file_name = str(BACKUP_FOLDER) + str(current_date) + "-dump_" + db_name + ".sql"
    file_name_without_path = str(current_date) + "-dump_" + db_name + ".sql"
    os.system("mysqldump -u " + MYSQL_USER + " -p" + MYSQL_PASSWORD + " " + db_name + " > " + file_name)
    
    print(colors.GREEN + "\nDatabase " + colors.ESCAPE + db_name + colors.GREEN + " successfully saved in folder "+ colors.ESCAPE + colors.YELLOW + BACKUP_FOLDER + colors.ESCAPE + colors.GREEN + " under the name : " +colors.ESCAPE +  file_name_without_path +"\n")


# TODO : externaliser cette fonction dans un autre fichier
# dans cette fct, on executera l'autre fichier
def save_all_db() -> None:
    """
    Sauvegarde de toutes les bases de données
    """
    command = ['mysqldump', '-u', MYSQL_USER, '-p' + MYSQL_PASSWORD, '-h', MYSQL_HOST, '--all-databases', '--events']

    current_date = get_date()
    file_name = str(BACKUP_FOLDER) + current_date + "-dump_all_db.sql"
    file_name_without_path = current_date + "-dump_all_db.sql"

    touch(file_name)
    f = open(file_name, "w")

    return_code = subprocess.call(command, stdout=f)
    
    clear_screen()
    colors.print_cyan("Saving all your databases...\n")

    if return_code == 0:
        print(colors.GREEN + "Databases successfully saved in: " + colors.YELLOW +str(BACKUP_FOLDER) + colors.ESCAPE + colors.GREEN + " under the name : " + colors.ESCAPE + file_name_without_path)
        print(" ")
    else:
        sys.stderr.write("Error Code : " + str(return_code))
        sys.exit(1)


def restore_db(db_name, db_version) -> None:
    """
    Restauration de la base de données passée en paramètre
    """
    command = ['mysql', '-u', MYSQL_USER, '-p' + MYSQL_PASSWORD, '-h', MYSQL_HOST, db_name]

    backup_file = open(BACKUP_FOLDER+db_version)
    process = subprocess.Popen(command, stdin=backup_file)
    process.wait()
    print(colors.GREEN + "\nVersion successfully restored.\n" + colors.ESCAPE)


def restore_all_db(db_version) -> None:

    command = ['mysql', '-u', MYSQL_USER, '-p' + MYSQL_PASSWORD, '-h', MYSQL_HOST]

    backup_file = open(BACKUP_FOLDER+db_version, 'r')
    process = subprocess.Popen(command, stdin=backup_file)
    process.wait()
    print(colors.GREEN + "\nVersion successfully restored.\n" + colors.ESCAPE)


def choose_db() -> str:
    db_list = get_list_own_db()

    while True:

        colors.print_cyan("Your databases are : \n")

        print_choice_db(db_list)

        db_choice = input(colors.CYAN +"\nEnter the number matching the database your want to save:"+ colors.ESCAPE +"\n> ")

        if db_choice.isdigit():
            db_choice = int(db_choice)
            if 0 <= db_choice < len(db_list):
                break
            else:
                print("Invalid index")
        else:
            print("Invalid index, please enter a valid index")

    db_chosen = str(db_list[db_choice])
    print(colors.CYAN + "\nYou selected database : " + colors.ESCAPE + db_chosen)
    return db_chosen


def choose_version(array_all_versions_db) -> str:

    while True:
        print_choice_db(array_all_versions_db)
        version_choice = input(colors.CYAN + "\nPlease select enter the number matching the database you want to restore : \n" + colors.ESCAPE + "> ")

        if version_choice.isdigit():
            version_choice = int(version_choice)
            if 0 <= version_choice < len(array_all_versions_db):
                break
            else:
                print("Invalid index")
        else:
            print("Invalid index, please enter a valid index")

    version_chosen = str(array_all_versions_db[version_choice])
    print(colors.CYAN + "\nYou selected version : " + colors.ESCAPE + version_chosen)
    return version_chosen


def get_list_db_versions(db_chosen="dump_all_db"):
    # define the ls command
    ls = subprocess.Popen(["ls", "-p", BACKUP_FOLDER],
                          stdout=subprocess.PIPE,
                          )

    # define the grep command
    grep = subprocess.Popen(["grep", db_chosen+'.sql'],
                            stdin=ls.stdout,
                            stdout=subprocess.PIPE,
                            )

    # read from the end of the pipe (stdout)
    endOfPipe = grep.stdout

    str_all_versions_db = ""

    # output the files line by line
    for line in endOfPipe:
        str_all_versions_db = str_all_versions_db + line.decode('utf-8')

    # split de str_all_versions_db
    if str_all_versions_db == "":
        print("No backup found. Please make one already !")
        sys.exit(1)
    else:
        array_all_versions_db_raw = str_all_versions_db.split('\n')
        array_all_versions_db = list(filter(None, array_all_versions_db_raw))

    print(colors.CYAN + "\nVersions of : " + colors.ESCAPE + db_chosen + "\n")
    return array_all_versions_db


def process_user_choice(user_choice) -> None:
    clear_screen()

    # List databases
    if user_choice == 1:

        print(colors.VIOLET + "LIST OF YOUR DATABASES\n" + colors.ESCAPE)
        list_db = get_list_own_db()
        print_list_db(list_db)

    # Save all databases
    elif user_choice == 2:

        print(colors.VIOLET + "SAVE ALL YOUR DATABASES\n" + colors.ESCAPE)
        save_all_db()

    # Restore all databases
    elif user_choice == 3:

        print(colors.VIOLET + "SAVE ALL YOUR DATABASES\n" + colors.ESCAPE)
        array_all_versions_db = get_list_db_versions()
        version_chosen = choose_version(array_all_versions_db)
        restore_all_db(version_chosen)

    # Save a single database
    elif user_choice == 4:

        print(colors.VIOLET + "SAVE A SINGLE DATABASE\n" + colors.ESCAPE)
        db_chosen = choose_db()
        save_db(db_chosen)

    # Restore a single database
    elif user_choice == 5:

        print(colors.VIOLET + "RESTORE ALL YOUR DATABASES\n" + colors.ESCAPE)
        db_chosen = choose_db()
        array_all_versions_db = get_list_db_versions(db_chosen)
        version_chosen = choose_version(array_all_versions_db)
        restore_db(db_chosen, version_chosen)

    elif user_choice == 6:
        exit(0)

    else:
        sys.stderr.write("Error : Undefined choice\n")
        sys.exit(1)







'''
 ==== MAIN ====
'''


def main():

    print("Welcome to the database management program.\n")
    colors.print_cyan("Please enter a number matching your choice :\n")

    print("\t[1] =>" + colors.YELLOW + " List" + colors.ESCAPE +" your databases")
    print("\n\t[2] =>" + colors.YELLOW +" Save all" + colors.ESCAPE +" your databases")
    print("\t[3] =>" + colors.YELLOW + " Restore all"+ colors.ESCAPE + " your databases")

    print("\n\t[4] =>" + colors.YELLOW +  " Save a single" + colors.ESCAPE + " database")
    print("\t[5] =>" + colors.YELLOW +  " Restore a single" + colors.ESCAPE + " database")

    print("\n\t[6] =>" +colors.YELLOW + " Exit\n\n" + colors.ESCAPE)

    try:
        user_choice = int(input(colors.CYAN + "Enter your choice: " + colors.ESCAPE + "\n > "))
    except ValueError:
        sys.stderr.write("Error : Undefined choice\n")
        sys.exit(1)

    process_user_choice(user_choice)



'''
INSTALLATION PY YAML

tar zxvf PyYAML-3.12.tar.gz 
sudo chown -R $USER /usr/local/lib/python3.4
python3 setup.py install
http://pyyaml.org/wiki/PyYAML
'''

'''
 ==== Constantes ====  
'''
home = expanduser("~")
config_file = home+"/.backup_db_config.yml"

clear_screen()
config = load_config(config_file)


MYSQL_USER = config['mysql']['user']
MYSQL_PASSWORD = config['mysql']['passwd']
MYSQL_HOST = config['mysql']['host']
BACKUP_FOLDER = config['backup']['backup_folder']

try:
    main()
except KeyboardInterrupt:
    print('Process Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        sys.exit(0)




'''
Voulez-vous programmez une sauvegarde automatique de l'ensemble des BDD ?
est-ce que vous voulez dans un intervalle de :
- minutes
- heures
- jours
- semaines
- mois

dans quel intervalle de (m/h/j/s/m) voulez vous executer la save ?

Combien de sauvegarde max voulez vous garder ? 
# Faire la diff entre save manu et save auto pour éliminer le surplus ?


-> remplir la conf avec l'attribut NB_MAX_SAVE

-> écrire dans la crontab l'execution de l'autre fichier save all


'''