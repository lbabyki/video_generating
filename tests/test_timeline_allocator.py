from decimal import Decimal

import pytest

from app.timeline_allocator import DeterministicTimelineAllocator, TimelineAllocationError, TIMELINE_ALLOCATOR_VERSION


@pytest.mark.parametrize("count", [7, 8, 9, 10])
def test_allocator_meets_duration_constraints_for_supported_scene_counts(count):
    allocation = DeterministicTimelineAllocator().allocate([Decimal("1")] * count, 45)
    assert len(allocation.durations) == count
    assert sum(allocation.durations) == 45
    assert all(3 <= duration <= 8 for duration in allocation.durations)
    assert all(isinstance(duration, int) for duration in allocation.durations)
    assert allocation.allocator_version == TIMELINE_ALLOCATOR_VERSION


def test_suggestions_that_are_too_large_or_small_are_clamped_by_allocator():
    allocator = DeterministicTimelineAllocator()
    high = allocator.allocate([10000] + [1] * 7, 45)
    low = allocator.allocate([0.00001] + [1] * 7, 45)
    assert high.durations[0] == 8
    assert low.durations[0] == 3
    for result in (high, low):
        assert sum(result.durations) == 45
        assert all(3 <= value <= 8 for value in result.durations)


def test_equal_weights_use_scene_order_for_largest_remainder_ties():
    result = DeterministicTimelineAllocator().allocate([4] * 8, 45)
    assert result.durations == (6, 6, 6, 6, 6, 5, 5, 5)


def test_missing_suggestions_fall_back_to_even_distribution_and_are_recorded():
    result = DeterministicTimelineAllocator().allocate([None] * 8, 45)
    assert result.durations == (6, 6, 6, 6, 6, 5, 5, 5)
    assert all(item["suggested_duration_seconds"] is None for item in result.provenance)
    assert all(item["adjustment_reason"] for item in result.provenance)


def test_allocator_is_repeatable_and_records_adjustment_reason():
    allocator = DeterministicTimelineAllocator()
    first = allocator.allocate([9, 5, 4, 3, 2, 1, 1, 1], 45)
    second = allocator.allocate([9, 5, 4, 3, 2, 1, 1, 1], 45)
    assert first == second
    assert first.provenance[0]["adjusted"] is True
    assert first.provenance[0]["adjustment_reason"]


@pytest.mark.parametrize(("suggestions", "target", "error_type"), [
    ([5] * 6, 45, "scene_count_infeasible"),
    ([5] * 11, 45, "scene_count_infeasible"),
    ([5] * 7, 20, "target_duration_infeasible"),
])
def test_allocator_reports_infeasible_inputs(suggestions, target, error_type):
    with pytest.raises(TimelineAllocationError) as caught:
        DeterministicTimelineAllocator().allocate(suggestions, target)
    assert caught.value.issue["type"] == error_type
