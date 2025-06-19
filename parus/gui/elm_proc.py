import sys
from datetime import datetime
from PySide6 import QtCore, QtWidgets
import warnings


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
        return "<span style=\"color:blue;white-space:pre;\">[%s] </span>" % time

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
            message = time + "<span style=\"color:green;font-weight:bold;\">%s started...</span>" % self.name
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
            message = time + "<span style=\"color:purple;font-weight:bold;\">Process manually stopped!</span>"
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
        message = time + "<span style=\"color:green;font-weight:bold;\">%s finished!</span>" % self.name
        self.__append_message(message)
        self.__append_message('')  # Extra blank line
        # Set trigger texts
        self._trigger.setText(self.trig_ti)
        # Finalizing stop
        self.fin_stop = not (self.man_stop or self.err_stop)
        self.__idle = True  # Reset instance status
        self.finished.emit()  # Send process control signal
