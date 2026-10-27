"""Unit tests for role classifier in scraper.categories (supports both pytest and unittest)."""
import unittest
from scraper.categories import categorize


class TestCategories(unittest.TestCase):
    def test_tech_roles(self):
        cases = [
            ("Software Engineering Intern", "Software"),
            ("SDE Intern - Summer 2027", "Software"),
            ("MTS 1 Intern", "Software"),
            ("Full Stack Developer Intern", "Software"),
            ("2027 Technology Program Intern", "Software"),
            ("Graduate Engineer Trainee - SWE", "Software"),
            ("Machine Learning Research Intern", "AI/ML"),
            ("AI Engineer Intern - GenAI", "AI/ML"),
            ("Computer Vision Intern", "AI/ML"),
            ("Deep Learning Scientist Intern", "AI/ML"),
            ("Applied Scientist Intern", "AI/ML"),
            ("Data Science Intern", "Data"),
            ("Data Engineer Intern", "Data"),
            ("Business Intelligence Engineer Intern", "Data"),
            ("Silicon Design Engineering Intern", "Hardware/Silicon"),
            ("VLSI Verification Intern", "Hardware/Silicon"),
            ("ASIC Hardware Intern", "Hardware/Silicon"),
            ("FPGA Engineer Intern", "Hardware/Silicon"),
            ("Android Developer Intern", "Mobile"),
            ("iOS Application Engineer Intern", "Mobile"),
            ("Flutter Mobile Intern", "Mobile"),
            ("Frontend Web Engineer Intern", "Frontend"),
            ("UI Engineer Intern (React / TypeScript)", "Frontend"),
            ("Backend Systems Intern", "Backend/Infra"),
            ("Cloud Infrastructure Intern", "Backend/Infra"),
            ("Site Reliability Engineering (SRE) Intern", "Backend/Infra"),
            ("DevOps Engineering Intern", "Backend/Infra"),
            ("Quality Assurance (QA) Intern", "QA"),
            ("SDET Intern", "QA"),
            ("Software Test Engineering Intern", "QA"),
            ("Cybersecurity Operations Intern", "Security"),
            ("Application Security (AppSec) Intern", "Security"),
            ("Vulnerability Assessment & Penetration Testing Intern", "Security"),
        ]
        for title, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(categorize(title), expected)

    def test_out_of_scope_roles(self):
        out_of_scope = [
            "Sales & Business Development Intern",
            "HR Talent Acquisition Intern",
            "Finance & Accounting Intern",
            "Legal Counsel Intern",
            "Marketing & Social Media Intern",
            "Operations & Supply Chain Intern",
            "Warehouse Logistics Intern",
            "Civil Engineering Construction Intern",
            "Mechanical Technician Intern",
        ]
        for title in out_of_scope:
            with self.subTest(title=title):
                self.assertIsNone(categorize(title))

    def test_empty_and_none(self):
        self.assertIsNone(categorize(""))
        self.assertIsNone(categorize(None))


if __name__ == "__main__":
    unittest.main()
