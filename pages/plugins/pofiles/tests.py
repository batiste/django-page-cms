from pages.tests.testcase import TestCase
from pages.plugins.pofiles.utils import export_po_files

class PoTests(TestCase):

    def test_po_file_imoprt_export(self):
        """Test the po files export and import."""
        try:
            import polib
        except ImportError:
            raise unittest.SkipTest("Polib is not installed")

        page1 = self.new_page(content={'slug':'page1', 'title':'english title'})
        page1.save()
        #Content(page=page1, language='en-us', type='title', body='toto').save()
        Content(page=page1, language='fr-ch', type='title', body='french title').save()
        page1.invalidate()

        import io
        stdout = io.StringIO()

        # TODO: might be nice to use a temp dir for this test
        export_po_files(path='potests', stdout=stdout)
        self.assertTrue("Export language fr-ch" in stdout.getvalue())

        f = open("potests/fr-ch.po", "r+")
        old = f.read().replace('french title', 'translated')
        f.seek(0)
        f.write(old)
        f.close()

        stdout = io.StringIO()
        import_po_files(path='potests', stdout=stdout)

        self.assertTrue("Update language fr-ch" in stdout.getvalue())
        self.assertTrue(("Update page %d" % page1.id) in stdout.getvalue())
        self.assertTrue(page1.title(language='fr-ch'), 'translated')