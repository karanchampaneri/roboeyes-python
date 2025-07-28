"""
Animation sequence system for desktop RoboEyes implementation.

This module provides desktop-compatible versions of the StepData, Sequence, and Sequences
classes that use standard Python timing functions instead of MicroPython's timing system.
"""

from typing import Callable, List, Optional, Any
from .timing import ticks_ms, ticks_diff


class StepData:
    """
    Represents a single step in an animation sequence.
    
    Desktop-compatible version of the original StepData class that uses
    standard Python timing functions.
    """
    
    __slots__ = ["done", "ms_timing", "_lambda", "owner_seq"]
    
    def __init__(self, owner_seq: 'Sequence', ms_timing: int, _lambda: Callable):
        """
        Initialize a step in an animation sequence.
        
        Args:
            owner_seq: The Sequence that owns this step
            ms_timing: Timing in milliseconds when this step should execute
            _lambda: Function to execute when the step triggers
        """
        self.done = False
        self.ms_timing = ms_timing
        self._lambda = _lambda
        self.owner_seq = owner_seq
    
    def update(self, current_ticks: int) -> None:
        """
        Update the step and execute if timing conditions are met.
        
        Args:
            current_ticks: Current time in milliseconds
        """
        # Execute the _lambda if applicable then switch the flag
        if self.done:
            return
        
        if ticks_diff(current_ticks, self.owner_seq._start) < self.ms_timing:
            return
        
        # Execute the _lambda expression (with RoboEyes)
        self._lambda(self.owner_seq.owner)
        self.done = True


class Sequence(list):
    """
    A sequence is a collection of animation steps.
    
    Desktop-compatible version of the original Sequence class that uses
    standard Python timing functions.
    """
    
    def __init__(self, owner: Any, name: str):
        """
        Initialize an animation sequence.
        
        Args:
            owner: The RoboEyes instance that owns this sequence
            name: Name identifier for this sequence
        """
        super().__init__()
        self.owner = owner  # the RoboEyes class
        self.name = name
        self._start: Optional[int] = None
    
    def step(self, ms_timing: int, _lambda: Callable) -> None:
        """
        Add a step to the sequence at a given timing.
        
        Args:
            ms_timing: Timing in milliseconds when this step should execute
            _lambda: Function to execute when the step triggers
        """
        step_data = StepData(self, ms_timing, _lambda)
        self.append(step_data)
    
    def start(self) -> None:
        """Start the sequence by recording the start time."""
        self._start = ticks_ms()
    
    def reset(self) -> None:
        """Reset the animation sequence to its initial state."""
        self._start = None
        for step in self:
            step.done = False
    
    @property
    def done(self) -> bool:
        """
        Check if the sequence is complete.
        
        Returns:
            True if the sequence hasn't started or all steps are done
        """
        if self._start is None:
            return True
        return all(step.done for step in self)
    
    def update(self, current_ticks: int) -> None:
        """
        Update the sequence and execute any pending steps.
        
        Args:
            current_ticks: Current time in milliseconds
        """
        # Check if we have to execute a step
        if self._start is None:
            return
        
        # Update all incomplete steps
        for step in self:
            if not step.done:
                step.update(current_ticks)


class Sequences(list):
    """
    Collection of animation sequences.
    
    Desktop-compatible version of the original Sequences class that manages
    multiple animation sequences.
    """
    
    def __init__(self, owner: Any):
        """
        Initialize the sequences collection.
        
        Args:
            owner: The RoboEyes instance that owns these sequences
        """
        super().__init__()
        self.owner = owner  # the RoboEyes class
    
    def add(self, name: str) -> Sequence:
        """
        Add a new sequence to the collection.
        
        Args:
            name: Name identifier for the new sequence
            
        Returns:
            The newly created Sequence instance
        """
        sequence = Sequence(self.owner, name)
        self.append(sequence)
        return sequence
    
    @property
    def done(self) -> bool:
        """
        Check if all sequences are complete.
        
        Returns:
            True if all sequences are done
        """
        return all(seq.done for seq in self)
    
    def update(self) -> None:
        """Update all sequences and execute any pending steps."""
        current_ticks = ticks_ms()
        for seq in self:
            seq.update(current_ticks)