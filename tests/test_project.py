import copy, importlib.util, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import project, cad

class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.floor={'floor_id':'8F','coordinate_unit':'mm','geometry_status':'verified','site_status':'verified',
                    'world_to_svg':[1,0,0,-1,0,100],'source_drawing_sha256':'test-hash',
                    'calibration':{'status':'verified','evidence':['x-dimension','y-dimension']}}
        self.point={'point_id':'TEST-ONLY-8F-WF02-001','floor_id':'8F','template_code':'WF-02','template_revision':'V1.0',
                    'status':'proposed','quantity':1,'faces':2,'unit':'piece','position_world':{'x':1200,'y':3400},
                    'facing_degrees':90,'source_drawing_sha256':'test-hash','evidence':['synthetic-test-only']}
        self.templates={('WF-02','V1.0'):{}}
    def errors(self,p=None,f=None): return project.check_point(p or self.point,{'8F':f or self.floor},self.templates,ROOT)
    def test_real_package_integrity(self): self.assertTrue(project.validate()['passed'])
    def test_proposed_synthetic_point(self): self.assertEqual(self.errors(),[])
    def test_uncalibrated_point_blocked(self):
        f=copy.deepcopy(self.floor);f['calibration']['status']='pending';self.assertTrue(self.errors(f=f))
    def test_header_is_not_geometry(self):
        f=copy.deepcopy(self.floor);f['geometry_status']='header_only';self.assertTrue(self.errors(f=f))
    def test_bad_transform(self):
        f=copy.deepcopy(self.floor);f['world_to_svg']=[0,0,0,0,0,0];self.assertTrue(self.errors(f=f))
    def test_one_calibration_is_not_enough(self):
        f=copy.deepcopy(self.floor);f['calibration']['evidence']=['x'];self.assertTrue(self.errors(f=f))
    def test_source_revision_mismatch(self):
        p=copy.deepcopy(self.point);p['source_drawing_sha256']='another';self.assertTrue(self.errors(p=p))
    def test_nonfinite_coordinates(self):
        p=copy.deepcopy(self.point);p['position_world']['x']=float('nan');self.assertTrue(self.errors(p=p))
    def test_unknown_template(self):
        p=copy.deepcopy(self.point);p['template_code']='UNKNOWN';self.assertTrue(self.errors(p=p))
    def test_units_not_mixed(self):
        p=copy.deepcopy(self.point);p['unit']='meter';self.assertTrue(self.errors(p=p))
    def test_no_approval_without_evidence(self):
        p=copy.deepcopy(self.point);p['status']='approved';self.assertTrue(self.errors(p=p))
    def test_double_sided_sign_is_one_piece(self):
        r=project.summarize_quantities([self.point],'proposal')[0]
        self.assertEqual(r['physical_signs'],1);self.assertEqual(r['printed_faces'],2)
    def test_proposals_not_approved_quantities(self): self.assertEqual(project.summarize_quantities([self.point],'approved'),[])
    def test_empty_does_not_become_zero_boq(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): project.quantity_export(ROOT,Path(d)/'boq.csv','proposal')
    def test_paths_cannot_escape(self):
        with self.assertRaises(ValueError): project.safe_path(ROOT,'../../etc/passwd')
    def test_dwg_report_does_not_invent_floors(self):
        p=ROOT/'inputs/cad/新厂房平面图（改）.dwg';r=cad.inspect_header(p)
        self.assertEqual(r['header_ascii'],'AC1018');self.assertIsNone(r['floor_count']);self.assertFalse(r['geometry_decoded'])
    def test_converter_does_not_overwrite_source(self):
        p=ROOT/'inputs/cad/新厂房平面图（改）.dwg'
        with self.assertRaises(ValueError): cad.protect_output(p,p)

@unittest.skipUnless(importlib.util.find_spec('ezdxf'),'Optional ezdxf not installed')
class DxfSyntheticTests(unittest.TestCase):
    def test_inventory_synthetic_dxf(self):
        import ezdxf
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.dxf';doc=ezdxf.new('R2018');doc.units=4
            doc.modelspace().add_line((0,0),(1000,0));doc.modelspace().add_text('SYNTHETIC FLOOR TITLE')
            doc.saveas(p);r=cad.inventory_dxf(p)
            self.assertEqual(r['insunits_raw'],4);self.assertIsNone(r['floor_count']);self.assertFalse(r['units_verified'])
            self.assertEqual(next(x for x in r['layouts'] if x['name']=='Model')['total'],2)
    def test_render_synthetic_is_still_preview(self):
        import ezdxf
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.dxf';out=Path(d)/'preview.svg';doc=ezdxf.new('R2018')
            doc.modelspace().add_line((0,0),(1000,500));doc.saveas(p)
            r=cad.render_layout(p,out,'Model');self.assertEqual(r['status'],'preview_only');self.assertIsNone(r['world_to_svg'])
            self.assertTrue(out.is_file())

if __name__=='__main__': unittest.main()
