#!/usr/bin/env python3
"""
Logging classes for the proxy.

"""
import logging





class BaseLogger(logging.Logger):
    """
    A simple logging class.

    """
    def __init__(self, name=None, logging_level="info", time=True):
        """
        Setup the base logging class.

        Set name and logging level.

        """
        super().__init__(name)

        if not logging_level:
            logging_level = logging.INFO

        elif logging_level == "quiet":
            logging_level = logging.NOTSET

        elif logging_level == "debug":
            logging_level = logging.DEBUG
        elif logging_level == "debug_warning":
            logging_level = 11  # custom

        elif logging_level == "verbose":
            logging_level = 15  # custom
        elif logging_level == "verbose_warning":
            logging_level = 16  # custom

        elif logging_level == "info":
            logging_level = logging.INFO
        elif logging_level == "warning":
            logging_level = logging.WARNING

        elif logging_level == "error":
            logging_level = logging.ERROR
        elif logging_level == "critical":
            logging_level = logging.CRITICAL
        elif logging_level == "fatal":
            logging_level = logging.FATAL

        # add a verbose setting
        logging.addLevelName(11, "DEBUG WARNING")

        # add a verbose setting
        logging.addLevelName(15, "VERBOSE")

        # add a verbose setting
        logging.addLevelName(16, "VERBOSE WARNING")

        if name and time:
            fmt = "[%(asctime)s,%(msecs)03d; %(name)s; %(levelname)s] %(message)s"
        elif name and not time:
            fmt = "[%(name)s; %(levelname)s] %(message)s"
        elif (not name or name == "") and time:
            fmt = "[%(asctime)s,%(msecs)03d; %(levelname)s] %(message)s"
        else:
            fmt = "[%(levelname)s] %(message)s"

        fmt_date = "%d.%m.%Y %T"
        formatter = logging.Formatter(fmt, fmt_date)
        handler = logging.StreamHandler()
        handler.setLevel(logging_level)
        handler.setFormatter(formatter)

        self.setLevel(logging_level)
        self.addHandler(handler)

        if logging_level == logging.NOTSET:
            logging.disable()


class LogWrapper(object):
    _wrapper_instance = None
    def __new__(cls, name, level, time):
        cls._wrapper_instance = BaseLogger(name, level, time)
        return cls

    @classmethod
    def _check_inst(cls):
        """
        Check for class instantiation.

        """
        if not cls._wrapper_instance:
            raise ValueError("LogWrapper not instantiated")

    @classmethod
    def debug(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.debug("\u001b[36m{}\u001b[0m".format(msg))

    @classmethod
    def debug_warning(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.log(11, "\u001b[33m{}\u001b[0m".format(msg))

    @classmethod
    def verbose(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.log(15, "{}".format(msg))

    @classmethod
    def verbose_warning(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.log(16, "\u001b[33m{}\u001b[0m".format(msg))

    @classmethod
    def info(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.info("{}".format(msg))

    @classmethod
    def warning(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.warning("\u001b[33m{}\u001b[0m".format(msg))

    @classmethod
    def error(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.error("\u001b[31m{}\u001b[0m".format(msg))

    @classmethod
    def critical(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.critical("\u001b[31;1m{}\u001b[0m".format(msg))

    @classmethod
    def fatal(cls, msg):
        cls._check_inst()
        cls._wrapper_instance.fatal("\u001b[31;1m{}\u001b[0m".format(msg))


class CoreLog(LogWrapper):
    _my_instance = None
    def __new__(cls, level=None, name="CORE", time=True):
        if not cls._my_instance:
            cls._my_instance = LogWrapper(name, level, time)
        return cls

    @classmethod
    def _clear(cls):
        cls._my_instance = None


class SimulationLog(LogWrapper):
    _my_instance = None
    def __new__(cls, level=None, name="SIMULATION", time=True):
        if not cls._my_instance:
            cls._my_instance = LogWrapper(name, level, time)
        return cls

    @classmethod
    def _clear(cls):
        cls._my_instance = None


class BackendLog(LogWrapper):
    _my_instance = None
    def __new__(cls, level=None, name="BACKEND", time=True):
        if not cls._my_instance:
            cls._my_instance = LogWrapper(name, level, time)
        return cls

    @classmethod
    def _clear(cls):
        cls._my_instance = None











# class BaseLogger(object):

#     class _BaseLogger(object):
#         _name = None
#         _logging_level = None

#         _logger = None
#         _ch = None

#         def __init__(self, name, logging_level=None):
#             if not name:
#                 raise AttributeError("Need to provide a name for the logger")
#             self._name = name
#             self.set_level(logging_level)

#         def set_level(self, logging_level):
#             if logging_level is None:
#                 logging_level = "quiet"

#             if logging_level not in ["quiet", "debug", "info", "warning",
#                                      "error", "critical"]:
#                 raise AttributeError(
#                     "Need name and logging_level ('debug', 'info', "
#                     "'warning', 'error', 'critical', 'quiet')"
#                 )

#             self._logging_level = logging_level

#             if logging_level == "quiet":
#                 logging_level = logging.NOTSET
#             elif logging_level == 'debug':
#                 logging_level = logging.DEBUG
#             elif logging_level == 'info':
#                 logging_level = logging.INFO
#             elif logging_level == 'warning':
#                 logging_level = logging.WARNING
#             elif logging_level == 'error':
#                 logging_level = logging.ERROR
#             elif logging_level == 'critical':
#                 logging_level = logging.CRITICAL

#             self._logger = logging.getLogger(self._name)
#             self._logger.setLevel(logging_level)
#             formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
#             if self._ch:
#                 self._logger.removeHandler(self._ch)
#             self._ch = logging.StreamHandler()
#             self._ch.setLevel(logging_level)
#             self._ch.setFormatter(formatter)
#             self._logger.addHandler(self._ch)

#     _logger = None
#     _name = None

#     def __init__(self, name, logging_level=None):
#         self.__class__._name = name
#         if not self.__class__._logger:
#             self.__class__._logger = BaseLogger._BaseLogger(
#                 self.__class__._name, logging_level)

#     @classmethod
#     def set_level(cls, logging_level=None):
#         class_exists = (cls._logger)
#         if not class_exists:
#             raise AttributeError("Instantiate class first to set the level")
#         name_exists = (cls._name is not None)
#         level_is_different = (cls._logger._logging_level != logging_level)
#         if class_exists:
#             if name_exists:
#                 cls._logger.set_level(logging_level)

#     @classmethod
#     def debug(cls, msg=None):
#         if cls._logger is None or msg is None:
#             pass
#         else:
#             cls._logger._logger.debug(msg)

#     @classmethod
#     def info(cls, msg=None):
#         if cls._logger is None or msg is None:
#             pass
#         else:
#             cls._logger._logger.info(msg)

#     @classmethod
#     def warning(cls, msg=None):
#         if cls._logger is None or msg is None:
#             pass
#         else:
#             cls._logger._logger.warning(msg)

#     @classmethod
#     def error(cls, msg=None):
#         if cls._logger is None or msg is None:
#             pass
#         else:
#             cls._logger._logger.error(msg)

#     @classmethod
#     def critical(cls, msg=None):
#         if cls._logger is None or msg is None:
#             pass
#         else:
#             cls._logger._logger.critical(msg)


# class CoreLog(BaseLogger):
#     def __init__(self, logging_level=None):
#         super().__init__("CORE", logging_level)

# class SimulationLog(BaseLogger):
#     def __init__(self, logging_level=None):
#         super().__init__("SIMULATION", logging_level)

# class BackendLog(BaseLogger):
#     def __init__(self, logging_level=None):
#         super().__init__("BACKEND", logging_level)
