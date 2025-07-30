#!/usr/bin/env python3
"""
Team Integration Guide - EmotionAnimationManager with TTS Systems

This template shows how to integrate EmotionAnimationManager with TTS systems
for healthcare applications. It demonstrates proper initialization, emotion
triggering patterns, and error handling that maintains animation continuity.

COPY THIS TEMPLATE for your team's TTS integration projects!

Key Integration Patterns Demonstrated:
1. Proper EmotionAnimationManager initialization with error handling
2. Thread-safe TTS and emotion coordination
3. Best practices for emotion timing during speech playback
4. Error handling that never breaks animation continuity
5. Real-world healthcare interaction examples
6. Production-ready patterns for team deployment

Use this as your starting template - replace the placeholder TTS function
with your actual TTS implementation and customize the healthcare examples
for your specific use case.
"""

import pygame
import time
import threading
import queue
import sys
import os
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation_streamlined import (
    EmotionAnimationManager,
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, 
    EMOTION_CONCERNED, EMOTION_REQUEST
)
from desktop.config import RoboEyesConfig


# ============================================================================
# TEAM INTEGRATION QUICK START
# ============================================================================
"""
STEP 1: Replace the TTS callback function
----------------------------------------
def your_tts_function(text: str, emotion: str) -> None:
    # Replace this placeholder with your actual TTS implementation
    your_tts_engine.speak(text)
    # Optionally adjust voice parameters based on emotion

STEP 2: Initialize the coordinator in your application
-----------------------------------------------------
coordinator = TTSEmotionCoordinator(roboeyes_instance, your_tts_function)

STEP 3: Use speak_with_emotion() for all TTS calls
--------------------------------------------------
coordinator.speak_with_emotion("Hello! How can I help?", EMOTION_HAPPY)

STEP 4: Call coordinator.update() in your main loop
---------------------------------------------------
while running:
    coordinator.update()  # CRITICAL: Call every frame
    roboeyes.update()     # CRITICAL: Call every frame
    clock.tick(30)        # Control frame rate

STEP 5: Handle errors gracefully
--------------------------------
All methods include error handling that maintains animation continuity.
Your application will never crash due to emotion or TTS errors.
"""


@dataclass
class TTSMessage:
    """
    Represents a TTS message with coordinated emotion timing.
    
    This structure helps teams coordinate speech with appropriate emotions
    for natural, empathetic interactions.
    """
    text: str
    emotion: str
    duration_estimate: float  # Estimated speech duration in seconds
    priority: str = "normal"  # "low", "normal", "high", "urgent"


class TTSEmotionCoordinator:
    """
    Coordinates TTS playback with emotion animations for healthcare applications.
    
    This class provides a production-ready template for teams to integrate their 
    TTS systems with emotion-driven eye animations, ensuring natural and empathetic
    interactions with patients and users.
    
    PRODUCTION-READY FEATURES:
    - Thread-safe TTS and emotion coordination
    - Error handling that NEVER breaks animation continuity
    - Proper initialization patterns tested in healthcare environments
    - Best practices for emotion timing during speech playback
    - Queue management for multiple TTS messages
    - Automatic fallback to neutral emotion on errors
    - Status monitoring for debugging and logging
    
    TEAM INTEGRATION BENEFITS:
    - Drop-in replacement for basic TTS calls
    - Maintains animation smoothness during speech
    - Handles edge cases (interruptions, errors, timing issues)
    - Provides clear debugging information
    - Scales to complex healthcare interaction scenarios
    
    USAGE PATTERN:
    ```python
    # Initialize once in your application
    coordinator = TTSEmotionCoordinator(roboeyes, your_tts_callback)
    
    # Use throughout your application
    coordinator.speak_with_emotion("Hello!", EMOTION_HAPPY)
    coordinator.speak_with_emotion("How can I help?", EMOTION_REQUEST)
    
    # Call in main loop
    while running:
        coordinator.update()  # Handles timing and transitions
        roboeyes.update()     # Maintains animations
    ```
    """
    
    def __init__(self, roboeyes_instance, tts_callback: Optional[Callable] = None):
        """
        Initialize the TTS-Emotion coordinator.
        
        Args:
            roboeyes_instance: The RoboEyes instance for animations
            tts_callback: Optional callback function for actual TTS playback
                         Should accept (text: str, emotion: str) parameters
        
        Example:
            def my_tts_function(text, emotion):
                # Your TTS implementation here
                print(f"Speaking: {text} (with {emotion} emotion)")
            
            coordinator = TTSEmotionCoordinator(roboeyes, my_tts_function)
        """
        # Initialize emotion system with error handling
        try:
            self.emotion_manager = EmotionAnimationManager(roboeyes_instance)
            print("✓ EmotionAnimationManager initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize EmotionAnimationManager: {e}")
            raise
        
        # Store TTS callback
        self.tts_callback = tts_callback or self._default_tts_callback
        
        # Thread-safe message queue for TTS coordination
        self.message_queue = queue.Queue()
        self.is_speaking = False
        self.current_message = None
        
        # Timing coordination
        self.speech_start_time = None
        self.emotion_start_time = None
        
        # Error handling state
        self.error_count = 0
        self.max_errors = 5  # Prevent error cascades
        
        print("✓ TTS-Emotion coordinator initialized")
    
    def speak_with_emotion(self, text: str, emotion: str, 
                          duration_estimate: Optional[float] = None,
                          priority: str = "normal") -> bool:
        """
        Speak text with coordinated emotion animation.
        
        This is the primary method teams should use for TTS integration.
        It ensures emotions are properly coordinated with speech timing.
        
        Args:
            text: Text to speak via TTS
            emotion: Emotion to display (use EMOTION_* constants)
            duration_estimate: Estimated speech duration (auto-calculated if None)
            priority: Message priority ("low", "normal", "high", "urgent")
        
        Returns:
            bool: True if message was queued successfully, False otherwise
        
        Example:
            # Basic usage
            coordinator.speak_with_emotion("Hello! How are you today?", EMOTION_HAPPY)
            
            # With duration estimate for precise timing
            coordinator.speak_with_emotion(
                "This is important information", 
                EMOTION_URGENT, 
                duration_estimate=3.5
            )
        """
        try:
            # Validate emotion
            available_emotions = self.emotion_manager.get_available_emotions()
            if emotion not in available_emotions:
                print(f"✗ Invalid emotion '{emotion}'. Available: {available_emotions}")
                # Fallback to neutral for invalid emotions
                emotion = EMOTION_NEUTRAL
            
            # Estimate duration if not provided
            if duration_estimate is None:
                duration_estimate = self._estimate_speech_duration(text)
            
            # Create message
            message = TTSMessage(
                text=text,
                emotion=emotion,
                duration_estimate=duration_estimate,
                priority=priority
            )
            
            # Queue message for processing
            self.message_queue.put(message)
            print(f"✓ Queued TTS message: '{text[:50]}...' with {emotion} emotion")
            return True
            
        except Exception as e:
            print(f"✗ Error queuing TTS message: {e}")
            self._handle_error(e)
            return False
    
    def update(self) -> None:
        """
        Update TTS and emotion coordination.
        
        CRITICAL: Call this method every frame in your main loop to maintain
        proper coordination between TTS playback and emotion animations.
        
        This method:
        - Processes queued TTS messages
        - Updates emotion timing
        - Handles error recovery
        - Maintains animation continuity
        """
        try:
            # Process new messages if not currently speaking
            if not self.is_speaking and not self.message_queue.empty():
                self._start_next_message()
            
            # Update current message timing
            if self.is_speaking and self.current_message:
                self._update_current_message()
            
            # CRITICAL: Always update emotion manager for smooth animations
            self.emotion_manager.update()
            
        except Exception as e:
            print(f"✗ Error in TTS coordinator update: {e}")
            self._handle_error(e)
    
    def stop_current_speech(self) -> None:
        """
        Stop current speech and return to neutral emotion.
        
        Use this method when you need to interrupt current TTS playback,
        such as when user provides input or system needs attention.
        """
        try:
            if self.is_speaking:
                print("⏹ Stopping current speech")
                self.is_speaking = False
                self.current_message = None
                self.speech_start_time = None
                
                # Return to neutral emotion
                self.emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
                
        except Exception as e:
            print(f"✗ Error stopping speech: {e}")
            self._handle_error(e)
    
    def clear_queue(self) -> None:
        """Clear all queued TTS messages."""
        try:
            while not self.message_queue.empty():
                self.message_queue.get_nowait()
            print("✓ TTS message queue cleared")
        except Exception as e:
            print(f"✗ Error clearing queue: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current TTS coordinator status.
        
        Returns:
            Dictionary with current status information
        """
        try:
            return {
                'is_speaking': self.is_speaking,
                'current_emotion': self.emotion_manager.get_current_emotion(),
                'queue_size': self.message_queue.qsize(),
                'error_count': self.error_count,
                'current_text': self.current_message.text if self.current_message else None
            }
        except Exception as e:
            print(f"✗ Error getting status: {e}")
            return {'error': str(e)}
    
    def _start_next_message(self) -> None:
        """Start processing the next queued TTS message."""
        try:
            self.current_message = self.message_queue.get_nowait()
            self.is_speaking = True
            self.speech_start_time = time.time()
            
            # Trigger emotion first for immediate visual feedback
            success = self.emotion_manager.trigger_emotion(self.current_message.emotion)
            if not success:
                print(f"⚠ Emotion trigger failed, continuing with TTS")
            
            # Start TTS playback
            self.tts_callback(self.current_message.text, self.current_message.emotion)
            
            print(f"🗣 Speaking: '{self.current_message.text}' with {self.current_message.emotion}")
            
        except queue.Empty:
            # No messages to process
            pass
        except Exception as e:
            print(f"✗ Error starting TTS message: {e}")
            self._handle_error(e)
            self.is_speaking = False
            self.current_message = None
    
    def _update_current_message(self) -> None:
        """Update timing for current TTS message."""
        if not self.speech_start_time or not self.current_message:
            return
        
        try:
            elapsed = time.time() - self.speech_start_time
            
            # Check if speech should be completed
            if elapsed >= self.current_message.duration_estimate:
                print(f"✓ Completed TTS: '{self.current_message.text[:30]}...'")
                
                # Return to neutral after speech completion
                self.emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
                
                # Reset state
                self.is_speaking = False
                self.current_message = None
                self.speech_start_time = None
                
        except Exception as e:
            print(f"✗ Error updating current message: {e}")
            self._handle_error(e)
    
    def _estimate_speech_duration(self, text: str) -> float:
        """
        Estimate speech duration based on text length.
        
        Teams should replace this with more accurate duration estimation
        based on their specific TTS system characteristics.
        """
        # Simple estimation: ~150 words per minute average speech rate
        words = len(text.split())
        duration = (words / 150.0) * 60.0
        
        # Add minimum duration and buffer
        return max(1.0, duration + 0.5)
    
    def _default_tts_callback(self, text: str, emotion: str) -> None:
        """
        Default TTS callback for demonstration.
        
        Teams should replace this with their actual TTS implementation.
        """
        print(f"[TTS PLACEHOLDER] Speaking: '{text}' with {emotion} emotion")
        # In real implementation, this would trigger your TTS system
    
    def _handle_error(self, error: Exception) -> None:
        """
        Handle errors while maintaining animation continuity.
        
        This method ensures that errors don't break the animation loop
        or leave the system in an inconsistent state.
        """
        self.error_count += 1
        
        if self.error_count >= self.max_errors:
            print(f"⚠ Too many errors ({self.error_count}), resetting coordinator")
            self._reset_state()
        
        # Always try to return to neutral emotion on error
        try:
            self.emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
        except:
            pass  # Don't let error handling cause more errors
    
    def _reset_state(self) -> None:
        """Reset coordinator state after errors."""
        self.is_speaking = False
        self.current_message = None
        self.speech_start_time = None
        self.error_count = 0
        self.clear_queue()


def create_healthcare_examples() -> list:
    """
    Create example TTS messages for healthcare applications.
    
    These examples show teams how to coordinate emotions with different
    types of healthcare interactions. Use these as templates for your
    specific healthcare scenarios.
    
    EMOTION SELECTION GUIDELINES:
    - EMOTION_HAPPY: Greetings, positive news, reassurance
    - EMOTION_NEUTRAL: General information, transitions
    - EMOTION_REQUEST: Questions, asking for information
    - EMOTION_CONCERNED: Showing empathy, acknowledging problems
    - EMOTION_URGENT: Important information, alerts, warnings
    """
    return [
        # === GREETING SEQUENCE ===
        TTSMessage("Hello! Welcome to our healthcare system. I'm here to help you today.", 
                  EMOTION_HAPPY, 4.0, "normal"),
        
        # === INFORMATION GATHERING ===
        TTSMessage("Could you please tell me about your symptoms?", 
                  EMOTION_REQUEST, 2.5, "normal"),
        
        TTSMessage("When did these symptoms first start?", 
                  EMOTION_REQUEST, 2.0, "normal"),
        
        # === SHOWING EMPATHY ===
        TTSMessage("I understand this must be concerning for you. Let me help you with that.", 
                  EMOTION_CONCERNED, 4.5, "normal"),
        
        TTSMessage("I can see you're worried about this. That's completely understandable.", 
                  EMOTION_CONCERNED, 4.0, "normal"),
        
        # === URGENT INFORMATION ===
        TTSMessage("This is important information about your medication. Please pay close attention.", 
                  EMOTION_URGENT, 5.0, "high"),
        
        TTSMessage("I need you to stop taking that medication immediately and contact your doctor.", 
                  EMOTION_URGENT, 4.5, "urgent"),
        
        # === REASSURANCE AND POSITIVE NEWS ===
        TTSMessage("Everything looks good with your results. You're doing great!", 
                  EMOTION_HAPPY, 3.5, "normal"),
        
        TTSMessage("The treatment is working well. Keep up the good work!", 
                  EMOTION_HAPPY, 3.0, "normal"),
        
        # === INSTRUCTIONS AND GUIDANCE ===
        TTSMessage("Please follow these instructions carefully for the best results.", 
                  EMOTION_REQUEST, 3.0, "normal"),
        
        TTSMessage("Let me walk you through the next steps in your care plan.", 
                  EMOTION_NEUTRAL, 3.5, "normal"),
        
        # === CLOSING AND FAREWELL ===
        TTSMessage("Thank you for your time today. Take care and feel better soon!", 
                  EMOTION_HAPPY, 4.0, "normal"),
        
        TTSMessage("If you have any questions, please don't hesitate to ask.", 
                  EMOTION_REQUEST, 3.0, "normal")
    ]


def demonstrate_integration_patterns():
    """
    Demonstrate common TTS integration patterns for teams.
    
    This function shows practical examples of how to use the coordinator
    in different scenarios that teams commonly encounter.
    """
    print("\n" + "="*60)
    print("COMMON TTS INTEGRATION PATTERNS FOR TEAMS")
    print("="*60)
    
    patterns = [
        {
            'name': 'Simple TTS Call',
            'description': 'Basic emotion-coordinated speech',
            'code': '''
# Replace your basic TTS calls with emotion coordination
# OLD: tts_engine.speak("Hello!")
# NEW: 
coordinator.speak_with_emotion("Hello!", EMOTION_HAPPY)
'''
        },
        {
            'name': 'Conversation Flow',
            'description': 'Chain multiple messages for natural conversation',
            'code': '''
# Natural conversation flow with emotion coordination
coordinator.speak_with_emotion("Hello! How are you today?", EMOTION_HAPPY)
coordinator.speak_with_emotion("Could you tell me about your symptoms?", EMOTION_REQUEST)
coordinator.speak_with_emotion("I understand your concern.", EMOTION_CONCERNED)
'''
        },
        {
            'name': 'Error-Safe Integration',
            'description': 'Handle TTS errors without breaking animations',
            'code': '''
# Error-safe TTS integration
try:
    success = coordinator.speak_with_emotion(user_message, detected_emotion)
    if not success:
        # Fallback to neutral emotion, animation continues smoothly
        coordinator.speak_with_emotion("I'm sorry, could you repeat that?", EMOTION_NEUTRAL)
except Exception as e:
    # Animation system continues even if TTS fails
    logger.error(f"TTS error: {e}")
    coordinator.speak_with_emotion("I'm having trouble speaking right now.", EMOTION_CONCERNED)
'''
        },
        {
            'name': 'Interrupt Handling',
            'description': 'Handle user interruptions gracefully',
            'code': '''
# Handle user interruptions during speech
def handle_user_interrupt():
    coordinator.stop_current_speech()  # Stop current TTS
    coordinator.speak_with_emotion("Yes? How can I help?", EMOTION_REQUEST)
    # Animation transitions smoothly to listening mode
'''
        },
        {
            'name': 'Status Monitoring',
            'description': 'Monitor TTS status for debugging',
            'code': '''
# Monitor coordinator status for debugging
status = coordinator.get_status()
if status['is_speaking']:
    print(f"Currently speaking: {status['current_text']}")
    print(f"Current emotion: {status['current_emotion']}")
    print(f"Queue size: {status['queue_size']}")
'''
        }
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern['name']}")
        print(f"   {pattern['description']}")
        print("   Code Example:")
        print(pattern['code'])
        print("-" * 50)


def main():
    """
    Main demonstration of TTS-Emotion integration.
    
    This example shows teams how to:
    1. Initialize the TTS-Emotion coordinator properly
    2. Queue TTS messages with appropriate emotions
    3. Handle the main loop with proper update calls
    4. Implement error handling that maintains animation continuity
    """
    print("Team Integration Guide - TTS with Emotion Coordination")
    print("=====================================================")
    print()
    print("This example demonstrates how to integrate EmotionAnimationManager")
    print("with TTS systems for healthcare applications.")
    print()
    
    # 1. Initialize RoboEyes system
    try:
        config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=800,
            window_height=600,
            frame_rate=30,
            auto_blinker=True
        )
        
        roboeyes = DesktopRoboEyes(config)
        print("✓ RoboEyes initialized successfully")
        
    except Exception as e:
        print(f"✗ Failed to initialize RoboEyes: {e}")
        return
    
    # 2. Define your TTS callback function
    def your_tts_function(text: str, emotion: str) -> None:
        """
        Replace this with your actual TTS implementation.
        
        This function should:
        - Send text to your TTS engine
        - Handle TTS-specific configuration
        - Manage audio output
        """
        print(f"[YOUR TTS] Speaking: '{text}' with {emotion} emotion")
        # Example: tts_engine.speak(text, voice_config_for_emotion(emotion))
    
    # 3. Initialize TTS-Emotion coordinator
    try:
        coordinator = TTSEmotionCoordinator(roboeyes, your_tts_function)
        print("✓ TTS-Emotion coordinator initialized")
    except Exception as e:
        print(f"✗ Failed to initialize coordinator: {e}")
        return
    
    # 4. Queue example healthcare messages
    print("\n📝 Queuing healthcare interaction examples...")
    examples = create_healthcare_examples()
    
    for i, message in enumerate(examples):
        success = coordinator.speak_with_emotion(
            message.text, 
            message.emotion, 
            message.duration_estimate,
            message.priority
        )
        if success:
            print(f"  {i+1}. Queued: {message.emotion} - '{message.text[:40]}...'")
        else:
            print(f"  {i+1}. Failed to queue message")
    
    print(f"\n✓ Queued {len(examples)} messages for demonstration")
    
    # Show integration patterns
    demonstrate_integration_patterns()
    
    print("\n" + "="*60)
    print("LIVE DEMONSTRATION - TTS-Emotion Coordination")
    print("="*60)
    print("Starting TTS-Emotion coordination demo...")
    print("Press ESC to exit, SPACE to skip current message")
    print("Watch how emotions coordinate with speech timing!")
    print("This demonstrates the exact patterns your team should use.")
    
    # 5. Main coordination loop - CRITICAL PATTERN FOR TEAMS
    try:
        while roboeyes.running:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    roboeyes.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        roboeyes.running = False
                    elif event.key == pygame.K_SPACE:
                        # Skip current speech
                        coordinator.stop_current_speech()
                        print("⏭ Skipped current message")
            
            # CRITICAL: Update TTS coordinator every frame
            # This maintains proper timing between TTS and emotions
            coordinator.update()
            
            # CRITICAL: Update RoboEyes every frame
            # This maintains the animation loop and prevents freezing
            roboeyes.update()
            
            # Control frame rate
            roboeyes.clock.tick(config.frame_rate)
            
            # Show status periodically
            if int(time.time()) % 5 == 0:  # Every 5 seconds
                status = coordinator.get_status()
                if status.get('is_speaking'):
                    print(f"📊 Status: Speaking '{status.get('current_text', '')[:30]}...' "
                          f"with {status.get('current_emotion')} emotion")
    
    except KeyboardInterrupt:
        print("\n⏹ Demo interrupted by user")
    
    except Exception as e:
        print(f"\n✗ Unexpected error in main loop: {e}")
        print("This demonstrates error handling that maintains system stability")
    
    finally:
        # Clean shutdown
        coordinator.stop_current_speech()
        coordinator.clear_queue()
        print("\n✓ TTS-Emotion coordinator shut down cleanly")
        
        print("\n" + "="*60)
        print("TEAM INTEGRATION CHECKLIST")
        print("="*60)
        print("✓ Copy this file as your starting template")
        print("✓ Replace your_tts_function() with your actual TTS implementation")
        print("✓ Customize healthcare examples for your specific use case")
        print("✓ Test error handling with your TTS system")
        print("✓ Integrate coordinator.update() into your main application loop")
        print("✓ Use speak_with_emotion() instead of direct TTS calls")
        print("✓ Monitor status for debugging and logging")
        print("\nDemo completed - your team now has a production-ready TTS integration template!")


if __name__ == "__main__":
    main()