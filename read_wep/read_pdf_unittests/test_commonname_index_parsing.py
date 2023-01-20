import unittest

from pkg_resources import resource_filename

from read_wep.parse_common_name_index import latin_common_names_from_index

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_common_names(self):
        common_name_df = latin_common_names_from_index('index_common_names.csv')
        with_common_name = ['Ziziphus mauritiana', 'Ziziphus jujuba',
                            'Zephyranthes rosea',
                            'Xylorhiza venusta', 'Yucca gloriosa', 'Woodfordia fruticosa',
                            'Xanthium spinosum',
                            'Welwitschia mirabilis']
        without_common_name = ['Yushania microphylla', 'Yushania microphylla (Munro) R. B. Majumdar',
                               'Vitis wilsonae hort. Veitch ex anon.', 'Vitex doniana', 'Sedum goldmanii']

        unresolved_df = common_name_df[common_name_df['matched_by'].isna()]
        self.assertEqual(len(unresolved_df.index), 0, msg=unresolved_df)
        for m in with_common_name:
            print(m)
            self.assertTrue(m in common_name_df['accepted_name'].values or m in common_name_df['name'].values)

        for nm in without_common_name:
            self.assertNotIn(nm, common_name_df['name'].values)

        common_names = {'babosilla': ['Modiola caroliniana', 'Sida acuta']}


if __name__ == '__main__':
    unittest.main()
