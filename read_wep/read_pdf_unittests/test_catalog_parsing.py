import unittest

import pandas as pd
from pkg_resources import resource_filename

from read_wep import get_commonnames_from_catalog, get_traditional_medicines_from_wiersema, \
    poisons_from_wiersema

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

        med_df = get_traditional_medicines_from_wiersema('wiersema_medic_folklore.csv')

        # med_df = pd.read_csv('wiersema_medic_folklore.csv')
        unresolved_df = med_df[med_df['matched_by'].isna()]
        self.assertEqual(len(unresolved_df.index), 0, msg=unresolved_df)
        for m in medicinal:
            print(m)
            self.assertTrue(m in med_df['accepted_name'].values or m in med_df['name'].values)

        for nm in not_medicinal:
            for given_name in med_df['name'].values:
                self.assertNotIn(nm, given_name)

        poison_df = poisons_from_wiersema('wiersema_poisonous_plants.csv')
        # poison_df = pd.read_csv('wiersema_poisonous_plants.csv')
        unresolved_df = poison_df[poison_df['matched_by'].isna()]
        self.assertEqual(len(unresolved_df.index), 0, msg=unresolved_df)

        poisonous = ['Acacia confusa', 'Pimelea curviflora', 'Pimelea flava', 'Ulmus minor subsp. minor',
                     'Ulmus glabra']
        not_poisonous = ['Pilocarpus microphyllus', 'Uncaria gambir', 'Ulmus parvifolia',
                         'Ulmus × hollandica', 'Ulmus fulva']
        for p in poisonous:
            self.assertIn(p, poison_df['accepted_name'].values)

        for np in not_poisonous:
            for given_name in poison_df['name'].values:
                self.assertNotIn(np, given_name)

    def test_common_names(self):
        common_name_df = get_commonnames_from_catalog('catalog_common_names.csv')
        # common_name_df = pd.read_csv('catalog_common_names.csv')

        with_common_name = ['Ziziphus mauritiana',
                            'Zephyranthes rosea',
                            'Xylorhiza venusta', 'Yucca gloriosa', 'Woodfordia fruticosa',
                            'Xanthium spinosum',
                            'Welwitschia mirabilis']
        without_common_name = ['Yushania microphylla', 'Yushania microphylla (Munro) R. B. Majumdar',
                               'Vitis wilsonae hort. Veitch ex anon.  ', 'Vitex doniana', 'Sedum goldmanii']

        unresolved_df = common_name_df[common_name_df['matched_by'].isna()]
        self.assertEqual(len(unresolved_df.index), 0, msg=unresolved_df)
        for m in with_common_name:
            print(m)
            self.assertTrue(m in common_name_df['accepted_name'].values or m in common_name_df['name'].values)

        for nm in without_common_name:
            for given_name in common_name_df['name'].values:
                self.assertNotIn(nm, given_name)


if __name__ == '__main__':
    unittest.main()
