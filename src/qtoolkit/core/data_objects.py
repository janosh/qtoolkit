from __future__ import annotations

import abc
from dataclasses import dataclass
from pathlib import Path

from qtoolkit.core.base import QBase, QEnum


class SubmissionStatus(QEnum):
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    JOB_ID_UNKNOWN = "JOB_ID_UNKNOWN"


@dataclass
class SubmissionResult(QBase):
    job_id: int | str | None = None
    step_id: int | None = None
    exit_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    status: SubmissionStatus | None = None


class CancelStatus(QEnum):
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    JOB_ID_UNKNOWN = "JOB_ID_UNKNOWN"


@dataclass
class CancelResult(QBase):
    job_id: int | str | None = None
    step_id: int | None = None
    exit_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    status: CancelStatus | None = None


class QState(QEnum):
    """Enumeration of possible ("standardized") job states.

    These "standardized" states are based on the drmaa specification.
    A mapping between the actual job states in a given
    queue manager (e.g. PBS, SLURM, ...) needs to be
    defined.

    Note that not all these standardized states are available in the
    actual queue manager implementations.
    """

    UNDETERMINED = "UNDETERMINED"
    QUEUED = "QUEUED"
    QUEUED_HELD = "QUEUED_HELD"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"
    REQUEUED = "REQUEUED"
    REQUEUED_HELD = "REQUEUED_HELD"
    DONE = "DONE"
    FAILED = "FAILED"


class QSubState(QEnum):
    """QSubState class defined without any enum values so it can be subclassed.

    These sub-states should be the actual job states in a given queuing system
    (e.g. PBS, SLURM, ...). This class is also extended to support multiple
    values for the same key.
    """

    def __new__(cls, *values):
        obj = object.__new__(cls)
        obj._value_ = values[0]
        for other_value in values[1:]:
            cls._value2member_map_[other_value] = obj
        obj._all_values = values
        return obj

    def __repr__(self):
        return "<{}.{}: {}>".format(
            self.__class__.__name__,
            self._name_,
            ", ".join([repr(v) for v in self._all_values]),
        )

    @property
    @abc.abstractmethod
    def qstate(self) -> QState:
        raise NotImplementedError


@dataclass
class QResources(QBase):
    """Data defining resources for a given job (submitted or to be submitted).

    Attributes
    ----------
    queue_name : str
        Name of the queue (or partition) used to submit a job or to which a job has
        been submitted.
    memory : int
        Maximum amount of memory requested for a job.
    nodes : int
        Number of nodes requested for a job.
    cpus_per_node : int
        Number of cpus for each node requested for a job.
    cores_per_cpu : int
        Number of cores for each cpu requested for a job.
    hyperthreading : int
        Number of threads to be used (hyperthreading).
        TODO: check this and how to combine with OpenMP environment. Also is it
         something that needs to be passed down somewhere to the queueing system
         (and thus, is it worth putting it here in the resources ?) ?
         On PBS (zenobe) if you use to many processes with respect
         to what you asked (in the case of a "shared" node), you get killed.
    """

    queue_name: str | None = None
    job_name: str | None = None
    memory_per_thread: int | None = 1024
    nodes: int | None = 1
    processes: int | None = 1
    processes_per_node: int | None = None
    threads_per_process: int | None = None
    time_limit: int | None = None
    account: str | None = None
    qos: str | None = None
    priority: int | str | None = None
    output_filepath: str | Path | None = None
    error_filepath: str | Path | None = None

    # TODO: how to allow heterogeneous resources (e.g. 1 node with 12 cores and
    #  1 node with 4 cores or heterogeneous memory requirements, e.g. "master"
    #  core needs more memory than the other ones)


@dataclass
class QJobInfo(QBase):
    memory: int | None = None  # in Kb
    memory_per_cpu: int | None = None  # in Kb
    nodes: int | None = None
    cpus: int | None = None
    threads_per_process: int | None = None
    time_limit: int | None = None


@dataclass
class QOptions(QBase):
    hold: bool | None = False
    account: str | None = None
    qos: str | None = None
    priority: int | None = None


@dataclass
class QJob(QBase):
    name: str | None = None
    job_id: str | None = None
    exit_status: int | None = None
    state: QState | None = None  # Standard
    sub_state: QSubState | None = None
    info: QJobInfo | None = None
    account: str | None = None
    runtime: int | None = None
    queue_name: str | None = None
