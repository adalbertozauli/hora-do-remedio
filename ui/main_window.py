import os
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.medication import Medication, REVIEW_LABEL, VALID_PERIODS
from services.doc_reader import extract_text_from_docx
from services.config_service import save_openai_key, user_env_path
from services.medication_parser import medications_to_json, parse_medications_json
from services.openai_service import MissingOpenAIKeyError, structure_prescription_text
from services.pdf_generator import export_medications_pdf
from ui.styles import APP_STYLE
from utils.horario_mapper import normalize_horarios
from utils.patient_extractor import extract_patient_name


class AIInterpretationWorker(QObject):
    finished = Signal(object)
    failed = Signal(str, str)

    def __init__(self, extracted_text: str) -> None:
        super().__init__()
        self.extracted_text = extracted_text

    @Slot()
    def run(self) -> None:
        try:
            raw_json = structure_prescription_text(self.extracted_text)
            medications = parse_medications_json(raw_json)
            self.finished.emit(medications)
        except MissingOpenAIKeyError as exc:
            self.failed.emit("missing_key", str(exc))
        except Exception as exc:
            self.failed.emit("generic", str(exc))


class MainWindow(QMainWindow):
    HEADERS = ["Medicamento", "Dose", "Posologia original", "Cedo", "Tarde", "Noite", "Observações"]

    def __init__(self) -> None:
        super().__init__()
        self.medications: list[Medication] = []
        self.current_docx_path: str | None = None
        self.patient_name = ""
        self.ai_thread: QThread | None = None
        self.ai_worker: AIInterpretationWorker | None = None

        self.setWindowTitle("Hora do Remédio")
        self.resize(1200, 780)
        self.setStyleSheet(APP_STYLE)

        self.import_button = QPushButton("Importar receita .docx")
        self.api_key_button = QPushButton("Configurar chave da API")
        self.copy_button = QPushButton("Copiar resultado")
        self.export_button = QPushButton("Exportar PDF")

        self.ai_status_label = QLabel("A IA está analisando a receita...")
        self.ai_status_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #1f4e79;")
        self.ai_status_label.hide()
        self.ai_progress_bar = QProgressBar()
        self.ai_progress_bar.setRange(0, 0)
        self.ai_progress_bar.setTextVisible(False)
        self.ai_progress_bar.setFixedHeight(16)
        self.ai_progress_bar.hide()

        self.patient_input = QLineEdit()
        self.patient_input.setPlaceholderText("Nome do paciente")
        self.patient_input.setMinimumHeight(42)

        self.text_view = QTextEdit()
        self.text_view.setPlaceholderText("O texto extraído da receita aparecerá aqui.")
        self.text_view.setMinimumHeight(220)

        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(95)
        self.table.itemChanged.connect(self._sync_from_table)

        self._build_layout()
        self._connect_actions()
        self.statusBar().showMessage("Pronto.")

    def _build_layout(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 12)
        layout.setSpacing(14)

        title = QLabel("Hora do Remédio")
        title.setStyleSheet("font-size: 28px; font-weight: 800;")
        layout.addWidget(title)

        actions = QHBoxLayout()
        actions.setSpacing(12)
        actions.addWidget(self.import_button)
        actions.addWidget(self.api_key_button)
        actions.addWidget(self.copy_button)
        actions.addWidget(self.export_button)
        actions.addStretch()
        layout.addLayout(actions)

        patient_row = QHBoxLayout()
        patient_row.setSpacing(10)
        patient_row.addWidget(QLabel("Paciente"))
        patient_row.addWidget(self.patient_input, 1)
        layout.addLayout(patient_row)

        ai_status_row = QVBoxLayout()
        ai_status_row.setSpacing(6)
        ai_status_row.addWidget(self.ai_status_label)
        ai_status_row.addWidget(self.ai_progress_bar)
        layout.addLayout(ai_status_row)

        splitter = QSplitter(Qt.Vertical)

        text_panel = QWidget()
        text_layout = QVBoxLayout(text_panel)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.addWidget(QLabel("Texto extraído"))
        text_layout.addWidget(self.text_view)

        table_panel = QWidget()
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.addWidget(QLabel("Tabela de medicações"))
        table_layout.addWidget(self.table)

        splitter.addWidget(text_panel)
        splitter.addWidget(table_panel)
        splitter.setSizes([280, 440])
        layout.addWidget(splitter, 1)

        self.setCentralWidget(root)

    def _connect_actions(self) -> None:
        self.import_button.clicked.connect(self.import_docx)
        self.api_key_button.clicked.connect(self.configure_api_key)
        self.copy_button.clicked.connect(self.copy_result)
        self.export_button.clicked.connect(self.export_pdf)

    def configure_api_key(self) -> None:
        api_key, ok = QInputDialog.getText(
            self,
            "Configurar chave da API",
            "Cole a chave da OpenAI:",
            QLineEdit.Password,
        )
        if not ok:
            return
        if not api_key.strip():
            QMessageBox.warning(self, "Chave vazia", "Informe uma chave da OpenAI para salvar.")
            return

        env_path = save_openai_key(api_key)
        QMessageBox.information(
            self,
            "Chave salva",
            f"A chave foi salva com sucesso.\n\nArquivo de configuração:\n{env_path}",
        )

    def import_docx(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar receita médica",
            "",
            "Documentos Word (*.docx)",
        )
        if not file_path:
            return

        self._set_busy(True, "Lendo documento...")
        try:
            self.current_docx_path = file_path
            extracted_text = extract_text_from_docx(file_path)
            self.patient_name = extract_patient_name(extracted_text)
            self.patient_input.setText(self.patient_name)
        except Exception as exc:
            self._set_busy(False)
            self.statusBar().showMessage("Não foi possível ler o documento.")
            QMessageBox.critical(self, "Erro ao ler documento", str(exc))
            return

        self.text_view.setPlainText(extracted_text)
        self._start_ai_interpretation(extracted_text)

    def _start_ai_interpretation(self, extracted_text: str) -> None:
        self._set_busy(True, "Interpretando receita com a IA...")
        self._show_ai_status()

        self.ai_thread = QThread(self)
        self.ai_worker = AIInterpretationWorker(extracted_text)
        self.ai_worker.moveToThread(self.ai_thread)

        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_worker.finished.connect(self._on_ai_finished)
        self.ai_worker.failed.connect(self._on_ai_failed)
        self.ai_worker.finished.connect(self.ai_thread.quit)
        self.ai_worker.failed.connect(self.ai_thread.quit)
        self.ai_thread.finished.connect(self.ai_worker.deleteLater)
        self.ai_thread.finished.connect(self._cleanup_ai_thread)
        self.ai_thread.start()

    def _show_ai_status(self) -> None:
        self.ai_status_label.show()
        self.ai_progress_bar.show()

    @Slot(object)
    def _on_ai_finished(self, medications: list[Medication]) -> None:
        self.medications = medications
        self._populate_table()
        self.statusBar().showMessage("Receita importada. Revise a tabela antes de exportar.")
        self._hide_ai_status()
        self._set_busy(False)

    @Slot(str, str)
    def _on_ai_failed(self, error_kind: str, message: str) -> None:
        self._hide_ai_status()
        self._set_busy(False)

        if error_kind == "missing_key":
            self.medications = []
            self.table.setRowCount(0)
            self.statusBar().showMessage("Texto extraído. Configure a chave da OpenAI para preencher a tabela.")
            QMessageBox.information(self, "Configurar OpenAI", message)
            return

        self.statusBar().showMessage("Texto extraído, mas a interpretação automática falhou.")
        QMessageBox.critical(
            self,
            "Erro ao interpretar receita",
            f"O texto foi extraído, mas não foi possível preencher a tabela automaticamente.\n\n{message}",
        )

    def _hide_ai_status(self) -> None:
        self.ai_status_label.hide()
        self.ai_progress_bar.hide()

    def _cleanup_ai_thread(self) -> None:
        self.ai_thread = None
        self.ai_worker = None

    def copy_result(self) -> None:
        self._sync_from_table()
        if not self.medications:
            QMessageBox.information(self, "Nada para copiar", "Importe uma receita ou preencha a tabela primeiro.")
            return

        QGuiApplication.clipboard().setText(medications_to_json(self.medications))
        self.statusBar().showMessage("Resultado copiado para a área de transferência.")

    def export_pdf(self) -> None:
        self._sync_from_table()
        if not self.medications:
            QMessageBox.information(self, "Nada para exportar", "Importe uma receita ou preencha a tabela primeiro.")
            return

        default_name = "hora_do_remedio.pdf"
        if self.current_docx_path:
            default_name = f"{Path(self.current_docx_path).stem}_hora_do_remedio.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar PDF",
            str(Path.cwd() / "outputs" / default_name),
            "PDF (*.pdf)",
        )
        if not file_path:
            return

        try:
            pdf_path = Path(file_path)
            if pdf_path.suffix.lower() != ".pdf":
                pdf_path = pdf_path.with_suffix(".pdf")
            self.patient_name = (
                self.patient_input.text().strip()
                or extract_patient_name(self.text_view.toPlainText())
                or self.patient_name
            )
            self.patient_input.setText(self.patient_name)
            export_medications_pdf(str(pdf_path), self.medications, self.patient_name)
            self.statusBar().showMessage("PDF exportado com sucesso.")
            try:
                os.startfile(str(pdf_path))
            except OSError:
                self.statusBar().showMessage("PDF exportado, mas não foi possível abrir automaticamente.")
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Information)
            message.setWindowTitle("PDF exportado")
            message.setText("O PDF foi gerado com sucesso.")
            message.setStandardButtons(QMessageBox.Ok)
            message.button(QMessageBox.Ok).setText("Fechar")
            message.exec()
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao exportar PDF", str(exc))

    def _populate_table(self) -> None:
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.medications))
        for row, medication in enumerate(self.medications):
            values = [
                medication.medicamento,
                medication.dose,
                medication.posologia_original,
                medication.period_text("cedo"),
                medication.period_text("tarde"),
                medication.period_text("noite"),
                medication.observacoes,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                if column in (3, 4, 5, 6):
                    font = QFont(item.font())
                    font.setBold(True)
                    item.setFont(font)
                if column in (3, 4, 5):
                    item.setTextAlignment(Qt.AlignCenter)
                if medication.needs_review:
                    item.setBackground(Qt.GlobalColor.yellow)
                self.table.setItem(row, column, item)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, max(self.table.columnWidth(0), 180))
        self.table.setColumnWidth(1, max(self.table.columnWidth(1), 130))
        self.table.setColumnWidth(2, max(self.table.columnWidth(2), 260))
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 110)
        self.table.resizeRowsToContents()
        self.table.blockSignals(False)

    def _sync_from_table(self) -> None:
        medications: list[Medication] = []
        for row in range(self.table.rowCount()):
            horarios, period_doses = self._period_data_from_row(row)
            med = Medication(
                medicamento=self._cell(row, 0),
                dose=self._cell(row, 1),
                posologia_original=self._cell(row, 2),
                horarios=horarios,
                observacoes=self._cell(row, 6),
                period_doses=period_doses,
            )
            if not med.horarios:
                med.horarios = normalize_horarios([], med.posologia_original)
            medications.append(med)
        self.medications = medications

    def _period_data_from_row(self, row: int) -> tuple[list[str], dict[str, str]]:
        periods = []
        period_doses = {}
        for index, period in enumerate(VALID_PERIODS, start=3):
            value = self._cell(row, index).strip()
            normalized = value.lower()
            if value and normalized not in ("não", "nao", "-", "0"):
                periods.append(period)
                if normalized not in ("sim", "x", "ok", "1", "✓"):
                    period_doses[period] = value
        observation = self._cell(row, 6).lower()
        if not periods and REVIEW_LABEL in observation:
            return [REVIEW_LABEL], {}
        return periods, period_doses

    def _cell(self, row: int, column: int) -> str:
        item = self.table.item(row, column)
        return item.text().strip() if item else ""

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        for button in (self.import_button, self.api_key_button, self.copy_button, self.export_button):
            button.setDisabled(busy)
        if message:
            self.statusBar().showMessage(message)
        QGuiApplication.processEvents()
