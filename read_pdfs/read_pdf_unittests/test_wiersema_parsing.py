import unittest

import pandas as pd
from pkg_resources import resource_filename

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_known_records(self):
        medicinal = ['Aconitum bisma (Buch.-Ham.) Rapaics  ', 'Aconitum brachypodum', 'Aconitum carmichaelii',
                     'Aconitum columbianum', 'Cucumis sativus', 'Cucumis melo', 'Zea mays subsp. mays',
                     'Breynia spatulifolia']
        not_medicinal = ['Aconitum ×cammarum', 'Aconitum ×cammarum L.  ', 'Cucumis metulifer',
                         'Cucumis myriocarpus', 'Satranala decussilvae', 'Clinopodium grandiflorum',
                         'Breynia androgyna', 'Zoysia japonica']

        # med_df = get_traditional_medicines_from_wiersema('trad_medicines.csv')

        med_df = pd.read_csv('trad_medicines.csv')
        unresolved_df = med_df[med_df['matched_by'].isna()]
        self.assertEqual(len(unresolved_df.index), 0, msg=unresolved_df)
        for m in medicinal:
            print(m)
            self.assertTrue(m in med_df['accepted_name'].values or m in med_df['name'].values)

        for nm in not_medicinal:
            self.assertNotIn(nm, med_df['name'].values)

        # poison_df = poisons_from_wiersema('poisons.csv')
        poison_df = pd.read_csv('poisons.csv')
        unresolved_df = poison_df[poison_df['matched_by'].isna()]
        self.assertEqual(len(unresolved_df.index), 0, msg=unresolved_df)

        poisonous = ['Acacia confusa', 'Pimelea curviflora', 'Pimelea flava', 'Ulmus minor subsp. minor',
                     'Ulmus glabra']
        not_poisonous = ['Pilocarpus microphyllus', 'Uncaria gambir', 'Ulmus parvifolia',
                         'Ulmus × hollandica', 'Ulmus fulva']
        for p in poisonous:
            self.assertIn(p, poison_df['accepted_name'].values)

        for np in not_poisonous:
            self.assertNotIn(np, poison_df['name'].values)


if __name__ == '__main__':
    unittest.main()
