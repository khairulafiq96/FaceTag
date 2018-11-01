from os import listdir, rename

from os.path import join


def rename_file(_dir):
    # Get the file name from folder
    lists = listdir(_dir)
    # Rename the folder name
    for each in lists:
        old_folder_path = join(_dir, each)
        new_folder_path = join(_dir, each.replace('.', ''))
        new_folder_path = join(_dir, each.replace(' ', '_'))

        rename(old_folder_path, new_folder_path)
    for each in lists:

        name_list = listdir(join(_dir, each))
        count = 0
        for name in name_list:
            if len(str(count)) == 1:
                number = '000'+str(count)
            elif len(str(count)) == 2:
                number = '00'+str(count)
            elif len(str(count)) == 3:
                number = '0'+str(count)
            else:
                number = str(count)
            old_path = join(_dir, each, name)
            new_path = join(_dir, each, each+"_"+number)

            rename(old_path, new_path)
            count += 1

    lists_after = listdir(_dir)


if __name__ == '__main__':
    _dir = './data'
    rename_file(_dir)
