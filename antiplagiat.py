import functools
import re
import binascii
import hashlib


def check_error(func):
    """This decorator handles errors"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            if type(e).__name__ == "ValueError":
                return ["To compare you should write at least 2 link"]
            else:
                return ["Something strange happened"]
        return func(*args, **kwargs)

    return wrapper


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
    This function checks russian symbols in the heads
    :param flag: boolean
    :param text: list
    """
    if flag:
        for word in text:
            for russian in {'а', 'с', 'х', 'у', 'е', 'о',
                            'т', 'в', 'м', 'н', 'р', 'к'}:
                if re.search(russian, word):
                    return "russian symbols"
        return "no russian symbols"


def get_hashed_shingle(text, algorithm='crc32', shingle_length=4):
    """
    This function divides the heads into shingles
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
def compare(texts, algorithm='crc32', shingle_length=2, flag=False):
    """
    This function compares heads files and shows parameters of similarity

    :param flag: boolean, call or not check_for_cheating
    :param texts: texts of sites
    :param algorithm: str, name hash function
    :param shingle_length: int
    """
    if len(texts) < 2:
        raise ValueError
    shingles = []
    results = []
    for counter, text in enumerate(texts):
        text = delete_noise(text)
        if flag:
            results.append(f"There are {check_for_cheating(text, flag=flag)} "
                           f"in site {counter + 1}")
        shingles_from_text = get_hashed_shingle(text, algorithm=algorithm,
                                                shingle_length=shingle_length)
        shingles.append(shingles_from_text)
    results.append(f"hash function: {algorithm}\t shingles length:"
                    f" {shingle_length}")
    number = 1
    for shingles_from_chosen_text in shingles:
        for i in range(number, len(shingles)):
            count = 0
            shingles_from_another_text = shingles[i]
            for j in range(len(shingles_from_chosen_text)):
                if shingles_from_chosen_text[j] in shingles_from_another_text:
                    count += 1
            result = 2 * count / (len(shingles_from_chosen_text) +
                                  len(shingles_from_another_text)) * 100
            results.append(f"Similarity between site {number} and site {i + 1}:"
                           f" {round(result, 2)}%")
        number += 1

    return results
