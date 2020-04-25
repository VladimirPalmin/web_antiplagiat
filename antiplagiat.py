import functools
import re
import binascii
import hashlib
import PySimpleGUI as sg
import webbrowser
import fitz


def check_error(func):
    """This decorator handles errors"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            if type(e).__name__ == "FileNotFoundError":
                print("Oops, I can't find your file")
            elif type(e).__name__ == "TypeError":
                print("I can't read it. Please, use txt or pdf format")
            elif type(e).__name__ == "ZeroDivisionError":
                print("The number of words in the file must be greater than "
                      "the shingles length")
            else:
                print(type(e).__name__)

    return wrapper


def get_text(link):
    """
    This function writes file.text (only txt and pdf) into list without
    any punctuation marks
    :param link: str
    :return: list of words in a file
    """
    if link[-3:] == 'txt':
        text_file = open(link, encoding='utf-8')
        text = text_file.read()
        text = text.lower()
        text = re.split(r'\W+', text)  # split the string into words, remove
        # punctuation marks
        text.pop()  # delete last empty item
        text_file.close()
        return text

    if link[-3:] == 'pdf':
        doc = fitz.open(link)
        text = []
        for i in range(doc.pageCount):
            page = doc.loadPage(i)
            page_text = page.getText("text")
            page_text = page_text.lower()
            page_text = re.split(r'\W+', page_text)
            page_text.pop()
            text += page_text
        return text


def check_grammar(word):
    """
    This function converts plural to singular
    :param word: str
    :return: str
    """
    if len(word) > 2:
        if word[-1] == 's':
            if word[-2] == 'e':
                if word[-3] == 'i':
                    word = word[0:-3] + 'y'  # convert ies to y
                elif word[-3] == 'y':  # don't change yes
                    pass
                else:
                    word = word[0:-2]  # delete 'es'
            else:
                word = word[0:-1]  # delete 's'
    return word


def delete_noise(text):
    """
    This function deletes all noises like articles, prepositions
    and converts different forms of be to be
    :param text: list
    :return: list
    """
    noises = {'a', 'an', 'the', 'this', 'that',
              'in', 'on', 'at', 'by', 'from',
              'to', 'and', 'but', 'for', 'of', 'or', 'as'}
    test_text = (word for word in text if word not in noises)
    clear_text = []
    for word in test_text:
        if word in {'is', 'am', 'are', 'was', 'were',
                    'been'}:  # convert different forms of be to be
            word = 'be'
        word = check_grammar(word)
        clear_text.append(word)

    return clear_text


def check_for_cheating(text, flag=False):
    """
    This function checks russian symbols in the text
    :param flag: boolean
    :param text: list
    """
    if flag:
        stop = False
        for word in text:
            for russian in {'а', 'с', 'х', 'у', 'е', 'о',
                            'т', 'в', 'м', 'н', 'р', 'к'}:
                if re.search(russian, word):
                    print("Bad guy, don't use russian symbols")
                    stop = True
                    break
            if stop:
                break


def get_hashed_shingle(text, algorithm='crc32', shingle_length=4):
    """
    This function divides the text into shingles
     and calculate check sums with CRC32
    :param text: list
    :param algorithm: str, name of hash function
    :param shingle_length: int, shingle length from 3 to 10, the shorter the
    length, the more accurate the test result
    :return: list
    """
    shingles_check_sum = []  # list of shingles
    for i in range(len(text) - shingle_length + 1):
        shingle = text[i: i + shingle_length]
        string_shingle = ' '.join(shingle)
        if algorithm == 'crc32':
            shingles_check_sum.append(
                binascii.crc32(string_shingle.encode('utf-8')))
        if algorithm == 'sha1':
            hash_object = hashlib.sha1(string_shingle.encode('utf-8'))
            shingles_check_sum.append(hash_object.hexdigest())
        if algorithm == 'md5':
            hash_object = hashlib.md5(string_shingle.encode('utf-8'))
            shingles_check_sum.append(hash_object.hexdigest())
    return shingles_check_sum


@check_error
def compare(links, algorithm, shingle_length, flag):
    """
    This function compares text files and shows parameters of similarity

    :param flag: boolean, call or not check_for_cheating
    :param links: list of links to files
    :param algorithm: str, name hash function
    :param shingle_length: int
    """
    shingles = []
    for link in links:
        text = delete_noise(get_text(link))
        check_for_cheating(text, flag=flag)
        shingles_from_text = get_hashed_shingle(text, algorithm=algorithm,
                                                shingle_length=shingle_length)
        shingles.append(shingles_from_text)
    count = 0
    for i in range(len(shingles[0])):
        if shingles[0][i] in shingles[1]:
            count += 1

    result = 2 * count / (len(shingles[0]) + len(shingles[1])) * 100
    print(f"hash function: {algorithm}\t shingles length: {shingle_length}")
    print(f"Similarity between text 1 and text 2: {round(result, 2)}%\n")


@check_error
def dialog():
    """
    This function is to start a dialogue with a user
    """
    sg.theme('DarkTeal9')

    # ------ Menu Definition ------ #
    menu_def = [['&Help', '&About...'], ]

    layout = [
        [sg.Menu(menu_def, tearoff=True)],
        [sg.Frame(layout=[
            [sg.Checkbox('CRC32', default=True, key='crc32'),
             sg.Checkbox('SHA1', key='sha1'),
             sg.Checkbox('MD5', key='md5'),
             sg.Text('hash function', font=('Helvetica 12')),
             ],
            [sg.Slider(range=(1, 10), orientation='h', default_value=4,
                       font=('Helvetica 12'), key='slider'),
             sg.Text('shingles length', font=('Helvetica 12'))],
            [sg.Checkbox('Check russian symbols',
                         font=('Helvetica 12'),  key='rus')]],
            title='Options', relief=sg.RELIEF_SUNKEN,
            tooltip='Use these to customize the comparison')],
        [sg.Text('File 1'), sg.InputText('File Link', key='link1'),
         sg.FileBrowse()],
        [sg.Text('File 2'), sg.InputText('File Link', key='link2'),
         sg.FileBrowse()],
        [sg.Output(size=(50, 20))],
        [sg.Submit(tooltip='Click to submit this form'), sg.Cancel()]]

    window = sg.Window('Antiplagiat', layout, default_element_size=(40, 1))

    # Event Loop
    while True:
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
            break
        if event == 'About...':
            print("About shingle algorithm, you can read this:")
            print("https://en.wikipedia.org/wiki/W-shingling")
            print("About hash functions, you can read this:")
            print("https://en.wikipedia.org/wiki/Hash_function")
            webbrowser.open("https://en.wikipedia.org/wiki/Plagiarism")

        if event == 'Submit':
            if not (values['crc32'] or values['sha1'] or values['md5']):
                print('You should choose at least 1 hash function')
            else:
                algorithm = []
                if values['crc32']:
                    algorithm.append('crc32')
                if values['sha1']:
                    algorithm.append('sha1')
                if values['md5']:
                    algorithm.append('md5')
                for alg in algorithm:
                    compare([values['link1'], values['link2']],
                            flag=values['rus'], algorithm=alg,
                            shingle_length=int(values['slider']))

    window.close()


if __name__ == '__main__':
    dialog()
