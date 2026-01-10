# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import threading
import typing
from os import linesep

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

finished_spans: typing.List[ReadableSpan] = []


class InMemorySpanExporter(SpanExporter):
    """Implementation of :class:`.SpanExporter` that stores spans in memory.

    This class can be used for testing purposes. It stores the exported spans
    in a list in memory that can be retrieved using the
    :func:`.get_finished_spans` method.
    """

    def __init__(self) -> None:
        self._finished_spans: typing.List[ReadableSpan] = finished_spans
        self._stopped = False
        self._lock = threading.Lock()
        print("finished spans id", id(self._finished_spans))

    def clear(self) -> None:
        """Clear list of collected spans."""
        with self._lock:
            self._finished_spans.clear()

    def get_finished_spans(self) -> typing.Tuple[ReadableSpan, ...]:
        """Get list of collected spans."""
        with self._lock:
            return tuple(self._finished_spans)

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        """Stores a list of spans in memory."""
        if self._stopped:
            return SpanExportResult.FAILURE
        with self._lock:
            self._finished_spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        """Shut downs the exporter.

        Calls to export after the exporter has been shut down will fail.
        """
        print("shutdown", len(self._finished_spans))
        self._stopped = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        print("force_flush", len(self._finished_spans))
        return True


class ConsoleSpanExporter(SpanExporter):
    """
    Implementation of :class:`SpanExporter` that prints spans to the console.

    This class can be used for diagnostic purposes. It prints the exported
    spans to the console STDOUT.
    """

    def __init__(
        self,
        service_name: str | None = None,
    ):
        import sys

        self.out = sys.stdout
        self.formatter = lambda span: span.to_json() + linesep
        self.service_name = service_name

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            self.out.write(self.formatter(span))
        self.out.flush()
        return SpanExportResult.SUCCESS

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
