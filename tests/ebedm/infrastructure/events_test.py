from embedm.infrastructure.events import (
    EmbedmEvent,
    EventDispatcher,
    SessionComplete,
    SessionStarted,
)

_STARTED = SessionStarted(version="1.0", config_source="DEFAULT", input_type="file", output_type="stdout")
_COMPLETE = SessionComplete(ok_count=1, error_count=0, total_elapsed=0.5)


def test_subscribe_and_emit() -> None:
    dispatcher = EventDispatcher()
    received: list[EmbedmEvent] = []
    dispatcher.subscribe(SessionStarted, received.append)

    dispatcher.emit(_STARTED)

    assert received == [_STARTED]


def test_emit_with_no_subscribers_does_not_raise() -> None:
    dispatcher = EventDispatcher()
    dispatcher.emit(_STARTED)  # no subscribers — must not raise


def test_emit_calls_all_subscribers_in_registration_order() -> None:
    dispatcher = EventDispatcher()
    order: list[int] = []
    dispatcher.subscribe(SessionStarted, lambda _: order.append(1))
    dispatcher.subscribe(SessionStarted, lambda _: order.append(2))

    dispatcher.emit(_STARTED)

    assert order == [1, 2]


def test_emit_does_not_notify_wrong_type_subscriber() -> None:
    dispatcher = EventDispatcher()
    received: list[EmbedmEvent] = []
    dispatcher.subscribe(SessionStarted, received.append)

    dispatcher.emit(_COMPLETE)

    assert received == []


def test_emit_exact_type_only_parent_subscription_does_not_match() -> None:
    """Subscribing to EmbedmEvent does not receive subclass events."""
    dispatcher = EventDispatcher()
    received: list[EmbedmEvent] = []
    dispatcher.subscribe(EmbedmEvent, received.append)

    dispatcher.emit(_STARTED)

    assert received == []


def test_multiple_event_types_dispatched_independently() -> None:
    dispatcher = EventDispatcher()
    started: list[EmbedmEvent] = []
    complete: list[EmbedmEvent] = []
    dispatcher.subscribe(SessionStarted, started.append)
    dispatcher.subscribe(SessionComplete, complete.append)

    dispatcher.emit(_STARTED)
    dispatcher.emit(_COMPLETE)

    assert started == [_STARTED]
    assert complete == [_COMPLETE]
