# -*- coding: utf-8 -*-

"""GUI process feature module

Reusable Qt widgets and helpers shared across the PARUS GUIs: table cells, subprocess execution with a
linked console, busy dialogs, and file/path selection utilities.
"""

import sys
import os
import re
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets
import warnings

__package__ = 'parus.gui'
__name__ = 'parus.gui.elm_proc'
from . import cs_dark

__all__ = ['CellCheckbox', 'CellData', 'PyScriptExec', 'ProcConsole', 'ProgBusyDialog',
           'path_selector', 'table_loader', 'selection_operator']
"""
Public class list:

- CellCheckbox(identifier, checked, func)                    : Table-cell checkbox widget
- CellData(val, size, aln, emp, clr, bkg, ro)                : Styled data-table cell item
- PyScriptExec(script, console, trigger, ...)                : Run a Python script as a subprocess with console output
- ProcConsole(console, btn_clr, btn_cpy, btn_scr, ...)       : Console-control combo for subprocess output
- ProgBusyDialog(parent, message, bar)                       : Non-interactive, application-modal busy dialog

Public function list:

- path_selector(line, mode, caption, flt, parent)            : Open a file/folder selection dialog
- table_loader(table, record, select, mode, caption, ...)    : Append selected paths/files to a table widget
- selection_operator(select, mode)                           : Bulk select/deselect/invert table-item checkboxes
"""


# Classes ------------------------------------------------------------------------------------------------------------ #

class CellCheckbox(QtWidgets.QWidget):
    """Centred checkbox widget for embedding inside a :class:`~PySide6.QtWidgets.QTableWidget` cell."""

    def __init__(self, identifier=None, checked=True, func=None):
        """Build the checkbox, set its initial state, and connect an optional click handler.

        Args:
            identifier: Free-form identifier attached to the instance for caller-side bookkeeping
            checked (bool): Initial checked status (default: ``True``)
            func (callable | None): Slot connected to the underlying checkbox's ``clicked`` signal (default: ``None``)
        """
        super(CellCheckbox, self).__init__()
        # Initialize a pre-checked checkbox
        self.chkbox = QtWidgets.QCheckBox()
        self.chkbox.setChecked(checked)
        self.id = identifier
        # Link function
        if func is not None:
            self.chkbox.clicked.connect(func)
        # Set layout
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.chkbox)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def isChecked(self):
        """Return checked status of checkbox."""
        return self.chkbox.isChecked()

    def setChecked(self, status: bool):
        """Set checked status of checkbox."""
        self.chkbox.setChecked(status)
        return status


class CellData(QtWidgets.QTableWidgetItem):
    """Styled :class:`~PySide6.QtWidgets.QTableWidgetItem` for the PARUS data-selection tables."""

    def __init__(self, val, size=None, aln='c', emp=None, clr=None, bkg=None, ro=False):
        """Build the cell with the given value, alignment, font emphasis, colours, and editability flag.

        Args:
            val: Value to display; converted to :class:`str` when not already a string
            size (int | None): Text point size; pass :data:`None` to keep the default (default: ``None``)
            aln (str): Alignment method; one of ``{'c', 'l', 'r'}`` (default: ``'c'``)
            emp (str | None): Text emphasis flags; combination of ``'b'`` (bold) and ``'i'`` (italic);
                pass :data:`None` for plain text (default: ``None``)
            clr (tuple[int, int, int] | None): RGB foreground colour; pass :data:`None` for the default
                (default: ``None``)
            bkg (tuple[int, int, int] | None): RGB background colour; pass :data:`None` for the default
                (default: ``None``)
            ro (bool): When :data:`True`, the cell is read-only (default: ``False``)
        """
        super(CellData, self).__init__()
        # Set cell text
        txt = val if isinstance(val, str) else str(val)
        self.setText(txt)
        font = self.font()
        # Set text size
        if size is not None:
            font.setPointSize(size)
        # Set text emphasize method
        if emp is not None:
            if 'b' in emp:
                font.setBold(True)
            if 'i' in emp:
                font.setItalic(True)
        # Set font
        self.setFont(font)
        # Set text colour
        if clr is not None:
            self.setForeground(QtGui.QColor(*clr))
        # Set background colour
        if bkg is not None:
            self.setBackground(QtGui.QColor(*bkg))
        # Set alignment
        if aln == 'l':
            self.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        elif aln == 'r':
            self.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        else:
            self.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # Set read-only mode
        if ro:
            self.setFlags(~QtCore.Qt.ItemFlag.ItemIsEditable)


class PyScriptExec(QtCore.QObject):
    """Run a Python script as a subprocess, mirroring its standard streams to a Qt rich-text console.

    Wraps :class:`~PySide6.QtCore.QProcess` and forwards both the script's standard output and standard
    error to the supplied console widget with timestamped, colour-coded formatting. The class also exposes
    the process lifecycle as Qt signals (:attr:`started`, :attr:`cancelled`, :attr:`finished`) so callers
    can connect cleanup or follow-up behaviour.

    Note:
        The subprocess is launched with the same Python interpreter as the parent process (:data:`sys.executable`),
        so virtual-environment isolation is preserved.
    """

    # Process control signals
    started = QtCore.Signal()
    cancelled = QtCore.Signal()
    finished = QtCore.Signal()

    def __init__(self, script, console, trigger, name=None, disp_time=True, clr_con=False, trig_txt=None, parent=None):
        """Wire the trigger button, console widget, and subprocess and prepare them for first run.

        Args:
            script (str): Path to the Python script to execute
            console (QtWidgets.QTextEdit): Rich-text widget that displays the subprocess output
            trigger (QtWidgets.QPushButton): Push button that toggles the subprocess on and off
            name (str | None): Process name shown in console messages; defaults to ``"Process"`` when
                :data:`None` (default: ``None``)
            disp_time (bool): When :data:`True`, prepend a timestamp to every console line (default: ``True``)
            clr_con (bool): When :data:`True`, clear the console before starting the subprocess (default: ``False``)
            trig_txt (tuple[str, str] | None): Idle and running texts shown on the trigger button;
                defaults to ``("Start", "Stop")`` when :data:`None` (default: ``None``)
            parent (QtCore.QObject | None): Parent Qt object (default: ``None``)
        """
        super().__init__(parent)
        self.name = name if name else 'Process'

        # Subprocess definition
        self.__process = QtCore.QProcess(self)
        self.__process.setProgram(sys.executable)  # Use the same Python interpreter
        self.__process.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.SeparateChannels)
        # Script and command definition
        self.script = script
        self.command = [script]
        self.__idle = True  # Instance idle status including post-finished tasks, different from ProcessState.NotRunning
        # Commandline monitoring variable
        self.__auto_scr = True  # Auto scroll to vertical end control flag
        self.last_line = ''  # Last commandline print of script
        self.man_stop = False  # Manually stop flag
        self.err_stop = False  # Error stop flag
        self.fin_stop = False  # Normal (finished) stop flag

        # Initialize trigger
        self._trigger = trigger
        self.trig_ti = 'Start' if trig_txt is None else trig_txt[0]
        self.trig_ts = 'Stop' if trig_txt is None else trig_txt[1]
        self._trigger.setText(self.trig_ti)
        # Initialize console
        self._console = console
        self._console.setReadOnly(True)
        self._console.setUndoRedoEnabled(True)
        self._console.setFont("Consolas")  # Monospaced font for console outputs
        self.cmd_time = disp_time
        self.cmd_rclr = clr_con
        self.__newline_flag = True  # Newline in console control flag

        # Link functions
        self._trigger.clicked.connect(self.__proc_control)
        self.__process.readyReadStandardOutput.connect(self.__read_stdout)
        self.__process.readyReadStandardError.connect(self.__read_stderr)
        self.__process.finished.connect(self.__proc_finish)

    def set_arguments(self, args):
        """Replace the current script arguments with ``args``.

        Args:
            args (list[str]): New argument list (each item must be a :class:`str`)

        Returns:
            list: Full command including the script path and the new arguments
        """
        if isinstance(args, list) and all(isinstance(i, str) for i in args):
            self.command = [self.script] + args
        else:
            warnings.warn("Illegal data type encountered in arguments!", RuntimeWarning, stacklevel=2)
        return self.command

    def add_arguments(self, args):
        """Append script argument(s) to the current command.

        Args:
            args (str | list[str]): Single argument or list of arguments to append

        Returns:
            list: Full command including the script path and the updated arguments
        """
        if isinstance(args, str):
            self.command += [args]
        elif isinstance(args, list) and all(isinstance(i, str) for i in args):
            self.command += args
        else:
            warnings.warn("Illegal data type encountered in arguments!", RuntimeWarning, stacklevel=2)
        return self.command

    def reset_arguments(self):
        """Reset the script arguments back to the bare script path.

        Returns:
            list: Reset command containing just the script path
        """
        self.command = [self.script]
        return self.command

    def set_auto_scroll(self, flag=True):
        """Enable or disable auto-scroll-to-end on the linked console.

        Args:
            flag (bool): When :data:`True`, the console scrolls to the bottom on every new line (default: ``True``)

        Returns:
            bool: Effective auto-scroll mode after the call
        """
        self.__auto_scr = flag
        if flag:
            self._console.verticalScrollBar().setValue(self._console.verticalScrollBar().maximum())
        return self.__auto_scr

    def terminate(self):
        """Kill the running subprocess and emit :attr:`cancelled`.

        Returns:
            bool: :data:`True` when a running subprocess was actually killed, :data:`False` when it was already idle
        """
        if self.__process.state() != QtCore.QProcess.ProcessState.NotRunning:
            self.__process.kill()
            self.man_stop = True
            self.cancelled.emit()
            return True
        else:
            return False

    @staticmethod
    def _get_timestamp():
        """Return a HTML-formatted timestamp string for prefixing console messages."""
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return "<span style=\"color:%s;white-space:pre;\">[%s] </span>" % ('skyblue' if cs_dark() else 'blue', time)

    def __append_message(self, message):
        """Append a rich-text message to the console and apply the current scroll policy.

        Args:
            message (str): Rich-text message to append
        """
        pos = self._console.verticalScrollBar().value()  # Get current vertical scroll bar position
        self._console.append(message)
        # Set vertical scroll bar position
        if self.__auto_scr:
            self._console.verticalScrollBar().setValue(self._console.verticalScrollBar().maximum())
        else:
            self._console.verticalScrollBar().setValue(pos)

    def __undo_message(self):
        """Roll back the last console append while keeping the current scroll-bar state."""
        # Get current vertical scroll bar limit and position
        max_pos = self._console.verticalScrollBar().maximum()
        pos = self._console.verticalScrollBar().value()
        # Undo message
        self._console.undo()
        # Set vertical scroll bar to previous limit and position
        self._console.verticalScrollBar().setMaximum(max_pos)
        self._console.verticalScrollBar().setValue(pos)

    def __proc_control(self):
        """Toggle the subprocess on or off in response to the trigger button."""
        if self.__idle:
            # Prepare console
            self._console.clear() if self.cmd_rclr else None
            time = self._get_timestamp() if self.cmd_time else ''
            message = time + "<span style=\"color:%s;font-weight:bold;\">%s started...</span>" % (
                'lightgreen' if cs_dark() else 'green', self.name)
            self.__append_message(message)
            # Set trigger texts
            self._trigger.setText(self.trig_ts)
            # Reset status flags
            self.man_stop = False
            self.err_stop = False
            self.fin_stop = False
            # Start process
            self.__process.setArguments(self.command)
            self.__process.start()
            self.__idle = False  # Set instance status
            # Send process control signal
            self.started.emit()
        elif self.__process.state() != QtCore.QProcess.ProcessState.NotRunning:
            # Kill current process
            self.__process.kill()  # Preferred over terminate() for better cross-platform support
            self.man_stop = True
            # Notify in console
            self.__newline_flag = True
            time = self._get_timestamp() if self.cmd_time else ''
            message = time + "<span style=\"color:%s;font-weight:bold;\">Process manually stopped!</span>" % (
                'violet' if cs_dark() else 'purple')
            self.__append_message(message)
            # Send process control signal
            self.cancelled.emit()

    def __read_stdout(self):
        """Forward subprocess standard output to the console with carriage-return overwrite handling."""
        time = self._get_timestamp() if self.cmd_time else ''
        text = self.__process.readAllStandardOutput().data().decode()
        # Overwrite texts to meet the same behaviour as command line
        self.__undo_message() if (not self.__newline_flag) and text.startswith('\r') else None
        # Process standard output texts
        self.__newline_flag = text.endswith('\n')
        for l in text.rstrip().split('\n'):  # Avoid missing new lines in HTML format
            last = l.strip('\r').split('\r')[-1]  # Get last print when multiple '\r' exist
            message = time + "<span style=\"white-space:pre;\">%s</span>" % last
            self.__append_message(message)
            self.last_line = last  # Record last print

    def __read_stderr(self):
        """Forward subprocess standard error to the console; warnings are olive, errors are red."""
        time = self._get_timestamp() if self.cmd_time else ''
        text = self.__process.readAllStandardError().data().decode()
        # Process standard error texts
        self.__newline_flag = True
        if 'warning' in text.lower():
            message = time + "<span style=\"color:olive;white-space:pre;\">%s</span>" % text.rstrip()
        else:
            message = time + "<span style=\"color:red;white-space:pre;\">%s</span>" % text.rstrip()
            self.err_stop = True
        self.__append_message(message)
        self.last_line = text.rstrip()  # Record last print

    def __proc_finish(self, ec, es):
        """Finalise the subprocess: report any error, write the closing message, and emit :attr:`finished`.

        Args:
            ec (int): Subprocess exit code (only meaningful when ``es`` is normal exit)
            es (QtCore.QProcess.ExitStatus): Subprocess exit status
        """
        # Prepare console
        None if self.__newline_flag else self.__undo_message()  # Cancel temporary prints
        self.__newline_flag = True  # Reset print line flag
        # Check if errors exist in the stopped process
        if not (ec == 0 or self.man_stop):
            time = self._get_timestamp() if self.cmd_time else ''
            # Get error type
            if self.__process.error() == QtCore.QProcess.ProcessError.UnknownError:
                em = "UnspecifiedError @ %s -> please refer to SystemStandardError" % str(es).split('.')[-1]
            else:
                em = "%s @ %s" % (str(self.__process.error()).split('.')[-1], str(es).split('.')[-1])
            # Send to console
            message = time + "<span style=\"color:red;font-weight:bold;\">Non-zero exit code: %d (%s)</span>" % (ec, em)
            self.__append_message(message)
        # Notify in console
        time = self._get_timestamp() if self.cmd_time else ''
        message = time + "<span style=\"color:%s;font-weight:bold;\">%s finished!</span>" % (
            'lightgreen' if cs_dark() else 'green', self.name)
        self.__append_message(message)
        self.__append_message('')  # Extra blank line
        # Set trigger texts
        self._trigger.setText(self.trig_ti)
        # Finalizing stop
        self.fin_stop = not (self.man_stop or self.err_stop)
        self.__idle = True  # Reset instance status
        self.finished.emit()  # Send process control signal


class ProcConsole:
    """Bundle of console widgets and helper buttons that share a set of :class:`PyScriptExec` runners.

    Centralises the clear, copy, and auto-scroll controls for a console that is shared by one or more
    subprocess runners, so each runner stays responsible only for its own output.
    """

    def __init__(self, console, btn_clr, btn_cpy, btn_scr, lnk_proc, stat_bar=None, disp_time=True, init_msg=None):
        """Wire the console widgets, link the runners, and write the initial message.

        Args:
            console (QtWidgets.QTextEdit): Rich-text widget that displays the subprocess output
            btn_clr (QtWidgets.QPushButton): Button that clears the console
            btn_cpy (QtWidgets.QPushButton): Button that copies the console contents to the clipboard
            btn_scr (QtWidgets.QPushButton): Button that toggles auto-scroll-to-end
            lnk_proc (list[PyScriptExec]): Subprocess runners that share this console
            stat_bar (QtWidgets.QStatusBar | None): Status bar for transient messages (default: ``None``)
            disp_time (bool): When :data:`True`, prepend a timestamp to console lines (default: ``True``)
            init_msg (str | None): Message displayed when the console is (re-)initialised (default: ``None``)
        """
        # Initialize attributes
        self.console = console
        self.btn_clr = btn_clr
        self.btn_cpy = btn_cpy
        self.btn_scr = btn_scr
        self.stat_bar = stat_bar
        self.__lnk_proc = lnk_proc
        self.__disp_time = disp_time
        self.__init_msg = init_msg
        self.__auto_scr = True

        # Initialize console
        self.console_init()
        self.set_auto_scroll(self.__auto_scr)
        # Console easy access function control connection
        self.btn_clr.clicked.connect(self.console_init)
        self.btn_cpy.clicked.connect(self.console_copy)
        # Console auto scroll to end features control connection
        self.btn_scr.clicked.connect(self.__switch_auto_scroll)
        self.console.verticalScrollBar().sliderPressed.connect(self.__manual_slider_press)
        self.console.verticalScrollBar().sliderReleased.connect(self.__manual_slider_release)

    def console_init(self):
        """Clear the console and write the initial timestamp/banner message."""
        if self.__disp_time:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            time = "<span style=\"color:%s;white-space:pre;\">[%s] </span>" % ('skyblue' if cs_dark() else 'blue', time)
        else:
            time = ''
        message = time + "<span style=\"font-weight:bold;\">%s</span>" % self.__init_msg
        self.console.clear()
        self.console.append(message)
        self.console.append('')  # Extra blank line
        # Show status bar message
        if self.stat_bar is not None:
            self.stat_bar.showMessage("Console cleared")

    def console_copy(self):
        """Copy the console contents to the clipboard without disturbing the current scroll position."""
        pos = self.console.verticalScrollBar().value()
        # Copy all available messages
        self.console.selectAll()
        self.console.copy()
        # Clear selection
        tc = self.console.textCursor()
        tc.clearSelection()
        self.console.setTextCursor(tc)
        self.console.verticalScrollBar().setValue(pos)
        # Show status bar message
        if self.stat_bar is not None:
            self.stat_bar.showMessage("Console information successfully copied")

    def set_auto_scroll(self, mode):
        """Set the auto-scroll mode of this console and propagate it to every linked subprocess runner.

        Args:
            mode (bool): When :data:`True`, the console scrolls to the bottom on every new line
        """
        self.__auto_scr = mode
        # Set auto scroll button features
        self.btn_scr.setChecked(mode)
        if mode:
            self.btn_scr.setStyleSheet('QPushButton{color:%s;}' % ('lightgreen' if cs_dark() else 'green'))
            self.btn_scr.setText("Auto Scroll\nON")
        else:
            self.btn_scr.setStyleSheet('QPushButton{color:%s;}' % ('coral' if cs_dark() else 'red'))
            self.btn_scr.setText("Auto Scroll\nOFF")
        # Set connected process auto scroll functions
        for p in self.__lnk_proc:
            p.set_auto_scroll(mode)

    def __switch_auto_scroll(self):
        """Toggle auto-scroll in response to the dedicated button."""
        self.set_auto_scroll(not self.__auto_scr)

    def __manual_slider_press(self):
        """Disable auto-scroll when the user grabs the vertical scroll bar."""
        self.set_auto_scroll(False)

    def __manual_slider_release(self):
        """Re-enable auto-scroll when the user releases the slider at the very bottom."""
        if self.console.verticalScrollBar().value() == self.console.verticalScrollBar().maximum():
            self.set_auto_scroll(True)


class ProgBusyDialog(QtWidgets.QDialog):
    """Non-interactive, application-modal busy dialog with an optional progress bar.

    The window has no decorations and cannot be dismissed by the user; closing must be triggered
    programmatically by setting ``allow_close`` to :data:`True` before invoking :meth:`close`.
    """

    def __init__(self, parent=None, message="Busy\nPlease wait...", bar=False):
        """Build the busy dialog and (optionally) attach a progress bar.

        Args:
            parent (QtCore.QObject | None): Parent Qt object (default: ``None``)
            message (str): Dialog message; supports HTML rich text (default: ``"Busy\\nPlease wait..."``)
            bar (bool): When :data:`True`, attach a progress bar to the dialog (default: ``False``)
        """
        super().__init__(parent)
        self.allow_close = False  # Avoid user close [Alt+F4] and early programmatic close
        # Set window feature
        self.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        # Set UI feature
        lbl = QtWidgets.QLabel(message)
        lbl.setTextFormat(QtCore.Qt.TextFormat.RichText)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(lbl)
        if bar:
            self.prog_bar = QtWidgets.QProgressBar(self, minimum=0, maximum=100)
            layout.addWidget(self.prog_bar)
        else:
            self.prog_bar = None
        self.setLayout(layout)
        self.setFixedSize(200, 120) if bar else self.setFixedSize(200, 90)

    def closeEvent(self, event):
        event.accept() if self.allow_close else event.ignore()

    def set_progress(self, val):
        """Set the progress-bar value, clamped to ``[0, 100]``.

        Args:
            val (int): Progress value; values outside ``[0, 100]`` are clamped to the nearest endpoint
        """
        if self.prog_bar is not None:
            val = 0 if val < 0 else 100 if val > 100 else val
            self.prog_bar.setValue(val)


# Functions ---------------------------------------------------------------------------------------------------------- #

def path_selector(line, mode=None, caption=None, flt=None, parent=None):
    """Open a file/folder selection dialog and write the result back to a line-edit widget.

    On invalid input the user is prompted to retry; on cancel the line edit is cleared and :data:`None`
    is returned.

    Args:
        line (QtWidgets.QLineEdit): Line edit that displays and stores the selected path
        mode (str | None): Dialog mode; one of ``{'path', 'file', 'list'}`` (default: ``None`` = ``'path'``)
        caption (str | None): Dialog window caption (default: ``None``)
        flt (str | None): File-name filter (default: ``None``)
        parent (QtWidgets.QWidget | None): Parent Qt widget (default: ``None``)

    Returns:
        str | list[str] | None: Selected path(s); :data:`None` when the dialog was cancelled

    Raises:
        ValueError: If ``mode`` is not one of ``{'path', 'file', 'list'}``
    """
    mode = 'path' if mode is None else mode
    caption = '' if caption is None else caption
    btn_ok = QtWidgets.QMessageBox.StandardButton.Ok
    btn_re = QtWidgets.QMessageBox.StandardButton.Retry

    if mode == 'path':
        path = QtWidgets.QFileDialog.getExistingDirectory(parent, caption)
        if path and os.path.isdir(path):
            line.setText(path)
            return path
        else:
            if path:
                reply = QtWidgets.QMessageBox.warning(parent, "Warning", "Invalid directory!", btn_ok | btn_re, btn_ok)
                if reply == btn_ok:
                    line.clear()
                    return None
                else:
                    path_selector(line, mode, caption, flt, parent)  # Retry self
            else:
                # Operation cancelled
                return None
    elif mode == 'file':
        file, _ = QtWidgets.QFileDialog.getOpenFileName(parent, caption, filter=flt)
        if file and os.path.isfile(file):
            line.setText(file)
            return file
        else:
            if file:
                reply = QtWidgets.QMessageBox.warning(parent, "Warning", "Invalid file!", btn_ok | btn_re, btn_ok)
                if reply == btn_ok:
                    line.clear()
                    return None
                else:
                    path_selector(line, mode, caption, flt, parent)  # Retry self
            else:
                # Operation cancelled
                return None
    elif mode == 'list':
        flst, _ = QtWidgets.QFileDialog.getOpenFileNames(parent, caption, filter=flt)
        if flst and all([os.path.isfile(f) for f in flst]):
            line.setText('; '.join(flst))
            return flst
        else:
            if flst:
                reply = QtWidgets.QMessageBox.warning(parent, "Warning", "Invalid file found!", btn_ok | btn_re, btn_ok)
                if reply == btn_ok:
                    line.clear()
                    return None
                else:
                    path_selector(line, mode, caption, flt, parent)  # Retry self
            else:
                # Operation cancelled
                return None
    else:
        raise ValueError("Invalid operation mode, available modes ['path', 'file', 'list']")


def table_loader(table, record, select, mode=None, caption=None, flt=None, listdir=False, func=None, parent=None):
    """Append the user-selected paths or files as new rows in a Qt table widget.

    Each appended row carries a checkbox, a typed badge (``DIRS``/``FILE``/``LIST``), and the path. The
    function deduplicates against ``record`` and reports a short status string describing the outcome.

    Args:
        table (QtWidgets.QTableWidget): Target table widget
        record (list[str]): Existing item paths used for duplicate detection
        select (list[CellCheckbox]): Existing per-row checkboxes; the new rows are appended in place
        mode (str | None): Dialog mode; one of ``{'path', 'file'}`` (default: ``None`` = ``'path'``)
        caption (str | None): Dialog window caption (default: ``None``)
        flt (str | None): File-name filter; used in ``'file'`` mode and when ``listdir`` is :data:`True`
            (default: ``None``)
        listdir (bool): When :data:`True` (and ``mode == 'path'``), list the files in the selected
            directory rather than adding the directory itself (default: ``False``)
        func (callable | None): Slot connected to each new checkbox's ``clicked`` signal (default: ``None``)
        parent (QtWidgets.QWidget | None): Parent Qt widget (default: ``None``)

    Returns:
        tuple[str, list[str], list[CellCheckbox]]: Status message and the (potentially extended) ``record``
            and ``select`` lists

    Raises:
        ValueError: If ``mode`` is not one of ``{'path', 'file'}``
    """
    mode = 'path' if mode is None else mode
    caption = '' if caption is None else caption

    def __load_row(itm: str, typ: str, clr: tuple[int, int, int]):
        """Insert a new row carrying the item path, type badge, and selection checkbox."""
        record.append(itm)
        # Get current data
        curr_row = table.rowCount()
        curr_chk = CellCheckbox(identifier=itm, func=func)
        select.append(curr_chk)
        # Set cell values
        table.insertRow(curr_row)
        table.setCellWidget(curr_row, 0, curr_chk)
        table.setItem(curr_row, 1, CellData(typ, aln='c', emp='b', clr=clr))
        table.setItem(curr_row, 2, CellData(itm, aln='l'))

    if mode == 'path':
        path = QtWidgets.QFileDialog.getExistingDirectory(parent, caption)
        if path and os.path.isdir(path):
            if listdir:
                # Get file extension from [flt]
                ext = re.search(r'\((?!\*\.\*\))([^)]+?)\)', flt)
                ext = '' if ext is None else tuple(ext.group(1).replace('*', '').split(' '))
                # Scan and load file(s) in selected path
                flst = [os.path.join(path, f).replace('\\', '/') for f in os.listdir(path) if f.endswith(ext)]
                n = 0  # Counter
                for f in flst:
                    if f not in record:
                        __load_row(f, typ='LIST', clr=(255, 127, 0))
                        n += 1
                if n == 0:
                    # Return: noting to add from path
                    return "All file(s) in selected directory are duplicated or invalid", record, select
                elif len(flst) == n:
                    # Return: all file add from path
                    return "All file(s) in selected directory added to table", record, select
                else:
                    # Return: some file add from path
                    return "Some duplicated or invalid file(s) in selected directory not added", record, select
            else:
                path = path.rstrip('\\/').replace('\\', '/')  # Unifying path
                if path not in record:
                    __load_row(path, typ='DIRS', clr=(152, 110, 172))
                    # Return: path added
                    return "Selected folder added to table", record, select
                else:
                    # Return: nothing to add
                    return "Selected folder already exist in table", record, select
        if path:
            # Return: invalid path
            return "Invalid folder", record, select
        else:
            # Return: cancelled
            return "No folder selected", record, select
    elif mode == 'file':
        flst, _ = QtWidgets.QFileDialog.getOpenFileNames(parent, caption, filter=flt)
        if flst:
            n = 0  # Counter
            for f in flst:
                f = f.replace('\\', '/')  # Unifying path
                if os.path.isfile(f) and (f not in record):
                    __load_row(f, typ='FILE', clr=(92, 174, 99))
                    n += 1
            if n == 0:
                # Return: noting to add
                return "All selected file(s) found duplicated or invalid", record, select
            elif len(flst) == n:
                # Return: all file add
                return "All selected file(s) added to table", record, select
            else:
                # Return: some file add
                return "Some duplicated or invalid file(s) not added", record, select
        else:
            # Return: cancelled
            return "No data file selected", record, select
    else:
        raise ValueError("Invalid operation mode, available modes ['path', 'file']")


def selection_operator(select, mode):
    """Apply a bulk select/deselect/invert operation to a list of table-row checkboxes.

    Args:
        select (list[CellCheckbox]): Table-row checkboxes to update
        mode (str): Operation mode; one of ``{'all', 'non', 'inv'}`` (``'all'`` selects all, ``'non'``
            deselects all, ``'inv'`` inverts the current selection)

    Returns:
        str: Status message describing the action applied (or an error message for an unknown mode)
    """
    if mode == 'all':
        [cb.setChecked(True) for cb in select]
        return "Select all data items"
    elif mode == 'non':
        [cb.setChecked(False) for cb in select]
        return "Deselect all data items"
    elif mode == 'inv':
        [cb.setChecked(not cb.isChecked()) for cb in select]
        return "Data selection has been inverted"
    else:
        # Error not raised to bypass [mode]
        return "Invalid operation"
