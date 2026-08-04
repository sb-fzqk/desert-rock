import time
from tuner_engine import TunerEngine

# Observer function
def console_display_observer(note, target_freq, cents, detected_freq):
    if abs(cents) < 5:
        status = "In Tune"
    elif cents < 0:
        status = f"Flat ({cents:.1f} cents)"
    else:
        status = f"Sharp (+{cents:.1f} cents)"
    
    print(f"(Observer) Detected Frequency: {detected_freq:6.2f} Hz; \nNote: {note:<4}; \nStatus: {status} \n>---------<")

# Tuner instantiation
tuner = TunerEngine()

# Register observer
tuner.register_observer(console_display_observer)

# Start the engine
print("Starting engine thread... Pluck that string")
tuner.start()

# Main thread simulation
try:
    for i in range(10):
        time.sleep(1)
        print(f"Main thread doing other stuff... ({i + 1}s)")
except KeyboardInterrupt:
    print("\nKeyboard interrupt!")
finally:
    print("Stopping engine thread...")
    tuner.stop()