import pytest
from pathlib import Path
from src.reports.report_generator import ReportGenerator
from src.models.user import User
import os

@pytest.fixture
def report_generator(tmp_path):
    return ReportGenerator(str(tmp_path))

@pytest.fixture
def sample_users():
    return [
        User(id=1, name="Test User 1", username="test1", email="test1@example.com",
             post_count=5, avg_chars=100.0),
        User(id=2, name="Test User 2", username="test2", email="test2@example.com",
             post_count=3, avg_chars=150.0)
    ]

def test_report_generator_initialization(tmp_path):
    generator = ReportGenerator(str(tmp_path))
    assert generator.output_dir == tmp_path
    assert generator.styles is not None

def test_generate_pdf_report(report_generator, sample_users):
    filename = "test_report"
    pdf_path = report_generator.generate_pdf_report(sample_users, filename)
    
    assert Path(pdf_path).exists()
    assert Path(pdf_path).suffix == ".pdf"

def test_generate_excel_report(report_generator, sample_users):
    filename = "test_report"
    excel_path = report_generator.generate_excel_report(sample_users, filename)
    
    assert Path(excel_path).exists()
    assert Path(excel_path).suffix == ".xlsx"

def test_generate_reports_empty_users(report_generator):
    with pytest.raises(ValueError):
        report_generator.generate_pdf_report([], "empty_report")

def test_generate_reports(report_generator, sample_users):
    pdf_path, excel_path = report_generator.generate_reports(sample_users, "test_report")
    
    assert Path(pdf_path).exists()
    assert Path(excel_path).exists()
    assert Path(pdf_path).suffix == ".pdf"
    assert Path(excel_path).suffix == ".xlsx"

def test_custom_styles_defined(report_generator):
    assert hasattr(report_generator, 'title_style')
    assert hasattr(report_generator, 'section_style')
    assert hasattr(report_generator, 'toc_style')
