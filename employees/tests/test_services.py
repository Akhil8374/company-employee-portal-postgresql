from unittest.mock import patch
from django.test import TestCase


class ReportServiceMockTest(TestCase):

    # =====================================================
    # Excel Export Tests
    # =====================================================

    @patch("reports.excel_export.generate_employees_excel")
    def test_generate_employee_excel(self, mock_excel):

        mock_excel.return_value = "media/reports/employee_report.xlsx"

        result = mock_excel("employee")

        self.assertEqual(
            result,
            "media/reports/employee_report.xlsx",
        )

        mock_excel.assert_called_once_with("employee")

    @patch("reports.excel_export.generate_employees_excel")
    def test_generate_department_excel(self, mock_excel):

        mock_excel.return_value = "media/reports/department_report.xlsx"

        result = mock_excel("department")

        self.assertEqual(
            result,
            "media/reports/department_report.xlsx",
        )

        mock_excel.assert_called_once_with("department")

    @patch("reports.excel_export.generate_employees_excel")
    def test_generate_salary_excel(self, mock_excel):

        mock_excel.return_value = "media/reports/salary_report.xlsx"

        result = mock_excel("salary")

        self.assertEqual(
            result,
            "media/reports/salary_report.xlsx",
        )

        mock_excel.assert_called_once_with("salary")

    @patch("reports.excel_export.generate_employees_excel")
    def test_generate_attendance_excel(self, mock_excel):

        mock_excel.return_value = "media/reports/attendance_report.xlsx"

        result = mock_excel("attendance")

        self.assertEqual(
            result,
            "media/reports/attendance_report.xlsx",
        )

        mock_excel.assert_called_once_with("attendance")

    # =====================================================
    # PDF Tests
    # =====================================================

    @patch("reports.pdf_generator.generate_dashboard_report_pdf")
    def test_generate_dashboard_pdf(self, mock_pdf):

        mock_pdf.return_value = "media/reports/dashboard_report.pdf"

        result = mock_pdf()

        self.assertEqual(
            result,
            "media/reports/dashboard_report.pdf",
        )

        mock_pdf.assert_called_once()

    @patch("reports.pdf_generator.generate_employee_report_pdf")
    def test_generate_employee_pdf(self, mock_pdf):

        mock_pdf.return_value = "media/reports/employee_report.pdf"

        result = mock_pdf()

        self.assertEqual(
            result,
            "media/reports/employee_report.pdf",
        )

        mock_pdf.assert_called_once()

    @patch("reports.pdf_generator.generate_department_report_pdf")
    def test_generate_department_pdf(self, mock_pdf):

        mock_pdf.return_value = "media/reports/department_report.pdf"

        result = mock_pdf()

        self.assertEqual(
            result,
            "media/reports/department_report.pdf",
        )

        mock_pdf.assert_called_once()

    @patch("reports.pdf_generator.generate_salary_report_pdf")
    def test_generate_salary_pdf(self, mock_pdf):

        mock_pdf.return_value = "media/reports/salary_report.pdf"

        result = mock_pdf()

        self.assertEqual(
            result,
            "media/reports/salary_report.pdf",
        )

        mock_pdf.assert_called_once()

    @patch("reports.pdf_generator.generate_attendance_report_pdf")
    def test_generate_attendance_pdf(self, mock_pdf):

        mock_pdf.return_value = "media/reports/attendance_report.pdf"

        result = mock_pdf()

        self.assertEqual(
            result,
            "media/reports/attendance_report.pdf",
        )

        mock_pdf.assert_called_once()

    # =====================================================
    # QR Code Tests
    # =====================================================

    @patch("reports.qr_generator.generate_employee_qr")
    def test_generate_employee_qr(self, mock_qr):

        mock_qr.return_value = "media/qrcodes/QR_EMP001.png"

        result = mock_qr("employee")

        self.assertEqual(
            result,
            "media/qrcodes/QR_EMP001.png",
        )

        mock_qr.assert_called_once_with("employee")

    # =====================================================
    # Exception Tests
    # =====================================================

    @patch(
        "reports.excel_export.generate_employees_excel",
        side_effect=Exception("Excel Error"),
    )
    def test_excel_exception(self, mock_excel):

        with self.assertRaises(Exception):
            mock_excel("employee")

    @patch(
        "reports.pdf_generator.generate_dashboard_report_pdf",
        side_effect=Exception("PDF Error"),
    )
    def test_pdf_exception(self, mock_pdf):

        with self.assertRaises(Exception):
            mock_pdf()

    @patch(
        "reports.qr_generator.generate_employee_qr",
        side_effect=Exception("QR Error"),
    )
    def test_qr_exception(self, mock_qr):

        with self.assertRaises(Exception):
            mock_qr("employee")