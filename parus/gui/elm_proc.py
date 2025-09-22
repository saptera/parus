# Parus GUI process related features

import sys
import os
import re
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets
import warnings

__package__ = 'parus.gui'
from . import cs_dark

__all__ = ['CellCheckbox', 'CellData', 'PyScriptExec', 'ProcConsole', 'ProgBusyDialog',
           'path_selector', 'table_loader', 'selection_operator']
"""
Class list:
  CellCheckbox(identifier=None, func=None): Table checkbox class.
  CellData(val, aln='c', emp=None, clr=None, bkg=None, ro=False): Data selection table cell data class.
  PyScriptExec: Execute Python script as a subprocess, with its console displayed.
  ProcConsole: GUI process console control combo class.
  ProgBusyDialog(parent=None, message="Please wait.."): Non-interactive, application-modal busy dialog.
Functon list:
  path_selector(line, mode=None, caption=None, flt=None, parent=None): Select signal folder or file dialog.
  table_loader(table, record, select, mode=None, caption=None, flt=None, func=None, parent=None): Path item to table.
  selection_operator(select, mode): Item selection checkbox group operation.
"""


# Classes ------------------------------------------------------------------------------------------------------------ #

class CellCheckbox(QtWidgets.QWidget):
    def __init__(self, identifier=None, func=None):
        """ Table checkbox class.

        Args:
            identifier: Instance identifier
            func (function | None): Checkbox clicked connect function
        """
        super(CellCheckbox, self).__init__()
        # Initialize a pre-checked checkbox
        self.chkbox = QtWidgets.QCheckBox()
        self.chkbox.setChecked(True)
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
        """ Return checked status of checkbox. """
        return self.chkbox.isChecked()

    def setChecked(self, status: bool):
        """ Set checked status of checkbox. """
        self.chkbox.setChecked(status)
        return status


class CellData(QtWidgets.QTableWidgetItem):
    def __init__(self, val, aln='c', emp=None, clr=None, bkg=None, ro=False):
        """ Data selection table cell data class.

        Args:
            val:Value to fill in the cell, any type can convert to string
            aln (str): Alignment method 'c' = centre | 'l' = left |  'r' = right (default: 'c' = centre)
            emp (str | None): {'b' | 'i' | 'bi' | 'ib'} Text emphasize method 'b' = bold | 'i' = italic (default: None)
            clr (tuple[int, int, int] | None): Text colour in RGB (default: None)
            bkg (tuple[int, int, int] | None): Background colour in RGB (default: None)
            ro (bool): Item read-only flag (default: False)
        """
        super(CellData, self).__init__()
        # Set cell text
        txt = val if isinstance(val, str) else str(val)
        self.setText(txt)
        # Set text emphasize method
        if emp is not None:
            font = self.font()
            if 'b' in emp:
                font.setBold(True)
            if 'i' in emp:
                font.setItalic(True)
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
    # Process control signals
    started = QtCore.Signal()
    cancelled = QtCore.Signal()
    finished = QtCore.Signal()

    def __init__(self, script, console, trigger, name=None, disp_time=True, clr_con=False, trig_txt=None, parent=None):
        """ Execute Python script as a subprocess, with its console displayed.

        Args:
            script (str): Python script to execute
            console (QtWidgets.QTextEdit): Qt rich text widget to display Python script commandline prints
            trigger (QtWidgets.QPushButton): Qt push button to control script execution
            name (str | None): Process name for this instance (default: None)
            disp_time (bool): Print timestamp of commandline (default: True)
            clr_con (bool): Clear console texts before start (default: False)
            trig_txt (tuple[str, str] | None): Start and stop texts to display on push button (default: Start | Stop)
            parent (QtCore.QObject | None): Parent Qt object
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
        """ Set script argument(s) for execution, this will overwrite previous arguments.

        Args:
            args (list[str]): List of arguments for execution

        Returns:
            list: Current full argument
        """
        if isinstance(args, list) and all(isinstance(i, str) for i in args):
            self.command = [self.script] + args
        else:
            warnings.warn("Illegal data type encountered in arguments!", RuntimeWarning, stacklevel=2)
        return self.command

    def add_arguments(self, args):
        """ Add script argument(s) for execution.

        Args:
            args (str | list[str]): List of arguments for execution

        Returns:
            list: Current full argument
        """
        if isinstance(args, str):
            self.command += [args]
        elif isinstance(args, list) and all(isinstance(i, str) for i in args):
            self.command += args
        else:
            warnings.warn("Illegal data type encountered in arguments!", RuntimeWarning, stacklevel=2)
        return self.command

    def reset_arguments(self):
        """ Reset script arguments.

        Returns:
            list: Default command
        """
        self.command = [self.script]
        return self.command

    def set_auto_scroll(self, flag=True):
        """ Set console to auto scroll to vertical end.

        Args:
            flag (bool): Vertical scroll mode to set

        Returns:
            bool: Current vertical auto scroll mode
        """
        self.__auto_scr = flag
        if flag:
            self._console.verticalScrollBar().setValue(self._console.verticalScrollBar().maximum())
        return self.__auto_scr

    def terminate(self):
        """ Terminate current process.

        Returns:
            bool: If the process requires termination
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
        """ Get current timestamp. """
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return "<span style=\"color:%s;white-space:pre;\">[%s] </span>" % ('skyblue' if cs_dark() else 'blue', time)

    def __append_message(self, message):
        """ Append message to the console display.

        Args:
            message (str): Rich text message to append to console
        """
        pos = self._console.verticalScrollBar().value()  # Get current vertical scroll bar position
        self._console.append(message)
        # Set vertical scroll bar position
        if self.__auto_scr:
            self._console.verticalScrollBar().setValue(self._console.verticalScrollBar().maximum())
        else:
            self._console.verticalScrollBar().setValue(pos)

    def __undo_message(self):
        """ Undo last console display operation. """
        # Get current vertical scroll bar limit and position
        max_pos = self._console.verticalScrollBar().maximum()
        pos = self._console.verticalScrollBar().value()
        # Undo message
        self._console.undo()
        # Set vertical scroll bar to previous limit and position
        self._console.verticalScrollBar().setMaximum(max_pos)
        self._console.verticalScrollBar().setValue(pos)

    def __proc_control(self):
        """ Trigger button process control function. """
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
        """ Read system standard output data. """
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
        """ Read system standard error data. """
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
        """ Process finalizing function.

        Args:
            ec (int): Exit code of the process (only valid for normal exits)
            es (QtCore.QProcess.ExitStatus): Exit status of the process
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
    def __init__(self, console, btn_clr, btn_cpy, btn_scr, lnk_proc, stat_bar=None, disp_time=True, init_msg=None):
        """ GUI process console control combo class.

        Args:
            console (QtWidgets.QTextEdit): Qt rich text widget to display Python script commandline prints
            btn_clr (QtWidgets.QPushButton): Qt push button to clear console
            btn_cpy (QtWidgets.QPushButton): Qt push button to copy console texts
            btn_scr (QtWidgets.QPushButton): Qt push button to switch console auto-scroll feature
            lnk_proc (list[PyScriptExec]): List of script execution class linked to this console
            stat_bar (QtWidgets.QStatusBar | None): Status bar for displaying extra info (default: None)
            disp_time (bool): Print timestamp of commandline (default: True)
            init_msg (str | None): Message when the console is re-initialized (default: None)
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
        """ Initialize process system console. """
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
        """ Copy all texts in console to clipboard. """
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
        """ Set console auto scroll to end status.

        Args:
            mode (bool): Auto scroll to end status
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
        """ Auto scroll button connected function. """
        self.set_auto_scroll(not self.__auto_scr)

    def __manual_slider_press(self):
        """ Console vertical slider user PRESSED connected function. """
        self.set_auto_scroll(False)

    def __manual_slider_release(self):
        """ Console vertical slider user RELEASED connected function. """
        if self.console.verticalScrollBar().value() == self.console.verticalScrollBar().maximum():
            self.set_auto_scroll(True)


class ProgBusyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, message="Busy\nPlease wait.."):
        """ Non-interactive, application-modal busy dialog.

        Args:
            parent (QtCore.QObject | None): Parent Qt object
            message (str): Messagebox message, support HTML formatting (default: "Please wait...")
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
        self.setLayout(layout)
        self.setFixedSize(200, 90)

    def closeEvent(self, event):
        event.accept() if self.allow_close else event.ignore()


# Functions ---------------------------------------------------------------------------------------------------------- #

def path_selector(line, mode=None, caption=None, flt=None, parent=None):
    """ Select signal folder or file dialog.

    Args:
        line (QtWidgets.QLineEdit): Text line edit for showing and editing the path
        mode (str | None): {'path' | 'file' | 'list'} File dialog mode (default: None = open path)
        caption (str | None): Window caption
        flt (str | None): Selector filter (default: None)
        parent (QtWidgets.QWidget | None): Parent Qt object

    Returns:
        str | list[str] | None: Selected path
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
    """ Load path item to table.

    Args:
        table (QtWidgets.QTableWidget): Path item view table widget
        record (list[str]): Table item records for checking duplications
        select (list[CellCheckbox]): Table item selection checkboxes
        mode (str | None): {'path' | 'file'} File dialog mode (default: None = open path)
        caption (str | None): Window caption
        flt (str | None): Selector filter, valid for file and path-listdir mode (default: None)
        listdir (bool): List all files in selected path, valid for path mode (default: False)
        func (function | None): Checkbox clicked connected function (default: None)
        parent (QtWidgets.QWidget | None): Parent Qt object

    Returns:
        tuple[str, list[str], list[CellCheckbox]]: Loading status and updated [record] and [select] list
    """
    mode = 'path' if mode is None else mode
    caption = '' if caption is None else caption

    def __load_row(itm: str, typ: str, clr: tuple[int, int, int]):
        """ Helper function to load table row. """
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
    """ Item selection checkbox group operation.

    Args:
        select (list[CellCheckbox]): Table item selection checkboxes
        mode (str): {'all' | 'non' | 'inv'} Operation mode 'all' = all | 'non' = none | 'inv' = invert

    Returns:
        str: Operation report
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
