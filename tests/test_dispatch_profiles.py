"""Tests use constructed dummy payloads, not players' personal save data."""
import importlib.util
import struct
import sys
import tempfile
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('auronui_reset', ROOT / 'auronui_reset.py')
patcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = patcher
SPEC.loader.exec_module(patcher)


def fixture(profile=(2, 2, 2), record_size=64, progress=121.5):
    op = 200
    data = bytearray(500)
    data[op-51:op-49] = b'\x5b\x42'
    data[op-47] = 0x92 if record_size == 64 else 0x90
    data[op-27:op-17] = bytes.fromhex('003e460f00003e460f00')
    template = patcher.KNOWN_RECORD_TEMPLATE
    core = bytearray(template if record_size == 64 else template[:32] + template[40:])
    for i,kind in zip((8,16,24),profile):
        struct.pack_into('<I',core,i,kind)
    for i,tag in zip((4,12,20),(0x12345678,0x12345678,0x98765432)):
        struct.pack_into('<I',core,i,tag)
    struct.pack_into('<f',core,28,progress)
    data[op:op+record_size] = core
    data[op+record_size:op+record_size+16] = b'\x01\x00\x00\x00' + b'\xff'*8 + b'\x00'*4
    return bytes(data)


class TestAuronuiProfiles(unittest.TestCase):
    def test_known_profiles_detected_without_special_cases(self):
        for profile in sorted(patcher.KNOWN_METADATA_PROFILES):
            for size in (56,64):
                with self.subTest(profile=profile, size=size):
                    match = patcher.locate_auronui_record(fixture(profile,size))
                    self.assertEqual(match.metadata_profile, profile)
                    self.assertTrue(match.previously_tested_profile)
                    self.assertEqual(match.record_size,size)

    def test_unseen_profiles_recognized_but_flagged_as_untested(self):
        for profile in ((2, 3, 5), (5, 5, 5), (7, 8, 9), (255, 1, 255)):
            match = patcher.locate_auronui_record(fixture(profile, 64))
            self.assertFalse(match.previously_tested_profile)
            self.assertEqual(match.metadata_profile,profile)

    def test_zero_and_out_of_range_rejected(self):
        for profile in ((0,1,1),(1,256,1),(4294967295,1,1)):
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                patcher.locate_auronui_record(fixture(profile))

    def test_structural_corruptions_rejected(self):
        original = fixture()
        for i in (149, 173, 200+32, 200+45, 200+55, 200+64+4):
            bad = bytearray(original)
            bad[i] ^= 0x01
            with self.subTest(i=i), self.assertRaises(ValueError):
                patcher.locate_auronui_record(bytes(bad))

    def test_nonfinite_progress_rejected(self):
        for value in (float('nan'), float('inf'), float('-inf')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                patcher.locate_auronui_record(fixture(progress=value))

    def test_stage2_edits_are_reversible_for_both_layouts(self):
        for size in (56,64):
            for profile in ((1,1,1), (4,4,5), (2,3,5)):
                with self.subTest(size=size, profile=profile):
                    payload = fixture(profile,size)
                    match = patcher.locate_stage2_field(payload)
                    edited = patcher.apply_stage2(payload,match)
                    self.assertEqual(len(edited),len(payload))
                    self.assertNotEqual(edited,payload)

    def test_unknown_profile_needs_extra_opt_in_even_with_yes(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'sample.save'
            header = bytearray(patcher.HEADER_SIZE)
            header[:4] = b'SAVE'
            struct.pack_into('<H',header,4,2)
            blob = patcher.encode_save(bytes(header),fixture((5,5,5)),2)
            p.write_bytes(blob)
            for flags, expected in ((['--stage','1','--check'],0),(['--stage','1','--yes'],1)):
                proc = subprocess.run([sys.executable,str(ROOT/'auronui_reset.py'),str(p),*flags],
                                      input='',capture_output=True,text=True,timeout=30)
                self.assertEqual(proc.returncode,expected,proc.stderr)
                self.assertEqual(p.read_bytes(),blob)
                self.assertEqual(list(Path(td).glob('*')),[p])
            proc = subprocess.run([sys.executable,str(ROOT/'auronui_reset.py'),str(p),
                                    '--stage','1','--yes','--allow-untested-profile'],
                                  input='UNTESTED\n',capture_output=True,text=True,timeout=30)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(p.read_bytes(),blob)
            output = list(Path(td).glob('*STAGE1*.save'))
            self.assertEqual(len(output),1)
            raw,_ = patcher.decode_save(output[0].read_bytes())
            self.assertEqual(patcher.locate_auronui_record(raw).field_value,0.0)

    def test_combined_in_memory_for_known_and_unseen_profiles(self):
        for size in (56, 64):
            for profile in ((1,1,1), (3,3,3), (4,4,5), (3,4,5), (255,1,255)):
                with self.subTest(size=size, profile=profile):
                    raw = fixture(profile, size, progress=876.54)
                    before = patcher.locate_auronui_field(raw)
                    first = patcher.make_stage1_patch(raw, before)
                    second_match = patcher.locate_stage2_field(first)
                    expected = patcher.apply_stage2(first, second_match)
                    self.assertEqual(patcher.make_combined_patch(raw, before), expected)
                    self.assertEqual(len(raw), len(expected))
                    self.assertNotEqual(raw, expected)
                    self.assertEqual(raw[before.op_pos + 32:], expected[before.op_pos + 32:])

    def test_cli_combined_known_profile_and_backup(self):
        for size in (56, 64):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as td:
                p = Path(td) / 'sample.save'
                header = bytearray(patcher.HEADER_SIZE)
                header[:4] = b'SAVE'; struct.pack_into('<H',header,4,2)
                raw = fixture((3,3,3), size, 247.1)
                src = patcher.encode_save(bytes(header),raw,2)
                p.write_bytes(src)
                proc = subprocess.run([sys.executable,str(ROOT/'auronui_reset.py'),str(p),'--yes'],
                                      input='',capture_output=True,text=True,timeout=30)
                self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
                self.assertEqual(p.read_bytes(),src)
                outputs = list(Path(td).glob('*_AURONUI_COMBINED_*.save'))
                backups = list(Path(td).glob('*.bak'))
                self.assertEqual(len(outputs),1)
                self.assertEqual(len(backups),1)
                self.assertEqual(backups[0].read_bytes(), src)
                out,version = patcher.decode_save(outputs[0].read_bytes())
                self.assertEqual(version,2)
                self.assertEqual(out,patcher.make_combined_patch(raw,patcher.locate_auronui_record(raw)))

    def test_cli_combined_unknown_profile_requires_interactive_opt_in(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'sample.save'
            header = bytearray(patcher.HEADER_SIZE)
            header[:4] = b'SAVE'; struct.pack_into('<H',header,4,2)
            blob = patcher.encode_save(bytes(header),fixture((3,4,5)),2)
            p.write_bytes(blob)
            proc = subprocess.run([sys.executable,str(ROOT/'auronui_reset.py'),str(p),'--yes'],
                                  input='NO\n',capture_output=True,text=True,timeout=30)
            self.assertEqual(proc.returncode,2,proc.stderr)
            self.assertEqual(list(Path(td).iterdir()),[p])
            proc = subprocess.run([sys.executable,str(ROOT/'auronui_reset.py'),str(p)],
                                  input='UNTESTED\nFIX\n',capture_output=True,text=True,timeout=30)
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
            self.assertEqual(p.read_bytes(),blob)
            self.assertEqual(len(list(Path(td).glob('*_AURONUI_COMBINED_*.save'))),1)

    def test_cli_combined_zero_progress_refuses_noop(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'sample.save'
            header = bytearray(patcher.HEADER_SIZE)
            header[:4] = b'SAVE'; struct.pack_into('<H',header,4,2)
            src=patcher.encode_save(bytes(header),fixture(progress=0.0),2)
            p.write_bytes(src)
            proc = subprocess.run([sys.executable,str(ROOT/'auronui_reset.py'),str(p),'--yes'],
                                  capture_output=True,text=True,timeout=30)
            self.assertEqual(proc.returncode,2,proc.stderr)
            self.assertEqual(list(Path(td).iterdir()),[p])
            self.assertEqual(p.read_bytes(),src)

    def test_stage2_requires_ingame_confirmation(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'sample.save'
            header=bytearray(patcher.HEADER_SIZE)
            header[:4]=b'SAVE';struct.pack_into('<H',header,4,2)
            p.write_bytes(patcher.encode_save(bytes(header),fixture(),2))
            proc = subprocess.run([sys.executable,str(ROOT/'auronui_reset.py'),str(p),'--stage','2','--yes'],
                                  capture_output=True,text=True,timeout=30)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('--after-ingame-resave',proc.stderr)
            self.assertEqual(len(list(Path(td).iterdir())),1)

if __name__=='__main__': unittest.main()
