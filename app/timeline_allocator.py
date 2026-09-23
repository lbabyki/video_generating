"""Deterministic integer timeline allocation for planner candidates."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR
from typing import Sequence

TIMELINE_ALLOCATOR_VERSION = "largest-remainder-v1"
MIN_SCENE_SECONDS = 3
MAX_SCENE_SECONDS = 8
MIN_SCENES = 7
MAX_SCENES = 10


class TimelineAllocationError(ValueError):
    def __init__(self, message: str, *, error_type: str, scene_orders: list[int] | None = None):
        super().__init__(message)
        self.issue = {"loc": ["scenes"], "type": error_type, "msg": message}
        self.failed_scene_orders = scene_orders or []


@dataclass(frozen=True)
class TimelineAllocation:
    durations: tuple[int, ...]
    provenance: tuple[dict, ...]
    allocator_version: str = TIMELINE_ALLOCATOR_VERSION


class DeterministicTimelineAllocator:
    version = TIMELINE_ALLOCATOR_VERSION

    def allocate(self, suggestions: Sequence[Decimal | float | int | None], target_seconds: int = 45,
                 weights: Sequence[Decimal | float | int | None] | None = None) -> TimelineAllocation:
        count = len(suggestions)
        if not MIN_SCENES <= count <= MAX_SCENES:
            raise TimelineAllocationError(
                f"scene count {count} is outside the feasible range {MIN_SCENES}–{MAX_SCENES}",
                error_type="scene_count_infeasible",
                scene_orders=list(range(1, count + 1)),
            )
        minimum = count * MIN_SCENE_SECONDS
        maximum = count * MAX_SCENE_SECONDS
        if not minimum <= target_seconds <= maximum:
            raise TimelineAllocationError(
                f"target duration {target_seconds} seconds is infeasible for {count} scenes; allowed range is {minimum}–{maximum}",
                error_type="target_duration_infeasible",
                scene_orders=list(range(1, count + 1)),
            )

        declared_weights = list(weights) if weights is not None else [None] * count
        if len(declared_weights) != count:
            raise TimelineAllocationError("duration weights must match the scene count", error_type="duration_weight_count_mismatch")
        allocation_weights = [self._weight(weight if weight is not None else suggestion)
                              for suggestion, weight in zip(suggestions, declared_weights)]
        if not any(allocation_weights):
            allocation_weights = [Decimal(1)] * count
        allocated = [MIN_SCENE_SECONDS] * count
        remaining = target_seconds - minimum
        while remaining:
            active = [index for index, value in enumerate(allocated) if value < MAX_SCENE_SECONDS]
            active_weight = sum((allocation_weights[index] for index in active), Decimal(0))
            if active_weight == 0:
                active_weights = {index: Decimal(1) for index in active}
                active_weight = Decimal(len(active))
            else:
                active_weights = {index: allocation_weights[index] for index in active}

            ideal = {index: Decimal(remaining) * active_weights[index] / active_weight for index in active}
            saturated = [index for index in active if ideal[index] >= MAX_SCENE_SECONDS - allocated[index]]
            if saturated:
                for index in saturated:
                    capacity = MAX_SCENE_SECONDS - allocated[index]
                    allocated[index] += capacity
                    remaining -= capacity
                continue

            floors = {index: int(ideal[index].to_integral_value(rounding=ROUND_FLOOR)) for index in active}
            for index, seconds in floors.items():
                allocated[index] += seconds
                remaining -= seconds
            order = sorted(active, key=lambda index: (-(ideal[index] - floors[index]), index))
            for index in order:
                if remaining == 0:
                    break
                if allocated[index] < MAX_SCENE_SECONDS:
                    allocated[index] += 1
                    remaining -= 1

        provenance = []
        for order, (suggestion, declared_weight, duration) in enumerate(zip(suggestions, declared_weights, allocated), start=1):
            proposed = None if suggestion is None else float(suggestion)
            recorded_weight = self._weight(declared_weight)
            provenance.append({
                "scene_order": order,
                "suggested_duration_seconds": proposed,
                "duration_weight": float(recorded_weight) if recorded_weight else None,
                "final_duration_seconds": duration,
                "adjusted": proposed is None or Decimal(str(proposed)) != Decimal(duration),
                "adjustment_reason": self._reason(proposed, duration, recorded_weight),
            })
        return TimelineAllocation(tuple(allocated), tuple(provenance))

    @staticmethod
    def _weight(value: Decimal | float | int | None) -> Decimal:
        if value is None:
            return Decimal(0)
        try:
            parsed = Decimal(str(value))
        except Exception:
            return Decimal(0)
        return parsed if parsed.is_finite() and parsed > 0 else Decimal(0)

    @staticmethod
    def _reason(proposed: float | None, final: int, weight: Decimal | None = None) -> str | None:
        if proposed is None:
            if weight:
                return "No exact duration was suggested; compiler allocated integer seconds using the model duration weight."
            return "No duration suggestion; compiler distributed time evenly by largest remainder."
        if Decimal(str(proposed)) == Decimal(final):
            return None
        return "Compiler normalized the model suggestion to an integer timeline totaling the requested duration."
