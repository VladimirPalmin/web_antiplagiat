import unittest
import antiplagiat
import parsing


class TestAntiplagiat(unittest.TestCase):
    def test_list(self):
        self.texts = [['a', 'b', 'v'], ['a', 'b', 'v']]
        self.assertIsInstance((antiplagiat.compare(self.texts), list))

    def test_one_text(self):
        self.text = [['a', 'b', 'v']]
        self.result = ["To compare you should write at least 2 link"]
        self.assertEqual(antiplagiat.compare(self.text), self.result)

    def test_same_texts(self):
        self.texts = [['a', 'b', 'v'], ['a', 'b', 'v']]
        results = ["hash function: crc32\t shingles length: 2",
                   "Similarity between site 1 and site 2: 100.0%"]
        self.assertEqual(antiplagiat.compare(self.texts), results)

    def test_several_texts(self):
        self.texts = [['a', 'b', 'v'], ['a', 'b', 'v'], ['a', 'b', 'v']]
        results = ["hash function: crc32\t shingles length: 2",
                   "Similarity between site 1 and site 2: 100.0%",
                   "Similarity between site 1 and site 3: 100.0%",
                   "Similarity between site 2 and site 3: 100.0%"]
        self.assertEqual(antiplagiat.compare(self.texts), results)

    def test_cheating(self):
        self.texts = [['a', 'b', 'v'], ['а', 'b', 'v']]
        self.results_0 = f"There are no russian symbols in site 1"
        self.results_1 = f"There are russian symbols in site 2"
        self.assertEqual(antiplagiat.compare(self.texts, flag=True)[0],
                         self.results_0)
        self.assertEqual(antiplagiat.compare(self.texts, flag=True)[1],
                         self.results_1)

    def test_noise(self):
        self.text = ['a', 'an', 'the', 'this', 'that',
                     'in', 'on', 'at', 'by', 'from',
                     'to', 'and', 'but', 'for', 'of', 'or', 'as',
                     'is', 'am', 'are', 'was', 'were', 'been']
        self.result = ['be']*6
        self.assertEqual(antiplagiat.delete_noise(self.text), self.result)

    def test_grammar(self):
        self.assertEqual(antiplagiat.check_grammar('yes'), 'yes')
        self.assertEqual(antiplagiat.check_grammar('kisses'), 'kiss')
        self.assertEqual(antiplagiat.check_grammar('goes'), 'go')
        self.assertEqual(antiplagiat.check_grammar('flies'), 'fly')
        self.assertEqual(antiplagiat.check_grammar('cosmos'), 'cosmo')
        self.assertEqual(antiplagiat.check_grammar('classes'), 'class')
        self.assertEqual(antiplagiat.check_grammar('class'), 'clas')


class TestParsing(unittest.TestCase):
    def test_list(self):
        self.url = ["https://www.bbc.com/news/world-europe-52510545"]
        self.assertIsInstance(parsing.parsing(self.url), list)

    def test_size(self):
        self.url = ["https://www.bbc.com/news/world-europe-52510545",
                    "https://www.bbc.com/news/world-europe-52510545"]
        self.assertEqual(len(parsing.parsing(self.url)), 2)
