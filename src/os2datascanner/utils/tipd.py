import os
import sys
import code
import signal


def __debug_interrupt(globals):
    def __debug_interrupt_(sig, frame):
        in_fifo = f"/tmp/tipd.in.{os.getpid()}"
        out_fifo = f"/tmp/tipd.out.{os.getpid()}"

        print("*** INTERRUPTED ***\n"
                "Trivial in-process debugger running\n"
                f"\twrite to {in_fifo}\n\tread from {out_fifo}")

        os.mkfifo(in_fifo)
        os.mkfifo(out_fifo)
        try:
            context = {}
            with open(in_fifo, "rt") as in_fp, \
                    open(out_fifo, "wt") as out_fp:
                i, o, e = sys.stdin, sys.stdout, sys.stderr
                try:
                    sys.stdin, sys.stdout, sys.stderr = in_fp, out_fp, out_fp
                    code.interact(local=globals)
                finally:
                    sys.stdin, sys.stdout, sys.stderr = i, o, e
        finally:
            print("*** CONTINUING ***")
            os.unlink(in_fifo)
            os.unlink(out_fifo)
    return __debug_interrupt_


def install_debugger(local, signum=signal.SIGUSR2):
    """Installs an interrupt handler that runs a Python REPL over a pair of
    named pipes. When the REPL session ends, the named pipes will be unlinked,
    the interrupt handler will return, and normal execution of this process
    will continue.

    The local parameter specifies the environment of the REPL: this should
    usually be the result of calling globals().

    Named pipes are not bidirectional, so one pipe is used as the REPL's
    standard input stream and another is used as its standard output/error. To
    stitch these pipes together for a more familiar experience, use a shell
    invocation like this:

    $ cat /tmp/tipd.out.* & cat > /tmp/tipd.in.*

    Note that the REPL gives complete and unrestricted access to the Python
    context of this process -- only call this function with the system owner's
    informed consent."""
    return signal.signal(signum, __debug_interrupt(local))


__all__ = ("install_debugger",)
