from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from openpyxl import Workbook

from nadejda_94_django.glasses.forms import GlassUpdateForm
from nadejda_94_django.glasses.importing import parse_glass_kind
from nadejda_94_django.glasses.models import Record
from nadejda_94_django.glasses.views import ImportGlassView


class GlassImportTests(SimpleTestCase):
    def test_parse_panes(self):
        cases = [
            ('40 4/4/K', ('40', '4', '4', 'K')),
            ('40 4/4/К', ('40', '4', '4', 'K')),
            (' 40  4 / 4 / К ', ('40', '4', '4', 'K')),
            ('40\t4/4/ K', ('40', '4', '4', 'K')),
            ('24 4/К', ('24', '4', 'K', None)),
            ('40 4S/4/6_К', ('40', '4S', '4', '6_К')),
            ('24 т. зел./4', ('24', 'т. зел.', '4', None)),
            ('4 4', ('4', '4', None, None)),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(parse_glass_kind(value), expected)

    def test_first_imported_triple_pane_remains_selected_in_edit_form(self):
        workbook = Workbook()
        for row, kind in enumerate(('40 4/4/ К', '40 4/4/K'), start=6):
            for column, value in {1: kind, 3: 500, 4: 600, 6: 'module_1', 7: 2, 11: 50}.items():
                workbook.active.cell(row, column, value)
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)
        view = ImportGlassView()
        view.kwargs = {'record_pk': 1}
        form = SimpleNamespace(cleaned_data={'excel_file': excel_file})

        with patch.object(view, 'get_context_data', return_value={}), \
                patch('nadejda_94_django.glasses.views.Record.objects.get',
                      return_value=Record(pk=1)), \
                patch('nadejda_94_django.glasses.views.Glasses.objects.bulk_create') as create, \
                patch('nadejda_94_django.glasses.views.redirect'):
            view.form_valid(form)

        orders = create.call_args.args[0]
        self.assertEqual(len(orders), 2)
        for order in orders:
            self.assertEqual(order.third_glass, 'K')
            field = GlassUpdateForm(instance=order)['third_glass']
            self.assertIn('value="K" selected', str(field))
