import sys
from datetime import datetime
from PySide6 import QtCore, QtWidgets
import warnings


class PyScriptExec(QtCore.QObject):
    # Process control signals
    started = QtCore.Signal()
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
        self.__process.setProcessChannelMode(QtCore.QProcess.SeparateChannels)
        # Script and command definition
        self.script = script
        self.command = [script]
        # Commandline monitoring variable
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

    @staticmethod
    def _get_timestamp():
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return "<span style=\"color:blue;white-space:pre;\">[%s] </span>" % time

    def __proc_control(self):
        """ Trigger button process control function. """
        if self._trigger.text() == self.trig_ti:
            # Prepare console
            self._console.clear() if self.cmd_rclr else None
            time = self._get_timestamp() if self.cmd_time else ''
            message = time + "<span style=\"color:green;font-weight:bold;\">%s started...</span>" % self.name
            self._console.append(message)
            # Reset status flags
            self.man_stop = False
            self.err_stop = False
            self.fin_stop = False
            # Set trigger texts
            self._trigger.setText(self.trig_ts)
            # Start process
            self.__process.setArguments(self.command)
            self.__process.start()
            self.started.emit()  # Send signal
        elif self._trigger.text() == self.trig_ts:
            self.__process.kill()
            self.man_stop = True
            # Notify in console
            self._console.clear() if self.cmd_rclr else None
            time = self._get_timestamp() if self.cmd_time else ''
            message = time + "<span style=\"color:purple;font-weight:bold;\">Process manually stopped!</span>"
            self._console.append(message)

    def __read_stdout(self):
        """ Read system standard output data. """
        time = self._get_timestamp() if self.cmd_time else ''
        text = self.__process.readAllStandardOutput().data().decode()
        # Overwrite texts to meet the same behaviour as command line
        self._console.undo() if (not self.__newline_flag) and text.startswith('\r') else None
        # Process standard output texts
        self.__newline_flag = text.endswith('\n')
        for l in text.rstrip().split('\n'):  # Avoid missing new lines in HTML format
            last = l.strip('\r').split('\r')[-1]  # Get last print when multiple '\r' exist
            message = time + "<span style=\"white-space:pre;\">%s</span>" % last
            self._console.append(message)
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
            message = time + "<span style=\"color:red;font-weight:bold;white-space:pre;\">%s</span>" % text.rstrip()
            self.err_stop = True
        self._console.append(message)
        self.last_line = text.rstrip()  # Record last print

    def __proc_finish(self):
        """ Process finalizing function. """
        # Notify in console
        time = self._get_timestamp() if self.cmd_time else ''
        message = time + "<span style=\"color:green;font-weight:bold;\">%s finished!</span>" % self.name
        self._console.append(message)
        self._console.append('')  # Extra blank line
        # Set trigger texts
        self._trigger.setText(self.trig_ti)
        # Check stop status and emit signal
        self.fin_stop = False if self.man_stop or self.err_stop else True
        self.finished.emit()

