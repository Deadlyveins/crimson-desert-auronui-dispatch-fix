"""Basic format/guardrail tests: use synthetic bytes, no real save fixtures."""
import unittest
import auronui_reset as fixer

class SafetyTests(unittest.TestCase):
    def test_bad_header_rejected(self):
        with self.assertRaises(ValueError):
            fixer.decode_save(b'not a save')
    def test_invalid_key_version_rejected(self):
        with self.assertRaises(ValueError):
            fixer.save_key(999)
    def test_missing_operation_rejected_stage1(self):
        with self.assertRaises(ValueError):
            fixer.locate_auronui_field(b'\x00' * 512)
    def test_missing_operation_rejected_stage2(self):
        with self.assertRaises(ValueError):
            fixer.locate_stage2_field(b'\x00' * 512)

if __name__ == '__main__':
    unittest.main()
