#!/usr/bin/env python3
"""
Performance optimization demonstration for desktop RoboEyes.

This script demonstrates the performance monitoring and optimization features,
including dirty rectangle updates, frame rate monitoring, and memory usage tracking.
"""

import sys
import os
import time
import threading

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.roboeyes.desktop_roboeyes import DesktopRoboEyes, DEFAULT, HAPPY, ANGRY, TIRED
from src.desktop.config import RoboEyesConfig
from src.desktop.logging import setup_logging, get_logger


def performance_stress_test(roboeyes):
    """
    Run a stress test to demonstrate performance optimizations.
    
    Args:
        roboeyes: DesktopRoboEyes instance
    """
    logger = get_logger()
    logger.info("Starting performance stress test...")
    
    # Test sequence: rapid mood changes and animations
    moods = [DEFAULT, HAPPY, ANGRY, TIRED]
    
    for i in range(20):  # 20 iterations of stress test
        # Rapid mood changes
        for mood in moods:
            roboeyes.mood = mood
            time.sleep(0.1)  # Brief pause
            
            # Trigger animations
            if i % 4 == 0:
                roboeyes.blink()
            elif i % 4 == 1:
                roboeyes.wink(left=True)
            elif i % 4 == 2:
                roboeyes.confuse()
            else:
                roboeyes.laugh()
            
            time.sleep(0.1)
        
        # Position changes
        positions = [1, 2, 3, 4, 5, 6, 7, 8, 0]  # N, NE, E, SE, S, SW, W, NW, CENTER
        for pos in positions:
            roboeyes.position = pos
            time.sleep(0.05)
    
    logger.info("Performance stress test completed")


def memory_usage_test(roboeyes):
    """
    Test memory usage during extended animation sequences.
    
    Args:
        roboeyes: DesktopRoboEyes instance
    """
    logger = get_logger()
    logger.info("Starting memory usage test...")
    
    # Enable auto-blinker and idle mode for continuous animation
    roboeyes.set_auto_blinker(True, interval=1, variation=2)
    roboeyes.set_idle_mode(True, interval=2, variation=3)
    
    # Log initial memory usage
    if hasattr(roboeyes, 'performance_monitor'):
        initial_summary = roboeyes.performance_monitor.get_performance_summary()
        logger.info(f"Initial memory usage: {initial_summary['avg_memory_mb']:.2f} MB")
    
    # Run for extended period
    start_time = time.time()
    duration = 30  # 30 seconds
    
    logger.info(f"Running continuous animation for {duration} seconds...")
    
    while time.time() - start_time < duration:
        # Occasional mood changes to create variety
        if int(time.time() - start_time) % 5 == 0:
            roboeyes.mood = (roboeyes.mood + 1) % 7
        
        time.sleep(0.1)
    
    # Log final memory usage
    if hasattr(roboeyes, 'performance_monitor'):
        final_summary = roboeyes.performance_monitor.get_performance_summary()
        logger.info(f"Final memory usage: {final_summary['avg_memory_mb']:.2f} MB")
        logger.info(f"Memory change: {final_summary['avg_memory_mb'] - initial_summary['avg_memory_mb']:.2f} MB")
    
    # Disable continuous animations
    roboeyes.set_auto_blinker(False)
    roboeyes.set_idle_mode(False)
    
    logger.info("Memory usage test completed")


def frame_rate_test(roboeyes):
    """
    Test frame rate consistency under different loads.
    
    Args:
        roboeyes: DesktopRoboEyes instance
    """
    logger = get_logger()
    logger.info("Starting frame rate consistency test...")
    
    # Test different frame rates
    test_rates = [20, 30, 60]
    
    for target_fps in test_rates:
        logger.info(f"Testing {target_fps} FPS target...")
        roboeyes.set_framerate(target_fps)
        
        # Run for a few seconds and measure actual FPS
        start_time = time.time()
        test_duration = 5  # 5 seconds
        
        while time.time() - start_time < test_duration:
            # Create some animation load
            if int((time.time() - start_time) * 10) % 20 == 0:
                roboeyes.blink()
            
            time.sleep(0.01)  # Small delay to prevent busy waiting
        
        # Log performance results
        if hasattr(roboeyes, 'performance_monitor'):
            summary = roboeyes.performance_monitor.get_performance_summary()
            logger.info(f"Target: {target_fps} FPS, Actual: {summary['avg_fps']:.1f} FPS")
    
    logger.info("Frame rate consistency test completed")


def dirty_rectangle_demo(roboeyes):
    """
    Demonstrate dirty rectangle optimization effectiveness.
    
    Args:
        roboeyes: DesktopRoboEyes instance
    """
    logger = get_logger()
    logger.info("Starting dirty rectangle optimization demo...")
    
    # Perform operations that should benefit from dirty rectangles
    operations = [
        ("Small blink", lambda: roboeyes.blink()),
        ("Left wink", lambda: roboeyes.wink(left=True)),
        ("Right wink", lambda: roboeyes.wink(right=True)),
        ("Position change", lambda: setattr(roboeyes, 'position', 3)),  # East
        ("Mood change", lambda: setattr(roboeyes, 'mood', HAPPY)),
    ]
    
    for operation_name, operation in operations:
        logger.info(f"Testing: {operation_name}")
        
        # Perform the operation
        operation()
        
        # Allow a moment for the operation to complete
        time.sleep(0.5)
        
        # Log efficiency if available
        if hasattr(roboeyes.fb, 'get_update_efficiency'):
            efficiency = roboeyes.fb.get_update_efficiency()
            logger.info(f"  Update efficiency: {efficiency:.1f}% of screen")
    
    logger.info("Dirty rectangle optimization demo completed")


def interactive_performance_demo():
    """
    Run an interactive performance demonstration.
    """
    # Set up logging
    setup_logging(debug=False)
    logger = get_logger()
    
    logger.info("Starting RoboEyes Performance Demonstration")
    
    try:
        # Create configuration optimized for performance testing
        config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=800,
            window_height=600,
            frame_rate=60,  # High frame rate for performance testing
            resizable=True,
            fullscreen=False
        )
        
        # Initialize RoboEyes with performance monitoring
        logger.info("Initializing RoboEyes with performance monitoring...")
        roboeyes = DesktopRoboEyes(config=config)
        
        # Enable performance display by default
        if hasattr(roboeyes, 'performance_monitor'):
            roboeyes.performance_monitor.toggle_performance_display()
            logger.info("Performance display enabled - press 'P' to toggle")
        
        logger.info("RoboEyes initialized successfully")
        logger.info("Performance demonstration controls:")
        logger.info("  1-7: Change moods")
        logger.info("  SPACE: Blink")
        logger.info("  Q/E: Wink left/right")
        logger.info("  C: Confuse")
        logger.info("  L: Laugh")
        logger.info("  P: Toggle performance display")
        logger.info("  H: Show help")
        logger.info("  ESC: Exit")
        
        # Start background performance tests
        def run_background_tests():
            """Run background performance tests."""
            time.sleep(5)  # Wait for initialization
            
            logger.info("Running automated performance tests...")
            
            # Run tests in sequence
            performance_stress_test(roboeyes)
            time.sleep(2)
            
            dirty_rectangle_demo(roboeyes)
            time.sleep(2)
            
            frame_rate_test(roboeyes)
            time.sleep(2)
            
            memory_usage_test(roboeyes)
            
            logger.info("All automated performance tests completed")
        
        # Start background tests in a separate thread
        test_thread = threading.Thread(target=run_background_tests, daemon=True)
        test_thread.start()
        
        # Run the main application loop
        roboeyes.run()
        
    except KeyboardInterrupt:
        logger.info("Performance demonstration interrupted by user")
    except Exception as e:
        logger.exception(f"Error in performance demonstration: {e}")
    finally:
        logger.info("Performance demonstration ended")


if __name__ == "__main__":
    interactive_performance_demo()