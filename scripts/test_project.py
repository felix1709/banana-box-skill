# -*- coding: utf-8 -*-
"""project.py 单元测试（用 --dir 指向临时目录）。"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import project


class TestProject(unittest.TestCase):
    def test_init_creates_project_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            project.init_project(tmp, "p1", "project", r"C:\refs")
            rec = project.load_records(tmp)
            self.assertEqual(rec["projects"]["p1"]["mode"], "project")
            self.assertEqual(rec["projects"]["p1"]["lib"], r"C:\refs")

    def test_init_duplicate_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            project.init_project(tmp, "p1", "concept", "")
            with self.assertRaises(ValueError):
                project.init_project(tmp, "p1", "concept", "")

    def test_add_frame_and_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            project.init_project(tmp, "p1", "concept", "")
            project.add_frame(tmp, "p1", "f1", "C:/p/f1.md")
            frames = project.list_frames(tmp, "p1")
            self.assertEqual(len(frames), 1)
            self.assertEqual(frames[0]["name"], "f1")

    def test_list_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            project.init_project(tmp, "p1", "concept", "")
            project.init_project(tmp, "p2", "project", "")
            names = project.list_projects(tmp)
            self.assertEqual(set(names), {"p1", "p2"})


if __name__ == "__main__":
    unittest.main()